#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Select and scan 20 library reading units for the daily literature-enrichment run.

This tool is deliberately read-only with respect to the site content.  It only
writes under ``_tmp/library-scan/<date>/`` and, with ``mark``, updates the
reading ledger under ``_reports/library-reading/``.

A "reading unit" is normally one chunk file from
``_unpublished/文库/manifest.json`` (``full.txt`` or ``part-00N.txt`` /
``0001-0200.txt``).  The 94 chunks are read round-robin across the 36 archived
works so that every work is sampled before any work gets a second pass.

The queue also contains abstract-only records from ``.sources/index.json``.
Those records have no library chunk, but their archived ``evidence`` quotes
carry the abstract text (``fulltext_status: abstract-no-oa`` or a locator such
as ``摘要`` / ``Abstract``).  They are selected as separate units and marked
``abstract_only`` so a draft never presents them as full-text reading.

Typical use::

    python _tools/library_scan.py --limit 20 --abstract 5
    python _tools/library_scan.py --limit 5 --focus taxonomy --date 2026-11-12
    python _tools/library_scan.py mark --date 2026-11-12

Outputs (UTF-8):
    units.json         the selected units, with source ids and absolute paths
    candidates.jsonl   every scored paragraph/taxon candidate
    top.json           the capped review shortlist
    top.md             a human-readable shortlist grouped by target page
    summary.json       counts and warnings
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "_unpublished" / "文库" / "manifest.json"
SOURCE_INDEX_PATH = ROOT / ".sources" / "index.json"
TAXONOMY_PATH = ROOT / "_data" / "taxonomy.json"
SPECIES_PATH = ROOT / "_data" / "species_by_genus.json"
NAME_ISSUES_PATH = ROOT / "_data" / "name_issues.json"
LITERATURE_PATH = ROOT / "_data" / "taxon_literature.json"
PROGRESS_PATH = ROOT / "_reports" / "library-reading" / "progress.json"
REFETCH_PATH = ROOT / "_reports" / "library-reading" / "refetch.json"


def load_refetch():
    """待重抓取队列：抽取失败／乱码／只有摘要的来源，下一轮优先重扫并重抓。"""
    data = load_json(REFETCH_PATH, {}) or {}
    items = data.get("items") or []
    return [item for item in items if item.get("status") == "pending" and item.get("id")]


FOCUS_ORDER = ["taxonomy", "morphology", "ecology"]

# English and Chinese claim keywords.  English is matched case-insensitively;
# Chinese is matched literally.  Weights steer the shortlist, they are not
# evidence of anything.
KEYWORDS = {
    "taxonomy": {
        "new species": 3.0, "new genus": 3.0, "new subgenus": 2.5,
        "sp. nov.": 3.0, "gen. nov.": 3.0, "subsp. nov.": 2.5,
        "synonym": 3.0, "syn.": 1.5, "synonymy": 2.5,
        "comb. nov.": 3.0, "new combination": 3.0, "combination": 1.5,
        "homonym": 3.0, "nomen novum": 3.0, "replacement name": 2.5,
        "type species": 2.0, "type locality": 1.5, "type specimen": 1.5,
        "subspecies": 1.5, "species group": 1.5, "genus group": 1.5,
        "distribution": 1.2, "geographic": 1.0, "record": 1.0,
        "revision": 2.0, "taxonomy": 2.0, "classification": 2.0,
        "phylogen": 1.2, "diagnosis": 1.2, "key to": 1.2,
        "described": 1.0, "description": 1.0, "named": 1.0,
        "新种": 3.0, "新属": 3.0, "新亚种": 2.5, "新记录": 2.5,
        "异名": 3.0, "同物异名": 3.0, "新组合": 3.0, "订正": 2.5,
        "分类": 2.0, "系统": 1.2, "分布": 1.2, "模式种": 2.0,
        "模式产地": 1.5, "亚种": 1.5, "属": 0.8, "科": 0.8,
        "命名": 1.5, "发表": 1.0, "记录": 1.0, "检索表": 1.2,
    },
    "morphology": {
        "morphology": 2.5, "diagnosis": 2.0, "description": 1.5,
        "head": 1.0, "mandible": 1.5, "antenna": 1.2, "pronotum": 1.5,
        "mesonotum": 1.0, "metanotum": 1.0, "tibia": 1.2, "tarsus": 1.0,
        "fontanelle": 1.5, "labrum": 1.0, "clypeus": 1.0, "postmentum": 1.2,
        "worker": 1.2, "soldier": 1.2, "alate": 1.2, "imago": 1.0,
        "nymph": 1.0, "caste": 1.2, "seta": 0.8, "setae": 0.8,
        "形态": 2.5, "鉴别": 2.0, "描述": 1.5, "头": 1.0, "上颚": 1.5,
        "触角": 1.2, "前胸背板": 1.5, "中胸背板": 1.0, "后胸背板": 1.0,
        "胫节": 1.2, "跗节": 1.0, "囟": 1.5, "上唇": 1.0, "唇基": 1.0,
        "后颏": 1.2, "工蚁": 1.2, "兵蚁": 1.2, "有翅成虫": 1.2,
        "若虫": 1.0, "品级": 1.2, "刚毛": 0.8, "毛": 0.6,
    },
    "ecology": {
        "nest": 2.0, "nesting": 2.0, "colony": 1.5, "feeding": 1.5,
        "diet": 1.5, "food": 1.2, "habitat": 1.5, "soil": 1.0,
        "wood": 1.0, "fungus": 1.5, "fungus garden": 2.5, "symbiont": 1.5,
        "gut": 1.2, "microbiome": 1.5, "foraging": 1.5, "swarming": 1.2,
        "dispersal": 1.2, "mound": 1.5, "carton": 1.2, "moisture": 1.0,
        "temperature": 1.0, "behavior": 1.2, "behaviour": 1.2,
        "巢": 2.0, "巢群": 1.5, "群体": 1.5, "食性": 1.5, "食物": 1.2,
        "生境": 1.5, "土壤": 1.0, "木材": 1.0, "真菌": 1.5, "菌圃": 2.5,
        "共生": 1.5, "肠道": 1.2, "微生物": 1.5, "觅食": 1.5,
        "分飞": 1.2, "扩散": 1.2, "蚁丘": 1.5, "纸巢": 1.2, "湿度": 1.0,
        "温度": 1.0, "行为": 1.2,
    },
}

