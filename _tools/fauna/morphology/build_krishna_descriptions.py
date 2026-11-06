#!/usr/bin/env python3
"""Combine hand-written genus morphology descriptions into _data/morphology_genera.json.

Each file in descriptions/ is a flat JSON object keyed by page URL, e.g.
"/genus/allotermes/".  Entries carry sections (label/text), one or more
sources (id/citation/locator) and an optional note.  The builder refuses
duplicate keys so two authors cannot silently overwrite each other.

Usage: python _tools/fauna/morphology/build_krishna_descriptions.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parent / "descriptions"
OUT = ROOT / "_data" / "morphology_genera.json"


def main() -> int:
    merged: dict[str, dict] = {}
    origin: dict[str, str] = {}
    for path in sorted(SRC.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path}: top level must be an object keyed by page URL")
        for url, entry in data.items():
            if not url.startswith("/genus/") or not url.endswith("/"):
                raise SystemExit(f"{path}: bad page URL {url!r}")
            if url in merged:
                raise SystemExit(f"{path}: duplicate {url} (already in {origin[url]})")
            if not entry.get("sections"):
                raise SystemExit(f"{path}: {url} has no sections")
            srcs = entry.get("sources")
            if srcs is None:
                src = entry.get("source")
                srcs = src if isinstance(src, list) else ([src] if src else [])
            for src in srcs:
                if not src.get("id") or not src.get("citation"):
                    raise SystemExit(f"{path}: {url} source needs id and citation")
            merged[url] = entry
            origin[url] = path.name
    OUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(merged)} genera from {len(list(SRC.glob('*.json')))} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())