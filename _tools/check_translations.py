# -*- coding: utf-8 -*-
"""Verify _data/translations_en.json and _data/translations_es.json.

Checks, per language and per translated data file:
  * the JSON is valid and the top-level layout follows the contract order;
  * every source key has an entry, and every translatable field is present
    (structure is identical to the translatable subset of the source);
  * no Chinese characters survive in a translated value;
  * numbers / measurement tokens and Latin names are preserved (same rules as
    translations_merge.py, which is imported so the two cannot drift apart);
  * section labels use the canonical English / Spanish wording;
  * an empty source string stays an empty string.

Usage:
  python _tools/check_translations.py            # human report
  python _tools/check_translations.py --ci       # exit 1 on any problem
  python _tools/check_translations.py --ci --files fauna_genera,morphology_genera
  python _tools/check_translations.py --langs es
"""
from __future__ import print_function

import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from translations_split import DATA, ROOT, count_chars, extract  # noqa: E402
from translations_merge import (  # noqa: E402
    CJK_RE,
    LABELS,
    NAMES,
    ORDER,
    check_string,
)

MAX_PRINTED = 12


def load_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_source(name):
    return load_json(os.path.join(DATA, name + ".json"))


def walk(src, dst, path, problems, lang):
    """Compare a translatable source subset with the merged translation."""
    if isinstance(src, dict):
        if not isinstance(dst, dict):
            problems.append("%s: expected object" % path)
            return
        for key, val in src.items():
            if key not in dst:
                problems.append("%s.%s: field missing" % (path, key))
                continue
            walk(val, dst[key], "%s.%s" % (path, key), problems, lang)
        return
    if isinstance(src, list):
        if not isinstance(dst, list):
            problems.append("%s: expected array" % path)
            return
        if len(src) != len(dst):
            problems.append("%s: array length %d -> %d" % (path, len(src), len(dst)))
            return
        for i, (a, b) in enumerate(zip(src, dst)):
            walk(a, b, "%s[%d]" % (path, i), problems, lang)
        return
    if isinstance(src, str):
        check_string(src, dst, path, problems, lang)
        return
    if src != dst:
        problems.append("%s: %r -> %r" % (path, src, dst))


def check_labels(block, lang, problems, name):
    if not name.startswith("morphology_"):
        return
    canon = LABELS[lang]
    for url, entry in block.items():
        for i, sec in enumerate(entry.get("sections", [])):
            src_label = sec.get("_src_label")
            dst_label = sec.get("label", "")
            if src_label is None:
                continue
            want = canon.get(src_label)
            if want is None:
                continue
            if dst_label != want:
                problems.append("%s sections[%d].label: %r != %r"
                                % (url, i, dst_label, want))


def check_one(lang, name, doc, problems, stats):
    src_all = load_source(name)
    block = doc.get(name)
    if block is None:
        stats["missing_keys"] += len(src_all)
        problems.append("[%s] %s: whole section missing from translations_%s.json"
                        % (lang, name, lang))
        return
    translated = 0
    chars = 0
    for url, entry in src_all.items():
        sub = extract(url, entry)
        tr = block.get(url)
        if tr is None:
            stats["missing_keys"] += 1
            stats["missing_by_name"][name] = stats["missing_by_name"].get(name, 0) + 1
            continue
        translated += 1
        chars += count_chars(sub)
        walk(sub, tr, "%s.%s" % (name, url), problems, lang)
        if name.startswith("morphology_"):
            for i, sec in enumerate(entry.get("sections", [])):
                if i < len(tr.get("sections", [])):
                    want = LABELS[lang].get(sec.get("label", ""))
                    got = tr["sections"][i].get("label", "")
                    if want is not None and got != want:
                        problems.append("%s.%s sections[%d].label: %r != %r"
                                        % (name, url, i, got, want))
    extra = [u for u in block if u not in src_all]
    if extra:
        problems.append("[%s] %s: %d keys not in the source (%s)"
                        % (lang, name, len(extra), extra[:3]))
    stats["keys"] += len(src_all)
    stats["translated"] += translated
    stats["chars"] += chars
    stats["files"][name] = {"keys": len(src_all), "translated": translated, "chars": chars}