STRONG_CHANGE_TERMS = (
    "synonym", "syn.", "comb. nov.", "new combination", "homonym",
    "nomen novum", "replacement name", "sp. nov.", "gen. nov.", "subsp. nov.",
    "异名", "同物异名", "新组合", "订正", "新种", "新属", "新亚种",
)

STOPWORDS = {
    "sp.", "spp.", "sp", "spp", "cf.", "cf", "aff.", "aff", "nr.", "nr",
    "and", "or", "of", "the", "in", "from", "with", "without", "new",
    "a", "an", "to", "for", "on", "by", "at", "as", "is", "are", "was",
    "were", "be", "been", "this", "that", "these", "those", "its", "their",
}
ROMAN_YEAR_RE = re.compile(r"\b(1[6-9]\d{2}|20\d{2})\b")
TOC_RE = re.compile(r"(\.{4,}|·{4,}|…{3,})")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-]*")
ABSTRACT_LOCATOR_RE = re.compile(r"摘要|abstract", re.IGNORECASE)


def load_json(path: Path, default=None):
    if not path.is_file():
        return default
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def norm_latin(value: str) -> str:
    value = (value or "").replace("×", " ").replace("—", " ").replace("–", " ")
    value = re.sub(r"[^A-Za-z\- ]+", " ", value)
    return " ".join(value.lower().split())


def latin_key(value: str) -> str:
    """Extract the bare binomen/trinomen, dropping author and year.

    ``Amitermes wheeleri (Desneux, 1906)`` -> ``amitermes wheeleri``
    ``Coptotermes formosanus shiraki`` -> the three words if the third is
    lowercase (a subspecies epithet), otherwise the first two.
    """
    raw = value or ""
    match = re.search(r"\b([A-Z][A-Za-z\-]+)\s+([a-z][A-Za-z\-]+)(?:\s+([a-z][A-Za-z\-]+))?", raw)
    if match:
        parts = [p.lower() for p in match.groups() if p]
        return " ".join(parts)
    return norm_latin(raw)


def norm_path(value: str) -> str:
    return (value or "").replace("\\", "/")


def fold_text(value: str) -> str:
    return value.casefold()


class Trie:
    """A tiny prefix trie for Chinese names and claim keywords."""

    def __init__(self):
        self.root = {}

    def add(self, key: str, payload):
        if not key:
            return
        node = self.root
        for ch in key:
            node = node.setdefault(ch, {})
        node["$"] = payload

    def scan(self, text: str):
        """Yield (start, end, payload, key) for non-overlapping longest matches."""
        i = 0
        n = len(text)
        while i < n:
            node = self.root
            j = i
            best = None
            best_key = None
            while j < n and text[j] in node:
                node = node[text[j]]
                j += 1
                if "$" in node:
                    best = node["$"]
                    best_key = text[i:j]
            if best is not None:
                yield i, j, best, best_key
                i = j
            else:
                i += 1


