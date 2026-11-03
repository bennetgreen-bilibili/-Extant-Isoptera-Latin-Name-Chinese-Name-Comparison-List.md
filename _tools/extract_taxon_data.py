#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性迁移脚本：把三语 /list/ 名录里的分类层级与科/亚科正文抽成数据文件。

背景
----
/list/ 原本同时承担三件事：分类框架说明、科/亚科正文（含插图）、逐条名录（326 属 /
3021 种）。逐条名录已经迁到 /family/、/subfamily/、/genus/ 各级页面，正文也随之迁走，
于是 /list/ 只剩索引职能。这个脚本完成迁移所需的数据抽取，之后 list.md 由
_tools/build_list_index.py 从这两个 JSON 重新生成，不再手写。

产出（均为确定性输出，LF 换行）
----
_data/taxonomy.json          支系 → 科 → 亚科 → 属 的层级（id / 中文名 / 拉丁名 / 父级）
_data/taxon_prose.json       三语的科、亚科正文段落与插图（zh / en / es）
_data/list_index_blocks.json 三语索引页原样保留的说明块（H1 / 导语 / 按科浏览 / 参考文献）

用法
----
    python _tools/extract_taxon_data.py            # 从旧名录页抽取并写入（迁移期）
    python _tools/extract_taxon_data.py --check    # 校验已提交的 JSON 自身是否自洽

脚本只在迁移期抽取：list.md 一旦改成索引页（不再有 <h3 id="…">科</h3> 小节），抽取路径会
直接退出——那之后的数据源就是这三个 JSON 本身。--check 因此不读 list.md，只校验 JSON 的
结构（counts 与列表长度一致、三语都覆盖每个科的正文、每语的索引块齐全），供 CI 每次跑。
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIST_MD = ROOT / "list.md"
LIST_MD_EN = ROOT / "en" / "list.md"
LIST_MD_ES = ROOT / "es" / "list.md"
TAXONOMY_OUT = ROOT / "_data" / "taxonomy.json"
PROSE_OUT = ROOT / "_data" / "taxon_prose.json"
BLOCKS_OUT = ROOT / "_data" / "list_index_blocks.json"

HEADING_RE = re.compile(r'<h([2-5])\s+id="([a-z0-9\-]+)"[^>]*>(.*?)</h\1>', re.S)
FIGURE_RE = re.compile(r'<figure class="taxa-illustration">.*?</figure>', re.S)
IMG_RE = re.compile(r"/assets/images/([a-z0-9\-]+)\.(?:jpg|png)")
INCLUDE_MAP_RE = re.compile(r"^[ \t]*\{%\s*include\s+distribution-map\.html.*?%\}[ \t]*$", re.M)
TAG_ONLY_RE = re.compile(r"^[ \t]*<[^>]+>[ \t]*$")
CJK_RE = re.compile(u"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]")
TITLE_RE = re.compile(r"^(\S.*?)\s+([A-Za-z].*)$")
TAG_RE = re.compile(r"<[^>]+>")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from checklist_headings import SKIP_IDS  # noqa: E402  名录里的导航标题（按科浏览 / 目录 / 参考文献）


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def reflow(lines):
    """与 build_taxonomy_pages.reflow 一致：中文换行不是空格，拉丁词之间的换行是空格。"""
    out = ""
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if not out:
            out = line
        elif CJK_RE.match(out[-1]) or CJK_RE.match(line[0]):
            out += line
        else:
            out += " " + line
    return out


def split_title(text: str):
    plain = TAG_RE.sub("", text).strip()
    m = TITLE_RE.match(plain)
    if not m:
        return "", plain
    return m.group(1).strip(), m.group(2).strip()


def parse_sections(text: str):
    """返回 (heads, sections)：heads 按版面顺序，sections[id] = {paragraphs, figures}。"""
    body = FIGURE_RE.sub("", text)
    body = INCLUDE_MAP_RE.sub("", body)
    heads = list(HEADING_RE.finditer(body))
    sections = {}
    for index, head in enumerate(heads):
        end = heads[index + 1].start() if index + 1 < len(heads) else len(body)
        paragraphs = []
        for block in re.split(r"\n[ \t]*\n", body[head.end():end]):
            lines = [ln for ln in block.splitlines() if ln.strip() and not TAG_ONLY_RE.match(ln)]
            if not lines:
                continue
            paragraph = reflow(lines).strip()
            if paragraph:
                paragraphs.append(paragraph)
        sections[head.group(2)] = {"level": int(head.group(1)), "title": head.group(3),
                                   "paragraphs": paragraphs}
    return heads, sections


