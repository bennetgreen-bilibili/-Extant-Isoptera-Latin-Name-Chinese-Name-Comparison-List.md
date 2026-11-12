#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate unique, indexable body text for every _species/*.md page.

Why: _layouts/species.html renders a fixed <dl> fact table plus {{ content }},
and 3042 of the 3071 species pages have an empty {{ content }}. Search engines
therefore see 3000+ templated, near-duplicate pages and index none of them.

What: this script turns the existing front matter (latin / zh / author_year /
type_locality / distribution / synonyms / subspecies) plus isoptera-data.json
and data/index.json (genus & family counts, type species, data file paths)
into ~600-2000 characters of factual prose per page.

How (safety):
  * Idempotent: the generated text lives between the AUTO markers below;
    everything outside the markers is never touched.
  * No invented facts: every sentence restates an existing field.
  * No new URLs: the page count stays exactly 3071.
  * Dry-run by default; --write is required to modify files.

Usage:
  python build_species_body.py                          # stats only, no writes
  python build_species_body.py --sample SLUG [SLUG..]   # print generated body
  python build_species_body.py --write                  # rewrite _species/*.md
  python build_species_body.py --check-idempotent       # second pass identical?
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "_species"
DATA_JSON = ROOT / "isoptera-data.json"
INDEX_JSON = ROOT / "data" / "index.json"
CONFIG = ROOT / "_config.yml"
ETYMOLOGY_JSON = ROOT / "_data" / "etymology.json"
FAUNA_JSON = ROOT / "_data" / "fauna_species.json"
MORPH_JSON = ROOT / "_data" / "morphology_species.json"
TRANS_JSON = {"en": ROOT / "_data" / "translations_en.json", "es": ROOT / "_data" / "translations_es.json"}
LANG_DIRS = {"en": ROOT / "en" / "species", "es": ROOT / "es" / "species"}

