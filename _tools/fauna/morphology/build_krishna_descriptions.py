#!/usr/bin/env python3
"""Combine hand-written genus morphology descriptions into the _data/morphology_genera/ shards.

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
sys.path.insert(0, str(ROOT / "_tools"))
import shard_io  # noqa: E402

DATA = "morphology_genera"
SRC = Path(__file__).resolve().parent / "descriptions"


def main() -> int:
    # Start from what is already on disk: this builder only owns the genera that
    # have a description file, and must not drop the ones that do not.
    existing = shard_io.load(DATA)
    merged: dict[str, dict] = dict(existing)
    origin: dict[str, str] = {}
    for path in sorted(SRC.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path}: top level must be an object keyed by page URL")
        for url, entry in data.items():
            if not url.startswith("/genus/") or not url.endswith("/"):
                raise SystemExit(f"{path}: bad page URL {url!r}")
            if url in origin:
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
            # Normalise to one shape: a sources array.  The site and the
            # worklist builders can then stop guessing between source/sources.
            clean = {k: v for k, v in entry.items() if k != "source"}
            clean["sources"] = srcs
            merged[url] = clean
            origin[url] = path.name
    written, removed = shard_io.save(DATA, merged)
    print(f"wrote _data/{DATA}/: {len(merged)} genera ({len(existing)} kept, "
          f"{written} files written, {removed} removed) from "
          f"{len(list(SRC.glob('*.json')))} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())