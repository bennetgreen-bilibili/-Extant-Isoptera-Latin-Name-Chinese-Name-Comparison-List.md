#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate _data/species_by_genus.json for the "同属其他种" block.

Reads the front matter of every _species/*.md, groups species (rank: species,
3071 files = 3008 species + 63 subspecies, subspecies are skipped) by genus_id,
and writes a compact lookup used by _layouts/species.html:

    site.data.species_by_genus[page.genus_id] -> [ {slug, latin, zh, url}, ... ]

The file is generated on every CI build (see .github/workflows/pages.yml) and is
also committed so local `jekyll serve` has it. Never edit it by hand.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "_species"
OUT = ROOT / "_data" / "species_by_genus.json"

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


def main():
    if not SPECIES_DIR.is_dir():
        sys.exit("missing directory: %s" % SPECIES_DIR)
    by_genus = {}
    per_genus = {}
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
        if not genus_id or not latin:
            sys.exit("bad front matter in %s (genus_id/latin missing)" % path.name)
        by_genus.setdefault(genus_id, []).append(
            {"slug": slug, "latin": latin, "zh": zh, "url": "/species/%s/" % slug}
        )
        per_genus[genus_id] = per_genus.get(genus_id, 0) + 1

    for genus_id in by_genus:
        by_genus[genus_id].sort(key=lambda item: item["latin"])

    total = sum(len(v) for v in by_genus.values())
    if total < 3000:
        sys.exit("only %d species parsed, refusing to write (expected >= 3000)" % total)

    if not by_genus:
        sys.exit("no species collected")

    multi = sorted(((n, g) for g, n in per_genus.items()), reverse=True)
    payload = {"_meta": {"species": total, "genera": len(by_genus)}}
    payload.update(by_genus)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    print("wrote %s: %d species in %d genera, %d subspecies skipped, %.0f KB"
          % (OUT.relative_to(ROOT), total, len(by_genus), skipped, OUT.stat().st_size / 1024))
    print("largest genera: " + ", ".join("%s=%d" % (g, n) for n, g in multi[:5]))


if __name__ == "__main__":
    main()
