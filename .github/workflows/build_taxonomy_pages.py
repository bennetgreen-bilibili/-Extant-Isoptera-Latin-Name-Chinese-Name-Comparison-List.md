#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate taxonomic hub pages: family/, subfamily/, genus/ (3,089 species pages' parents).

Why this exists
---------------
The site has 3,089 species pages but, before this script, their only "parent" was the
single 450 KB /list/ page. Search engines therefore saw almost no intermediate
classification level: crawl depth 2 for every species, no page that answers
"what is genus X" / "which genera are in family Y".

This script reads the front matter of every _species/*.md (same minimal YAML parser as
build_genus_index.py, no PyYAML dependency) and writes one page per taxon:

    family/<family_id>.md        13 pages
    subfamily/<subfamily_id>.md  18 pages (all currently in Termitidae)
    genus/<genus_id>.md         326 pages

Each page is Chinese-only: a short unique summary (BreadcrumbList comes from
_includes/breadcrumb-jsonld.html via the breadcrumb list in front matter), a local search
box scoped to that taxon, a distribution map (reusing _includes/distribution-map.html),
the family/subfamily prose copied out of /list/, and the child list.

The prose (形态/分布/经济意义) is copied from the /list/ section between a family (<h3>) or
subfamily (<h4>) heading and the next heading. It still lives in /list/ as well — the hub
page links back to that anchor. Copying it is deliberate: /list/ is a single 450 KB page,
so "白蚁科的形态特征" had no citable, shareable landing page of its own before this.

The subfamily maps (assets/geo/subfamily/<id>.geojson, _data/subfamily_maps.json) are
merged here from the committed per-genus maps: build_occurrence_geojson.py pulls GBIF
records per genus and has no subfamily level, and merging offline keeps this script
deterministic and network-free.

It also writes _data/taxonomy_images.json, used by _layouts/default.html as the og:image
fallback for species pages (per-family photo) and by the hub pages themselves.

Pages are generated deterministically and idempotently: sorted keys, LF endings, files
whose content did not change are left untouched. Run it after build_species_body.py and
before build_sitemap_txt.py (see .github/workflows/pages.yml).

Usage:
    python .github/workflows/build_taxonomy_pages.py           # write
    python .github/workflows/build_taxonomy_pages.py --check   # verify without writing
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "_species"
IMAGES_DIR = ROOT / "assets" / "images"
LIST_MD = ROOT / "list.md"
DATA_OUT = ROOT / "_data" / "taxonomy_images.json"
OUT_DIRS = {"family": ROOT / "family", "subfamily": ROOT / "subfamily", "genus": ROOT / "genus"}
DEFAULT_IMAGE = "/assets/images/mastotermitidae.jpg"
RANK_LABEL = {"family": "Family", "subfamily": "Subfamily", "genus": "Genus"}
SB = "{{ site.base_url }}"
DATASET_ID = "{{ site.base_url }}/#dataset"
DATASET_VERSION = "{{ site.dataset.version }}"
DATASET_DATE = "{{ site.dataset.version | replace: '.', '-' }}"

FM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)[ \t]*:[ \t]*(.*)$")
FIGURE_RE = re.compile(r'<figure class="taxa-illustration">.*?</figure>', re.S)
IMG_RE = re.compile(r"/assets/images/([a-z0-9\-]+)\.(?:jpg|png)")
HEADING_RE = re.compile(r'<h([2-5])\s+id="([a-z0-9\-]+)"[^>]*>.*?</h\1>', re.S)
INCLUDE_MAP_RE = re.compile(r"^[ \t]*\{%\s*include\s+distribution-map\.html.*?%\}[ \t]*$", re.M)
TAG_ONLY_RE = re.compile(r"^[ \t]*<[^>]+>[ \t]*$")
CJK_RE = re.compile(u"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]")
GEO_DIR = ROOT / "assets" / "geo"
GEO_FAMILY = GEO_DIR / "family"
GEO_GENUS = GEO_DIR / "genus"
GEO_SUBFAMILY = GEO_DIR / "subfamily"
SUBFAMILY_MAPS_OUT = ROOT / "_data" / "subfamily_maps.json"


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


def list_figures():
    """Map taxon id -> <figure> block copied verbatim from list.md.

    Reusing the block keeps the same caption and photo credit as /list/ (the photos are
    CC BY-NC / CC BY-NC-SA from iNaturalist and must keep their attribution), instead of
    re-deriving credits here.
    """
    if not LIST_MD.is_file():
        return {}
    text = LIST_MD.read_text(encoding="utf-8")
    figures = {}
    for block in FIGURE_RE.findall(text):
        m = IMG_RE.search(block)
        if not m:
            continue
        key = re.sub(r"-\d+$", "", m.group(1))
        figures.setdefault(key, block.strip())
    return figures


def html_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def reflow(lines):
    """Re-join the hard-wrapped lines of one /list/ paragraph.

    Chinese may break anywhere, so a newline inside a paragraph is not a space; between
    two Latin tokens it is ("Termes Linnaeus," + "1758；" -> "Termes Linnaeus, 1758；").
    """
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


def list_sections():
    """Map taxon id -> list of prose paragraphs, copied out of the /list/ sections.

    Only the family (<h3>) and subfamily (<h4>) sections carry prose; a genus section
    (<h5>) is just its map plus the species links. Illustration <figure> blocks and the
    distribution-map includes are dropped here, because a hub page shows its own map.
    """
    if not LIST_MD.is_file():
        return {}
    text = LIST_MD.read_text(encoding="utf-8")
    text = FIGURE_RE.sub("", text)
    text = INCLUDE_MAP_RE.sub("", text)
    heads = list(HEADING_RE.finditer(text))
    sections = {}
    for index, head in enumerate(heads):
        if int(head.group(1)) not in (3, 4):
            continue
        end = heads[index + 1].start() if index + 1 < len(heads) else len(text)
        paragraphs = []
        for block in re.split(r"\n[ \t]*\n", text[head.end():end]):
            lines = [ln for ln in block.splitlines() if ln.strip() and not TAG_ONLY_RE.match(ln)]
            if not lines:
                continue
            paragraph = reflow(lines).strip()
            if paragraph:
                paragraphs.append(paragraph)
        if paragraphs:
            sections[head.group(2)] = paragraphs
    return sections


def parse_cells(path):
    """Read the 1 degree grid of one committed taxon map -> {(lon, lat): records}."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}, ""
    cells = {}
    for feature in data.get("features") or []:
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        if len(coords) < 2:
            continue
        key = (round(float(coords[0]), 3), round(float(coords[1]), 3))
        count = int((feature.get("properties") or {}).get("n") or 0)
        cells[key] = cells.get(key, 0) + count
    props = data.get("properties") or {}
    return cells, str(props.get("generated") or "")


def render_geojson(properties, cells):
    """Same byte layout as build_occurrence_geojson.render_geojson (review-friendly)."""
    body = ",\n".join(
        "    " + json.dumps(
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]},
             "properties": {"n": cells[(lon, lat)]}},
            ensure_ascii=False, separators=(",", ":"))
        for lon, lat in sorted(cells, key=lambda key: (key[1], key[0]))
    )
    return (
        "{\n"
        '"type":"FeatureCollection",\n'
        '"properties":%s,\n'
        '"features":[\n%s\n'
        "]\n"
        "}\n"
    ) % (json.dumps(properties, ensure_ascii=False, separators=(",", ":")), body)


def image_path(taxon_id):
    for name in ("%s.jpg" % taxon_id, "%s.png" % taxon_id, "%s-1.jpg" % taxon_id):
        if (IMAGES_DIR / name).is_file():
            return "/assets/images/" + name
    return None


def plural(n, unit):
    return "%d %s" % (n, unit)


def count_phrase(species, subspecies):
    parts = [plural(species, "种")]
    if subspecies:
        parts.append(plural(subspecies, "亚种"))
    return "、".join(parts)


def count_phrase_full(subfamilies, genera, species, subspecies):
    parts = []
    if subfamilies:
        parts.append(plural(subfamilies, "个亚科"))
    parts.append(plural(genera, "个属"))
    parts.append(plural(species, "个种"))
    if subspecies:
        parts.append(plural(subspecies, "个亚种"))
    return "、".join(parts)


# Short neutral tails used only to pad a description up to the 150-character target.
# They are appended after the rank-specific pool, shortest last, and never repeated.
FILLERS = [
    "详见完整名录。",
    "按分类系统逐级排列。",
    "数据来自 CC BY 4.0 数据集。",
    "并附中文正名与引用格式。",
    "亦可从名录对应章节进入。",
    "页面持续更新。",
]


def fit_description(core, pool, fillers=None):
    """Append sentences from pool/fillers while keeping the result within 150-160 chars.

    Bing's SEO report flags descriptions shorter than ~150 characters; the site target is
    150-160 characters (character count, not bytes), so padding stops as soon as the text
    reaches 150 and never crosses 160.
    """
    desc = core
    for sentence in pool:
        if len(desc) >= 150:
            break
        if len(desc) + len(sentence) <= 160:
            desc += sentence
    for sentence in (fillers or FILLERS):
        if len(desc) >= 150:
            break
        if len(desc) + len(sentence) <= 160:
            desc += sentence
    return desc


def main():
    write = "--check" not in sys.argv

    figures = list_figures()
    families, subfamilies, genera = {}, {}, {}
    per_genus = {}
    species_total = subspecies_total = 0

    for path in sorted(SPECIES_DIR.glob("*.md")):
        slug = path.stem
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        if not fm.get("latin") or not fm.get("family_id") or not fm.get("genus_id"):
            sys.exit("bad front matter in %s" % path.name)
        rank = str(fm.get("rank", "species")).lower()
        is_ssp = rank == "subspecies"
        fid = fm["family_id"].strip()
        sid = (fm.get("subfamily_id") or "").strip()
        gid = fm["genus_id"].strip()

        fam = families.setdefault(fid, {
            "id": fid, "zh": fm["family_zh"].strip(), "latin": fm["family_latin"].strip(),
            "clade_zh": fm["clade_zh"].strip(), "clade_latin": fm["clade_latin"].strip(),
            "subfamilies": [], "species": 0, "subspecies": 0, "genera": {},
        })
        if is_ssp:
            fam["subspecies"] += 1
        else:
            fam["species"] += 1
        fam["genera"][gid] = True

        if sid:
            sub = subfamilies.setdefault(sid, {
                "id": sid, "zh": fm["subfamily_zh"].strip(), "latin": fm["subfamily_latin"].strip(),
                "family": fid, "species": 0, "subspecies": 0, "genera": {},
            })
            if is_ssp:
                sub["subspecies"] += 1
            else:
                sub["species"] += 1
            sub["genera"][gid] = True
            if sid not in fam["subfamilies"]:
                fam["subfamilies"].append(sid)

        gen = genera.setdefault(gid, {
            "id": gid, "zh": fm["genus_zh"].strip(), "latin": fm["genus_latin"].strip(),
            "family": fid, "subfamily": sid,
            "species": 0, "subspecies": 0, "rows": [], "type_species": "",
        })
        if is_ssp:
            gen["subspecies"] += 1
        else:
            gen["species"] += 1
        if str(fm.get("type", "")).lower() == "true":
            gen["type_species"] = fm["latin"].strip()
        gen["rows"].append({
            "slug": slug, "latin": fm["latin"].strip(), "zh": (fm.get("zh") or "").strip(),
            "author_year": (fm.get("author_year") or "").strip(), "rank": rank,
            "type": str(fm.get("type", "")).lower() == "true",
        })
        if is_ssp:
            subspecies_total += 1
        else:
            species_total += 1

    if species_total != 3021 or subspecies_total != 68:
        sys.exit("unexpected counts: %d species / %d subspecies (expected 3021 / 68)"
                 % (species_total, subspecies_total))
    if len(families) != 13 or len(subfamilies) != 18 or len(genera) != 326:
        sys.exit("unexpected taxa: %d families / %d subfamilies / %d genera"
                 % (len(families), len(subfamilies), len(genera)))

    # 科 / 亚科介绍：直接取自 /list/ 对应小节的正文（属小节只有地图与物种链接，没有正文）
    intros = list_sections()
    no_prose = [tid for tid in list(families) + list(subfamilies) if tid not in intros]
    if no_prose:
        sys.exit("list.md has no prose for: %s" % ", ".join(sorted(no_prose)))

    for gen in genera.values():
        gen["rows"].sort(key=lambda r: (0 if r["rank"] != "subspecies" else 1,
                                        r["latin"].casefold(), r["slug"]))
    for fam in families.values():
        fam["subfamilies"].sort()
        fam["genera"] = sorted(fam["genera"])
    for sub in subfamilies.values():
        sub["genera"] = sorted(sub["genera"])

    # 亚科级分布图：GBIF 的抓取是按属做的，没有亚科层级；这里把本亚科各属已提交的
    # 1° 网格地图按坐标合并，得到一份可直接给 distribution-map.html 用的单文件。
    subfamily_maps, geo_outputs = [], {}
    for sid in sorted(subfamilies):
        sub = subfamilies[sid]
        cells, generated = {}, ""
        for gid in sub["genera"]:
            path = GEO_GENUS / (gid + ".geojson")
            if not path.is_file():
                continue
            part, stamp = parse_cells(path)
            for key, count in part.items():
                cells[key] = cells.get(key, 0) + count
            generated = stamp or generated
        if not cells:
            continue
        fam = families[sub["family"]]
        props = {
            "level": "subfamily",
            "subfamily": sub["latin"],
            "subfamily_zh": sub["zh"],
            "subfamily_id": sid,
            "family": fam["latin"],
            "family_zh": fam["zh"],
            "family_id": fam["id"],
            "records": sum(cells.values()),
            "cells": len(cells),
            "genera": len(sub["genera"]),
            "species": sub["species"],
            "grid": "1 degree",
            "taxon_scope": "checklist_extant",
            "generated": generated,
            "source": ("merged by build_taxonomy_pages.py from the per-genus 1 degree maps of "
                       "this subfamily; original records: GBIF occurrence search API "
                       "(assets/geo/genus/*.geojson, generated %s)" % generated),
        }
        geo_outputs[GEO_SUBFAMILY / (sid + ".geojson")] = render_geojson(props, cells)
        subfamily_maps.append({
            "id": sid, "zh": sub["zh"], "latin": sub["latin"],
            "family_id": fam["id"], "family_zh": fam["zh"],
            "records": props["records"], "cells": props["cells"],
            "species": sub["species"], "genera": len(sub["genera"]),
            "file": "assets/geo/subfamily/%s.geojson" % sid,
        })
    subfamily_map_ids = {entry["id"] for entry in subfamily_maps}

    images = {"_meta": {"families": len(families), "subfamilies": len(subfamilies),
                        "default": DEFAULT_IMAGE},
              "family": {}, "subfamily": {}}
    for fid in families:
        path = image_path(fid)
        if path:
            images["family"][fid] = path
    for sid in subfamilies:
        path = image_path(sid)
        if path:
            images["subfamily"][sid] = path

    def taxon_link(taxon_id, rank):
        return SB + "/" + rank + "/" + taxon_id + "/"

    def stats_line(fam=None, sub=None, gen=None):
        bits = []
        if fam:
            if fam["subfamilies"]:
                bits.append(plural(len(fam["subfamilies"]), "亚科"))
            bits.append(plural(len(fam["genera"]), "属"))
            bits.append(count_phrase(fam["species"], fam["subspecies"]))
        elif sub:
            bits.append(plural(len(sub["genera"]), "属"))
            bits.append(count_phrase(sub["species"], sub["subspecies"]))
        else:
            bits.append(count_phrase(gen["species"], gen["subspecies"]))
        return " · ".join(bits)

    def crumb_nav(rank, fam=None, sub=None, gen=None):
        parts = ['<a href="%s/list/">名录</a>' % SB]
        if fam:
            parts.append('<a href="%s/list/#%s">%s</a>' % (SB, fam["id"], fam["zh"]))
        if sub:
            parts.append('<a href="%s/list/#%s">%s</a>' % (SB, sub["id"], sub["zh"]))
        if gen:
            parts.append('<a href="%s/list/#%s">%s <i>%s</i></a>' % (SB, gen["id"], gen["zh"], gen["latin"]))
        label = {"family": "科", "subfamily": "亚科", "genus": "属"}[rank]
        return ('<nav class="taxon-crumbs" aria-label="分类位置">' + " › ".join(parts)
                + " › <span>本%s</span></nav>" % label)

    def html_list(items):
        return "<ul class=\"taxon-list\">" + "".join(items) + "</ul>"

    def genus_item(gid):
        gen = genera[gid]
        return ('<li><a href="%s/genus/%s/"><i>%s</i> %s</a> <span class="taxon-count">%s</span></li>'
                % (SB, gid, gen["latin"], gen["zh"], count_phrase(gen["species"], gen["subspecies"])))

    def species_items(gen):
        out = []
        for row in gen["rows"]:
            mark = ' <span class="taxon-type" title="模式种">★ 模式种</span>' if row["type"] else ""
            if row["rank"] == "subspecies":
                out.append('<li class="taxon-sub"><a href="%s/species/%s/"><i>%s</i> %s %s</a>%s</li>'
                           % (SB, row["slug"], row["latin"], row["author_year"], row["zh"], mark))
            else:
                out.append('<li><a href="%s/species/%s/"><i>%s</i> %s %s</a>%s</li>'
                           % (SB, row["slug"], row["latin"], row["author_year"], row["zh"], mark))
        return out

    def taxon_jsonld(rank, taxon_id, latin, zh, parent, title_rank_zh):
        payload = {
            "@context": "https://schema.org",
            "@type": "Taxon",
            "@id": SB + "/%(r)s/%(i)s/#taxon" % {"r": rank, "i": taxon_id},
            "name": display_latin(latin),
            "alternateName": [zh],
            "taxonRank": RANK_LABEL[rank],
            "url": taxon_link(taxon_id, rank),
            "isPartOf": {"@type": "Dataset", "@id": DATASET_ID},
            "version": DATASET_VERSION,
            "dateModified": DATASET_DATE,
        }
        if parent:
            payload["parentTaxon"] = parent
        return ('<script type="application/ld+json">\n'
                + json.dumps(payload, ensure_ascii=False, indent=1) + "\n</script>")

    def display_latin(latin):
        return latin.capitalize() if latin.isupper() else latin

    def figure_html(taxon_id, alt_prefix):
        block = figures.get(taxon_id)
        if not block or not image_path(taxon_id):
            return ""
        return "\n" + block + "\n"

    def desc_for(rank, fam=None, sub=None, gen=None):
        if rank == "family":
            core = ("%s（%s）是%s（%s）下的一个科，本站收录 %s。"
                    % (fam["zh"], fam["latin"], fam["clade_zh"], fam["clade_latin"],
                       count_phrase_full(len(fam["subfamilies"]), len(fam["genera"]),
                                         fam["species"], fam["subspecies"])))
            pool = [
                "本页按分类系统列出该科的全部%s与属，并汇总各级物种数量。" % ("亚科" if fam["subfamilies"] else ""),
                "点击任一属可查看其全部物种与亚种，点击物种可查看模式产地、分布地图、同属物种与 GB/T 7714、BibTeX、RIS 引用格式。",
                "科的形态特征、分布格局与经济意义见完整名录的对应章节。",
            ]
            if not fam["subfamilies"]:
                pool[0] = "本页按分类系统列出该科的全部属，并汇总各级物种数量。"
            return fit_description(core, pool)
        if rank == "subfamily":
            parent = families[sub["family"]]
            core = ("%s（%s）是%s（%s）下的一个亚科，本站收录 %s。"
                    % (sub["zh"], sub["latin"], parent["zh"], parent["latin"],
                       count_phrase_full(0, len(sub["genera"]), sub["species"], sub["subspecies"])))
            pool = [
                "本页列出该亚科下属的全部属及其物种数量，逐级链接到属页面与物种页面。",
                "物种页包含拉丁学名与命名人年份、中文正名、模式产地、分布地图、同属物种、参考文献与引用格式。",
                "亚科的形态、分布与经济意义见完整名录的对应章节。",
            ]
            return fit_description(core, pool)
        parent = families[gen["family"]]
        where = ""
        if gen["subfamily"]:
            where = "，隶属%s（%s）" % (subfamilies[gen["subfamily"]]["zh"],
                                         subfamilies[gen["subfamily"]]["latin"])
        core = ("%s（%s）是%s（%s）下的一个属%s，本站收录 %s。"
                % (gen["zh"], gen["latin"], parent["zh"], parent["latin"], where,
                   count_phrase(gen["species"], gen["subspecies"])))
        pool = [
            "本页列出该属的全部物种与亚种%s，物种页含模式产地、分布地图与同属物种。" % ("，并标注模式种" if gen["type_species"] else ""),
            "每一条目均可跳转到对应的物种页面，查看拉丁学名、命名人年份、中文正名、参考文献与引用格式。",
            "属的分类位置与名录锚点见完整名录的对应章节。",
        ]
        return fit_description(core, pool)

    def front_matter(title, description, permalink, breadcrumb, image, family_id,
                     last_modified="2026-10-30", has_map=False, taxon_search=False):
        lines = ["---", "layout: default", "title: " + json.dumps(title, ensure_ascii=False),
                 "description: " + json.dumps(description, ensure_ascii=False),
                 "lang: zh-CN", "lang_only: true", "author: 班奈特格林",
                 "family_id: " + family_id,
                 "last_modified_at: " + last_modified,
                 "permalink: " + permalink, "sitemap: true"]
        if has_map:
            lines.append("has_map: true")
        if taxon_search:
            lines.append("taxon_search: true")
        if image:
            lines.append("image: " + json.dumps(image))
        lines.append("breadcrumb:")
        for crumb in breadcrumb:
            lines.append("  - name: " + json.dumps(crumb[0], ensure_ascii=False))
            lines.append("    url: " + json.dumps(crumb[1]))
        lines.append("---")
        return "\n".join(lines) + "\n"

    def breadcrumb_for(rank, fam=None, sub=None, gen=None):
        crumbs = [("名录", "/list/")]
        if fam:
            crumbs.append(("%s %s" % (fam["zh"], fam["latin"]), "/family/%s/" % fam["id"]))
        if sub:
            crumbs.append(("%s %s" % (sub["zh"], sub["latin"]), "/subfamily/%s/" % sub["id"]))
        if gen:
            crumbs.append(("%s %s" % (gen["zh"], gen["latin"]), "/genus/%s/" % gen["id"]))
        return crumbs

    def footer_nav(rank, taxon_id):
        back = ('<p class="taxon-more">该%s的形态、分布与经济意义：'
                '<a href="%s/list/#%s">完整名录对应章节</a>；'
                '结构化数据：<a href="%s/data/">数据与下载</a>。</p>'
                % ({"family": "科", "subfamily": "亚科", "genus": "属"}[rank], SB, taxon_id, SB))
        return back + '\n<p class="taxon-back"><a href="%s/list/">← 返回完整名录</a> · <a href="%s/">首页</a></p>' % (SB, SB)

    def has_geo(rank, taxon_id):
        if rank == "subfamily":
            return taxon_id in subfamily_map_ids
        directory = {"family": GEO_FAMILY, "genus": GEO_GENUS}[rank]
        return (directory / (taxon_id + ".geojson")).is_file()

    def distribution_section(rank, taxon_id):
        if not has_geo(rank, taxon_id):
            return ""
        return ('<section class="taxon-section taxon-distribution" data-pagefind-ignore>\n'
                '<h2>分布图</h2>\n'
                '{%% include distribution-map.html mode="%s" id="%s" %%}\n'
                '</section>\n' % (rank, taxon_id))

    def intro_section(taxon_id, heading):
        paragraphs = intros.get(taxon_id) or []
        if not paragraphs:
            return ""
        body = "".join("<p>%s</p>\n" % html_escape(p) for p in paragraphs)
        return ('<section class="taxon-section taxon-intro" data-pagefind-ignore>\n<h2>' + heading + '</h2>\n'
                + body
                + '<p class="taxon-src">以上文字取自<a href="%s/list/#%s">完整名录</a>的对应章节，'
                  '参考文献与完整论述见该页。</p>\n</section>\n' % (SB, taxon_id))

    def genus_intro(gen, mapped):
        fam = families[gen["family"]]
        parts = ['本属隶属<a href="%s/family/%s/">%s <i>%s</i></a>'
                 % (SB, fam["id"], fam["zh"], display_latin(fam["latin"]))]
        if gen["subfamily"]:
            sub = subfamilies[gen["subfamily"]]
            parts.append('下的<a href="%s/subfamily/%s/">%s <i>%s</i></a>'
                         % (SB, sub["id"], sub["zh"], display_latin(sub["latin"])))
        paragraphs = ["".join(parts) + "，本站收录 %s。"
                      % count_phrase(gen["species"], gen["subspecies"])]
        if gen["type_species"]:
            paragraphs.append("模式种：<i>%s</i>。" % gen["type_species"])
        if mapped:
            paragraphs.append("本页附有本属的分布图（GBIF 记录按 1° 网格汇总）；"
                              "点开物种条目可查看各自模式产地、分布与参考文献。")
        else:
            paragraphs.append("GBIF 中暂无本属带坐标的记录，本页因此不附图；"
                              "点开物种条目仍可查看各自模式产地与参考文献。")
        body = "".join("<p>%s</p>\n" % text for text in paragraphs)
        return '<section class="taxon-section taxon-intro" data-pagefind-ignore>\n<h2>属级介绍</h2>\n' + body + "</section>\n"

    # 数据键必须与 _data/ 里的文件名一致：_data/fauna_families.json → site.data.fauna_families。
    # 曾按单数拼成 fauna_family / fauna_genus，与文件名不匹配 → fz 恒为 nil，
    # 整段形态描述永远不渲染（且不报错），只有页面 diff 会露馅。
    FAUNA_DATA_KEY = {"family": "fauna_families", "genus": "fauna_genera", "species": "fauna_species"}

    def fauna_section(kind, taxon_id):
        """据《中国动物志·昆虫纲 第十七卷 等翅目》(2000) 改写而来的形态描述。

        数据在 _data/fauna_<复数>.json，键为页面 URL；没有对应条目时不输出任何内容。
        """
        return ('{%%- assign fz = site.data.%s["/%s/%s/"] -%%}'
                '{%%- if fz %%}\n{%% include fauna-%s.html fauna=fz %%}\n{%%- endif %%}\n'
                % (FAUNA_DATA_KEY[kind], kind, taxon_id, kind))

    def genus_map_note(gen):
        fam = families[gen["family"]]
        links = ['<a href="%s/family/%s/">%s的科级分布图</a>' % (SB, fam["id"], fam["zh"])]
        if gen["subfamily"]:
            sub = subfamilies[gen["subfamily"]]
            links.append('<a href="%s/subfamily/%s/">%s的亚科级分布图</a>' % (SB, sub["id"], sub["zh"]))
        return ('<section class="taxon-section taxon-distribution" data-pagefind-ignore>\n<h2>分布图</h2>\n'
                '<p class="taxon-map-empty">GBIF 中暂无该属带坐标的记录，因此本页没有属级地图；'
                '可参考%s。</p>\n</section>\n' % "或".join(links))

    def search_box(scope_zh, anchors, species_count):
        return (
            '<div class="taxon-search" data-pagefind-ignore data-anchors="%s" '
            'data-index="%s/search-index.json" data-search-page="%s/search/">\n'
            '<label class="taxon-search-label" for="taxon-search-input">'
            '在本%s范围内检索（%d 个种与亚种）：中文名或拉丁学名</label>\n'
            '<input type="search" id="taxon-search-input" class="taxon-search-input" '
            'placeholder="如 白蚁 / Amitermes / abruptus" autocomplete="off" spellcheck="false" '
            'role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">\n'
            '<p class="taxon-search-status" hidden></p>\n'
            '<ul class="taxon-search-results" hidden></ul>\n'
            '<p class="taxon-search-hint">只检索本%s登记的分类单元；全站网页请用'
            '<a href="%s/search/">全文搜索</a>。</p>\n'
            '</div>\n'
            % (",".join(anchors), SB, SB, scope_zh, species_count, scope_zh, SB))

    outputs = {}
    for fid in sorted(families):
        fam = families[fid]
        parent = {"@type": "Taxon", "name": fam["clade_zh"], "alternateName": [fam["clade_latin"]],
                  "taxonRank": "Clade"}
        sections = []
        if fam["subfamilies"]:
            items = []
            for sid in fam["subfamilies"]:
                sub = subfamilies[sid]
                items.append('<li><a href="%s/subfamily/%s/"><i>%s</i> %s</a> <span class="taxon-count">%s</span></li>'
                             % (SB, sid, sub["latin"], sub["zh"],
                                count_phrase_full(0, len(sub["genera"]), sub["species"], sub["subspecies"])))
            sections.append("<h2>亚科（%d）</h2>" % len(fam["subfamilies"]) + html_list(items))
        genus_items = [genus_item(gid) for gid in fam["genera"]]
        sections.append("<h2>属（%d）</h2>" % len(fam["genera"]) + html_list(genus_items))
        body = (
            '<article class="taxon-page">\n'
            + crumb_nav("family", fam=fam) + "\n"
            + '<header class="taxon-header">\n'
            + '<h1>%s <i>%s</i></h1>\n' % (fam["zh"], display_latin(fam["latin"]))
            + '<p class="taxon-meta">%s · %s</p>\n' % (fam["clade_zh"] + " " + fam["clade_latin"], stats_line(fam=fam))
            + "</header>\n"
            + search_box("科", [fid] + fam["subfamilies"] + fam["genera"],
                         fam["species"] + fam["subspecies"])
            + figure_html(fid, fam["zh"])
            + distribution_section("family", fid)
            + intro_section(fid, "科级介绍")
            + fauna_section("family", fid)
            + "\n".join('<section class="taxon-section">\n' + s + "\n</section>" for s in sections) + "\n"
            + footer_nav("family", fid) + "\n</article>\n"
            + taxon_jsonld("family", fid, fam["latin"], fam["zh"], parent, "科")
        )
        desc = desc_for("family", fam=fam)
        outputs[OUT_DIRS["family"] / (fid + ".md")] = (
            front_matter("%s %s 分类名录" % (fam["zh"], fam["latin"]), desc,
                         "/family/%s/" % fid, breadcrumb_for("family", fam=fam),
                         image_path(fid), fid,
                         has_map=has_geo("family", fid), taxon_search=True)
            + body)

    for sid in sorted(subfamilies):
        sub = subfamilies[sid]
        fam = families[sub["family"]]
        parent = {"@type": "Taxon", "name": display_latin(fam["latin"]), "alternateName": [fam["zh"]],
                  "taxonRank": "Family", "url": SB + "/family/" + fam["id"] + "/"}
        sections = []
        items = [genus_item(gid) for gid in sub["genera"]]
        sections.append("<h2>属（%d）</h2>" % len(sub["genera"]) + html_list(items))
        body = (
            '<article class="taxon-page">\n'
            + crumb_nav("subfamily", fam=fam, sub=sub) + "\n"
            + '<header class="taxon-header">\n'
            + '<h1>%s <i>%s</i></h1>\n' % (sub["zh"], display_latin(sub["latin"]))
            + '<p class="taxon-meta">%s · %s</p>\n' % (fam["zh"] + " " + fam["latin"], stats_line(sub=sub))
            + "</header>\n"
            + search_box("亚科", [sid] + sub["genera"], sub["species"] + sub["subspecies"])
            + figure_html(sid, sub["zh"])
            + distribution_section("subfamily", sid)
            + intro_section(sid, "亚科级介绍")
            + "\n".join('<section class="taxon-section">\n' + s + "\n</section>" for s in sections) + "\n"
            + footer_nav("subfamily", sid) + "\n</article>\n"
            + taxon_jsonld("subfamily", sid, sub["latin"], sub["zh"], parent, "亚科")
        )
        desc = desc_for("subfamily", sub=sub)
        outputs[OUT_DIRS["subfamily"] / (sid + ".md")] = (
            front_matter("%s %s 属与物种名录" % (sub["zh"], sub["latin"]), desc,
                         "/subfamily/%s/" % sid, breadcrumb_for("subfamily", fam=fam, sub=sub),
                         image_path(sid), fam["id"],
                         has_map=has_geo("subfamily", sid), taxon_search=True)
            + body)

    for gid in sorted(genera):
        gen = genera[gid]
        fam = families[gen["family"]]
        parent = None
        if gen["subfamily"]:
            sub = subfamilies[gen["subfamily"]]
            parent = {"@type": "Taxon", "name": display_latin(sub["latin"]),
                      "alternateName": [sub["zh"]], "taxonRank": "Subfamily",
                      "url": SB + "/subfamily/" + sub["id"] + "/"}
        else:
            parent = {"@type": "Taxon", "name": display_latin(fam["latin"]),
                      "alternateName": [fam["zh"]], "taxonRank": "Family",
                      "url": SB + "/family/" + fam["id"] + "/"}
        sections = ["<h2>物种（%s）</h2>" % count_phrase(gen["species"], gen["subspecies"])
                    + html_list(species_items(gen))]
        mapped = has_geo("genus", gid)
        body = (
            '<article class="taxon-page">\n'
            + crumb_nav("genus", fam=fam, sub=subfamilies.get(gen["subfamily"]), gen=gen) + "\n"
            + '<header class="taxon-header">\n'
            + '<h1>%s <i>%s</i></h1>\n' % (gen["zh"], display_latin(gen["latin"]))
            + '<p class="taxon-meta">%s · %s</p>\n' % (fam["zh"] + " " + fam["latin"], stats_line(gen=gen))
            + "</header>\n"
            + search_box("属", [gid], gen["species"] + gen["subspecies"])
            + figure_html(gid, gen["zh"])
            + (distribution_section("genus", gid) if mapped else genus_map_note(gen))
            + genus_intro(gen, mapped)
            + fauna_section("genus", gid)
            + "\n".join('<section class="taxon-section">\n' + s + "\n</section>" for s in sections) + "\n"
            + footer_nav("genus", gid) + "\n</article>\n"
            + taxon_jsonld("genus", gid, gen["latin"], gen["zh"], parent, "属")
        )
        desc = desc_for("genus", gen=gen)
        outputs[OUT_DIRS["genus"] / (gid + ".md")] = (
            front_matter("%s %s 物种名录" % (gen["zh"], gen["latin"]), desc,
                         "/genus/%s/" % gid,
                         breadcrumb_for("genus", fam=fam, sub=subfamilies.get(gen["subfamily"]), gen=gen),
                         image_path(gen["family"]), fam["id"],
                         has_map=mapped, taxon_search=True)
            + body)

    problem = False
    descs = {}
    for path, content in sorted(outputs.items()):
        fm = parse_front_matter(content)
        desc = fm.get("description", "")
        if not (150 <= len(desc) <= 160):
            print("BAD desc length %d: %s (%s)" % (len(desc), path.relative_to(ROOT), desc))
            problem = True
        if desc in descs:
            print("DUP desc: %s and %s" % (descs[desc], path.relative_to(ROOT)))
            problem = True
        descs[desc] = path.relative_to(ROOT)

    if problem:
        sys.exit("refusing to write: description problems above")

    changed = 0
    for path, content in sorted(outputs.items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        changed += 1
        if write:
            with path.open("w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)
    stale = 0
    for rank, out_dir in OUT_DIRS.items():
        expected = {p.name for p in outputs if p.parent == out_dir}
        if out_dir.is_dir():
            for path in sorted(out_dir.glob("*.md")):
                if path.name not in expected:
                    stale += 1
                    print("stale page: %s" % path.relative_to(ROOT))
                    if write:
                        path.unlink()

    geo_changed = 0
    for path, content in sorted(geo_outputs.items()):
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        geo_changed += 1
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    geo_stale = 0
    if GEO_SUBFAMILY.is_dir():
        for path in sorted(GEO_SUBFAMILY.glob("*.geojson")):
            if path in geo_outputs:
                continue
            geo_stale += 1
            print("stale map: %s" % path.relative_to(ROOT))
            if write:
                path.unlink()

    payload = json.dumps(images, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    data_changed = not DATA_OUT.is_file() or DATA_OUT.read_text(encoding="utf-8") != payload
    if data_changed and write:
        DATA_OUT.write_text(payload, encoding="utf-8", newline="\n")

    maps_payload = json.dumps({
        "_meta": {"subfamilies": len(subfamily_maps),
                  "note": "亚科级 1° 网格分布图：由 build_taxonomy_pages.py 合并本亚科各属地图生成"},
        "subfamilies": subfamily_maps,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    maps_changed = (not SUBFAMILY_MAPS_OUT.is_file()
                    or SUBFAMILY_MAPS_OUT.read_text(encoding="utf-8") != maps_payload)
    if maps_changed and write:
        SUBFAMILY_MAPS_OUT.parent.mkdir(parents=True, exist_ok=True)
        SUBFAMILY_MAPS_OUT.write_text(maps_payload, encoding="utf-8", newline="\n")

    total = len(outputs)
    n_changed = changed + (1 if data_changed else 0) + (1 if maps_changed else 0) + geo_changed
    print("taxonomy hub pages: %d pages (13 family / 18 subfamily / 326 genus), %d stale"
          % (total, stale))
    print("description length %d-%d chars, all unique" % (min(len(d) for d in descs), max(len(d) for d in descs)))
    print("subfamily maps: %d of 18 subfamilies have merged geometry, %d changed, %d stale"
          % (len(subfamily_maps), geo_changed, geo_stale))
    print("%s: %d file(s) changed%s" % (DATA_OUT.relative_to(ROOT), n_changed,
                                        "" if write else " (--check: nothing written)"))
    if not write and (changed or data_changed or maps_changed or geo_changed or geo_stale or stale):
        sys.exit("generated files are out of date; rerun without --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())