def build_keyword_trie():
    trie = Trie()
    for focus, words in KEYWORDS.items():
        for word, weight in words.items():
            trie.add(word.casefold(), (focus, word, weight))
    return trie


def build_taxonomy():
    taxonomy = load_json(TAXONOMY_PATH, {})
    species_data = load_json(SPECIES_PATH, {})
    pages = {}
    genera = {}
    latin_genus = {}
    latin_species = {}
    zh_names = {}

    for fam in taxonomy.get("families", []):
        url = "/family/%s/" % fam["id"]
        info = {"url": url, "rank": "family", "id": fam["id"],
                "latin": fam.get("latin", ""), "zh": fam.get("zh", "")}
        pages[url] = info
        if fam.get("zh"):
            zh_names[fam["zh"]] = info

    for sub in taxonomy.get("subfamilies", []):
        url = "/subfamily/%s/" % sub["id"]
        info = {"url": url, "rank": "subfamily", "id": sub["id"],
                "latin": sub.get("latin", ""), "zh": sub.get("zh", ""),
                "family": sub.get("family", "")}
        pages[url] = info
        if sub.get("zh"):
            zh_names[sub["zh"]] = info

    for gen in taxonomy.get("genera", []):
        url = "/genus/%s/" % gen["id"]
        info = {"url": url, "rank": "genus", "id": gen["id"],
                "latin": gen.get("latin", ""), "zh": gen.get("zh", ""),
                "family": gen.get("family", ""), "subfamily": gen.get("subfamily", "")}
        pages[url] = info
        genera[gen["id"]] = info
        latin_genus[norm_latin(gen.get("latin", ""))] = info
        if gen.get("zh"):
            zh_names[gen["zh"]] = info

    for genus_id, items in species_data.items():
        if genus_id == "_meta" or not isinstance(items, list):
            continue
        gen = genera.get(genus_id, {})
        for sp in items:
            url = sp.get("url") or "/species/%s/" % sp.get("slug", "")
            if not url.startswith("/"):
                url = "/" + url
            if not url.endswith("/"):
                url += "/"
            info = {"url": url, "rank": "species", "id": sp.get("slug", ""),
                    "latin": sp.get("latin", ""), "zh": sp.get("zh", ""),
                    "genus_id": genus_id, "family": gen.get("family", ""),
                    "subfamily": gen.get("subfamily", "")}
            pages[url] = info
            key = latin_key(sp.get("latin", ""))
            if key and len(key.split()) >= 2:
                latin_species[key] = info
            if sp.get("zh"):
                zh_names[sp["zh"]] = info

    return pages, genera, latin_genus, latin_species, zh_names


def build_aliases(pages, latin_species):
    """Map old / synonym names in _data/name_issues.json to current pages."""
    issues = load_json(NAME_ISSUES_PATH, {})
    alias_names = {}  # normalized latin -> current page info
    by_slug = {p.get("id"): p for p in pages.values() if p.get("rank") == "species"}

    for pair in issues.get("synonym_pairs", []):
        our = pair.get("our") or {}
        slug = our.get("slug")
        target = by_slug.get(slug)
        if not target:
            continue
        raw_names = [
            (pair.get("external") or {}).get("latin"),
            (pair.get("external") or {}).get("name"),
            (pair.get("receiving") or {}).get("latin"),
            (pair.get("receiving") or {}).get("name"),
        ]
        for raw in raw_names:
            key = latin_key(raw)
            if key and len(key.split()) >= 2:
                alias_names.setdefault(key, target)

    for slug, entry in (issues.get("species_authority") or {}).items():
        target = by_slug.get(slug)
        if not target:
            continue
        for bucket in ("incoming", "outgoing"):
            for item in entry.get(bucket, []) or []:
                for raw in (item.get("latin"), item.get("name")):
                    key = latin_key(raw)
                    if key and len(key.split()) >= 2:
                        alias_names.setdefault(key, target)
    return alias_names


def build_alias_token_map(alias_names):
    out = defaultdict(list)
    for key, target in alias_names.items():
        words = tuple(key.split())
        if 2 <= len(words) <= 4:
            out[words].append(target)
    return out


def build_zh_trie(zh_names):
    trie = Trie()
    for name, info in zh_names.items():
        if len(name) >= 2:
            trie.add(name, info)
    return trie


