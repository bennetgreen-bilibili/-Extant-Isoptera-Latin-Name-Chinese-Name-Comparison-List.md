#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the /photos/ pages: one page per taxon that actually has photos.

The crawler (.github/workflows/build_species_photos.py) no longer stops at six
photos per taxon: it keeps everything both sources return (PHOTO_SET_VERSION 2).
Species pages still show only the first six (SPECIES_PAGE_PHOTOS), so every taxon
with photos gets a page here that lists the complete set.  Each page exists in
three languages (the site is split into zh-CN / en / es pages):

    photos/species/<slug>.md      -> /species/<slug>/photos/
    en/photos/species/<slug>.md   -> /en/species/<slug>/photos/
    es/photos/species/<slug>.md   -> /es/species/<slug>/photos/
    photos/genus/<id>.md          -> /genus/<id>/photos/           (6 per species + links)
    ... same for /subfamily/<id>/photos/ and /family/<id>/photos/

Only taxa with at least one licensed photo get a file; the genus/subfamily/family
pages group their photos by species and link to each species page for the rest, so
a family page never tries to render several hundred <img> tags at once.  Every page
is single-language: front matter `lang` is zh-CN / en / es and the breadcrumb names,
title, description and back label are written in that language (Latin names for
en/es, Chinese names only on the zh pages; `photo_zh` is kept for the species name).