def figures_by_id(text: str):
    out = {}
    for block in FIGURE_RE.findall(text):
        m = IMG_RE.search(block)
        if not m:
            continue
        key = re.sub(r"-\d+$", "", m.group(1))
        out.setdefault(key, block.strip())
    return out


def load_hierarchy(text: str):
    """从中文名录的标题顺序读出支系/科/亚科/属，以及每一级的父级。"""
    clades, families, subfamilies, genera = [], [], [], []
    clade = family = subfamily = None
    for head in HEADING_RE.finditer(text):
        level, anchor, title = int(head.group(1)), head.group(2), head.group(3)
        if anchor in SKIP_IDS:
            continue
        zh, latin = split_title(title)
        if level == 2:
            clade = {"id": anchor, "zh": zh, "latin": latin, "families": []}
            clades.append(clade)
            family = subfamily = None
        elif level == 3:
            family = {"id": anchor, "zh": zh, "latin": latin,
                      "clade": clade["id"] if clade else "", "subfamilies": [], "genera": []}
            families.append(family)
            if clade:
                clade["families"].append(anchor)
            subfamily = None
        elif level == 4:
            subfamily = {"id": anchor, "zh": zh, "latin": latin,
                         "family": family["id"] if family else "", "genera": []}
            subfamilies.append(subfamily)
            if family:
                family["subfamilies"].append(anchor)
        elif level == 5:
            entry = {"id": anchor, "zh": zh, "latin": latin,
                     "family": family["id"] if family else "",
                     "subfamily": subfamily["id"] if subfamily else ""}
            genera.append(entry)
            if subfamily:
                subfamily["genera"].append(anchor)
            elif family:
                family["genera"].append(anchor)
            else:
                sys.exit("error: 属 %s 没有父级科" % anchor)
    if not clades or not families:
        sys.exit("error: list.md 里读不到支系/科标题——它可能已经是索引页了；"
                 "数据源现在是 _data/taxonomy.json 与 _data/taxon_prose.json")
    return clades, families, subfamilies, genera


def prose_for(text: str, language: str):
    """取科（h3）与亚科（h4）小节的段落与插图。"""
    _, sections = parse_sections(text)
    figures = figures_by_id(text)
    families, subfamilies = {}, {}
    for anchor, section in sections.items():
        if section["level"] == 3:
            bucket = families
        elif section["level"] == 4:
            bucket = subfamilies
        else:
            continue
        if not section["paragraphs"]:
            continue
        entry = {"paragraphs": section["paragraphs"]}
        if anchor in figures:
            entry["figure"] = figures[anchor]
        bucket[anchor] = entry
    return {"families": families, "subfamilies": subfamilies}


def index_blocks(text: str, language: str):
    """取索引页要原样保留的三块：H1 与导语、按科浏览、参考文献。

    这三块含翻译过的说明文字、搜索框与参考文献条目，手写容易与原有措辞走样，
    所以整体原样搬进 JSON，再由 build_list_index.py 组装回页面。
    """
    lines = text.split("\n")

    def find(prefix):
        for index, line in enumerate(lines):
            if line.startswith(prefix):
                return index
        return -1

    i_h1 = find("# ")
    i_family = find('<h2 id="by-family"')
    i_toc = find('<h2 id="toc"')
    i_refs = find('<h2 id="references"')
    missing = [name for name, index in (("h1", i_h1), ("by-family", i_family),
                                        ("toc", i_toc), ("references", i_refs))
               if index < 0]
    if missing:
        sys.exit("error: %s 缺少 %s 标题——它可能已经是索引页了" % (language, "/".join(missing)))
    return {
        "h1": lines[i_h1][2:].strip(),
        "intro": "\n".join(lines[i_h1 + 1:i_family]).strip(),
        "by_family": "\n".join(lines[i_family:i_toc]).strip(),
        "references": "\n".join(lines[i_refs:]).strip(),
    }