def source_for_work(work, records):
    book = work.get("book", "")
    for rec in records:
        lib = rec.get("library")
        if isinstance(lib, dict) and lib.get("book") == book:
            return rec
    for rec in records:
        if rec.get("canonical_key") == "library:%s" % book:
            return rec
    for rec in records:
        fp = norm_path(rec.get("file_path", ""))
        if fp.rstrip("/").endswith("/" + book):
            return rec
    return None


def resolve_chunk_path(work, chunk):
    raw = chunk.get("out")
    if raw:
        path = ROOT / norm_path(raw)
        if path.is_file():
            return path
    fallback = ROOT / "_unpublished" / "文库" / work["book"] / (str(chunk.get("chunk")) + ".txt")
    if fallback.is_file():
        return fallback
    return None


def select_units(limit, records, progress, pending=None):
    manifest = load_json(MANIFEST_PATH, {})
    pending = pending or set()
    works = manifest.get("books") or []
    units = []
    for wi, work in enumerate(works):
        for ci, chunk in enumerate(work.get("chunks") or []):
            path = resolve_chunk_path(work, chunk)
            if not path:
                continue
            key = "%s::%s" % (work["book"], chunk.get("chunk"))
            rec = source_for_work(work, records)
            units.append({
                "key": key,
                "book": work["book"],
                "chunk": chunk.get("chunk"),
                "chunk_index": ci,
                "work_order": wi,
                "path": path,
                "chars": int(chunk.get("chars") or 0),
                "source_id": rec.get("id") if rec else None,
                "source_title": rec.get("title") if rec else None,
            })

    def sort_key(u):
        state = (progress.get("units") or {}).get(u["key"], {})
        # 新单元优先：先读得少的，同次数时先读最久没碰过的。
        # 待重抓取（refetch）只做标记，不改变选单元顺序——抓新论文优先，重抓不是。
        return (int(state.get("reads", 0)), state.get("last_read") or "",
                u["chunk_index"], u["work_order"])

    units.sort(key=sort_key)
    return units[:limit]


def abstract_text(record):
    """Reconstruct the archived abstract from verbatim evidence quotes.

    The OpenAlex-derived records split one abstract across several quotes of
    up to 400 characters, often in the middle of a word.  Join a lower-case
    continuation directly; insert a space only where the split is a real word
    boundary.  This is a reading aid, not a new quotation: the original
    fragments remain the authoritative record in ``.sources``.
    """
    quotes = []
    for item in record.get("evidence") or []:
        locator = item.get("locator") or ""
        if not ABSTRACT_LOCATOR_RE.search(locator):
            continue
        quote = (item.get("quote") or "").strip()
        if quote:
            quotes.append(quote)
    if not quotes:
        return ""
    text = quotes[0]
    for quote in quotes[1:]:
        if text.endswith("-") or (text and text[-1].isalnum() and quote[:1].islower()):
            text += quote
        else:
            text += " " + quote
    return re.sub(r"\s+", " ", text).strip()


def is_abstract_record(record):
    if record.get("library"):
        return False
    if record.get("fulltext_status") == "abstract-no-oa":
        return True
    return any(
        ABSTRACT_LOCATOR_RE.search(item.get("locator") or "")
        for item in (record.get("evidence") or [])
    )


def abstract_is_relevant(record):
    """Keep termite/Isoptera abstracts, not papers that merely mention termites.

    A chimpanzee diet paper or a lizard ecology paper can contain termite genus
    names in its abstract without being a termite study.  Requiring a termite
    signal in the title (or an order name in the opening lines) keeps those out
    of the enrichment queue.
    """
    title = record.get("title") or ""
    opening = abstract_text(record)[:320]
    pattern = re.compile(r"termit|terme|isoptera|blattodea|dictyoptera|白蚁|等翅目", re.IGNORECASE)
    return bool(pattern.search(title) or pattern.search(opening))


def select_abstract_units(limit, records, progress, pending=None):
    """Select abstract-only source records, least-read first (refetch queue first)."""
    pending = pending or set()
    units = []
    for idx, record in enumerate(records):
        if not is_abstract_record(record):
            continue
        if not abstract_is_relevant(record):
            continue
        text = abstract_text(record)
        if len(text) < 80:
            continue
        rid = record.get("id") or ""
        if not rid:
            continue
        key = "abstract:%s" % rid
        units.append({
            "key": key,
            "kind": "abstract",
            "book": record.get("title") or rid,
            "chunk": "摘要",
            "chunk_index": 0,
            "work_order": 10000 + idx,
            "path": None,
            "chars": len(text),
            "source_id": rid,
            "source_title": record.get("title"),
            "source_year": record.get("year"),
            "text": text,
            "locator": "摘要 / %s" % (record.get("title") or rid),
            "abstract_only": True,
        })

    def sort_key(u):
        state = (progress.get("units") or {}).get(u["key"], {})
        # 同上：refetch 只标记，不插队。
        return (int(state.get("reads", 0)), state.get("last_read") or "", u["source_id"])

    units.sort(key=sort_key)
    return units[:limit]


