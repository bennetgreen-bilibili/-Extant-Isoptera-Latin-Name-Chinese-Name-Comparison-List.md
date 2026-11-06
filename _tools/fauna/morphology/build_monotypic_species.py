#!/usr/bin/env python3
"""Copy genus-level descriptions to the single species of monotypic genera.

This is deliberately conservative: only monotypic genera (one species in
_data/species_by_genus.json) get an entry, and the note says the text is
genus-level. Species-specific descriptions must come from the original paper.
Existing non-monotypic entries in _data/morphology_species.json are preserved.

Usage: python _tools/fauna/morphology/build_monotypic_species.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GENUS = ROOT / "_data" / "morphology_genera.json"
SPECIES = ROOT / "_data" / "morphology_species.json"
BY_GENUS = ROOT / "_data" / "species_by_genus.json"
NOTE = "该属为单型属，仅含本种；以下为据原始文献的属级描述，种级量度与种内变异见原文。"


def main() -> int:
    genera = json.loads(GENUS.read_text(encoding="utf-8"))
    by_genus = json.loads(BY_GENUS.read_text(encoding="utf-8"))
    out = json.loads(SPECIES.read_text(encoding="utf-8")) if SPECIES.exists() else {}
    added = 0
    for gid, species in by_genus.items():
        if len(species) != 1:
            continue
        g = genera.get(f"/genus/{gid}/")
        if not g:
            continue
        sp = species[0]
        if sp["url"] in out:
            continue
        srcs = g.get("sources")
        if srcs is None:
            src = g.get("source")
            srcs = src if isinstance(src, list) else ([src] if src else [])
        out[sp["url"]] = {
            "zh_name": sp.get("zh", ""),
            "sections": [dict(s) for s in g["sections"]],
            "sources": srcs,
            "note": NOTE,
        }
        added += 1
    SPECIES.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {SPECIES.relative_to(ROOT)}: {len(out)} species ({added} monotypic added)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
