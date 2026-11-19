#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split the big _data JSON files into one-file-per-taxon shards, and merge them back.

Layout contract (the shard file holds the VALUE itself, except where marked):

    _data/morphology_species/<genus>/<slug>.json      key "/species/<slug>/"
    _data/fauna_species/<genus>/<slug>.json           key "/species/<slug>/"
    _data/fauna_measurements/<genus>/<slug>.json      key "/species/<slug>/"
    _data/morphology_genera/<genus>.json              key "/genus/<id>/"
    _data/genus_sources/<genus>.json                  key "/genus/<id>/"
    _data/taxon_literature/<rank>/<id>.json           key "/<rank>/<id>/"  (+ meta.json = "_meta")
    _data/etymology/meta.json                         whole "meta" object
    _data/etymology/genera/<genus>.json               key "<genus>"
    _data/etymology/epithets/<letter>.json            key "<epithet>" (one file per initial)
    _data/taxon_prose/<lang>/<families|subfamilies>/<id>.json   key "<id>"
    _data/translations_<lang>/meta.json
    _data/translations_<lang>/morphology_species/<genus>/<slug>.json   (also fauna_species)
    _data/translations_<lang>/morphology_genera/<genus>.json
    _data/translations_<lang>/fauna_genera.json       small subs stay single files
    _data/translations_<lang>/fauna_families.json
    _data/translations_<lang>/fauna_keys.json
    _data/papers/meta.json + genera/<genus>.json       key "<genus>"
    _data/species_photos/meta.json + species/<genus>.json          WRAPPED {binomial: value}
    _data/authority_links/meta.json + taxa/<genus>.json            WRAPPED {binomial: value}
    _data/bsf_links/meta.json + name_map/<genus>.json              WRAPPED {binomial: value}

"WRAPPED" is only used for the three caches keyed by a Latin binomial: the original
spelling cannot be recovered from the slugified filename, so the file keeps its key.

Usage:
    python _tools/data_shards.py --status
    python _tools/data_shards.py --save-originals
    python _tools/data_shards.py --split-all
    python _tools/data_shards.py --verify-all

修复「聚合文件回潮」（定时工作流用旧脚本提交的 `_data/<name>.json` 与分片目录并存）：
    python _tools/data_shards.py --adopt papers        # 拆分 → 校验 → 删聚合，一条命令