BEGIN = "<!-- AUTO:BEGIN -->"
END = "<!-- AUTO:END -->"
SITE = "{{ site.base_url }}"
FM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)[ \t]*:[ \t]*(.*)$")
AUTHOR_YEAR_RE = re.compile(r"^(?P<author>.+?),\s*(?P<year>\d{4})")
SYN_AUTHOR_RE = re.compile(
    r"^(?P<name>.+?)\s+(?P<auth>[A-Z][A-Za-z\u00C0-\u024F.'&-]*"
    r"(?:\s*&\s*[A-Z][A-Za-z\u00C0-\u024F.'&-]*)?,\s*\d{4}.*)$"
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- front matter
def parse_front_matter(text):
    """Minimal YAML parser for the flat, single-line front matter used here."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = {}
    for line in text[3:end].splitlines():
        m = FM_RE.match(line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
            raw = raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        elif len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
            raw = raw[1:-1].replace("''", "'")
        data[key] = raw
    return data


def split_doc(text):
    """Return (front_matter_dict, head, body, newline). head is byte-exact."""
    nl = "\r\n" if "\r\n" in text else "\n"
    if not text.startswith("---"):
        return {}, "", text, nl
    m = re.match(r"^---\r?\n(?P<fm>.*?)\r?\n---[ \t]*(\r?\n)?", text, re.S)
    if not m:
        return {}, "", text, nl
    head = text[: m.start()] + "---" + nl + m.group("fm") + nl + "---"
    return parse_front_matter("---\n" + m.group("fm") + "\n---"), head, text[m.end():], nl


# ------------------------------------------------------------------ data model
def walk_tree(node):
    yield node
    for child in node.get("children") or []:
        yield from walk_tree(child)
    for sub in node.get("subfamilies") or []:
        yield sub


def load_meta():
    data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    index = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    fam_counts, fam_file, sub_file, sub_counts = {}, {}, {}, {}
    for node in walk_tree(index["tree"]):
        if node.get("type") == "family":
            fam_counts[node["id"]] = node.get("counts") or {}
            fam_file[node["id"]] = node.get("file")
        elif node.get("type") == "subfamily":
            sub_file[node["id"]] = node.get("file")
            sub_counts[node["id"]] = node.get("counts") or {}
    clades = {c["id"]: c for c in index.get("clades") or []}
    genus = {}
    for fam in data["families"]:
        buckets = list(fam.get("genera") or []) 
        for sub in fam.get("subfamilies") or []:
            buckets += list(sub.get("genera") or [])
        for g in buckets:
            genus[g["id"]] = {
                "zh": g.get("zh", ""), "latin": g.get("latin", ""),
                "species_count": g.get("species_count") or len(g.get("species") or []),
                "type_species": (g.get("type_species") or "").strip(),
            }
    return {
        "version": index.get("version", ""),
        "published": index.get("datePublished", ""),
        "modified": index.get("dateModified", ""),
        "creator": (index.get("creator") or {}).get("name", ""),
        "clades": clades,
        "family_clade": index.get("familyClade") or {},
        "fam_counts": fam_counts,
        "fam_file": fam_file,
        "sub_file": sub_file,
        "sub_counts": sub_counts,
        "genus": genus,
    }


def site_base_url():
    url = baseurl = ""
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(url|baseurl):\s*(\S.*)$", line)
        if m:
            val = m.group(2).strip().strip('"').strip("'")
            if m.group(1) == "url":
                url = val
            else:
                baseurl = val
    return (url + baseurl).rstrip("/")


# ----------------------------------------------------------------- text helpers
def clean(value):
    return (value or "").strip()


MD_SPECIAL = str.maketrans({"[": r"\[", "]": r"\]", "`": r"\`"})


def md_escape(value):
    """Escape markdown-significant characters coming from source data.

    The source data contains stray unbalanced brackets (e.g. a truncated
    "[incorrectly given as Tripolitana by Sjöstedt"); left raw they can turn
    the rest of the paragraph into a link or swallow text.
    """
    return clean(value).translate(MD_SPECIAL)


def strip_orphan_parens(value):
    s = clean(value)
    while s and s[-1] in "）)" and s.count("）") + s.count(")") > s.count("（") + s.count("("):
        s = s[:-1].rstrip()
    return s


def split_top(value):
    """Split on 、；; at paren depth 0 (CJK and ASCII parens both nest)."""
    items, buf, depth = [], [], 0
    for ch in value:
        if ch in "（(":
            depth += 1
        elif ch in "）)":
            depth = max(0, depth - 1)
        if ch in "、；;" and depth == 0:
            item = "".join(buf).strip()
            if item:
                items.append(item)
            buf = []
        else:
            buf.append(ch)
    item = "".join(buf).strip()
    if item:
        items.append(item)
    if len(items) == 1 and "，" in items[0]:
        items = [x.strip() for x in re.split(r"[，,]", items[0]) if x.strip()]
    return items


def parse_distribution(value):
    """Return (native_items, introduced_items, notes); source strings are dirty."""
    native, introduced, notes = [], [], []
    for item in split_top(strip_orphan_parens(value)):
        item = item.strip(" 。.;；")
        if not item or item in {"?", "-", "—"}:
            continue
        if re.match(r"^引入\s*[:：]?\s*", item):
            item = re.sub(r"^引入\s*[:：]?\s*", "", item)
            if item:
                introduced.append(md_escape(item))
        elif item in {"原产", "原生"}:
            continue
        elif re.search(r"广布|随木材|随贸易|随货物|为害|传入", item):
            notes.append(md_escape(item))
        else:
            native.append(md_escape(item))
    return native, introduced, notes


def join_zh(items):
    return "、".join(items)


def name_author_year(value):
    m = AUTHOR_YEAR_RE.match(clean(value))
    if m:
        return m.group("author").strip(), m.group("year")
    return clean(value), ""


def split_synonym(entry):
    """Coptotermes formosae Holmgren, 1911: 192 -> (name, author+year+ref).

    Taxon name = genus token, optional parenthetical subgenus, then the
    lowercase specific (and optional subspecific) epithets; everything after is
    the author citation. Falls back to the first two tokens.
    """
    entry = re.sub(r"\(\s+", "(", entry)
    entry = re.sub(r"\s+\)", ")", entry)
    entry = re.sub(r"\s+", " ", entry).strip()
    tokens = entry.split(" ")
    if len(tokens) < 2:
        return entry, ""
    name_tokens, i = [tokens[0]], 1
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("(") and tok.endswith(")"):
            name_tokens.append(tok)
            i += 1
        elif tok == "(":
            parts = ["("]
            i += 1
            while i < len(tokens) and tokens[i] != ")":
                parts.append(tokens[i])
                i += 1
            if i < len(tokens):
                parts.append(")")
                i += 1
            name_tokens[-1] += "".join(parts)
        elif re.match(r"^[a-z\u00C0-\u024F][a-z\u00C0-\u024F-]*$", tok):
            name_tokens.append(tok)
            i += 1
        else:
            break
    if len(name_tokens) < 2:
        return " ".join(tokens[:2]), " ".join(tokens[2:])
    return " ".join(name_tokens), " ".join(tokens[i:])


def parse_list(value):
    return [x.strip() for x in clean(value).split(";") if x.strip()]


# 外部权威库补录的异名：front matter 的 authority_synonym_sources 用这几个代码
AUTHORITY_LABELS = {
    "gbif": "GBIF",
    "col": "Catalogue of Life",
    "bsf": "Blattodea Species File",
}


def authority_labels(value):
    """gbif,col,bsf -> "GBIF · Catalogue of Life · Blattodea Species File"。

    front matter 里多来源用逗号分隔（分号留给多个异名之间的分隔）；未知代码忽略、去重保序。
    """
    labels = []
    for code in re.split(r"[,;]", clean(value)):
        label = AUTHORITY_LABELS.get(code.strip().lower())
        if label and label not in labels:
            labels.append(label)
    return " · ".join(labels)


# ----------------------------------------------------------------- generators
def html_link(label, path):
    return "[%s](%s%s)" % (label, SITE, path)


def html_text(value):
    """放进原始 HTML 段落的文本：只转义会破坏标签的三个字符。"""
    return clean(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pick_es(entry):
    """_data/etymology.json 条目的 es 字段；缺失 / 非字符串一律视为没有（绝不回落英文）。"""
    value = (entry or {}).get("es")
    return value.strip() if isinstance(value, str) else ""


def classify(rank, is_type, genus_info):
    if rank == "subspecies":
        return "一个亚种"
    if genus_info and genus_info.get("species_count") == 1:
        return "现存唯一种"
    if is_type:
        return "一种，也是本属的模式种"
    return "一种"


def strip_cjk_parens(value):
    """Remove Chinese parentheticals so a locality can appear on an en/es page."""
    value = re.sub(r"[（(][^）)]*[\u4e00-\u9fff][^）)]*[）)]", "", value or "")
    return re.sub(r"\s+", " ", value).strip()


def build_body(fm, meta, subs_of_parent, parent_fm, lang="zh"):
    if lang == "zh":
        return build_body_zh(fm, meta, subs_of_parent, parent_fm)
    return build_body_foreign(fm, meta, subs_of_parent, parent_fm, lang)


CJK_RUN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")
CJK_NOTE_RE = re.compile(r"[（(][^（）()\n]*[\u4e00-\u9fff][^（）()\n]*[）)]")


def sanitize_foreign(text):
    """Remove Chinese glosses and full-width punctuation from en / es prose."""
    prev = None
    while prev != text:
        prev = text
        text = CJK_NOTE_RE.sub("", text)
    for src, dst in (("（", " ("), ("）", ") "), ("、", ", "), ("：", ": "),
                     ("；", "; "), ("，", ", "), ("。", ". "), ("！", "! "),
                     ("？", "? "), ("「", '"'), ("」", '"')):
        text = text.replace(src, dst)
    text = CJK_RUN_RE.sub("", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"[ \t]+([,.;:)])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def build_body_zh(fm, meta, subs_of_parent, parent_fm):
    latin = clean(fm.get("latin"))
    zh = clean(fm.get("zh"))
    rank = (clean(fm.get("rank")) or "species").lower()
    is_type = str(fm.get("type", "")).strip().lower() == "true"
    family_zh, family_latin = clean(fm.get("family_zh")), clean(fm.get("family_latin"))
    sub_zh, sub_latin = clean(fm.get("subfamily_zh")), clean(fm.get("subfamily_latin"))
    genus_zh, genus_latin = clean(fm.get("genus_zh")), clean(fm.get("genus_latin"))
    family_id, sub_id, genus_id = clean(fm.get("family_id")), clean(fm.get("subfamily_id")), clean(fm.get("genus_id"))
    clade_latin = clean(fm.get("clade_latin"))
    author_year = clean(fm.get("author_year"))
    author, year = name_author_year(author_year)
    type_locality = md_escape(fm.get("type_locality"))
    genus_info = meta["genus"].get(genus_id) or {}
    gcount = genus_info.get("species_count") or 0
    fam = meta["fam_counts"].get(family_id) or {}
    lines = []

    rank_word = "亚种" if rank == "subspecies" else "种"
    fam_phrase = "%s（%s）" % (family_zh, family_latin)
    if sub_zh:
        fam_phrase += "%s（%s）" % (sub_zh, sub_latin)

    # ---- 摘要 -------------------------------------------------------------
    if rank == "subspecies":
        parent_zh, parent_latin = clean(fm.get("parent_zh")), clean(fm.get("parent_latin"))
        lead = "**%s**（*%s*）是%s（*%s*）的一个亚种，隶属%s%s（*%s*）" % (
            zh, latin, parent_zh, parent_latin, fam_phrase, genus_zh, genus_latin)
    else:
        klass = classify(rank, is_type, genus_info)
        lead = "**%s**（*%s*）是%s%s（*%s*）的%s" % (
            zh, latin, fam_phrase, genus_zh, genus_latin, klass)

    sents = [lead + "。"]
    if author and year:
        sents.append("本%s由 %s 于 %s 年描述，模式产地为 %s。" % (
            rank_word, author, year, type_locality or "未记录"))
    elif author_year:
        sents.append("本%s的命名信息为 %s，模式产地为 %s。" % (
            rank_word, author_year, type_locality or "未记录"))

    native, introduced, notes = parse_distribution(fm.get("distribution_zh"))
    parent_native, _, _ = parse_distribution((parent_fm or {}).get("distribution_zh"))
    own_dist = bool(native or introduced or notes)
    if own_dist:
        if native:
            sents.append("分布记录包括%s。" % join_zh(native))
        if introduced:
            sents.append("另有记录显示其已引入%s。" % join_zh(introduced))
        if notes:
            sents.append("文献另注：%s。" % "；".join(notes))
    elif parent_fm:
        sents.append("本页暂无单列的分布记录，母种 *%s* 的分布见下文「分布」一节。" % clean(parent_fm.get("latin")))

    syn_count = clean(fm.get("synonym_count"))
    if syn_count.isdigit() and int(syn_count) > 0:
        sents.append("本站记录本%s有 %s 个次异名。" % (rank_word, syn_count))
    lines += ["## 摘要", "", "".join(sents)]

    # ---- 词源 -------------------------------------------------------------
    ety = meta.get("etymology") or {}
    ety_gen = (ety.get("genera") or {}).get(genus_id)
    _parts = latin.split()
    epithet = _parts[-1].lower() if _parts else ""
    ety_epi = (ety.get("epithets") or {}).get(epithet)
    if ety_gen or ety_epi:
        lines += ["", "## 词源", ""]
        if ety_gen:
            lines.append("属名 *%s*：%s" % (genus_latin, md_escape(ety_gen.get("zh") or "")))
            lines.append("")
        if ety_epi:
            lines.append("种加词 *%s*：%s" % (epithet, md_escape(ety_epi.get("zh") or "")))
            lines.append("")
        lines.append("<!-- src:S0018 -->")

    # ---- 分类位置 ---------------------------------------------------------
    lines += ["", "## 分类位置", ""]
    fam_stat = ""
    if fam:
        _fg, _fs = fam.get("genera", "?"), fam.get("species", "?")
        fam_stat = " —— 本站收录 %s 属 %s 种" % (_fg, _fs)
    lines.append("- **科**：%s%s" % (
        html_link("%s %s" % (family_zh, family_latin), "/family/%s/" % family_id), fam_stat))
    if sub_zh and sub_id:
        sub_stat = ""
        sc = meta["sub_counts"].get(sub_id) or {}
        if sc:
            _sg, _ss = sc.get("genera", "?"), sc.get("species", "?")
            sub_stat = " —— 本站收录 %s 属 %s 种" % (_sg, _ss)
        lines.append("- **亚科**：%s%s" % (
            html_link("%s %s" % (sub_zh, sub_latin), "/subfamily/%s/" % sub_id), sub_stat))
    if rank == "subspecies":
        lines.append("- **属**：%s —— %s" % (
            html_link("%s *%s*" % (genus_zh, genus_latin), "/genus/%s/" % genus_id),
            "单型属，仅含 1 种" if gcount == 1 else "共 %s 种" % gcount))
        lines.append("- **种**：%s" % html_link(
            "%s *%s*" % (clean(fm.get("parent_zh")), clean(fm.get("parent_latin"))),
            "/species/%s/" % clean(fm.get("parent_slug"))))
        lines.append("- **亚种**：本页（*%s*）" % latin)
    else:
        genus_desc = "单型属，仅含 1 种" if gcount == 1 else "共 %s 种" % gcount
        lines.append("- **属**：%s —— %s" % (
            html_link("%s *%s*" % (genus_zh, genus_latin), "/genus/%s/" % genus_id), genus_desc))
        ts = genus_info.get("type_species")
        if ts and ts != latin:
            lines.append("- **本属模式种**：*%s*" % ts)

    # ---- 分布 -------------------------------------------------------------
    if own_dist:
        lines += ["", "## 分布", ""]
        if native:
            lines.append("- **分布记录**：%s" % join_zh(native))
        if introduced:
            lines.append("- **引入记录**：%s" % join_zh(introduced))
        if notes:
            lines.append("- **补充记录**：%s" % "；".join(notes))
        lines += ["", "以上记录沿用原始数据的写法，未做地理编码与译名统一。"]
    elif parent_fm:
        lines += ["", "## 分布", ""]
        parent_zh = join_zh(parent_native) or "未记录"
        lines.append("本亚种暂未单列分布记录；母种 *%s* 的分布为：%s。" % (
            clean(parent_fm.get("latin")), parent_zh))

    # ---- 次异名 -----------------------------------------------------------
    syns = parse_list(fm.get("synonyms"))
    locs = parse_list(fm.get("synonym_localities"))
    authority_syns = parse_list(fm.get("authority_synonyms"))
    if syns or authority_syns:
        lines += ["", "## 次异名", ""]
    if syns:
        n_syn = len(syns)
        lines.append("本站记录本%s有 %d 个次异名（junior synonyms），按原始文献出处列出：" % (rank_word, n_syn))
        lines.append("")
        for i, entry in enumerate(syns, 1):
            name, auth = split_synonym(entry)
            loc = md_escape(locs[i - 1]) if i - 1 < len(locs) else ""
            tail = " —— 模式产地：%s" % loc if loc else ""
            lines.append("%d. *%s* %s%s" % (i, name, auth, tail))
        old_names = "、".join("*%s*" % split_synonym(s)[0] for s in syns[:8])
        if len(syns) > 1:
            lines += ["", "在旧文献、地方名录与数据库检索中，本%s可能以上述异名（%s 等）出现，本站统一归入 *%s*。"
                      % (rank_word, old_names, latin)]
        else:
            lines += ["", "在旧文献、地方名录与数据库检索中，本%s可能以异名 %s 出现，本站统一归入 *%s*。"
                      % (rank_word, old_names, latin)]

    # ---- 依外部权威库补录的异名 -------------------------------------------
    if authority_syns:
        authority_locs = parse_list(fm.get("authority_synonym_localities"))
        authority_srcs = parse_list(fm.get("authority_synonym_sources"))
        lines += ["", "### 依外部权威库补录的异名", ""]
        lines.append("外部权威库在命名对照中把下列名字记为本%s的异名，已补录在案；本名录中它们另有独立记录，是否合并待定：" % rank_word)
        lines.append("")
        for i, entry in enumerate(authority_syns):
            name, auth = split_synonym(entry)
            loc = md_escape(authority_locs[i]) if i < len(authority_locs) else ""
            src = authority_labels(authority_srcs[i]) if i < len(authority_srcs) else ""
            tail = " —— 模式产地：%s" % loc if loc else ""
            suffix = "（%s）" % src if src else ""
            lines.append("- *%s* %s%s%s" % (name, auth, suffix, tail))

    # ---- 亚种 -------------------------------------------------------------
    subs = subs_of_parent.get(latin) or []
    if subs:
        n_sub = len(subs)
        lines += ["", "## 亚种", ""]
        lines.append("本种下分 %d 个亚种：" % n_sub)
        lines.append("")
        for sub in subs:
            extra = []
            if sub.get("author_year"):
                extra.append(sub["author_year"])
            if sub.get("type_locality"):
                extra.append("模式产地：%s" % md_escape(sub["type_locality"]))
            suffix = (" —— " + "，".join(extra)) if extra else ""
            lines.append("- %s%s" % (
                html_link("*%s* %s" % (sub["latin"], sub["zh"]), "/species/%s/" % sub["slug"]), suffix))

    return "\n".join(lines).rstrip("\n")


def build_body_foreign(fm, meta, subs_of_parent, parent_fm, lang):
    """Single-language body for the en / es pages (no Chinese prose at all)."""
    en = lang == "en"
    lp = "/" + lang
    latin = clean(fm.get("latin"))
    rank = (clean(fm.get("rank")) or "species").lower()
    is_sub = rank == "subspecies"
    is_type = str(fm.get("type", "")).strip().lower() == "true"
    family_latin = clean(fm.get("family_latin"))
    sub_latin = clean(fm.get("subfamily_latin"))
    genus_latin = clean(fm.get("genus_latin"))
    family_id, sub_id, genus_id = clean(fm.get("family_id")), clean(fm.get("subfamily_id")), clean(fm.get("genus_id"))
    author_year = clean(fm.get("author_year"))
    author, year = name_author_year(author_year)
    type_locality = md_escape(strip_cjk_parens(clean(fm.get("type_locality"))))
    genus_info = meta["genus"].get(genus_id) or {}
    gcount = genus_info.get("species_count") or 0
    fam = meta["fam_counts"].get(family_id) or {}
    lines = []

    rank_word = ("subspecies" if is_sub else "species") if en else ("subespecie" if is_sub else "especie")
    family_phrase = ("the family %s" if en else "la familia %s") % family_latin
    if sub_latin:
        family_phrase += (" (subfamily %s)" if en else " (subfamilia %s)") % sub_latin

    # ---- summary ----------------------------------------------------------
    if is_sub:
        parent_latin = clean(fm.get("parent_latin"))
        if en:
            lead = "***%s*** is a subspecies of *%s*, in %s, genus *%s*" % (
                latin, parent_latin, family_phrase, genus_latin)
        else:
            lead = "***%s*** es una subespecie de *%s*, en %s, género *%s*" % (
                latin, parent_latin, family_phrase, genus_latin)
    elif gcount == 1:
        if en:
            lead = "***%s*** is the only extant species of the genus *%s*, in %s" % (
                latin, genus_latin, family_phrase)
        else:
            lead = "***%s*** es la única especie viviente del género *%s*, en %s" % (
                latin, genus_latin, family_phrase)
    elif is_type:
        if en:
            lead = "***%s*** is a species and the type species of the genus *%s*, in %s" % (
                latin, genus_latin, family_phrase)
        else:
            lead = "***%s*** es una especie y la especie tipo del género *%s*, en %s" % (
                latin, genus_latin, family_phrase)
    else:
        if en:
            lead = "***%s*** is a species of the genus *%s*, in %s" % (
                latin, genus_latin, family_phrase)
        else:
            lead = "***%s*** es una especie del género *%s*, en %s" % (
                latin, genus_latin, family_phrase)

    sents = [lead + "."]
    if author and year:
        if en:
            sents.append("The %s was described by %s in %s; the type locality is %s." % (
                rank_word, author, year, type_locality or "not recorded"))
        else:
            sents.append("La %s fue descrita por %s en %s; la localidad tipo es %s." % (
                rank_word, author, year, type_locality or "no registrada"))
    elif author_year:
        if en:
            sents.append("The %s is recorded under the name %s; the type locality is %s." % (
                rank_word, author_year, type_locality or "not recorded"))
        else:
            sents.append("La %s se registra bajo el nombre %s; la localidad tipo es %s." % (
                rank_word, author_year, type_locality or "no registrada"))

    dist_en = md_escape(clean(fm.get("distribution_en")))
    parent_dist_en = md_escape(clean((parent_fm or {}).get("distribution_en")))
    if dist_en:
        if en:
            sents.append("Distribution: %s." % dist_en)
        else:
            sents.append("Distribución según la fuente: %s." % dist_en)
    elif is_sub and parent_fm:
        if en:
            sents.append("No separate distribution record is listed on this page; see the parent species *%s* below." % clean(parent_fm.get("latin")))
        else:
            sents.append("No se incluye un registro de distribución separado en esta página; véase la especie parental *%s* más abajo." % clean(parent_fm.get("latin")))

    syn_count = clean(fm.get("synonym_count"))
    if syn_count.isdigit() and int(syn_count) > 0:
        if en:
            sents.append("This site records %s junior synonym%s for the %s." % (
                syn_count, "" if syn_count == "1" else "s", rank_word))
        else:
            sents.append("Este sitio registra %s sinónimo%s junior para la %s." % (
                syn_count, "" if syn_count == "1" else "s", rank_word))
    lines += ["## %s" % ("Summary" if en else "Resumen"), "", " ".join(sents)]

    # ---- etymology --------------------------------------------------------
    ety = meta.get("etymology") or {}
    ety_gen = (ety.get("genera") or {}).get(genus_id)
    _parts = latin.split()
    epithet = _parts[-1].lower() if _parts else ""
    ety_epi = (ety.get("epithets") or {}).get(epithet)
    gen_text = ""
    epi_text = ""
    if ety_gen:
        gen_text = md_escape(sanitize_foreign((ety_gen.get("en") if en else pick_es(ety_gen)) or ""))
    if ety_epi:
        epi_text = md_escape(sanitize_foreign((ety_epi.get("en") if en else pick_es(ety_epi)) or ""))
    if gen_text or epi_text:
        lines += ["", "## %s" % ("Etymology" if en else "Etimología"), ""]
        if gen_text:
            lines.append("%s *%s*: %s" % ("Genus name" if en else "Nombre del género", genus_latin, gen_text))
            lines.append("")
        if epi_text:
            lines.append("%s *%s*: %s" % ("Specific epithet" if en else "Epíteto específico", epithet, epi_text))
            lines.append("")
        lines.append("<!-- src:S0018 -->")

    # ---- taxonomic position ----------------------------------------------
    lines += ["", "## %s" % ("Taxonomic position" if en else "Posición taxonómica"), ""]
    fam_stat = ""
    if fam:
        _fg, _fs = fam.get("genera", "?"), fam.get("species", "?")
        if en:
            fam_stat = " — %s %s, %s %s" % (_fg, "genus" if _fg == 1 else "genera", _fs, "species" if _fs == 1 else "species")
        else:
            fam_stat = " — %s %s, %s %s" % (_fg, "género" if _fg == 1 else "géneros", _fs, "especie" if _fs == 1 else "especies")
    lines.append("- **%s**: %s%s" % (
        "Family" if en else "Familia",
        html_link(family_latin, "%s/family/%s/" % (lp, family_id)), fam_stat))
    if sub_latin and sub_id:
        sub_stat = ""
        sc = meta["sub_counts"].get(sub_id) or {}
        if sc:
            _sg, _ss = sc.get("genera", "?"), sc.get("species", "?")
            if en:
                sub_stat = " — %s %s, %s %s" % (_sg, "genus" if _sg == 1 else "genera", _ss, "species")
            else:
                sub_stat = " — %s %s, %s %s" % (_sg, "género" if _sg == 1 else "géneros", _ss, "especie" if _ss == 1 else "especies")
        lines.append("- **%s**: %s%s" % (
            "Subfamily" if en else "Subfamilia",
            html_link(sub_latin, "%s/subfamily/%s/" % (lp, sub_id)), sub_stat))
    if is_sub:
        genus_desc = ("monotypic, 1 species" if en else "monotípico, 1 especie") if gcount == 1 else (
            "%s species" % gcount if en else "%s especies" % gcount)
        lines.append("- **%s**: %s — %s" % (
            "Genus" if en else "Género",
            html_link("*%s*" % genus_latin, "%s/genus/%s/" % (lp, genus_id)), genus_desc))
        lines.append("- **%s**: %s" % (
            "Species" if en else "Especie",
            html_link("*%s*" % clean(fm.get("parent_latin")), "%s/species/%s/" % (lp, clean(fm.get("parent_slug"))))))
        lines.append("- **%s**: %s (*%s*)" % ("Subspecies" if en else "Subespecie", "this page" if en else "esta página", latin))
    else:
        genus_desc = ("monotypic, 1 species" if en else "monotípico, 1 especie") if gcount == 1 else (
            "%s species" % gcount if en else "%s especies" % gcount)
        lines.append("- **%s**: %s — %s" % (
            "Genus" if en else "Género",
            html_link("*%s*" % genus_latin, "%s/genus/%s/" % (lp, genus_id)), genus_desc))
        ts = genus_info.get("type_species")
        if ts and ts != latin:
            lines.append("- **%s**: *%s*" % ("Type species of the genus" if en else "Especie tipo del género", ts))

    # ---- distribution -----------------------------------------------------
    if dist_en:
        lines += ["", "## %s" % ("Distribution" if en else "Distribución"), ""]
        if en:
            lines.append("- **Distribution records**: %s" % dist_en)
            lines += ["", "The record above follows the wording of the original data; no geocoding or standardized place names have been applied."]
        else:
            lines.append("- **Registros de distribución (según la fuente)**: %s" % dist_en)
            lines += ["", "El registro anterior sigue la redacción de los datos originales; no se han aplicado geocodificación ni nombres de lugar normalizados."]
    elif is_sub and parent_fm:
        lines += ["", "## %s" % ("Distribution" if en else "Distribución"), ""]
        parent_name = md_escape(clean(parent_fm.get("latin")))
        if en:
            lines.append("No separate distribution record is listed for this subspecies; the distribution of the parent species *%s* is: %s." % (
                parent_name, parent_dist_en or "not recorded"))
        else:
            lines.append("No se incluye un registro de distribución separado para esta subespecie; la distribución de la especie parental *%s* es: %s." % (
                parent_name, parent_dist_en or "no registrada"))

    # ---- junior synonyms --------------------------------------------------
    syns = parse_list(fm.get("synonyms"))
    locs = parse_list(fm.get("synonym_localities"))
    authority_syns = parse_list(fm.get("authority_synonyms"))
    if syns or authority_syns:
        lines += ["", "## %s" % ("Junior synonyms" if en else "Sinónimos junior"), ""]
    if syns:
        n_syn = len(syns)
        one = n_syn == 1
        if en:
            lead = "This site records %d junior synonym%s for the %s, listed by %s original literature source" % (
                n_syn, "" if one else "s", rank_word, "its" if one else "their")
        else:
            if one:
                lead = "Este sitio registra %d sinónimo junior para la %s, ordenado según su fuente bibliográfica original" % (n_syn, rank_word)
            else:
                lead = "Este sitio registra %d sinónimos junior para la %s, ordenados según sus fuentes bibliográficas originales" % (n_syn, rank_word)
        lines.append(lead + ":")
        lines.append("")
        for i, entry in enumerate(syns, 1):
            name, auth = split_synonym(entry)
            loc = md_escape(locs[i - 1]) if i - 1 < len(locs) else ""
            tail = " — type locality: %s" % loc if loc else ""
            lines.append("%d. *%s* %s%s" % (i, name, auth, tail))
        old_names = ", ".join("*%s*" % split_synonym(s)[0] for s in syns[:8])
        if len(syns) > 1:
            if en:
                lines += ["", "In older literature, regional checklists and database searches, this %s may appear under the synonyms above (%s); this site treats them all under *%s*." % (
                    rank_word, old_names, latin)]
            else:
                lines += ["", "En la literatura antigua, los listados regionales y las búsquedas en bases de datos, esta %s puede aparecer bajo los sinónimos anteriores (%s); este sitio los reúne todos bajo *%s*." % (
                    rank_word, old_names, latin)]
        else:
            if en:
                lines += ["", "In older literature, regional checklists and database searches, this %s may appear under the synonym %s; this site treats it under *%s*." % (
                    rank_word, old_names, latin)]
            else:
                lines += ["", "En la literatura antigua, los listados regionales y las búsquedas en bases de datos, esta %s puede aparecer bajo el sinónimo %s; este sitio lo reúne bajo *%s*." % (
                    rank_word, old_names, latin)]

    # ---- synonyms recorded from external authorities -----------------------
    if authority_syns:
        authority_locs = parse_list(fm.get("authority_synonym_localities"))
        authority_srcs = parse_list(fm.get("authority_synonym_sources"))
        lines += ["", "### %s" % ("Synonyms recorded from external authorities" if en else "Sinónimos registrados desde autoridades externas"), ""]
        if en:
            lines.append("The external authorities give the following names as synonyms of this %s; they are recorded here for review, and each of them keeps its own record in this checklist for the time being:" % rank_word)
        else:
            lines.append("Las autoridades externas dan los siguientes nombres como sinónimos de esta %s; se registran aquí para su revisión y cada uno conserva por ahora su propio registro en esta lista:" % rank_word)
        lines.append("")
        for i, entry in enumerate(authority_syns):
            name, auth = split_synonym(entry)
            loc = md_escape(authority_locs[i]) if i < len(authority_locs) else ""
            src = authority_labels(authority_srcs[i]) if i < len(authority_srcs) else ""
            tail = " — type locality: %s" % loc if loc else ""
            suffix = " (%s)" % src if src else ""
            lines.append("- *%s* %s%s%s" % (name, auth, suffix, tail))

    # ---- subspecies -------------------------------------------------------
    subs = subs_of_parent.get(latin) or []
    if subs:
        n_sub = len(subs)
        lines += ["", "## %s" % ("Subspecies" if en else "Subespecies"), ""]
        if en:
            lines.append("This species includes %d subspecies:" % n_sub)
        else:
            lines.append("Esta especie incluye %d %s:" % (n_sub, "subespecie" if n_sub == 1 else "subespecies"))
        lines.append("")
        for sub in subs:
            extra = []
            if sub.get("author_year"):
                extra.append(sub["author_year"])
            if sub.get("type_locality"):
                extra.append("type locality: %s" % md_escape(strip_cjk_parens(sub["type_locality"])))
            suffix = (" — " + ", ".join(extra)) if extra else ""
            lines.append("- %s%s" % (
                html_link("*%s*" % sub["latin"], "%s/species/%s/" % (lp, sub["slug"])), suffix))

    return sanitize_foreign("\n".join(lines)).rstrip("\n")


# ------------------------------------------------------------------- assembly
def assemble(head, body, block, nl):
    body = body.strip("\r\n")
    if BEGIN in body and END in body:
        pre, rest = body.split(BEGIN, 1)
        _, post = rest.split(END, 1)
        new_body = pre.rstrip("\r\n") + "\n\n" + BEGIN + "\n" + block + "\n" + END + post.rstrip("\r\n")
    elif not body:
        new_body = BEGIN + "\n" + block + "\n" + END
    elif body.lstrip().startswith("## 亚种"):
        # legacy auto-generated subspecies list (29 pages): superseded, no human prose
        new_body = BEGIN + "\n" + block + "\n" + END
    else:
        new_body = body + "\n\n" + BEGIN + "\n" + block + "\n" + END
    new_body = new_body.replace("\r\n", "\n").strip("\n")
    return head + nl + nl + new_body.replace("\n", nl) + nl


def yaml_quote(value):
    return '"%s"' % clean(value).replace("\\", "\\\\").replace('"', '\\"')


FOREIGN_SKIP = {
    "layout", "title", "lang", "permalink", "species_page", "single_lang",
    "slug", "lang_only", "description",
}


def foreign_front_matter(fm, slug, lang, pending):
    lines = [
        "layout: species",
        "title: %s" % yaml_quote(fm.get("title")),
        "lang: %s" % lang,
        "permalink: /%s/species/%s/" % (lang, slug),
        "species_page: true",
        "single_lang: true",
        "slug: %s" % yaml_quote(slug),
    ]
    for key, raw in fm.items():
        if key in FOREIGN_SKIP:
            continue
        if key == "type_locality":
            lines.append("type_locality: %s" % yaml_quote(strip_cjk_parens(raw)))
            continue
        if key == "type":
            lines.append("type: %s" % ("true" if clean(raw).lower() == "true" else "false"))
            continue
        if key == "synonym_count" and clean(raw).isdigit():
            lines.append("synonym_count: %s" % clean(raw))
            continue
        lines.append("%s: %s" % (key, yaml_quote(raw)))
    if pending:
        lines.append("translation_pending: true")
    return "\n".join(lines)


def foreign_page(fm, slug, lang, body, pending):
    return ("---\n" + foreign_front_matter(fm, slug, lang, pending)
            + "\n---\n\n" + BEGIN + "\n" + body + "\n" + END + "\n")


def ensure_zh_front_matter(head, nl, slug):
    """zh pages lose lang_only and gain lang, single_lang and permalink."""
    head = re.sub(r"^[ \t]*lang_only:.*\r?\n?", "", head, flags=re.M)
    insert = []
    if re.search(r"^lang:", head, re.M) is None:
        insert.append("lang: zh-CN")
    if re.search(r"^single_lang:", head, re.M) is None:
        insert.append("single_lang: true")
    if re.search(r"^permalink:", head, re.M) is None:
        insert.append("permalink: /species/%s/" % slug)
    if insert:
        head = re.sub(
            r"^(layout: species)[ \t\r]*$",
            lambda m: m.group(1) + nl + nl.join(insert),
            head, count=1, flags=re.M)
    return head


def translation_pending(slug, lang, fauna, morph, trans):
    if lang == "zh":
        return False
    key = "/species/%s/" % slug
    data = trans.get(lang) or {}
    if key in (fauna or {}) and key not in (data.get("fauna_species") or {}):
        return True
    if key in (morph or {}) and key not in (data.get("morphology_species") or {}):
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite _species/*.md and en|es/species/*.md")
    ap.add_argument("--sample", nargs="*", default=None, help="print generated bodies for these slugs")
    ap.add_argument("--lang", choices=("zh", "en", "es"), default="zh", help="language for --sample")
    ap.add_argument("--render", action="store_true", help="resolve the Liquid base_url tag in output")
    ap.add_argument("--check-idempotent", action="store_true")
    ap.add_argument("--assemble-sample", nargs="*", default=None,
                    help="print the full rewritten file (front matter + body) for these slugs")
    args = ap.parse_args()

    meta = load_meta()
    meta["etymology"] = json.loads(ETYMOLOGY_JSON.read_text(encoding="utf-8")) if ETYMOLOGY_JSON.is_file() else {}
    base_url = site_base_url()
    fauna = json.loads(FAUNA_JSON.read_text(encoding="utf-8")) if FAUNA_JSON.is_file() else {}
    morph = json.loads(MORPH_JSON.read_text(encoding="utf-8")) if MORPH_JSON.is_file() else {}
    trans = {}
    for lang, path in TRANS_JSON.items():
        trans[lang] = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    files, fms = {}, {}
    for path in sorted(SPECIES_DIR.glob("*.md")):
        text = path.read_bytes().decode("utf-8")
        fm, head, body, nl = split_doc(text)
        files[path.stem] = (path, head, body, nl)
        fms[path.stem] = fm

    subs_of_parent = {}
    for slug, fm in fms.items():
        if (clean(fm.get("rank")) or "species").lower() == "subspecies":
            parent = clean(fm.get("parent_latin"))
            if parent:
                subs_of_parent.setdefault(parent, []).append({
                    "slug": slug, "latin": clean(fm.get("latin")), "zh": clean(fm.get("zh")),
                    "author_year": clean(fm.get("author_year")),
                    "type_locality": clean(fm.get("type_locality")),
                })
    for key in subs_of_parent:
        subs_of_parent[key].sort(key=lambda x: x["latin"])

    def parent_for(fm):
        if (clean(fm.get("rank")) or "species").lower() == "subspecies":
            return fms.get(clean(fm.get("parent_slug")))
        return None

    bodies = {slug: build_body(fm, meta, subs_of_parent, parent_for(fm), "zh") for slug, fm in fms.items()}

    if args.assemble_sample is not None:
        for slug in args.assemble_sample:
            if slug not in files:
                sys.exit("unknown slug: %s" % slug)
            path, head, body, nl = files[slug]
            if args.lang == "zh":
                print("===== %s (%s) =====" % (slug, args.lang))
                print(assemble(ensure_zh_front_matter(head, nl, slug), body, bodies[slug], nl))
            else:
                out = foreign_page(fms[slug], slug, args.lang, build_body(
                    fms[slug], meta, subs_of_parent, parent_for(fms[slug]), args.lang),
                    translation_pending(slug, args.lang, fauna, morph, trans))
                if args.render:
                    out = out.replace(SITE, base_url)
                print("===== %s (%s) =====" % (slug, args.lang))
                print(out)
            print()
        return

    if args.sample is not None:
        for slug in args.sample:
            if slug not in fms:
                sys.exit("unknown slug: %s" % slug)
            out = build_body(fms[slug], meta, subs_of_parent, parent_for(fms[slug]), args.lang)
            if args.render:
                out = out.replace(SITE, base_url)
            print("===== %s (%s) =====" % (slug, args.lang))
            print(out)
            print()
        return

    if args.check_idempotent:
        bad = 0
        for slug, (path, head, body, nl) in files.items():
            first = assemble(ensure_zh_front_matter(head, nl, slug), body, bodies[slug], nl)
            fm2, head2, body2, nl2 = split_doc(first)
            second = assemble(head2, body2, bodies[slug], nl2)
            if first != second:
                bad += 1
                if bad <= 5:
                    print("NOT IDEMPOTENT: %s" % slug)
        print("idempotency: %d/%d pages differ on second pass" % (bad, len(files)))
        return

    lengths = [len(b) for b in bodies.values()]
    short = [s for s, b in bodies.items() if len(b) < 400]
    summaries = set()
    for b in bodies.values():
        m = re.search(r"## 摘要\s*\n\s*\n(.*)", b)
        summaries.add(m.group(1).strip() if m else "")
    print("zh pages: %d" % len(bodies))
    print("zh body chars: min=%d  median=%d  max=%d" % (
        min(lengths), int(statistics.median(lengths)), max(lengths)))
    print("zh pages under 400 chars: %d" % len(short))
    print("zh distinct 摘要 sentences: %d / %d" % (len(summaries), len(bodies)))
    for lang in ("en", "es"):
        fl = [len(build_body(fm, meta, subs_of_parent, parent_for(fm), lang)) for fm in fms.values()]
        print("%s bodies: %d (min=%d, median=%d, max=%d)" % (
            lang, len(fl), min(fl), int(statistics.median(fl)), max(fl)))
        pend = sum(1 for slug in fms if translation_pending(slug, lang, fauna, morph, trans))
        print("%s translation_pending: %d" % (lang, pend))

    if args.write:
        changed = 0
        for slug, (path, head, body, nl) in files.items():
            new = assemble(ensure_zh_front_matter(head, nl, slug), body, bodies[slug], nl)
            old = path.read_bytes().decode("utf-8")
            if new != old:
                path.write_bytes(new.encode("utf-8"))
                changed += 1
        print("rewrote %d zh files" % changed)
        for lang in ("en", "es"):
            out_dir = LANG_DIRS[lang]
            out_dir.mkdir(parents=True, exist_ok=True)
            wrote = 0
            for slug, fm in fms.items():
                body = build_body(fm, meta, subs_of_parent, parent_for(fm), lang)
                pending = translation_pending(slug, lang, fauna, morph, trans)
                text = foreign_page(fm, slug, lang, body, pending)
                target = out_dir / ("%s.md" % slug)
                old = target.read_bytes().decode("utf-8") if target.is_file() else None
                if text != old:
                    target.write_bytes(text.encode("utf-8"))
                    wrote += 1
            print("wrote %d %s files" % (wrote, lang))
    else:
        print("dry-run: no files written")


if __name__ == "__main__":
    main()
