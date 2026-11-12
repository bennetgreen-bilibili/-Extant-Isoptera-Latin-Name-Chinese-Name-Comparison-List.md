#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""审计「一段涉及多个分类单元，却只写在一个单元页面上」的问题（SOP §4.4）。

用法：

    python _tools/audit_taxon_spread.py                 # 查 _data/taxon_literature.json
    python _tools/audit_taxon_spread.py --draft _tmp/review/2026-11-12-r2/draft.json

输出三段：

1. 段落里出现了别的单元（属／种）的学名，而该单元在站内有页面；
2. 其中目标页**还没有**承载同一个来源的记述 —— 这些才是真正要判断的遗漏；
3. 段落里出现的、站内没有页面的学名（只能留在属页或标「待核」）。

列出的每一条都要人工判断：是「该单元自身的事实」（补写到它的页面），
还是「仅作比较／仅出现在名录里」（可以不补，但要能说明理由）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BINOM = re.compile(r"\b([A-Z][a-z]{2,})\s+([a-z][a-z\-]{2,})\b")


def load_taxa():
    sbg = json.loads((ROOT / "_data" / "species_by_genus.json").read_text(encoding="utf-8"))
    species = {}
    genera = {}
    for gid, rows in sbg.items():
        if gid.startswith("_"):
            continue
        genera[gid] = "/genus/%s/" % gid
        for row in rows:
            species[row["latin"].lower()] = row["url"]
    return species, genera


def iter_paragraphs(store):
    for key, page in store.items():
        if key.startswith("_"):
            continue
        for sec in page.get("sections") or []:
            for para in sec.get("paragraphs") or []:
                yield key, para


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="_data/taxon_literature.json")
    ap.add_argument("--draft", action="append", default=[])
    args = ap.parse_args()

    species, genera = load_taxa()
    stores = [("data", json.loads((ROOT / args.data).read_text(encoding="utf-8")))]
    for path in args.draft:
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        if p.exists():
            label = "draft:" + p.parent.name
            stores.append((label, json.loads(p.read_text(encoding="utf-8"))))

    # 目标页已有哪个来源的记述
    have = {}
    for label, store in stores:
        for key, para in iter_paragraphs(store):
            for sid in para.get("src") or []:
                have.setdefault((key, sid), True)

    external = []
    unknown = []
    for label, store in stores:
        for key, para in iter_paragraphs(store):
            text = para.get("text") or ""
            for m in BINOM.finditer(text):
                latin = "%s %s" % m.groups()
                url = species.get(latin.lower())
                if not url:
                    unknown.append((label, key, latin))
                    continue
                if url != key:
                    external.append((label, key, url, latin, para.get("src") or []))

    print("=== 段落提到别的单元（%d 条） ===" % len(external))
    for label, key, url, latin, src in external:
        print("%-22s %-50s -> %-46s %-30s src=%s" % (label, key, url, latin, ",".join(src)))

    missing = []
    for label, key, url, latin, src in external:
        if not any((url, sid) in have for sid in src):
            missing.append((label, key, url, latin, src))
    print("\n=== 目标页还没有同一来源的记述（%d 条） ===" % len(missing))
    for label, key, url, latin, src in missing:
        print("%-22s %-50s -> %-46s src=%s" % (label, key, url, ",".join(src)))

    uniq = sorted({u for _, _, u in unknown})
    print("\n=== 站内没有页面的学名（%d 个） ===" % len(uniq))
    for u in uniq:
        print("  " + u)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
