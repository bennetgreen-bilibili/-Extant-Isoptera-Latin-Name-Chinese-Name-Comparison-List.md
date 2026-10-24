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


# ----------------------------------------------------------------- generators
def html_link(label, path):
    return "[%s](%s%s)" % (label, SITE, path)


def classify(rank, is_type, genus_info):
    if rank == "subspecies":
        return "一个亚种"
    if genus_info and genus_info.get("species_count") == 1:
        return "现存唯一种"
    if is_type:
        return "一种，也是本属的模式种"
    return "一种"


def build_body(fm, meta, subs_of_parent, parent_fm):
    latin = clean(fm.get("latin"))
    zh = clean(fm.get("zh"))
    rank = (clean(fm.get("rank")) or "species").lower()
    is_type = str(fm.get("type", "")).strip().lower() == "true"
    family_zh, family_latin = clean(fm.get("family_zh")), clean(fm.get("family_latin"))
    sub_zh, sub_latin = clean(fm.get("subfamily_zh")), clean(fm.get("subfamily_latin"))
    genus_zh, genus_latin = clean(fm.get("genus_zh")), clean(fm.get("genus_latin"))
    family_id, sub_id, genus_id = clean(fm.get("family_id")), clean(fm.get("subfamily_id")), clean(fm.get("genus_id"))
    clade_zh, clade_latin = clean(fm.get("clade_zh")), clean(fm.get("clade_latin"))
    author_year = clean(fm.get("author_year"))
    author, year = name_author_year(author_year)
    type_locality = md_escape(fm.get("type_locality"))
    genus_info = meta["genus"].get(genus_id) or {}
    gcount = genus_info.get("species_count") or 0
    fam = meta["fam_counts"].get(family_id) or {}
    lines = []

    # ---- 摘要 -------------------------------------------------------------
    rank_word = "亚种" if rank == "subspecies" else "种"
    fam_phrase = "%s（%s）" % (family_zh, family_latin)
    if sub_zh:
        fam_phrase += "%s（%s）" % (sub_zh, sub_latin)
    if rank == "subspecies":
        parent_zh, parent_latin = clean(fm.get("parent_zh")), clean(fm.get("parent_latin"))
        lead = "**%s**（*%s*）是%s（*%s*）的一个亚种，隶属%s%s（*%s*），所属支系为%s（%s）" % (
            zh, latin, parent_zh, parent_latin, fam_phrase, genus_zh, genus_latin,
            clade_zh, clade_latin)
    else:
        lead = "**%s**（*%s*）是%s%s（*%s*）的%s，隶属%s（%s）" % (
            zh, latin, fam_phrase, genus_zh, genus_latin,
            classify(rank, is_type, genus_info), clade_zh, clade_latin)

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

    # ---- 分类位置 ---------------------------------------------------------
    lines += ["", "## 分类位置", ""]
    clade = meta["clades"].get(meta["family_clade"].get(family_id, ""))
    if clade:
        lines.append("- **支系 Clade**：%s" % html_link(
            "%s %s" % (clade.get("zh", clade_zh), clade.get("latin", clade_latin)),
            "/list/#%s" % clade.get("id", "isoptera")))
    else:
        lines.append("- **支系 Clade**：%s %s" % (clade_zh, clade_latin))
    fam_stat = ""
    if fam:
        fam_stat = " —— 本站收录 %s 属 %s 种" % (fam.get("genera", "?"), fam.get("species", "?"))
    lines.append("- **科 Family**：%s%s" % (
        html_link("%s %s" % (family_zh, family_latin), "/list/#%s" % family_id), fam_stat))
    if sub_zh and sub_id:
        sub_stat = ""
        sc = meta["sub_counts"].get(sub_id) or {}
        if sc:
            sub_stat = " —— 本站收录 %s 属 %s 种" % (sc.get("genera", "?"), sc.get("species", "?"))
        lines.append("- **亚科 Subfamily**：%s%s" % (
            html_link("%s %s" % (sub_zh, sub_latin), "/list/#%s" % sub_id), sub_stat))
    if rank == "subspecies":
        lines.append("- **属 Genus**：%s —— %s" % (
            html_link("%s *%s*" % (genus_zh, genus_latin), "/list/#%s" % genus_id),
            "单型属，仅含 1 种" if gcount == 1 else "共 %s 种" % gcount))
        lines.append("- **种 Species**：%s" % html_link(
            "%s *%s*" % (clean(fm.get("parent_zh")), clean(fm.get("parent_latin"))),
            "/species/%s/" % clean(fm.get("parent_slug"))))
        lines.append("- **亚种 Subspecies**：本页（*%s*）" % latin)
    else:
        genus_desc = "单型属，仅含 1 种" if gcount == 1 else "共 %s 种" % gcount
        lines.append("- **属 Genus**：%s —— %s" % (
            html_link("%s *%s*" % (genus_zh, genus_latin), "/list/#%s" % genus_id), genus_desc))
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
        if clean(fm.get("distribution_en")):
            lines.append("- **英文记录**：%s" % md_escape(fm.get("distribution_en")))
        lines += ["", "以上记录沿用原始数据的写法，未做地理编码与译名统一。"]
    elif parent_fm:
        lines += ["", "## 分布", ""]
        lines.append("本亚种暂未单列分布记录；母种 *%s* 的分布为：%s。" % (
            clean(parent_fm.get("latin")), join_zh(parent_native) or "未记录"))
        if clean(parent_fm.get("distribution_en")):
            lines += ["", "母种英文记录：%s。" % md_escape(parent_fm.get("distribution_en"))]

    # ---- 次异名 -----------------------------------------------------------
    syns = parse_list(fm.get("synonyms"))
    locs = parse_list(fm.get("synonym_localities"))
    if syns:
        lines += ["", "## 次异名", ""]
        lines.append("本站记录本%s有 %d 个次异名（junior synonyms），按原始文献出处列出：" % (rank_word, len(syns)))
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

    # ---- 亚种 -------------------------------------------------------------
    subs = subs_of_parent.get(latin) or []
    if subs:
        lines += ["", "## 亚种", ""]
        lines.append("本种下分 %d 个亚种：" % len(subs))
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

    # ---- 数据出处 ---------------------------------------------------------
    data_file = meta["fam_file"].get(family_id) or ""
    if sub_id and meta["sub_file"].get(sub_id):
        data_file = meta["sub_file"][sub_id]
    lines += ["", "## 数据出处与引用", ""]
    lines.append(
        "本条记录出自《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》%s 版（%s 发布，%s 更新），"
        "作者%s，以 CC BY 4.0 许可发布；对应的机器可读数据见 %s。" % (
            meta["version"], meta["published"], meta["modified"], meta["creator"],
            html_link(data_file, "/" + data_file) if data_file else "data/index.json"))
    lines += ["", "引用格式（APA）：%s. (%s). 《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》(%s 正式版). %s/" % (
        meta["creator"], meta["version"].split(".")[0], meta["version"], SITE)]
    return "\n".join(lines)


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite _species/*.md")
    ap.add_argument("--sample", nargs="*", default=None, help="print generated bodies for these slugs")
    ap.add_argument("--render", action="store_true", help="resolve the Liquid base_url tag in output")
    ap.add_argument("--check-idempotent", action="store_true")
    ap.add_argument("--assemble-sample", nargs="*", default=None,
                    help="print the full rewritten file (front matter + body) for these slugs")
    args = ap.parse_args()

    meta = load_meta()
    base_url = site_base_url()
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

    bodies = {}
    for slug, fm in fms.items():
        parent_fm = None
        if (clean(fm.get("rank")) or "species").lower() == "subspecies":
            parent_fm = fms.get(clean(fm.get("parent_slug")))
        bodies[slug] = build_body(fm, meta, subs_of_parent, parent_fm)

    if args.assemble_sample is not None:
        for slug in args.assemble_sample:
            if slug not in files:
                sys.exit("unknown slug: %s" % slug)
            path, head, body, nl = files[slug]
            print("===== %s =====" % slug)
            print(assemble(head, body, bodies[slug], nl))
            print()
        return

    if args.sample is not None:
        for slug in args.sample:
            if slug not in bodies:
                sys.exit("unknown slug: %s" % slug)
            out = bodies[slug]
            if args.render:
                out = out.replace(SITE, base_url)
            print("===== %s =====" % slug)
            print(out)
            print()
        return

    if args.check_idempotent:
        bad = 0
        for slug, (path, head, body, nl) in files.items():
            first = assemble(head, body, bodies[slug], nl)
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
    print("pages: %d" % len(bodies))
    print("body chars: min=%d  median=%d  max=%d" % (
        min(lengths), int(statistics.median(lengths)), max(lengths)))
    print("pages under 400 chars: %d" % len(short))
    print("distinct 摘要 sentences: %d / %d" % (len(summaries), len(bodies)))

    if args.write:
        changed = 0
        for slug, (path, head, body, nl) in files.items():
            new = assemble(head, body, bodies[slug], nl)
            old = path.read_bytes().decode("utf-8")
            if new != old:
                path.write_bytes(new.encode("utf-8"))
                changed += 1
        print("rewrote %d files" % changed)
    else:
        print("dry-run: no files written")


if __name__ == "__main__":
    main()
