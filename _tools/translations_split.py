#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split taxonomy prose data into ~N-CJK-char translation shards.

Usage:
    python _tools/translations_split.py --file morphology_genera
    python _tools/translations_split.py --files fauna_families,fauna_genera,fauna_keys,morphology_genera
    python _tools/translations_split.py --file fauna_species --max-chars 3800 --reset

Output:
    _tmp/tr/<lang>/<name>-<NNN>.json      (same content for en and es)
    _tmp/tr/manifest_<name>.json          (shard -> keys, char counts)

Each shard has exactly the same nesting as the translation target (values still
in Chinese).  Fields that must NOT be translated (`en`, `book_n`, `zh_name`,
`sources`, couplet numbers, leaf objects) are stripped from the shard so the
translator cannot touch them; translations_merge.py splices the translated
leave back into a copy of the source structure.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_data")
TR = os.path.join(ROOT, "_tmp", "tr")
LANGS = ("en", "es")

# fields that must not appear in a translation shard
FAUNA_SKIP = {"en", "book_n"}

FAUNA_FILES = ("fauna_families", "fauna_genera", "fauna_species", "fauna_keys")


def cjk_count(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def count_chars(obj):
    if isinstance(obj, str):
        return cjk_count(obj)
    if isinstance(obj, dict):
        return sum(count_chars(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_chars(v) for v in obj)
    return 0


def extract(url, entry):
    """Return the translatable subset of one source entry (Chinese values)."""
    if isinstance(entry, dict) and "sections" in entry:
        out = {
            "sections": [
                {"label": sec.get("label", ""), "text": sec.get("text", "")}
                for sec in entry["sections"]
            ]
        }
        if "note" in entry:
            out["note"] = entry["note"]
        return out
    if isinstance(entry, dict) and "keys" in entry and "n_couplets" in entry:
        keys = []
        for k in entry["keys"]:
            ks = {
                "title": k.get("title", ""),
                "caste": k.get("caste", ""),
                "couplets": [
                    {"leads": [{"t": lead.get("t", "")} for lead in cpl.get("leads", [])]}
                    for cpl in k.get("couplets", [])
                ],
            }
            for f in ("note", "source", "src_short"):
                if f in k:
                    ks[f] = k[f]
            keys.append(ks)
        out = {"keys": keys}
        if entry.get("omitted"):
            out["omitted"] = list(entry["omitted"])
        return out
    # fauna_* single-entry dicts
    out = {}
    for f, val in entry.items():
        if f in FAUNA_SKIP:
            continue
        if isinstance(val, str):
            out[f] = val
        elif isinstance(val, (int, float, bool)) or val is None:
            continue
        else:
            raise SystemExit("unexpected field type %s in %s: %r" % (f, url, type(val)))
    return out


def split_file(name, max_chars, reset):
    src_path = os.path.join(DATA, name + ".json")
    with open(src_path, encoding="utf-8") as fh:
        src = json.load(fh)

    for lang in LANGS:
        d = os.path.join(TR, lang)
        os.makedirs(d, exist_ok=True)
        for fn in os.listdir(d):
            if reset and fn.startswith(name + "-") and fn.endswith(".json"):
                os.remove(os.path.join(d, fn))

    shards = []
    cur = {}
    cur_chars = 0
    for url, entry in src.items():
        sub = extract(url, entry)
        n = count_chars(sub)
        if cur and cur_chars + n > max_chars:
            shards.append((cur, cur_chars))
            cur, cur_chars = {}, 0
        cur[url] = sub
        cur_chars += n
    if cur:
        shards.append((cur, cur_chars))

    manifest = {"name": name, "max_chars": max_chars, "source": src_path,
                "total_chars": count_chars({u: extract(u, e) for u, e in src.items()}),
                "n_keys": len(src), "shards": []}
    for i, (data, chars) in enumerate(shards):
        fn = "%s-%03d.json" % (name, i)
        manifest["shards"].append({"file": fn, "keys": list(data), "chars": chars})
        for lang in LANGS:
            with open(os.path.join(TR, lang, fn), "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=1, ensure_ascii=False)
                fh.write("\n")
    with open(os.path.join(TR, "manifest_%s.json" % name), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    print("%s: %d keys, %d CJK chars -> %d shards (max %d)"
          % (name, len(src), manifest["total_chars"], len(shards), max_chars))
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--files")
    ap.add_argument("--max-chars", type=int, default=4000)
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()
    names = []
    if args.file:
        names.append(args.file)
    if args.files:
        names.extend(x.strip() for x in args.files.split(",") if x.strip())
    if not names:
        ap.error("give --file or --files")
    for name in names:
        if not os.path.exists(os.path.join(DATA, name + ".json")):
            raise SystemExit("no such data file: %s" % name)
        split_file(name, args.max_chars, args.reset)


if __name__ == "__main__":
    main()