"""
import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_data")
ORIG = os.path.join(ROOT, "_tmp", "shard_orig")

ALL = [
    "morphology_species", "fauna_species", "fauna_measurements",
    "morphology_genera", "genus_sources", "taxon_literature",
    "etymology", "taxon_prose",
    "translations_en", "translations_es",
    "papers", "species_photos", "authority_links", "bsf_links",
]

NESTED = {"papers": ("genera", False), "species_photos": ("species", True),
          "authority_links": ("taxa", True), "bsf_links": ("name_map", True)}

# sub-blocks of the translation files that stay single files (small, no win)
TR_WHOLE = ("fauna_genera", "fauna_families", "fauna_keys")

# --------------------------------------------------------------------------- io


def jload(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def jdump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def slugify(text):
    s = text.strip().strip("/").replace("/", "-")
    s = re.sub(r"[^0-9A-Za-z\u00c0-\u024f_-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s.lower()


def url_slug(key):
    return key.strip("/").split("/")[-1]


_SPECIES = None


def url2genus():
    global _SPECIES
    if _SPECIES is None:
        _SPECIES = {}
        for genus, rows in jload(os.path.join(DATA, "species_by_genus.json")).items():
            if genus.startswith("_"):
                continue
            for row in rows:
                _SPECIES[row["url"]] = row["genus_id"]
    return _SPECIES


def shard_dir(name):
    return os.path.join(DATA, name)


def agg_path(name):
    return os.path.join(DATA, name + ".json")


# --------------------------------------------------------------------------- paths

# path(key) -> tuple of path segments (without .json); None means "keep whole file"
# key(path) -> original key


def p_species(key):
    return (url2genus().get(key, "_orphan"), url_slug(key))


def k_species(path):
    return "/species/%s/" % path[-1]


def p_genus(key):
    return (slugify(url_slug(key)),)


def k_genus(path):
    return "/genus/%s/" % path[-1]


def p_taxon(key):
    if key.startswith("_"):
        return (key.lstrip("_") or "meta",)
    parts = key.strip("/").split("/")
    return (slugify(parts[0]), slugify(parts[-1]))


def k_taxon(path):
    if len(path) == 1:
        return "_" + path[0]
    return "/%s/%s/" % (path[0], path[1])


def p_bare(key):
    return (slugify(url_slug(key)),)


def k_bare(path):
    return path[-1]


def p_latin(sub):
    def _p(key):
        return (sub, slugify(key.split()[0]), slugify(key))
    return _p


def p_epithet(key):
    word = url_slug(key)
    first = word[:1].lower()
    return ("epithets", first if first.isalpha() else "_", slugify(word))


def k_epithet(path):
    return path[-1]


def p_etgenus(key):
    return ("genera", slugify(key))


def k_etgenus(path):
    return path[-1]


# name -> (path_fn, key_fn, wrapped, whole)
RULES = {
    "morphology_species": (p_species, k_species, False, False),
    "fauna_species": (p_species, k_species, False, False),
    "fauna_measurements": (p_species, k_species, False, False),
    "morphology_genera": (p_genus, k_genus, False, False),
    "genus_sources": (p_genus, k_genus, False, False),
    "taxon_literature": (p_taxon, k_taxon, False, False),
    "species_photos": (p_latin("species"), None, True, False),
    "authority_links": (p_latin("taxa"), None, True, False),
    "bsf_links": (p_latin("name_map"), None, True, False),
}


def write_buckets(name, buckets):
    remove_shards(name)
    n = 0
    for path, entries in buckets.items():
        target = os.path.join(shard_dir(name), *path[:-1], path[-1] + ".json")
        jdump(entries, target)
        n += len(entries)
    return n


def remove_shards(name):
    d = shard_dir(name)
    if os.path.isdir(d):
        shutil.rmtree(d)


# --------------------------------------------------------------------------- split


def split_flat(name, root):
    pfn, kfn, wrapped, _ = RULES[name]
    buckets = {}
    for key, value in root.items():
        path = pfn(key)
        cell = buckets.setdefault(tuple(path), {})
        cell[key] = value                      # always store key when wrapped
        if not wrapped:
            buckets[tuple(path)] = value
    return write_buckets(name, buckets)


def split(name):
    src = agg_path(name)
    if not os.path.exists(src):
        return None
    root = jload(src)

    if name in NESTED:
        sub, wrapped = NESTED[name]
        remove_shards(name)
        n = 0
        buckets = {}
        if "meta" in root:
            jdump(root["meta"], os.path.join(shard_dir(name), "meta.json"))
        for key, value in root.get(sub, {}).items():
            if name == "papers":
                path = (slugify(key),)
                jdump(value, os.path.join(shard_dir(name), sub, *path) + ".json")
            else:
                buckets.setdefault(slugify(key.split()[0]), {})[key] = value
            n += 1
        for genus, items in buckets.items():
            jdump(items, os.path.join(shard_dir(name), sub, genus) + ".json")
        return n

    if name in RULES:
        return split_flat(name, root)

    buckets = {}
    if name == "etymology":
        if "meta" in root:
            buckets[("meta",)] = root["meta"]
        for key, value in root.get("genera", {}).items():
            buckets.setdefault(tuple(p_etgenus(key)), value)
        epi = {}
        for key, value in root.get("epithets", {}).items():
            word = url_slug(key)
            first = word[:1].lower() if word[:1].islower() or word[:1].isalpha() else "_"
            first = word[:1].lower()
            if not first.isalpha():
                first = "_"
            epi.setdefault(first, {})[key] = value
        remove_shards(name)
        for path, value in buckets.items():
            target = os.path.join(shard_dir(name), *path[:-1], path[-1] + ".json")
            jdump(value, target)
        for letter, items in epi.items():
            jdump(items, os.path.join(shard_dir(name), "epithets", letter + ".json"))
        return len(buckets) + len(root.get("epithets", {}))

    if name == "taxon_prose":
        remove_shards(name)
        n = 0
        for lang, levels in root.items():
            if lang == "meta":
                jdump(levels, os.path.join(shard_dir(name), "meta.json"))
                continue
            for level, items in levels.items():
                for key, value in items.items():
                    target = os.path.join(shard_dir(name), lang, level, slugify(key) + ".json")
                    jdump(value, target)
                    n += 1
        return n

    if name.startswith("translations_"):
        remove_shards(name)
        n = 0
        for sub, value in root.items():
            if sub == "meta":
                jdump(value, os.path.join(shard_dir(name), "meta.json"))
                continue
            if sub in TR_WHOLE:
                jdump(value, os.path.join(shard_dir(name), sub + ".json"))
                n += len(value)
                continue
            if sub in ("morphology_species", "fauna_species"):
                pfn, wrapped = p_species, False
            elif sub in ("morphology_genera", "fauna_genera"):
                pfn, wrapped = p_genus, False
            else:
                pfn, wrapped = p_taxon, False
            for key, item in value.items():
                path = tuple([sub] + list(pfn(key)))
                if wrapped:
                    cell = buckets.get(path) or {}
                    cell[key] = item
                    buckets[path] = cell
                else:
                    buckets[path] = item
        for path, value in buckets.items():
            target = os.path.join(shard_dir(name), *path[:-1], path[-1] + ".json")
            jdump(value, target)
            n += 1 if not isinstance(value, dict) or True else 1
        return n

    raise SystemExit("unknown dataset: " + name)


# --------------------------------------------------------------------------- merge


def walk_merge(base, rel=()):
    """{(seg, ...): value} from all shard files below base (direct-value mode)."""
    merged = {}
    for entry in sorted(os.listdir(base)):
        full = os.path.join(base, entry)
        if os.path.isdir(full):
            merged.update(walk_merge(full, rel + (entry,)))
        elif entry.endswith(".json"):
            merged[rel + (entry[:-5],)] = jload(full)
    return merged


def merge(name):
    d = shard_dir(name)
    if name in NESTED:
        sub, wrapped = NESTED[name]
        root = {"meta": jload(os.path.join(d, "meta.json"))}
        if name == "papers":
            root[sub] = {path[-1]: v
                         for path, v in walk_merge(os.path.join(d, sub)).items()}
        else:
            merged = {}
            base = os.path.join(d, sub)
            for entry in sorted(os.listdir(base)):
                if entry.endswith(".json"):
                    merged.update(jload(os.path.join(base, entry)))
            root[sub] = merged
        return root

    if name in RULES:
        pfn, kfn, wrapped, _ = RULES[name]
        flat = walk_merge(d)
        return {kfn(path): value for path, value in flat.items()}
    if name == "etymology":
        out = {}
        meta = os.path.join(d, "meta.json")
        if os.path.exists(meta):
            out["meta"] = jload(meta)
        out["genera"] = {path[-1]: v
                         for path, v in walk_merge(os.path.join(d, "genera")).items()}
        epi = {}
        base = os.path.join(d, "epithets")
        if os.path.isdir(base):
            for entry in sorted(os.listdir(base)):
                if entry.endswith(".json"):
                    epi.update(jload(os.path.join(base, entry)))
        out["epithets"] = epi
        return out

    if name == "taxon_prose":
        out = {}
        meta = os.path.join(d, "meta.json")
        if os.path.exists(meta):
            out["meta"] = jload(meta)
        for lang in sorted(os.listdir(d)):
            lp = os.path.join(d, lang)
            if not os.path.isdir(lp):
                continue
            out[lang] = {}
            for level in sorted(os.listdir(lp)):
                if os.path.isdir(os.path.join(lp, level)):
                    out[lang][level] = {path[-1]: v
                                        for path, v in walk_merge(os.path.join(lp, level)).items()}
        return out

    if name.startswith("translations_"):
        out = {}
        meta = os.path.join(d, "meta.json")
        if os.path.exists(meta):
            out["meta"] = jload(meta)
        for sub in sorted(os.listdir(d)):
            full = os.path.join(d, sub)
            if not os.path.isdir(full):
                out[sub[:-5]] = jload(full) if sub.endswith(".json") else None
                continue
            if sub in ("morphology_species", "fauna_species"):
                merged = walk_merge(full)
                out[sub] = {"/species/%s/" % path[-1]: v for path, v in merged.items()}
            elif sub in ("morphology_genera", "fauna_genera"):
                merged = walk_merge(full)
                out[sub] = {"/genus/%s/" % path[-1]: v for path, v in merged.items()}
            else:
                merged = walk_merge(full)
                out[sub] = {"/%s/%s/" % (path[0], path[-1]): v
                            for path, v in merged.items()}
        return out

    raise SystemExit("unknown dataset: " + name)


def _norm(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def verify(name):
    orig_file = os.path.join(ORIG, name + ".json")
    if not os.path.exists(orig_file):
        return "no-original"
    if not os.path.isdir(shard_dir(name)):
        return "no-shards"
    original = jload(orig_file)
    rebuilt = merge(name)
    if _norm(original) == _norm(rebuilt):
        return "OK"
    detail = []
    if isinstance(original, dict) and isinstance(rebuilt, dict):
        miss = sorted(set(original) - set(rebuilt))
        extra = sorted(set(rebuilt) - set(original))
        if miss:
            detail.append("missing=%s" % miss[:4])
        if extra:
            detail.append("extra=%s" % extra[:4])
        for k in sorted(set(original) & set(rebuilt)):
            if original[k] != rebuilt[k]:
                detail.append("value-diff at %r" % k)
                break
    return "DIFF " + "; ".join(detail)


def count_shards(name):
    n = 0
    for _, _, files in os.walk(shard_dir(name)):
        n += sum(1 for f in files if f.endswith(".json"))
    return n


def status():
    w = max(len(n) for n in ALL)
    print("%-*s %10s %8s  %s" % (w, "dataset", "agg KB", "shards", "state"))
    for name in ALL:
        agg = agg_path(name)
        kb = os.path.getsize(agg) // 1024 if os.path.exists(agg) else 0
        n = count_shards(name)
        state = "aggregate" if kb and not n else ("shards" if n and not kb else
                                                 ("BOTH" if kb and n else "missing"))
        print("%-*s %10d %8d  %s" % (w, name, kb, n, state))


def drop_aggregates():
    for name in ALL:
        p = agg_path(name)
        if os.path.exists(p):
            os.remove(p)
            print("removed", os.path.relpath(p, ROOT))


def save_originals():
    os.makedirs(ORIG, exist_ok=True)
    n = 0
    for name in ALL:
        src = agg_path(name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(ORIG, name + ".json"))
            n += 1
    print("saved %d originals to _tmp/shard_orig/" % n)


def adopt(names):
    """把一个「回潮」的聚合文件收编为分片：存档 → 拆分 → 校验 → 删除聚合。

    定时工作流用旧脚本提交的聚合文件与拆分后的目录合并后，会同时留下
    `_data/<name>.json` 与 `_data/<name>/`；check_site 会报错。用本命令一条
    命令修复，校验不过则保留聚合文件、退出码 1。
    """
    os.makedirs(ORIG, exist_ok=True)
    bad = 0
    for name in names:
        src = agg_path(name)
        if not os.path.exists(src):
            print("%-22s no aggregate (%d shard files)" % (name, count_shards(name)))
            continue
        shutil.copy2(src, os.path.join(ORIG, name + ".json"))
        split(name)
        r = verify(name)
        if r != "OK":
            bad += 1
            print("%-22s VERIFY FAILED (%s) — aggregate kept" % (name, r))
            continue
        os.remove(src)
        print("%-22s adopted %d shard files from %s.json" % (name, count_shards(name), name))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--save-originals", action="store_true")
    ap.add_argument("--adopt", nargs="*")
    ap.add_argument("--split", nargs="*")
    ap.add_argument("--split-all", action="store_true")
    ap.add_argument("--verify", nargs="*")
    ap.add_argument("--verify-all", action="store_true")
    ap.add_argument("--drop-aggregates", action="store_true")
    args = ap.parse_args()
    if args.status:
        return status()
    if args.save_originals:
        return save_originals()
    if args.drop_aggregates:
        return drop_aggregates()
    if args.adopt is not None:
        return adopt(ALL if not args.adopt else args.adopt)
    if args.split_all or args.split:
        names = ALL if args.split_all else args.split
        for name in names:
            n = split(name)
            print("%-22s %s" % (name, "skipped" if n is None else "%d files" % count_shards(name)))
        return 0
    if args.verify_all or args.verify:
        names = ALL if args.verify_all else args.verify
        bad = 0
        for name in names:
            r = verify(name)
            print("%-22s %s" % (name, r))
            bad += r != "OK"
        return 1 if bad else 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
