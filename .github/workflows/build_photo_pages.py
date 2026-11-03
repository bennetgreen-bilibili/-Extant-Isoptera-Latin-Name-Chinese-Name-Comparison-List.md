#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the /photos/ pages: one page per taxon that actually has photos.

The crawler (.github/workflows/build_species_photos.py) no longer stops at six
photos per taxon: it keeps everything both sources return (PHOTO_SET_VERSION 2).
Species pages still show only the first six (SPECIES_PAGE_PHOTOS), so every taxon
with photos gets a page here that lists the complete set:

    photos/species/<slug>.md      -> /species/<slug>/photos/      (all photos)
    photos/genus/<id>.md          -> /genus/<id>/photos/           (6 per species + links)
    photos/subfamily/<id>.md      -> /subfamily/<id>/photos/
    photos/family/<id>.md         -> /family/<id>/photos/

Only taxa with at least one licensed photo get a file; the genus/subfamily/family
pages group their photos by species and link to each species page for the rest, so
a family page never tries to render several hundred <img> tags at once.

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


def front_matter(title, description, permalink, family_id, extra, breadcrumb, image):
    """extra: list of (key, raw_value) inserted after sitemap."""
    lines = ["---", "layout: photos", "title: " + js(title), "description: " + js(description),
             "lang: zh-CN", "lang_only: true", "author: 班奈特格林",
             "family_id: " + family_id,
             "last_modified_at: " + LAST_MODIFIED,
             "permalink: " + permalink, "sitemap: true"]
    for key, value in extra:
        lines.append("%s: %s" % (key, value))
    if image:
        lines.append("image: " + js(image))
    lines.append("breadcrumb:")
    return "\n".join(lines) + "\n" + "".join(crumb(name, url) for name, url in breadcrumb) + "---\n"


def family_crumbs(fam):
    return [("名录", "/list/"), ("%s %s" % (fam["zh"], fam["latin"]), "/family/%s/" % fam["id"])]


def subfamily_crumbs(fam, sub):
    return family_crumbs(fam) + [("%s %s" % (sub["zh"], sub["latin"]), "/subfamily/%s/" % sub["id"])]


