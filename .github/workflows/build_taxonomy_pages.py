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

Each page is Chinese-only navigation + a short unique summary (BreadcrumbList comes from
_includes/breadcrumb-jsonld.html via the breadcrumb list in front matter). The prose
(形态/分布/经济意义) is NOT duplicated: those paragraphs stay in /list/, and the hub
pages link to the matching List-of-names anchor, so the two page families do not compete
for the same text.

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

    for gen in genera.values():
        gen["rows"].sort(key=lambda r: (0 if r["rank"] != "subspecies" else 1,
                                        r["latin"].casefold(), r["slug"]))
    for fam in families.values():
        fam["subfamilies"].sort()
        fam["genera"] = sorted(fam["genera"])
    for sub in subfamilies.values():
        sub["genera"] = sorted(sub["genera"])

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

    def front_matter(title, description, permalink, breadcrumb, image, family_id, last_modified="2026-10-30"):
        lines = ["---", "layout: default", "title: " + json.dumps(title, ensure_ascii=False),
                 "description: " + json.dumps(description, ensure_ascii=False),
                 "lang: zh-CN", "lang_only: true", "author: 班奈特格林",
                 "family_id: " + family_id,
                 "last_modified_at: " + last_modified,
                 "permalink: " + permalink, "sitemap: true"]
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
            + figure_html(fid, fam["zh"]) +
            "\n".join('<section class="taxon-section">\n' + s + "\n</section>" for s in sections) + "\n"
            + footer_nav("family", fid) + "\n</article>\n"
            + taxon_jsonld("family", fid, fam["latin"], fam["zh"], parent, "科")
        )
        desc = desc_for("family", fam=fam)
        outputs[OUT_DIRS["family"] / (fid + ".md")] = (
            front_matter("%s %s 分类名录" % (fam["zh"], fam["latin"]), desc,
                         "/family/%s/" % fid, breadcrumb_for("family", fam=fam),
                         image_path(fid), fid)
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
            + figure_html(sid, sub["zh"]) +
            "\n".join('<section class="taxon-section">\n' + s + "\n</section>" for s in sections) + "\n"
            + footer_nav("subfamily", sid) + "\n</article>\n"
            + taxon_jsonld("subfamily", sid, sub["latin"], sub["zh"], parent, "亚科")
        )
        desc = desc_for("subfamily", sub=sub)
        outputs[OUT_DIRS["subfamily"] / (sid + ".md")] = (
            front_matter("%s %s 属与物种名录" % (sub["zh"], sub["latin"]), desc,
                         "/subfamily/%s/" % sid, breadcrumb_for("subfamily", fam=fam, sub=sub),
                         image_path(sid), fam["id"])
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
        body = (
            '<article class="taxon-page">\n'
            + crumb_nav("genus", fam=fam, sub=subfamilies.get(gen["subfamily"]), gen=gen) + "\n"
            + '<header class="taxon-header">\n'
            + '<h1>%s <i>%s</i></h1>\n' % (gen["zh"], display_latin(gen["latin"]))
            + '<p class="taxon-meta">%s · %s</p>\n' % (fam["zh"] + " " + fam["latin"], stats_line(gen=gen))
            + "</header>\n"
            + figure_html(gid, gen["zh"]) +
            "\n".join('<section class="taxon-section">\n' + s + "\n</section>" for s in sections) + "\n"
            + footer_nav("genus", gid) + "\n</article>\n"
            + taxon_jsonld("genus", gid, gen["latin"], gen["zh"], parent, "属")
        )
        desc = desc_for("genus", gen=gen)
        outputs[OUT_DIRS["genus"] / (gid + ".md")] = (
            front_matter("%s %s 物种名录" % (gen["zh"], gen["latin"]), desc,
                         "/genus/%s/" % gid,
                         breadcrumb_for("genus", fam=fam, sub=subfamilies.get(gen["subfamily"]), gen=gen),
                         image_path(gen["family"]), fam["id"])
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

    payload = json.dumps(images, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    data_changed = not DATA_OUT.is_file() or DATA_OUT.read_text(encoding="utf-8") != payload
    if data_changed and write:
        DATA_OUT.write_text(payload, encoding="utf-8", newline="\n")

    total = len(outputs)
    n_changed = changed + (1 if data_changed else 0)
    print("taxonomy hub pages: %d pages (13 family / 18 subfamily / 326 genus), %d stale"
          % (total, stale))
    print("description length %d-%d chars, all unique" % (min(len(d) for d in descs), max(len(d) for d in descs)))
    print("%s: %d file(s) changed%s" % (DATA_OUT.relative_to(ROOT), n_changed,
                                        "" if write else " (--check: nothing written)"))
    if not write and (changed or data_changed or stale):
        sys.exit("generated files are out of date; rerun without --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