def cjk_in_value(val):
    if isinstance(val, str):
        return bool(CJK_RE.search(val))
    if isinstance(val, dict):
        return any(cjk_in_value(v) for v in val.values())
    if isinstance(val, list):
        return any(cjk_in_value(v) for v in val)
    return False


def translatable_cjk(block, name):
    """判断「未列入本次 --files 的桶」里，可译字段是否还留着汉字。

    只沿 extract() 给出的可译字段逐叶比对：zh / book_n / leaf.zh 这类专名
    字段本来就不翻译，不能因为它们含汉字就判整个桶没翻。（2026-11-12：
    原实现用 cjk_in_value 扫整块，fauna_keys 的 leaf.zh 属名会误报。）
    """
    src_all = load_source(name)
    for url, entry in src_all.items():
        dst = block.get(url)
        if dst is None:
            continue
        sub = extract(url, entry)
        stack = [(sub, dst)]
        while stack:
            a, b = stack.pop()
            if isinstance(a, dict) and isinstance(b, dict):
                for k, v in a.items():
                    if k in b:
                        stack.append((v, b[k]))
            elif isinstance(a, list) and isinstance(b, list):
                stack.extend(zip(a, b))
            elif isinstance(b, str) and CJK_RE.search(b):
                return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci", action="store_true", help="exit 1 on any problem")
    ap.add_argument("--files", default="", help="comma separated data file names")
    ap.add_argument("--langs", default="en,es")
    args = ap.parse_args()

    names = [x.strip() for x in args.files.split(",") if x.strip()] or NAMES
    langs = [x.strip() for x in args.langs.split(",") if x.strip()]

    problems = []
    per_lang = {}
    for lang in langs:
        path = os.path.join(DATA, "translations_%s.json" % lang)
        stats = {"keys": 0, "translated": 0, "chars": 0, "missing_keys": 0,
                 "missing_by_name": {}, "files": {}}
        if not os.path.exists(path):
            problems.append("[%s] missing file %s" % (lang, os.path.relpath(path, ROOT)))
            per_lang[lang] = stats
            continue
        try:
            doc = load_json(path)
        except Exception as exc:  # noqa: BLE001
            problems.append("[%s] invalid JSON: %s" % (lang, exc))
            per_lang[lang] = stats
            continue
        top = [k for k in doc if k != "meta"]
        order = [k for k in ORDER[1:] if k in top]
        if top != order:
            problems.append("[%s] top-level order %s != contract order %s" % (lang, top, order))
        meta = doc.get("meta", {})
        if meta.get("schema") != 1:
            problems.append("[%s] meta.schema != 1" % lang)
        for name in names:
            check_one(lang, name, doc, problems, stats)
        for name in top:
            if name not in names and translatable_cjk(doc.get(name), name):
                problems.append("[%s] %s: Chinese characters in an untranslated block" % (lang, name))
        per_lang[lang] = stats

    print("translations check%s" % (" (ci)" if args.ci else ""))
    for lang in langs:
        st = per_lang[lang]
        print("\n[%s] %d/%d keys translated, %d CJK source chars"
              % (lang, st["translated"], st["keys"], st["chars"]))
        for name in names:
            f = st["files"].get(name)
            if not f:
                print("  %-20s MISSING" % name)
                continue
            print("  %-20s %4d/%4d keys  %7d chars%s"
                  % (name, f["translated"], f["keys"], f["chars"],
                     "" if f["translated"] == f["keys"] else "   <- %d pending"
                     % (f["keys"] - f["translated"])))

    if problems:
        print("\n%d problem(s):" % len(problems))
        seen = set()
        shown = 0
        for p in problems:
            bucket = p.split(":")[0]
            if bucket in seen and shown >= MAX_PRINTED:
                continue
            seen.add(bucket)
            print("  -", p)
            shown += 1
            if shown >= MAX_PRINTED * 3:
                print("  ... (truncated)")
                break
    else:
        print("\nno problems found")

    failed = bool(problems)
    if args.ci:
        print("\nCI: %s" % ("FAIL" if failed else "PASS"))
        return 1 if failed else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
