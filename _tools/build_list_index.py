#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把三语 /list/ 从「全量名录」改成「分类索引页」，并生成 en / es 两份译文页。

背景
----
/list/ 原本一页承担三件事：分类框架说明、13 科与 18 亚科的正文（含插图）、以及 326 属
3021 种的逐条名录。逐条名录已迁到 /family/、/subfamily/、/genus/ 各级页面，科与亚科的
正文也随之迁往这些页面（中文）。于是 /list/ 只保留索引职能：说明结构、按科浏览、把读者
送到各级页面。英文与西班牙文的科·亚科正文不并入中文的科页/亚科页，而是集中到
/en/list/sections/、/es/list/sections/ 两个译文页。

数据来源
--------
_data/taxonomy.json        支系 → 科 → 亚科 → 属 的层级（由 _tools/extract_taxon_data.py 抽取）
_data/list_index_blocks.json 三语索引页要原样保留的说明块（H1、导语、按科浏览、参考文献）
_species/*.md              物种与亚种的 front matter（只取 rank / family_id / genus_id 用于计数）

用法
----
    python _tools/build_list_index.py            # 写入 5 个页面
    python _tools/build_list_index.py --check    # 只比对磁盘
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "_data" / "taxonomy.json"
BLOCKS = ROOT / "_data" / "list_index_blocks.json"
SPECIES_DIR = ROOT / "_species"

LIST_MD = ROOT / "list.md"
LIST_MD_EN = ROOT / "en" / "list.md"
LIST_MD_ES = ROOT / "es" / "list.md"
SECTIONS_EN = ROOT / "en" / "list" / "sections.md"
SECTIONS_ES = ROOT / "es" / "list" / "sections.md"

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
# 支系的从属关系（与 .github/workflows/build_taxonomy_data.py 的 CLADE_PARENT 一致）：
# 新等翅类属于近等翅类，土栖等翅类属于新等翅类，页面上按这一层级嵌套显示。
CLADE_PARENT = {
    "isoptera": None,
    "euisoptera": "isoptera",
    "teletisoptera": "euisoptera",
    "icoisoptera": "euisoptera",
    "neoisoptera": "icoisoptera",
    "geoisoptera": "neoisoptera",
}

FRONT_MATTER = {
    "zh": """---
layout: default
title: 名录索引 — 现存等翅下目（白蚁）分类层级与各级页面
description: "现存等翅下目（白蚁）分类索引：6 支系、13 科、18 亚科、326 属、3021 种。按科浏览，再进入科页、亚科页、属页看形态记述与逐条物种名录；附 77 篇参考文献。"
lang: zh-CN
author: 班奈特格林
date: 2026-10-17
version: 2026.10.30
keywords: [白蚁, 等翅目, Isoptera, 学名, 中文名, 名录索引, 分类, Termitidae]
permalink: /list/
---""",
    "en": """---
layout: default
title: Index — Extant Isoptera (termites) taxonomy
description: "Taxonomic index of extant Isoptera: 6 clades, 13 families, 18 subfamilies, 326 genera and 3,021 species. Browse by family, then open the family, subfamily and genus pages for morphology and full species lists."
lang: en
author: 班奈特格林 (Bennet Green)
date: 2026-10-17
version: 2026.10.30
keywords: [termites, Isoptera, index, families, genera, species, taxonomy, Termitidae]
permalink: /en/list/
---""",
    "es": """---
layout: default
title: Índice — taxonomía de Isoptera (termitas) actuales
description: "Índice taxonómico de Isoptera actuales: 6 clados, 13 familias, 18 subfamilias, 326 géneros y 3.021 especies. Navegue por familia y abra las páginas de familia, subfamilia y género para la morfología y las listas completas."
lang: es
author: 班奈特格林 (Bennet Green)
date: 2026-10-17
version: 2026.10.30
keywords: [termitas, Isoptera, índice, familias, géneros, especies, taxonomía, Termitidae]
permalink: /es/list/
---""",
}

H1 = {
    "zh": "# 现存等翅下目 Extant Isoptera（白蚁领科）分类索引（2026.10.30）",
    "en": "# Extant Isoptera (Termites) — Taxonomic Index (2026.10.30)",
    "es": "# Isópteros actuales (termitas) — índice taxonómico (2026.10.30)",
}

LABELS = {
    "zh": {"family": "科", "subfamily": "亚科", "genus": "属", "species": "种", "subspecies": "亚种"},
    "en": {"family": "family", "subfamily": "subfamily", "genus": "genus",
           "species": "species", "subspecies": "subspecies"},
    "es": {"family": "familia", "subfamily": "subfamilia", "genus": "género",
           "species": "especie", "subspecies": "subespecie"},
}

NOTE = {
    "zh": "<p class=\"list-note\">本页只是分类索引：分类框架、按科浏览与参考文献在这里，"
          "每一科、亚科、属的形态、生物学与分布记述都在各自页面上，物种条目（拉丁学名、"
          "中文正名、命名人与年份、模式产地、分布）也在科页、亚科页或属页逐条列出。</p>",
    "en": "<p class=\"list-note\">This page is an index only: the taxonomic framework, the "
          "family browser and the references live here, while each family, subfamily and "
          "genus page carries its own morphology, biology and distribution text plus the "
          "species entries (scientific name, Chinese name, author and year, type locality, "
          "distribution).</p>",
    "es": "<p class=\"list-note\">Esta página es solo un índice: aquí están el marco "
          "taxonómico, el navegador por familia y las referencias; cada página de familia, "
          "subfamilia y género contiene su texto de morfología, biología y distribución, "
          "además de las entradas de especies (nombre científico, nombre chino, autor y año, "
          "localidad típica, distribución).</p>",
}

SECTIONS_NOTE = {
    "en": "<p class=\"list-note\">The English text of the family and subfamily accounts, "
          "including the illustrations, is collected here. Chinese versions of the same "
          "accounts sit on the family and subfamily pages; for the species lists see those "
          "pages, and for the index see <a href=\"{{ site.base_url }}/en/list/\">the "
          "taxonomic index</a>.</p>",
    "es": "<p class=\"list-note\">Aquí se reúne el texto en español de las familias y "
          "subfamilias, con sus ilustraciones. Las versiones en chino de esos mismos textos "
          "están en las páginas de familia y subfamilia; las listas de especies, en esas "
          "mismas páginas, y el índice en <a href=\"{{ site.base_url }}/es/list/\">el índice "
          "taxonómico</a>.</p>",
}

SECTIONS_TITLE = {
    "en": "# Family and subfamily accounts (English)",
    "es": "# Textos de familias y subfamilias (español)",
}

SECTIONS_FRONT_MATTER = {
    "en": """---
layout: default
title: Sections in English — family and subfamily accounts
description: "English text of all 13 family accounts and 18 subfamily accounts of extant termites, with illustrations; the Chinese originals sit on the family and subfamily pages."
lang: en
date: 2026-10-17
version: 2026.10.30
keywords: [termites, Isoptera, families, subfamilies, morphology, distribution]
permalink: /en/list/sections/
---""",
    "es": """---
layout: default
title: Textos en español — familias y subfamilias
description: "Texto en español de las 13 familias y 18 subfamilias de termitas actuales, con ilustraciones; los originales en chino están en las páginas de familia y subfamilia."
lang: es
date: 2026-10-17
version: 2026.10.30
keywords: [termitas, Isoptera, familias, subfamilias, morfología, distribución]
permalink: /es/list/sections/
---""",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def front_matter(text: str) -> dict:
    match = FM_RE.match(text)
    if not match:
        return {}
    out = {}
    for line in match.group(1).split("\n"):
        if ":" not in line or line.startswith((" ", "\t", "#")):
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip('"')
    return out


def count_species():
    """按 front matter 统计：family -> {genera: set, species, subspecies}、genus -> {species, subspecies}。"""
    families = {}
    genera = {}
    for path in sorted(SPECIES_DIR.glob("*.md")):
        meta = front_matter(read(path))
        if not meta.get("latin"):
            continue
        rank = meta.get("rank") or "species"
        family = meta.get("family_id") or ""
        genus = meta.get("genus_id") or ""
        if not genus:
            continue
        bucket = genera.setdefault(genus, {"species": 0, "subspecies": 0})
        bucket["species" if rank == "species" else "subspecies"] += 1
        fam = families.setdefault(family, {"genera": set(), "species": 0, "subspecies": 0})
        fam["genera"].add(genus)
        fam["species" if rank == "species" else "subspecies"] += 1
    return families, genera


def build_page_links(taxonomy):
    """科的属数取 _species 里实际出现的 genus_id。

    白蚁科的属挂在亚科之下，_data/taxonomy.json 中该科的 "genera" 是空列表，
    用 len(entry["genera"]) 会得到 0 属；按属页的实际来源统计才与科页、属页一致。
    """
    families_by_id = {entry["id"]: entry for entry in taxonomy["families"]}
    species_counts, _ = count_species()
    for family_id, entry in families_by_id.items():
        counts = species_counts.get(family_id) or {"genera": set(), "species": 0, "subspecies": 0}
        entry["counts"] = {
            "genus": len(counts["genera"]),
            "species": counts["species"],
            "subspecies": counts["subspecies"],
        }
    return families_by_id


def fmt_counts(language: str, counts, keys):
    labels = LABELS[language]
    parts = []
    for key in keys:
        value = counts.get(key) or 0
        if value:
            parts.append("%d %s" % (value, labels[key]))
    return " · ".join(parts)


CLADE_TOTALS_PREFIX = {"zh": "共 ", "en": "", "es": ""}
CLADE_TOTALS_SUFFIX = {
    "zh": "（含下分支系）",
    "en": " in total (including subordinate clades)",
    "es": " en total (incluidos los clados subordinados)",
}
CLADE_CHILD_JOIN = {"zh": "、", "en": " and ", "es": " y "}
CLADE_SENTENCE = {
    "zh": {"only": "本支系不含直接归属的科，下分 %s（见下文）。",
           "with": "下分 %s（见下文）。直接归入本支系的科如下："},
    "en": {"only": "This clade holds no families of its own; it is divided into %s (below).",
           "with": "It is divided into %s (below). The families placed directly in it are "
                   "listed below:"},
    "es": {"only": "Este clado no contiene familias propias; se divide en %s (abajo).",
           "with": "Se divide en %s (abajo). Las familias asignadas directamente a él se "
                   "listan a continuación:"},
}


def clade_order(taxonomy):
    """返回 (clade_by_id, children, roots)；子支系的顺序沿用 taxonomy 的文档顺序。"""
    clade_by_id = {entry["id"]: entry for entry in taxonomy["clades"]}
    children = {clade_id: [] for clade_id in clade_by_id}
    roots = []
    for entry in taxonomy["clades"]:
        clade_id = entry["id"]
        if clade_id not in CLADE_PARENT:
            sys.exit("error: 支系 %s 未在 CLADE_PARENT 中登记上级支系" % clade_id)
        parent = CLADE_PARENT[clade_id]
        if parent is None:
            roots.append(clade_id)
        elif parent in children:
            children[parent].append(clade_id)
        else:
            sys.exit("error: 支系 %s 的上级支系 %s 不存在" % (clade_id, parent))
    return clade_by_id, children, roots


def clade_totals(clade_id, clade_by_id, children, families_by_id, cache):
    """本支系与下分各支系的合计（科 / 亚科 / 属 / 种 / 亚种）。"""
    if clade_id in cache:
        return cache[clade_id]
    totals = {"family": 0, "subfamily": 0, "genus": 0, "species": 0, "subspecies": 0}
    for family_id in clade_by_id[clade_id]["families"]:
        member = families_by_id.get(family_id)
        if not member:
            continue
        totals["family"] += 1
        totals["subfamily"] += len(member["subfamilies"])
        for key in ("genus", "species", "subspecies"):
            totals[key] += member["counts"][key]
    for child_id in children[clade_id]:
        child = clade_totals(child_id, clade_by_id, children, families_by_id, cache)
        for key in totals:
            totals[key] += child[key]
    cache[clade_id] = totals
    return totals


def clade_heading(language: str, clade) -> str:
    return "%s %s" % (clade["zh"], clade["latin"]) if language == "zh" else clade["latin"]


def clade_link(language: str, clade_id, clade_by_id) -> str:
    heading = clade_heading(language, clade_by_id[clade_id])
    return '<a href="#%s">%s</a>' % (clade_id, html.escape(heading))


def clade_section(language, clade_id, depth, clade_by_id, children, families_by_id, cache):
    """一个支系一节：标题层级按嵌套深度递进（h2 → h6），计数含下分各支系。"""
    clade = clade_by_id[clade_id]
    level = min(depth + 1, 6)
    heading = html.escape(clade_heading(language, clade))
    lines = ['<h%d id="%s" class="clade-h clade-lvl-%d">%s</h%d>'
             % (level, clade_id, depth, heading, level), ""]
    totals = clade_totals(clade_id, clade_by_id, children, families_by_id, cache)
    count_text = CLADE_TOTALS_PREFIX[language] + fmt_counts(
        language, totals, ("family", "subfamily", "genus", "species", "subspecies"))
    if children[clade_id]:
        count_text += CLADE_TOTALS_SUFFIX[language]
    lines.append('<p class="clade-count clade-lvl-%d">%s</p>' % (depth, count_text))
    members = [families_by_id[family_id] for family_id in clade["families"]
               if family_id in families_by_id]
    kids = children[clade_id]
    if kids:
        links = CLADE_CHILD_JOIN[language].join(
            clade_link(language, kid, clade_by_id) for kid in kids)
        sentence = CLADE_SENTENCE[language]["with" if members else "only"] % links
        lines.append('<p class="clade-sub clade-lvl-%d">%s</p>' % (depth, sentence))
    if members:
        lines.append("")
        lines.append('<ul class="taxon-list clade-lvl-%d">' % depth)
        for member in members:
            if language == "zh":
                label = "%s <i>%s</i>" % (member["zh"], member["latin"])
            else:
                label = "<i>%s</i> %s" % (member["latin"], member["zh"])
            count_line = fmt_counts(language, member["counts"], ("genus", "species", "subspecies"))
            lines.append('<li><a href="{{ site.base_url }}/family/%s/">%s</a> '
                         '<span class="taxon-count">%s</span></li>'
                         % (member["id"], label, count_line))
        lines.append("</ul>")
    for kid in kids:
        lines.append("")
        lines.append(clade_section(language, kid, depth + 1, clade_by_id, children,
                                   families_by_id, cache))
    return "\n".join(lines)


def clade_index(language: str, taxonomy, families_by_id):
    clade_by_id, children, roots = clade_order(taxonomy)
    cache = {}
    return "\n\n".join(clade_section(language, root, 1, clade_by_id, children,
                                     families_by_id, cache) for root in roots)


def sections_page(language: str, taxonomy, prose):
    """把某一语言的科/亚科正文集中成一页（en / es）。"""
    entry = prose.get(language) or {"families": {}, "subfamilies": {}}
    fam_prose = entry.get("families") or {}
    sub_prose = entry.get("subfamilies") or {}
    parts = [SECTIONS_FRONT_MATTER[language], "", SECTIONS_TITLE[language], "",
             SECTIONS_NOTE[language], ""]

    def prose_block(prose_entry):
        block = []
        for paragraph in prose_entry.get("paragraphs") or []:
            block.append("<p>%s</p>" % html.escape(paragraph))
        if prose_entry.get("figure"):
            block.append(prose_entry["figure"])
        return "\n\n".join(block)

    index_items = []
    body = []
    for clade in taxonomy["clades"]:
        for family in taxonomy["families"]:
            if family["id"] not in clade["families"]:
                continue
            heading = "<i>%s</i> %s" % (family["latin"], family["zh"])
            index_items.append('<li><a href="#%s">%s</a></li>' % (family["id"], heading))
            body.append("<h2 id=\"%s\">%s</h2>" % (family["id"], heading))
            body.append("")
            body.append(prose_block(fam_prose.get(family["id"]) or {}))
            for subfamily in taxonomy["subfamilies"]:
                if subfamily["family"] != family["id"]:
                    continue
                sub_heading = "<i>%s</i> %s" % (subfamily["latin"], subfamily["zh"])
                body.append("")
                body.append("<h3 id=\"%s\">%s</h3>" % (subfamily["id"], sub_heading))
                body.append("")
                body.append(prose_block(sub_prose.get(subfamily["id"]) or {}))
    parts.append('<ul class="taxon-list">')
    parts.extend(index_items)
    parts.append("</ul>")
    parts.append("")
    parts.append("\n\n".join(body))
    return "\n".join(parts).rstrip() + "\n"


def index_page(language: str, taxonomy, blocks):
    block = blocks[language]
    families_by_id = build_page_links(taxonomy)
    parts = [FRONT_MATTER[language], "", H1[language], ""]
    if block.get("intro"):
        parts.append(block["intro"])
        parts.append("")
    if block.get("by_family"):
        parts.append(block["by_family"])
        parts.append("")
    parts.append(NOTE[language])
    parts.append("")
    parts.append(clade_index(language, taxonomy, families_by_id))
    parts.append("")
    if language == "en":
        parts.append("<p>English text of the family and subfamily accounts: "
                     "<a href=\"{{ site.base_url }}/en/list/sections/\">sections in English</a>.</p>")
        parts.append("")
    elif language == "es":
        parts.append("<p>Texto en español de las familias y subfamilias: "
                     "<a href=\"{{ site.base_url }}/es/list/sections/\">textos en español</a>.</p>")
        parts.append("")
    if language == "zh":
        # 目级分科检索表（_data/fauna_keys.json 的 "/list/" 条目；据 Hellemans 等 2024 Note 2）
        parts.append('{%- assign fk = site.data.fauna_keys["/list/"] -%}'
                     '{%- if fk %}{% include fauna-keys.html fk=fk %}{%- endif %}')
        parts.append("")
    if block.get("references"):
        parts.append(block["references"])
    return "\n".join(parts).rstrip() + "\n"


def render():
    taxonomy = json.loads(read(TAXONOMY))
    blocks = json.loads(read(BLOCKS))
    prose = json.loads(read(ROOT / "_data" / "taxon_prose.json"))
    outputs = {
        LIST_MD: index_page("zh", taxonomy, blocks),
        LIST_MD_EN: index_page("en", taxonomy, blocks),
        LIST_MD_ES: index_page("es", taxonomy, blocks),
        SECTIONS_EN: sections_page("en", taxonomy, prose),
        SECTIONS_ES: sections_page("es", taxonomy, prose),
    }
    return {path: text.encode("utf-8") for path, text in outputs.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    if args.check:
        bad = [str(path.relative_to(ROOT)) for path, data in outputs.items()
               if not path.is_file() or path.read_bytes() != data]
        if bad:
            sys.exit("not up to date: " + ", ".join(sorted(bad)))
        print("ok")
        return 0
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print("wrote %s (%d bytes)" % (path.relative_to(ROOT), len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
