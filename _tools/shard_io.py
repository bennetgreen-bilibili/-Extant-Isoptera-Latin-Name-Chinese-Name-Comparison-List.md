#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read and write the sharded `_data/` datasets as if they were still one JSON file.

The 14 big datasets were split into `_data/<name>/` directories; the aggregate
`_data/<name>.json` files are gone. Every consumer should go through this module
instead of opening `_data/<name>.json`:

    from shard_io import load, save
    data = load("taxon_literature")   # same dict the old aggregate had
    data["/family/x/"] = ...
    save("taxon_literature", data)    # writes shards, never an aggregate

`load` is `data_shards.merge`: it rebuilds the exact pre-split top-level
structure (keys back to `/species/<slug>/`, `/genus/<id>/`, ...), so callers that
only read need no other change.

`save` splits in memory using the same path rules and writes one file per shard,
byte-identical for unchanged entries (unchanged files are not rewritten, stale
files are removed). It never creates `_data/<name>.json`.

Both are no-ops on a missing directory: `load` returns `{}`, `save` writes
nothing new except the files it was given.
"""
from __future__ import annotations

import json
import os
import sys

_TOOLS = os.path.dirname(os.path.abspath(__file__))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import data_shards as ds  # noqa: E402


def load(name):
    """Merged view of `_data/<name>/` ({} when the directory is absent)."""
    if not os.path.isdir(ds.shard_dir(name)):
        return {}
    return ds.merge(name)


def exists(name):
    """True when the dataset has shards on disk."""
    return os.path.isdir(ds.shard_dir(name))


def _dumps(value):
    return json.dumps(value, indent=1, ensure_ascii=False) + "\n"


def buckets(name, root):
    """{(path segments...): value or {key: value}} — mirrors data_shards.split."""
    out = {}

    if name in ds.NESTED:
        sub, wrapped = ds.NESTED[name]
        if "meta" in root:
            out[("meta",)] = root["meta"]
        for key, value in (root.get(sub) or {}).items():
            if name == "papers":
                out[(sub, ds.slugify(key))] = value
            else:
                cell = out.get((sub, ds.slugify(key.split()[0]))) or {}
                cell[key] = value
                out[(sub, ds.slugify(key.split()[0]))] = cell
        return out

    if name in ds.RULES:
        pfn, _kfn, wrapped, _whole = ds.RULES[name]
        for key, value in root.items():
            path = tuple(pfn(key))
            if wrapped:
                cell = out.get(path) or {}
                cell[key] = value
                out[path] = cell
            else:
                out[path] = value
        return out

    if name == "etymology":
        if "meta" in root:
            out[("meta",)] = root["meta"]
        for key, value in (root.get("genera") or {}).items():
            out[tuple(ds.p_etgenus(key))] = value
        epi = {}
        for key, value in (root.get("epithets") or {}).items():
            word = ds.url_slug(key)
            first = word[:1].lower()
            if not first.isalpha():
                first = "_"
            epi.setdefault(first, {})[key] = value
        for letter, items in epi.items():
            out[("epithets", letter)] = items
        return out

    if name == "taxon_prose":
        if "meta" in root:
            out[("meta",)] = root["meta"]
        for lang, levels in root.items():
            if lang == "meta":
                continue
            for level, items in (levels or {}).items():
                for key, value in items.items():
                    out[(lang, level, ds.slugify(key))] = value
        return out

    if name.startswith("translations_"):
        for sub, value in root.items():
            if sub == "meta":
                out[("meta",)] = value
                continue
            if sub in ds.TR_WHOLE:
                out[(sub,)] = value
                continue
            if sub in ("morphology_species", "fauna_species"):
                pfn = ds.p_species
            elif sub in ("morphology_genera", "fauna_genera"):
                pfn = ds.p_genus
            else:
                pfn = ds.p_taxon
            for key, item in (value or {}).items():
                out[(sub,) + tuple(pfn(key))] = item
        return out

    raise SystemExit("unknown dataset: " + name)


def save(name, root):
    """Write the merged structure back as shards. Returns (written, removed)."""
    table = buckets(name, root)
    base_dir = ds.shard_dir(name)
    keep = set()
    written = []
    for path, value in table.items():
        target = os.path.join(base_dir, *path[:-1], path[-1] + ".json")
        keep.add(os.path.normcase(target))
        text = _dumps(value)
        if os.path.exists(target):
            with open(target, encoding="utf-8") as fh:
                if fh.read() == text:
                    continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        written.append(target)

    removed = []
    for here, _dirs, files in os.walk(base_dir):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            full = os.path.normcase(os.path.join(here, fn))
            if full not in keep:
                os.remove(full)
                removed.append(full)
    for here, _dirs, _files in os.walk(base_dir, topdown=False):
        if here != base_dir and not os.listdir(here):
            os.rmdir(here)
    return written, removed


def summary(written, removed, name):
    return "%s: %d file(s) written, %d removed" % (name, len(written), len(removed))