def read_paragraphs(path: Path):
    """Yield (start_line, end_line, text) paragraphs with line numbers."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    buf = []
    start = None
    end = None

    def flush():
        nonlocal buf, start, end
        if not buf:
            return None
        block = "\n".join(buf).strip()
        result = (start, end, block) if block else None
        buf = []
        start = None
        end = None
        return result

    for lineno, line in enumerate(lines, 1):
        if line.strip():
            if start is None:
                start = lineno
            end = lineno
            buf.append(line.rstrip())
            # Many extracted books have no blank lines between paragraphs.
            # Cut at a line boundary once the block is long enough for prose.
            if sum(len(part) + 1 for part in buf) >= 2200:
                item = flush()
                if item:
                    yield item
        else:
            item = flush()
            if item:
                yield item

    item = flush()
    if item:
        yield item


def split_long_paragraph(start, end, text, max_chars=1800):
    if len(text) <= max_chars:
        return [(start, end, text)]
    # Split at sentence boundaries, keeping the same line locator.  This loses
    # the exact line of each fragment, so the locator points at the paragraph.
    pieces = re.split(r"(?<=[。！？!?])\s+|(?<=\.)\s+(?=[A-Z])", text)
    out = []
    buf = ""
    for piece in pieces:
        if not piece:
            continue
        if buf and len(buf) + len(piece) > max_chars:
            out.append((start, end, buf.strip()))
            buf = ""
        buf += piece
    if buf.strip():
        out.append((start, end, buf.strip()))
    return out


def paragraph_ok(text):
    if len(text) < 90 or len(text) > 4000:
        return False
    if TOC_RE.search(text):
        return False
    if text.count("\ufffd") > 2:
        return False
    letters = sum(1 for ch in text if ch.isalpha())
    if letters < 45:
        return False
    upper = sum(1 for ch in text if ch.isupper())
    if letters and upper / letters > 0.62:
        return False
    return True


def score_paragraph(text, focus, kw_trie, tax_matches, has_year, alias_flag):
    score = 0.0
    hits = Counter()
    for _start, _end, payload, key in kw_trie.scan(text.casefold()):
        kfocus, _word, weight = payload
        if kfocus != focus:
            continue
        hits[key] += 1
        score += weight
    # Diminishing returns for repeated words.
    if hits:
        score -= sum(max(0, count - 2) * 0.4 for count in hits.values())
    if has_year:
        score += 0.35
    if alias_flag:
        score += 0.4
    ranks = {m["rank"] for m in tax_matches}
    if "species" in ranks:
        score += 1.2
    elif "genus" in ranks:
        score += 0.9
    elif "subfamily" in ranks:
        score += 0.6
    elif "family" in ranks:
        score += 0.4
    strong = sum(1 for term in STRONG_CHANGE_TERMS if term.casefold() in text.casefold())
    score += min(strong, 3) * 1.0
    if len(text) < 160:
        score -= 0.8
    return score, hits


def match_taxa(text, genus_map, species_map, alias_token_map, zh_trie):
    matches = {}
    tokens = list(WORD_RE.finditer(text))

    def add(info, via, alias=False):
        entry = matches.setdefault(info["url"], {
            "url": info["url"], "rank": info["rank"], "latin": info.get("latin", ""),
            "zh": info.get("zh", ""), "via": set(), "alias": False,
        })
        entry["via"].add(via)
        if alias:
            entry["alias"] = True

    for idx, match in enumerate(tokens):
        word = match.group(0)
        low = word.lower()
        gen = genus_map.get(low)
        if gen:
            seq = [low]
            j = idx + 1
            while j < len(tokens) and len(seq) < 3:
                nxt = tokens[j].group(0).lower()
                if nxt in STOPWORDS or len(nxt) < 2:
                    break
                seq.append(nxt)
                j += 1
            matched_species = None
            for n in (3, 2):
                key = " ".join(seq[:n])
                if key in species_map:
                    matched_species = species_map[key]
                    break
            if matched_species:
                add(matched_species, "latin")
                add(gen, "latin")
                gen_page = gen.get("url")
                # Keep the genus entry explicitly, even though the species
                # entry's page already carries its genus_id.
                if not gen_page:
                    pass
            else:
                add(gen, "latin")

        for n in (4, 3, 2):
            if idx + n > len(tokens):
                continue
            key = tuple(tokens[idx + k].group(0).lower() for k in range(n))
            for target in alias_token_map.get(key, []):
                add(target, "alias", alias=True)

    for _start, _end, info, _key in zh_trie.scan(text):
        add(info, "zh")

    return list(matches.values())


def make_candidate(unit, focus, page, paragraph, score, hits, date, has_lit):
    start, end, text = paragraph
    digits = hashlib.sha1(("%s|%s|%s|%s" % (page["url"], unit["key"], start, text[:80])).encode("utf-8")).hexdigest()[:12]
    if unit.get("kind") == "abstract":
        locator = unit.get("locator") or "摘要"
    else:
        locator = "第 %s–%s 行 / %s.txt" % (start, end, unit["chunk"])
    return {
        "id": digits,
        "date": date,
        "unit": unit["key"],
        "book": unit["book"],
        "chunk": unit["chunk"],
        "source_id": unit["source_id"],
        "focus": focus,
        "locator": locator,
        "abstract_only": bool(unit.get("abstract_only")),
        "page_url": page["url"],
        "rank": page["rank"],
        "latin": page.get("latin", ""),
        "zh": page.get("zh", ""),
        "score": round(score, 2),
        "keywords": [k for k, _ in hits.most_common(8)],
        "has_literature": bool(has_lit.get(page["url"])),
        "text": text,
        "text_chars": len(text),
    }


def scan(limit, focus_arg, date, top_n, abstract_limit=5):
    records = (load_json(SOURCE_INDEX_PATH, {}) or {}).get("sources", [])
    progress = load_json(PROGRESS_PATH, {}) or {"version": 1, "units": {}}
    pages, genera, latin_genus, latin_species, zh_names = build_taxonomy()
    alias_names = build_aliases(pages, latin_species)
    alias_token_map = build_alias_token_map(alias_names)
    zh_trie = build_zh_trie(zh_names)
    kw_trie = build_keyword_trie()
    has_lit = load_json(LITERATURE_PATH, {}) or {}

    abstract_pool = sum(
        1 for rec in records
        if is_abstract_record(rec) and abstract_is_relevant(rec) and len(abstract_text(rec)) >= 80
    )
    abstract_target = min(max(0, abstract_limit), max(0, limit))
    refetch_items = load_refetch()
    pending = {item["id"] for item in refetch_items}
    abstract_units = select_abstract_units(abstract_target, records, progress, pending)
    chunk_units = select_units(max(0, limit - len(abstract_units)), records, progress, pending)
    units = chunk_units + abstract_units
    all_candidates = []
    warnings = []
    scanned_chars = 0
    # 待重抓取（refetch）不插队：先按正常顺序选满本轮单元；还没被选中的，
    # 追加在本轮单元之后（不占 20 个名额），保证重抓一定发生。
    missing_refetch = sorted(pending - {u.get("source_id") for u in units})
    if missing_refetch:
        have_keys = {u["key"] for u in units}
        extra = []
        for u in select_units(10 ** 6, records, progress, pending):
            sid = u.get("source_id")
            if sid in missing_refetch and u["key"] not in have_keys:
                extra.append(u)
                missing_refetch.remove(sid)
            if not missing_refetch or len(extra) >= 3:
                break
        for u in extra:
            u["extra"] = True
            units.append(u)
        if extra:
            print("本轮追加待重抓取单元（不插队，排在 20 个单元之后）：%s" % "、".join(
                "%s（%s）" % (u.get("source_id"), (u.get("source_title") or "")[:40]) for u in extra))
    for unit in units:
        if unit.get("source_id") in pending:
            unit["refetch"] = True
    if missing_refetch:
        warnings.append("refetch pending but not selected: %s" % ", ".join(missing_refetch))

    genus_by_id = {g["id"]: g for g in genera.values()}

    for unit in units:
        state = (progress.get("units") or {}).get(unit["key"], {})
        reads = int(state.get("reads", 0))
        if focus_arg == "auto":
            focus = FOCUS_ORDER[reads % len(FOCUS_ORDER)]
        else:
            focus = focus_arg
        unit["focus"] = focus
        unit["pass"] = reads + 1
        if unit.get("kind") == "abstract":
            text = unit.get("text") or ""
            if not text:
                warnings.append("abstract %s has no usable text" % unit["source_id"])
                continue
            # The abstract may omit the taxon name that the title carries.
            # Keep the title in the matched block so genus/species pages can
            # still be identified, and so the reviewer sees what was read.
            title = (unit.get("source_title") or "").strip()
            block = ("%s. %s" % (title, text)) if title and title not in text else text
            blocks = [(1, 1, block)]
        else:
            try:
                text = unit["path"].read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                warnings.append("cannot read %s: %s" % (unit["path"], exc))
                continue
            blocks = read_paragraphs(unit["path"])
        scanned_chars += len(text)
        unit_seen = 0
        for start, end, block in blocks:
            pieces = split_long_paragraph(start, end, block)
            for piece in pieces:
                if not paragraph_ok(piece[2]):
                    continue
                tax_matches = match_taxa(piece[2], latin_genus, latin_species, alias_token_map, zh_trie)
                if not tax_matches:
                    continue
                if len(tax_matches) > 18:
                    # Long checklists are poor prose sources.
                    continue
                has_year = bool(ROMAN_YEAR_RE.search(piece[2]))
                alias_flag = any(m.get("alias") for m in tax_matches)
                score, hits = score_paragraph(piece[2], focus, kw_trie, tax_matches,
                                               has_year, alias_flag)
                # Abstracts are short and often omit taxonomy keywords; a
                # genuine genus/species match is enough for a lead there.
                min_score = 0.8 if unit.get("kind") == "abstract" else 2.0
                if score < min_score:
                    continue
                # Promote each species to a companion genus candidate.
                expanded = list(tax_matches)
                seen_urls = {m["url"] for m in expanded}
                for m in tax_matches:
                    if m["rank"] == "species":
                        gid = m.get("genus_id")
                        gen = genus_by_id.get(gid)
                        if gen and gen["url"] not in seen_urls:
                            expanded.append({"url": gen["url"], "rank": "genus",
                                             "latin": gen.get("latin", ""),
                                             "zh": gen.get("zh", ""),
                                             "via": {"species-context"}, "alias": False})
                            seen_urls.add(gen["url"])
                for page in expanded:
                    p_score = score
                    if page["rank"] == "genus" and page["url"] not in {x["url"] for x in tax_matches}:
                        p_score -= 0.7
                    if page["rank"] in ("family", "subfamily"):
                        p_score -= 0.5
                    if has_lit.get(page["url"]):
                        p_score -= 0.6
                    cand = make_candidate(unit, focus, page, piece, p_score, hits, date, has_lit)
                    cand["alias"] = bool(alias_flag)
                    all_candidates.append(cand)
                    unit_seen += 1
        unit["candidates"] = unit_seen

    # Deduplicate by page + normalized paragraph.
    dedup = {}
    for cand in all_candidates:
        key = (cand["page_url"], re.sub(r"\s+", "", cand["text"]).casefold()[:240])
        if key not in dedup or cand["score"] > dedup[key]["score"]:
            dedup[key] = cand
    all_candidates = list(dedup.values())
    # Reserve the head of ``top`` for abstract-only units: otherwise their
    # short, low-keyword paragraphs are crowded out by long book chunks and the
    # reviewer never sees the abstracts that the daily quota required reading.
    all_candidates.sort(key=lambda c: (
        0 if c.get("abstract_only") else 1,
        -c["score"], c["unit"], c["page_url"],
    ))

    # Caps: at most 4 per unit, 3 per page, top_n overall.
    per_unit = Counter()
    per_page = Counter()
    top = []
    for cand in all_candidates:
        if per_unit[cand["unit"]] >= 4:
            continue
        if per_page[cand["page_url"]] >= 3:
            continue
        top.append(cand)
        per_unit[cand["unit"]] += 1
        per_page[cand["page_url"]] += 1
        if len(top) >= top_n:
            break

    out_dir = ROOT / "_tmp" / "library-scan" / date
    out_dir.mkdir(parents=True, exist_ok=True)

    def public_unit(unit):
        item = {k: v for k, v in unit.items() if k not in ("path", "text")}
        if unit.get("path"):
            item["path"] = str(unit["path"])
        return item

    dump_json(out_dir / "units.json", [public_unit(u) for u in units])
    dump_json(out_dir / "top.json", top)
    dump_json(out_dir / "summary.json", {
        "date": date,
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "focus": focus_arg,
        "units_requested": limit,
        "units_selected": len(units),
        "chunk_units": len(chunk_units),
        "abstract_units": len(abstract_units),
        "abstract_pool": abstract_pool,
        "abstract_without_candidates": sum(
            1 for u in units if u.get("kind") == "abstract" and u.get("candidates") == 0
        ),
        "units_scanned": sum(1 for u in units if u.get("candidates") is not None),
        "chars_scanned": scanned_chars,
        "candidates_total": len(all_candidates),
        "top_count": len(top),
        "pages": len(per_page),
        "focus_counts": dict(Counter(c["focus"] for c in top)),
        "rank_counts": dict(Counter(c["rank"] for c in top)),
        "source_counts": dict(Counter(c["source_id"] for c in top)),
        "refetch_pending": sorted(pending),
        "refetch_included": [u.get("source_id") for u in units if u.get("refetch")],
        "refetch_extra": [u.get("source_id") for u in units if u.get("extra")],
        "warnings": warnings,
    })
    with (out_dir / "candidates.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for cand in all_candidates:
            fh.write(json.dumps(cand, ensure_ascii=False) + "\n")
    write_top_md(out_dir / "top.md", top, units)
    return out_dir, top, units, warnings


def write_top_md(path, top, units):
    lines = ["# 文库扫描候选（%s）" % datetime.now().strftime("%Y-%m-%d"), ""]
    lines.append("共 %d 条候选，来自 %d 个阅读单元。" % (len(top), len(units)))
    lines.append("")
    by_page = defaultdict(list)
    for cand in top:
        by_page[cand["page_url"]].append(cand)
    for url in sorted(by_page):
        items = by_page[url]
        lines.append("## `%s` — %s %s" % (url, items[0]["rank"], items[0]["latin"]))
        lines.append("")
        for cand in items:
            label = " · 据摘要" if cand.get("abstract_only") else ""
            lines.append("- **%s** · %s · %s · 分数 %.2f%s" % (
                cand["source_id"], cand["book"], cand["locator"], cand["score"], label))
            lines.append("  - " + cand["text"].replace("\n", " ")[:360].strip() + "…")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def mark_read(date):
    out_dir = ROOT / "_tmp" / "library-scan" / date
    units_path = out_dir / "units.json"
    if not units_path.is_file():
        print("找不到 %s；先运行扫描。" % units_path, file=sys.stderr)
        return 2
    units = load_json(units_path, [])
    progress = load_json(PROGRESS_PATH, {}) or {"version": 1, "units": {}}
    progress.setdefault("units", {})
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    for unit in units:
        state = progress["units"].setdefault(unit["key"], {"reads": 0, "last_read": None, "history": []})
        state["reads"] = int(state.get("reads", 0)) + 1
        state["last_read"] = now
        state.setdefault("history", []).append({
            "date": date,
            "focus": unit.get("focus"),
            "source_id": unit.get("source_id"),
        })
    progress["updated"] = now
    progress["version"] = 1
    dump_json(PROGRESS_PATH, progress)
    print("已登记 %d 个阅读单元，账本：%s" % (len(units), PROGRESS_PATH))
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    p_scan = sub.add_parser("scan", help="扫描阅读单元（默认）")
    p_scan.add_argument("--limit", type=int, default=20, help="阅读单元总数（默认 20）")
    p_scan.add_argument("--abstract", type=int, default=5,
                        help="其中仅摘要记录的条数（默认 5；其余为文库 chunk）")
    p_scan.add_argument("--focus", choices=FOCUS_ORDER + ["auto"], default="auto")
    p_scan.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    p_scan.add_argument("--top", type=int, default=120, help="候选上限（默认 120）")
    p_mark = sub.add_parser("mark", help="把某日扫描单元登记为已读")
    p_mark.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))

    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)
    if not argv or argv[0] not in ("scan", "mark", "-h", "--help"):
        argv = ["scan"] + argv
    args = parser.parse_args(argv)
    if args.command == "mark":
        return mark_read(args.date)
    out_dir, top, units, warnings = scan(args.limit, args.focus, args.date, args.top, args.abstract)
    print("输出目录：%s" % out_dir)
    print("阅读单元：%d（chunk %d + 摘要 %d）；候选：%d（top）" % (
        len(units),
        sum(1 for u in units if u.get("kind") != "abstract"),
        sum(1 for u in units if u.get("kind") == "abstract"),
        len(top),
    ))
    if warnings:
        print("警告：")
        for w in warnings[:10]:
            print("  - " + w)
    pending = [u for u in units if u.get("refetch")]
    if pending:
        print("本轮选中单元中的待重抓取来源（不插队；追加在本轮末尾的标 extra）：%s" % ", ".join(
            "%s（%s）%s" % (u.get("source_id"), (u.get("source_title") or "")[:40],
                            "·extra" if u.get("extra") else "") for u in pending))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