def dump(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")


def build():
    zh = read(LIST_MD)
    clades, families, subfamilies, genera = load_hierarchy(zh)
    taxonomy = {
        "meta": {
            "description": "分类层级数据：/list/ 改成索引页后，支系—科—亚科—属的关系与锚点以这里为准。",
            "source": "extracted from the pre-index /list/ page by _tools/extract_taxon_data.py",
            "counts": {"clades": len(clades), "families": len(families),
                       "subfamilies": len(subfamilies), "genera": len(genera)},
        },
        "clades": clades,
        "families": families,
        "subfamilies": subfamilies,
        "genera": genera,
    }
    prose = {
        "meta": {
            "description": "三语科/亚科正文与插图；中文正文渲染在 /family/、/subfamily/ 页面，"
                           "英文与西班牙文正文渲染在 /en/list/sections/、/es/list/sections/。",
            "source": "extracted from the pre-index list pages by _tools/extract_taxon_data.py",
            "languages": ["zh", "en", "es"],
        },
        "zh": prose_for(zh, "zh"),
    }
    for key, path in (("en", LIST_MD_EN), ("es", LIST_MD_ES)):
        if path.is_file():
            prose[key] = prose_for(read(path), key)
    blocks = {
        "meta": {
            "description": "三语索引页里原样保留的说明块（H1、导语、按科浏览、参考文献）。",
            "source": "extracted from the pre-index list pages by _tools/extract_taxon_data.py",
            "languages": ["zh", "en", "es"],
        },
        "zh": index_blocks(zh, "zh"),
    }
    for key, path in (("en", LIST_MD_EN), ("es", LIST_MD_ES)):
        if path.is_file():
            blocks[key] = index_blocks(read(path), key)
    return taxonomy, prose, blocks


def verify(taxonomy: dict, prose: dict, blocks: dict) -> list[str]:
    """校验已提交的 JSON 自身是否自洽（不读 list.md）。"""
    problems = []
    counts = taxonomy.get("meta", {}).get("counts") or {}
    for key in ("clades", "families", "subfamilies", "genera"):
        if counts.get(key) != len(taxonomy.get(key) or []):
            problems.append("taxonomy.json 的 meta.counts.%s 与列表长度不一致" % key)
    family_ids = {fam["id"] for fam in taxonomy.get("families") or []}
    for lang in ("zh", "en", "es"):
        entry = prose.get(lang) or {}
        missing = sorted(family_ids - set(entry.get("families") or {}))
        if missing:
            problems.append("taxon_prose.json 的 %s 缺 %d 个科的正文：%s"
                            % (lang, len(missing), "、".join(missing[:3])))
        block = blocks.get(lang) or {}
        absent = [key for key in ("h1", "intro", "by_family", "references") if not block.get(key)]
        if absent:
            problems.append("list_index_blocks.json 的 %s 缺块：%s" % (lang, "、".join(absent)))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="校验已提交的 JSON 是否自洽")
    args = parser.parse_args()
    if args.check:
        paths = (TAXONOMY_OUT, PROSE_OUT, BLOCKS_OUT)
        missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
        if missing:
            sys.exit("not generated yet: " + ", ".join(missing))
        taxonomy = json.loads(TAXONOMY_OUT.read_text(encoding="utf-8"))
        prose = json.loads(PROSE_OUT.read_text(encoding="utf-8"))
        blocks = json.loads(BLOCKS_OUT.read_text(encoding="utf-8"))
        problems = verify(taxonomy, prose, blocks)
        if problems:
            sys.exit("\n".join(problems))
        counts = taxonomy["meta"]["counts"]
        print("ok：%(clades)d 支系 · %(families)d 科 · %(subfamilies)d 亚科 · %(genera)d 属" % counts)
        return 0
    taxonomy, prose, blocks = build()
    outputs = {TAXONOMY_OUT: dump(taxonomy), PROSE_OUT: dump(prose),
               BLOCKS_OUT: dump(blocks)}
    if args.check:
        bad = [str(p) for p, data in outputs.items()
               if not p.is_file() or p.read_bytes() != data]
        if bad:
            sys.exit("not up to date: " + ", ".join(sorted(bad)))
        print("ok")
        return 0
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print("wrote %s (%d bytes)" % (path.relative_to(ROOT), len(data)))
    counts = taxonomy["meta"]["counts"]
    print("clades %(clades)d · families %(families)d · subfamilies %(subfamilies)d · genera %(genera)d"
          % counts)
    for key in ("zh", "en", "es"):
        entry = prose.get(key) or {}
        block = blocks.get(key) or {}
        print("%s prose: %d families, %d subfamilies; index blocks: intro %d chars, "
              "by-family %d chars, references %d chars"
              % (key, len(entry.get("families") or {}), len(entry.get("subfamilies") or {}),
                 len(block.get("intro") or ""), len(block.get("by_family") or ""),
                 len(block.get("references") or "")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
