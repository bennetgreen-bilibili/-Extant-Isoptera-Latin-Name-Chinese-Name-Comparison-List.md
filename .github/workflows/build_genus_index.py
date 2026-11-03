#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the species-by-taxon indexes used by the taxonomy pages.

Reads the front matter of every _species/*.md, groups species (rank: species,
subspecies are skipped) by genus_id, and writes three compact lookups:

    _data/species_by_genus.json      site.data.species_by_genus[page.genus_id]
    _data/species_by_family.json     site.data.species_by_family[page.family_id]
    _data/species_by_subfamily.json  site.data.species_by_subfamily[page.id]

Each entry is {slug, latin, zh, url, genus_id}; the two higher ranks are
derived from taxonomy.json (families[].genera are the genera that sit directly
in a family, subfamilies[].genera the ones that sit in a subfamily).

Used by:
  * _layouts/species.html        — 同属其他种
  * _includes/species-gallery.html — 图片图集与「查看全部」
  * _includes/taxon-photos.html  — 属 / 亚科 / 科页图片小节
  * _layouts/photos.html         — 属 / 亚科 / 科的全部图片页

The files are generated on every CI build (see .github/workflows/pages.yml) and
are also committed so local `jekyll serve` has them. Never edit them by hand.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "_species"
TAXONOMY = ROOT / "_data" / "taxonomy.json"
DATA_DIR = ROOT / "_data"

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


def load_taxon_maps():
    """genus_id -> family_id / subfamily_id, from the committed taxonomy."""
    if not TAXONOMY.is_file():
        sys.exit("missing file: %s (run build_taxonomy_data.py --write)" % TAXONOMY)
    data = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    genus_family = {}
    genus_subfamily = {}
    for fam in data.get("families") or []:
        for gid in fam.get("genera") or []:
            genus_family[gid] = fam["id"]
    for sub in data.get("subfamilies") or []:
        for gid in sub.get("genera") or []:
            genus_subfamily[gid] = sub["id"]
            genus_family[gid] = sub["family"]
    return genus_family, genus_subfamily


def write_json(path, payload):
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    print("wrote %s (%.0f KB)" % (path.relative_to(ROOT), path.stat().st_size / 1024))


def main():
    if not SPECIES_DIR.is_dir():
        sys.exit("missing directory: %s" % SPECIES_DIR)
    genus_family, genus_subfamily = load_taxon_maps()
    by_genus = {}
    by_family = {}
    by_subfamily = {}
    skipped = 0
    for path in sorted(SPECIES_DIR.glob("*.md")):
        slug = path.stem
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        if str(fm.get("rank", "species")).lower() == "subspecies":
            skipped += 1
            continue
        genus_id = (fm.get("genus_id") or "").strip()
        latin = (fm.get("latin") or "").strip()
        zh = (fm.get("zh") or "").strip()
        family_id = (fm.get("family_id") or "").strip() or genus_family.get(genus_id, "")
        if not genus_id or not latin:
            sys.exit("bad front matter in %s (genus_id/latin missing)" % path.name)
        if not family_id:
            sys.exit("no family for genus %s (species page %s)" % (genus_id, path.name))
        entry = {"slug": slug, "latin": latin, "zh": zh,
                 "url": "/species/%s/" % slug, "genus_id": genus_id}
        by_genus.setdefault(genus_id, []).append(entry)
        by_family.setdefault(family_id, []).append(entry)
        subfamily_id = genus_subfamily.get(genus_id)
        if subfamily_id:
            by_subfamily.setdefault(subfamily_id, []).append(entry)

    for bucket in (by_genus, by_family, by_subfamily):
        for key in bucket:
            bucket[key].sort(key=lambda item: item["latin"])

    total = sum(len(v) for v in by_genus.values())
    if total < 3000:
        sys.exit("only %d species parsed, refusing to write (expected >= 3000)" % total)

    if not by_genus:
        sys.exit("no species collected")

    genus_payload = {"_meta": {"species": total, "genera": len(by_genus)}}
    genus_payload.update(by_genus)
    write_json(DATA_DIR / "species_by_genus.json", genus_payload)

    family_payload = {"_meta": {"species": total, "families": len(by_family)}}
    family_payload.update(by_family)
    write_json(DATA_DIR / "species_by_family.json", family_payload)

    sub_payload = {"_meta": {"species": total, "subfamilies": len(by_subfamily)}}
    sub_payload.update(by_subfamily)
    write_json(DATA_DIR / "species_by_subfamily.json", sub_payload)

    multi = sorted(((n, g) for g, n in ((g, len(v)) for g, v in by_genus.items())), reverse=True)
    print("%d species in %d genera / %d families / %d subfamilies, %d subspecies skipped"
          % (total, len(by_genus), len(by_family), len(by_subfamily), skipped))
    print("largest genera: " + ", ".join("%s=%d" % (g, n) for n, g in multi[:5]))


if __name__ == "__main__":
    main()