def build_pages():
    families, subfamilies, genera = load_taxonomy()
    photos = load_photos()
    rows = load_species()
    outputs = {}
    # 有照片的分类单元清单：_data/photo_taxa.json。
    # build_taxonomy_pages.py 用它决定科 / 亚科 / 属页要不要挂图片小节、要不要加载
    # PhotoSwipe（front matter 的 has_photos），不必在 Liquid 里再遍历一遍物种表。
    taxa_index = {"_meta": {"generated_by": "build_photo_pages.py",
                            "note": "只列出至少有一张开放许可照片的分类单元；"
                                    "键为 species / genus / subfamily / family"},
                  "species": {}, "genus": {}, "subfamily": {}, "family": {}}

    def photo_count(latin):
        return len(photos.get(latin) or [])

    def first_image(latin):
        items = photos.get(latin) or []
        return items[0].get("src") if items else None

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
        breadcrumb = family_crumbs(fam)
        sub = subfamilies.get((genus or {}).get("subfamily") or "")
        if sub:
            breadcrumb = subfamily_crumbs(fam, sub)
        if genus:
            breadcrumb.append(("%s %s" % (genus["zh"], genus["latin"]), "/genus/%s/" % genus["id"]))
        breadcrumb.append((("%s %s" % (row["latin"], row["zh"])).strip(), "/species/%s/" % slug))
        label = ("%s %s" % (row["latin"], row["zh"])).strip()
        title = "%s 全部图片（%d 张）" % (label, count)
        description = ("%s（%s）在 iNaturalist 与 Wikimedia Commons 上的开放许可照片，共 %d 张；"
                       "每张标注作者、许可协议与原始页面，点击可放大浏览。" %
                       (row["zh"], row["latin"], count))
        extra = [
            ("photo_kind", "species"),
            ("photo_id", js(slug)),
            ("photo_latin", js(row["latin"])),
            ("photo_zh", js(row["zh"])),
            ("photo_count", str(count)),
            ("back_url", js("/species/%s/" % slug)),
            ("back_label", js(label)),
        ]
        outputs[OUT_DIR / "species" / (slug + ".md")] = front_matter(
            title, description, "/species/%s/photos/" % slug, fam["id"],
            extra, breadcrumb, first_image(row["latin"]))
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
        breadcrumb = subfamily_crumbs(fam, sub) if sub else family_crumbs(fam)
        label = "%s %s" % (gen["zh"], gen["latin"])
        title = "%s 全部图片（%d 张，%d 种）" % (display_latin(label), stats["photos"], stats["species"])
        description = ("%s（%s）属下 %d 个种的开放许可照片，共 %d 张，来自 iNaturalist 与 Wikimedia Commons；"
                       "按种分组，每个种可继续查看其全部照片。" %
                       (gen["zh"], gen["latin"], stats["species"], stats["photos"]))
        extra = [
            ("photo_kind", "genus"),
            ("photo_id", js(gid)),
            ("photo_latin", js(gen["latin"])),
            ("photo_zh", js(gen["zh"])),
            ("photo_count", str(stats["photos"])),
            ("photo_species", str(stats["species"])),
            ("back_url", js("/genus/%s/" % gid)),
            ("back_label", js(label)),
        ]
        outputs[OUT_DIR / "genus" / (gid + ".md")] = front_matter(
            title, description, "/genus/%s/photos/" % gid, fam["id"],
            extra, breadcrumb, None)
        taxa_index["genus"][gid] = {"photos": stats["photos"], "species": stats["species"],
                                    "page": "/genus/%s/photos/" % gid}

    for sid, stats in sorted(aggregate(subfamily_of).items()):
        sub = subfamilies.get(sid)
        if not sub:
            continue
        fam = families[sub["family"]]
        label = "%s %s" % (sub["zh"], sub["latin"])
        title = "%s 全部图片（%d 张，%d 种）" % (label, stats["photos"], stats["species"])
        description = ("%s（%s）亚科下 %d 个种的开放许可照片，共 %d 张，来自 iNaturalist 与 Wikimedia Commons；"
                       "按种分组，每个种可继续查看其全部照片。" %
                       (sub["zh"], sub["latin"], stats["species"], stats["photos"]))
        extra = [
            ("photo_kind", "subfamily"),
            ("photo_id", js(sid)),
            ("photo_latin", js(sub["latin"])),
            ("photo_zh", js(sub["zh"])),
            ("photo_count", str(stats["photos"])),
            ("photo_species", str(stats["species"])),
            ("back_url", js("/subfamily/%s/" % sid)),
            ("back_label", js(label)),
        ]
        outputs[OUT_DIR / "subfamily" / (sid + ".md")] = front_matter(
            title, description, "/subfamily/%s/photos/" % sid, fam["id"],
            extra, subfamily_crumbs(fam, sub), None)
        taxa_index["subfamily"][sid] = {"photos": stats["photos"], "species": stats["species"],
                                        "page": "/subfamily/%s/photos/" % sid}

    for fid, stats in sorted(aggregate(family_of).items()):
        fam = families.get(fid)
        if not fam:
            continue
        label = "%s %s" % (fam["zh"], fam["latin"])
        title = "%s 全部图片（%d 张，%d 种）" % (label, stats["photos"], stats["species"])
        description = ("%s（%s）科下 %d 个种的开放许可照片，共 %d 张，来自 iNaturalist 与 Wikimedia Commons；"
                       "按种分组，每个种可继续查看其全部照片。" %
                       (fam["zh"], fam["latin"], stats["species"], stats["photos"]))
        extra = [
            ("photo_kind", "family"),
            ("photo_id", js(fid)),
            ("photo_latin", js(fam["latin"])),
            ("photo_zh", js(fam["zh"])),
            ("photo_count", str(stats["photos"])),
            ("photo_species", str(stats["species"])),
            ("back_url", js("/family/%s/" % fid)),
            ("back_label", js(label)),
        ]
        outputs[OUT_DIR / "family" / (fid + ".md")] = front_matter(
            title, description, "/family/%s/photos/" % fid, fid,
            extra, family_crumbs(fam), None)
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
    if OUT_DIR.is_dir():
        for path in sorted(OUT_DIR.rglob("*.md")):
            if path not in outputs:
                stale.append(path)

    changed = []
    for path, content in sorted(outputs.items()):
        if path.is_file():
            current = path.read_text(encoding="utf-8")
            if current == content:
                continue
        changed.append(path)

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
        print("OK: %d photo pages (%d species / %d genus / %d subfamily / %d family), "
              "%d taxa in %s"
              % (len(outputs),
                 sum(1 for p in outputs if "species" in p.parts),
                 sum(1 for p in outputs if "genus" in p.parts),
                 sum(1 for p in outputs if "subfamily" in p.parts),
                 sum(1 for p in outputs if "family" in p.parts),
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
    for directory in sorted((p for p in OUT_DIR.rglob("*") if p.is_dir()), reverse=True):
        if directory != OUT_DIR and not any(directory.iterdir()):
            shutil.rmtree(directory)

    if data_changed:
        PHOTO_TAXA_JSON.write_text(payload, encoding="utf-8", newline="\n")

    print("wrote %d photo pages (%d species / %d genus / %d subfamily / %d family), %d stale removed"
          % (len(outputs),
             sum(1 for p in outputs if "species" in p.parts),
             sum(1 for p in outputs if "genus" in p.parts),
             sum(1 for p in outputs if "subfamily" in p.parts),
             sum(1 for p in outputs if "family" in p.parts),
             len(stale)))


if __name__ == "__main__":
    main()