Inputs (all committed):
    _data/species_photos.json  latin -> [photo, ...]
    _data/taxonomy.json        family / subfamily / genus names and parents
    _species/*.md              front matter (slug, latin, zh, rank, genus_id, family_id)

Output pages are rendered by _layouts/photos.html; the photo grids themselves come
from _includes/species-gallery.html (species) and _includes/taxon-photos.html
(genus / subfamily / family). Deterministic: sorted keys, LF endings, fixed
last_modified_at, unchanged files are left untouched (git stays clean in CI).

Run it after build_genus_index.py and before build_sitemap_txt.py
(see .github/workflows/pages.yml, .github/workflows/validate.yml).

Usage:
    python .github/workflows/build_photo_pages.py           # write
    python .github/workflows/build_photo_pages.py --check   # verify without writing
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "_species"
PHOTOS_JSON = ROOT / "_data" / "species_photos.json"
TAXONOMY_JSON = ROOT / "_data" / "taxonomy.json"
PHOTO_TAXA_JSON = ROOT / "_data" / "photo_taxa.json"
OUT_DIR = ROOT / "photos"
LAST_MODIFIED = "2026-10-30"
SITE_PHOTOS_LIMIT = 6

# (lang value, URL prefix, output directory)
LANGS = (
    ("zh-CN", "", OUT_DIR),
    ("en", "/en", ROOT / "en" / "photos"),
    ("es", "/es", ROOT / "es" / "photos"),
)
LIST_NAME = {"zh-CN": "名录", "en": "List", "es": "Listado"}

FM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)[ \t]*:[ \t]*(.*)$")


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


def js(value):
    """JSON string literal — front matter is YAML but JSON strings are valid YAML."""
    return json.dumps(value, ensure_ascii=False)


def display_latin(latin):
    return latin.capitalize() if latin.isupper() else latin


def load_taxonomy():
    if not TAXONOMY_JSON.is_file():
        sys.exit("missing %s (run build_taxonomy_data.py --write)" % TAXONOMY_JSON)
    data = json.loads(TAXONOMY_JSON.read_text(encoding="utf-8"))
    families = {fam["id"]: fam for fam in data.get("families") or []}
    subfamilies = {sub["id"]: sub for sub in data.get("subfamilies") or []}
    genera = {gen["id"]: gen for gen in data.get("genera") or []}
    if not families or not genera:
        sys.exit("empty taxonomy: %s" % TAXONOMY_JSON)
    return families, subfamilies, genera


def load_photos():
    if not PHOTOS_JSON.is_file():
        sys.exit("missing %s (run build_species_photos.py --write)" % PHOTOS_JSON)
    data = json.loads(PHOTOS_JSON.read_text(encoding="utf-8"))
    species = data.get("species") or {}
    if not isinstance(species, dict):
        sys.exit("bad shape in %s: species is not an object" % PHOTOS_JSON)
    return species


def load_species():
    rows = []
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        latin = (fm.get("latin") or "").strip()
        if not latin:
            continue
        rows.append({
            "slug": path.stem,
            "latin": latin,
            "zh": (fm.get("zh") or "").strip(),
            "rank": (fm.get("rank") or "species").strip(),
            "genus_id": (fm.get("genus_id") or "").strip(),
            "family_id": (fm.get("family_id") or "").strip(),
        })
    if len(rows) < 3000:
        sys.exit("only %d species parsed, refusing to write (expected >= 3000)" % len(rows))
    return rows


def crumb(name, url):
    return "  - name: %s\n    url: %s\n" % (js(name), js(url))


def front_matter(lang, prefix, title, description, permalink, family_id, extra,
                 breadcrumb, image):
    """extra: list of (key, raw_value) inserted after sitemap."""
    lines = ["---", "layout: photos", "title: " + js(title),
             "description: " + js(description),
             "lang: " + lang, "single_lang: true", "author: 班奈特格林",
             "family_id: " + family_id,
             "last_modified_at: " + LAST_MODIFIED,
             "permalink: " + js(prefix + permalink), "sitemap: true"]
    for key, value in extra:
        lines.append("%s: %s" % (key, value))
    if image:
        lines.append("image: " + js(image))
    lines.append("breadcrumb:")
    return "\n".join(lines) + "\n" + "".join(
        crumb(name, prefix + url) for name, url in breadcrumb) + "---\n"


def family_crumbs(lang, prefix, fam):
    name = "%s %s" % (fam["zh"], fam["latin"]) if lang == "zh-CN" else fam["latin"]
    return [(LIST_NAME[lang], "/list/"), (name, "/family/%s/" % fam["id"])]


def subfamily_crumbs(lang, prefix, fam, sub):
    name = "%s %s" % (sub["zh"], sub["latin"]) if lang == "zh-CN" else sub["latin"]
    return family_crumbs(lang, prefix, fam) + [(name, "/subfamily/%s/" % sub["id"])]


def build_pages():
    families, subfamilies, genera = load_taxonomy()
    photos = load_photos()
    rows = load_species()
    outputs = {}
    # 有照片的分类单元清单：_data/photo_taxa.json。
    # build_taxonomy_pages.py 用它决定科 / 亚科 / 属页要不要挂图片小节、要不要加载
    # PhotoSwipe（front matter 的 has_photos），不必在 Liquid 里再遍历一遍物种表。
    # 键与 page 均为 zh URL；taxon-photos.html 自己按 LP 拼出 /en、/es 地址。
    taxa_index = {"_meta": {"generated_by": "build_photo_pages.py",
                            "note": "只列出至少有一张开放许可照片的分类单元；"
                                    "键为 species / genus / subfamily / family"},
                  "species": {}, "genus": {}, "subfamily": {}, "family": {}}

    def photo_count(latin):
        return len(photos.get(latin) or [])

    def first_image(latin):
        items = photos.get(latin) or []
        return items[0].get("src") if items else None

    def emit(rel_dir, kind, page_id, zh_title, en_title, es_title,
             zh_description, en_description, es_description, permalink,
             family_id, extra, crumbs_for_lang, image):
        for lang, prefix, out_root in LANGS:
            title = {"zh-CN": zh_title, "en": en_title, "es": es_title}[lang]
            description = {"zh-CN": zh_description, "en": en_description,
                           "es": es_description}[lang]
            outputs[out_root / rel_dir / (page_id + ".md")] = front_matter(
                lang, prefix, title, description, permalink, family_id,
                extra, crumbs_for_lang(lang, prefix), image)

    # ---- species ----------------------------------------------------------
    for row in rows:
        count = photo_count(row["latin"])
        if not count:
            continue
        slug = row["slug"]
        genus = genera.get(row["genus_id"])
        fam = families.get(row["family_id"]) if row["family_id"] else None
        if genus and not fam:
            fam = families.get(genus.get("family"))
        if not fam:
            sys.exit("no family for species %s (genus %s)" % (row["latin"], row["genus_id"]))
        sub = subfamilies.get((genus or {}).get("subfamily") or "")

        def species_crumbs(lang, prefix):
            crumbs = (subfamily_crumbs(lang, prefix, fam, sub) if sub
                      else family_crumbs(lang, prefix, fam))
            if genus:
                gname = ("%s %s" % (genus["zh"], genus["latin"])
                         if lang == "zh-CN" else genus["latin"])
                crumbs.append((gname, "/genus/%s/" % genus["id"]))
            spname = (row["latin"] if lang != "zh-CN"
                      else ("%s %s" % (row["latin"], row["zh"])).strip())
            crumbs.append((spname, "/species/%s/" % slug))
            return crumbs

        zh_label = ("%s %s" % (row["latin"], row["zh"])).strip()
        extra = [
            ("photo_kind", "species"),
            ("photo_id", js(slug)),
            ("photo_latin", js(row["latin"])),
            ("photo_zh", js(row["zh"])),
            ("photo_count", str(count)),
            ("back_url", js("/" + "species/%s/" % slug)),
            ("back_label", js(zh_label)),
        ]
        emit("species", "species", slug,
             zh_title="%s 全部图片（%d 张）" % (zh_label, count),
             en_title="%s — all photos (%d)" % (row["latin"], count),
             es_title="%s — todas las fotos (%d)" % (row["latin"], count),
             zh_description=("%s（%s）在 iNaturalist 与 Wikimedia Commons 上的开放许可照片，共 %d 张；"
                             "每张标注作者、许可协议与原始页面，点击可放大浏览。" %
                             (row["zh"], row["latin"], count)),
             en_description=("Freely licensed photos of %s (%s) from iNaturalist and Wikimedia Commons, "
                             "%d in total; each photo gives its author, licence and original page, "
                             "and opens in a larger view." % (row["latin"], row["zh"], count)),
             es_description=("Fotos con licencia libre de %s (%s) de iNaturalist y Wikimedia Commons, "
                             "%d en total; cada foto indica autor, licencia y página original, "
                             "y se abre en tamaño mayor." % (row["latin"], row["zh"], count)),
             permalink="/species/%s/photos/" % slug, family_id=fam["id"],
             extra=extra, crumbs_for_lang=species_crumbs, image=first_image(row["latin"]))
        taxa_index["species"][slug] = {"photos": count,
                                       "page": "/species/%s/photos/" % slug}

    # ---- genus / subfamily / family --------------------------------------
    def aggregate(selector):
        buckets = {}
        for row in rows:
            count = photo_count(row["latin"])
            if not count:
                continue
            key = selector(row)
            if not key:
                continue
            entry = buckets.setdefault(key, {"photos": 0, "species": 0})
            entry["photos"] += count
            entry["species"] += 1
        return buckets

    def genus_of(row):
        return row["genus_id"]

    def subfamily_of(row):
        genus = genera.get(row["genus_id"]) or {}
        return genus.get("subfamily") or ""

    def family_of(row):
        if row["family_id"]:
            return row["family_id"]
        return (genera.get(row["genus_id"]) or {}).get("family") or ""

    for gid, stats in sorted(aggregate(genus_of).items()):
        gen = genera.get(gid)
        if not gen:
            continue
        fam = families.get(gen["family"])
        if not fam:
            sys.exit("genus %s has no family in taxonomy" % gid)
        sub = subfamilies.get(gen.get("subfamily") or "")
        latin = display_latin(gen["latin"])
        zh_label = "%s %s" % (gen["zh"], latin)

        def genus_crumbs(lang, prefix):
            return (subfamily_crumbs(lang, prefix, fam, sub) if sub
                    else family_crumbs(lang, prefix, fam))

        extra = [
            ("photo_kind", "genus"),
            ("photo_id", js(gid)),
            ("photo_latin", js(gen["latin"])),
            ("photo_zh", js(gen["zh"])),
            ("photo_count", str(stats["photos"])),
            ("photo_species", str(stats["species"])),
            ("back_url", js("/genus/%s/" % gid)),
            ("back_label", js(zh_label)),
        ]
        emit("genus", "genus", gid,
             zh_title="%s 全部图片（%d 张，%d 种）" % (zh_label, stats["photos"], stats["species"]),
             en_title="%s %s — all photos (%d, %d species)" % (latin, gen["zh"], stats["photos"], stats["species"]),
             es_title="%s %s — todas las fotos (%d, %d especies)" % (latin, gen["zh"], stats["photos"], stats["species"]),
             zh_description=("%s（%s）属下 %d 个种的开放许可照片，共 %d 张，来自 iNaturalist 与 Wikimedia Commons；"
                             "按种分组，每个种可继续查看其全部照片。" %
                             (gen["zh"], gen["latin"], stats["species"], stats["photos"])),
             en_description=("Freely licensed photos of the %d species in the genus %s (%s), %d in total, "
                             "from iNaturalist and Wikimedia Commons; grouped by species, each linking to "
                             "its full photo set." % (stats["species"], gen["latin"], gen["zh"],
                                                      stats["photos"])),
             es_description=("Fotos con licencia libre de las %d especies del género %s (%s), %d en total, "
                             "de iNaturalist y Wikimedia Commons; agrupadas por especie, cada una enlaza "
                             "a su conjunto completo." % (stats["species"], gen["latin"], gen["zh"],
                                                          stats["photos"])),
             permalink="/genus/%s/photos/" % gid, family_id=fam["id"],
             extra=extra, crumbs_for_lang=genus_crumbs, image=None)
        taxa_index["genus"][gid] = {"photos": stats["photos"], "species": stats["species"],
                                    "page": "/genus/%s/photos/" % gid}

    for sid, stats in sorted(aggregate(subfamily_of).items()):
        sub = subfamilies.get(sid)
        if not sub:
            continue
        fam = families[sub["family"]]
        zh_label = "%s %s" % (sub["zh"], sub["latin"])

        def subfamily_crumbs_l(lang, prefix):
            return family_crumbs(lang, prefix, fam)

        extra = [
            ("photo_kind", "subfamily"),
            ("photo_id", js(sid)),
            ("photo_latin", js(sub["latin"])),
            ("photo_zh", js(sub["zh"])),
            ("photo_count", str(stats["photos"])),
            ("photo_species", str(stats["species"])),
            ("back_url", js("/subfamily/%s/" % sid)),
            ("back_label", js(zh_label)),
        ]
        emit("subfamily", "subfamily", sid,
             zh_title="%s 全部图片（%d 张，%d 种）" % (zh_label, stats["photos"], stats["species"]),
             en_title="%s %s — all photos (%d, %d species)" % (sub["latin"], sub["zh"], stats["photos"], stats["species"]),
             es_title="%s %s — todas las fotos (%d, %d especies)" % (sub["latin"], sub["zh"], stats["photos"], stats["species"]),
             zh_description=("%s（%s）亚科下 %d 个种的开放许可照片，共 %d 张，来自 iNaturalist 与 Wikimedia Commons；"
                             "按种分组，每个种可继续查看其全部照片。" %
                             (sub["zh"], sub["latin"], stats["species"], stats["photos"])),
             en_description=("Freely licensed photos of the %d species in the subfamily %s (%s), %d in total, "
                             "from iNaturalist and Wikimedia Commons; grouped by species, each linking to "
                             "its full photo set." % (stats["species"], sub["latin"], sub["zh"],
                                                      stats["photos"])),
             es_description=("Fotos con licencia libre de las %d especies de la subfamilia %s (%s), %d en total, "
                             "de iNaturalist y Wikimedia Commons; agrupadas por especie, cada una enlaza "
                             "a su conjunto completo." % (stats["species"], sub["latin"], sub["zh"],
                                                          stats["photos"])),
             permalink="/subfamily/%s/photos/" % sid, family_id=fam["id"],
             extra=extra, crumbs_for_lang=subfamily_crumbs_l, image=None)
        taxa_index["subfamily"][sid] = {"photos": stats["photos"], "species": stats["species"],
                                        "page": "/subfamily/%s/photos/" % sid}

    for fid, stats in sorted(aggregate(family_of).items()):
        fam = families.get(fid)
        if not fam:
            continue
        zh_label = "%s %s" % (fam["zh"], fam["latin"])

        def family_crumbs_l(lang, prefix):
            return [(LIST_NAME[lang], "/list/")]

        extra = [
            ("photo_kind", "family"),
            ("photo_id", js(fid)),
            ("photo_latin", js(fam["latin"])),
            ("photo_zh", js(fam["zh"])),
            ("photo_count", str(stats["photos"])),
            ("photo_species", str(stats["species"])),
            ("back_url", js("/family/%s/" % fid)),
            ("back_label", js(zh_label)),
        ]
        emit("family", "family", fid,
             zh_title="%s 全部图片（%d 张，%d 种）" % (zh_label, stats["photos"], stats["species"]),
             en_title="%s %s — all photos (%d, %d species)" % (fam["latin"], fam["zh"], stats["photos"], stats["species"]),
             es_title="%s %s — todas las fotos (%d, %d especies)" % (fam["latin"], fam["zh"], stats["photos"], stats["species"]),
             zh_description=("%s（%s）科下 %d 个种的开放许可照片，共 %d 张，来自 iNaturalist 与 Wikimedia Commons；"
                             "按种分组，每个种可继续查看其全部照片。" %
                             (fam["zh"], fam["latin"], stats["species"], stats["photos"])),
             en_description=("Freely licensed photos of the %d species in the family %s (%s), %d in total, "
                             "from iNaturalist and Wikimedia Commons; grouped by species, each linking to "
                             "its full photo set." % (stats["species"], fam["latin"], fam["zh"],
                                                      stats["photos"])),
             es_description=("Fotos con licencia libre de las %d especies de la familia %s (%s), %d en total, "
                             "de iNaturalist y Wikimedia Commons; agrupadas por especie, cada una enlaza "
                             "a su conjunto completo." % (stats["species"], fam["latin"], fam["zh"],
                                                          stats["photos"])),
             permalink="/family/%s/photos/" % fid, family_id=fid,
             extra=extra, crumbs_for_lang=family_crumbs_l, image=None)
        taxa_index["family"][fid] = {"photos": stats["photos"], "species": stats["species"],
                                     "page": "/family/%s/photos/" % fid}

    return outputs, taxa_index


def main():
    writing = "--check" not in sys.argv
    outputs, taxa_index = build_pages()
    payload = json.dumps(taxa_index, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")) + "\n"
    data_changed = (not PHOTO_TAXA_JSON.is_file()
                    or PHOTO_TAXA_JSON.read_text(encoding="utf-8") != payload)

    stale = []
    for out_root in (OUT_DIR, ROOT / "en" / "photos", ROOT / "es" / "photos"):
        if out_root.is_dir():
            for path in sorted(out_root.rglob("*.md")):
                if path not in outputs:
                    stale.append(path)

    changed = []
    for path, content in sorted(outputs.items()):
        if path.is_file():
            current = path.read_text(encoding="utf-8")
            if current == content:
                continue
        changed.append(path)

    counts = lambda: (sum(1 for p in outputs if p.parent.name == "species"),
                      sum(1 for p in outputs if p.parent.name == "genus"),
                      sum(1 for p in outputs if p.parent.name == "subfamily"),
                      sum(1 for p in outputs if p.parent.name == "family"))

    if not writing:
        if changed or stale or data_changed:
            for path in changed[:5]:
                print("stale content: %s" % path.relative_to(ROOT), file=sys.stderr)
            for path in stale[:5]:
                print("stale file: %s" % path.relative_to(ROOT), file=sys.stderr)
            if data_changed:
                print("stale file: %s" % PHOTO_TAXA_JSON.relative_to(ROOT), file=sys.stderr)
            sys.exit("%d photo pages out of date, %d stale files (run without --check)"
                     % (len(changed), len(stale)))
        print("OK: %d photo pages in 3 languages (%d species / %d genus / %d subfamily / %d family each), "
              "%d taxa in %s"
              % (len(outputs),
                 counts()[0] // 3, counts()[1] // 3, counts()[2] // 3, counts()[3] // 3,
                 sum(len(taxa_index[k]) for k in ("species", "genus", "subfamily", "family")),
                 PHOTO_TAXA_JSON.relative_to(ROOT)))
        return

    for path in stale:
        path.unlink()
    for path in changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(outputs[path])

    # drop directories that lost their last page
    for out_root in (OUT_DIR, ROOT / "en" / "photos", ROOT / "es" / "photos"):
        if not out_root.is_dir():
            continue
        for directory in sorted((p for p in out_root.rglob("*") if p.is_dir()), reverse=True):
            if directory != out_root and not any(directory.iterdir()):
                shutil.rmtree(directory)

    if data_changed:
        PHOTO_TAXA_JSON.write_text(payload, encoding="utf-8", newline="\n")

    print("wrote %d photo pages in 3 languages (%d species / %d genus / %d subfamily / %d family each), "
          "%d stale removed"
          % (len(outputs),
             counts()[0] // 3, counts()[1] // 3, counts()[2] // 3, counts()[3] // 3,
             len(stale)))


if __name__ == "__main__":
    main()
