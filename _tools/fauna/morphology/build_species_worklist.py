#!/usr/bin/env python3
"""Build a worklist of species/subspecies pages lacking a compiled morphology section.

Reads _species/*.md front matter, _data/fauna_species.json and
_data/morphology_species.json.  Writes _reports/species-morphology-worklist.csv
(one row per page) and .md (summary + per-family counts).  Review aid only.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPECIES = ROOT / "_species"
OUT_CSV = ROOT / "_reports" / "species-morphology-worklist.csv"
OUT_MD = ROOT / "_reports" / "species-morphology-worklist.md"
FAUNA = ROOT / "_data" / "fauna_species.json"
MORPH = ROOT / "_data" / "morphology_species.json"

FIELD = re.compile(r'^([a-z_]+):\s*(.*)$')


def unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        try:
            return json.loads(v)
        except Exception:
            return v[1:-1]
    return v


def read_front(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    for line in text[3:end].splitlines():
        m = FIELD.match(line)
        if m:
            out[m.group(1)] = unquote(m.group(2))
    return out


def main() -> int:
    fauna = json.loads(FAUNA.read_text(encoding="utf-8")) if FAUNA.exists() else {}
    morph = json.loads(MORPH.read_text(encoding="utf-8")) if MORPH.exists() else {}
    rows = []
    for path in sorted(SPECIES.glob("*.md")):
        fm = read_front(path)
        url = f"/species/{path.stem}/"
        if url in morph:
            status = "已有补充描述"
        elif url in fauna:
            status = "已有《中国动物志》描述"
        else:
            status = "待补"
        rows.append({
            "科": fm.get("family_zh", ""),
            "亚科": fm.get("subfamily_zh", ""),
            "属": fm.get("genus_zh", ""),
            "属（拉丁）": fm.get("genus_latin", ""),
            "种/亚种（拉丁）": fm.get("latin", ""),
            "中文名": fm.get("zh", ""),
            "rank": fm.get("rank", ""),
            "命名人年代": fm.get("author_year", ""),
            "模式产地": fm.get("type_locality", ""),
            "分布": fm.get("distribution_zh", ""),
            "状态": status,
            "页面": url,
        })
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    counts = Counter(r["状态"] for r in rows)
    by_family: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        by_family[r["科"]][r["状态"]] += 1
    lines = ["# 物种 / 亚种形态描述工作清单", ""]
    lines.append(f"生成自 _species/*.md、_data/fauna_species.json、_data/morphology_species.json；共 **{len(rows)}** 个页面。")
    lines.append("")
    lines.append("| 状态 | 页面数 |")
    lines.append("| --- | ---: |")
    for k in ("已有补充描述", "已有《中国动物志》描述", "待补"):
        lines.append(f"| {k} | {counts.get(k, 0)} |")
    lines.append("")
    lines.append("完整逐页清单见 _reports/species-morphology-worklist.csv（UTF-8 BOM，可用 Excel 打开）。")
    lines.append("")
    lines.append("## 各科进度")
    lines.append("")
    lines.append("| 科 | 总页数 | 补充描述 | 动物志描述 | 待补 |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for fam in sorted(by_family, key=lambda x: (-sum(by_family[x].values()), x)):
        c = by_family[fam]
        lines.append(f"| {fam or '（未填）'} | {sum(c.values())} | {c.get('已有补充描述', 0)} | {c.get('已有《中国动物志》描述', 0)} | {c.get('待补', 0)} |")
    lines.append("")
    lines.append("状态含义：已有补充描述 = _data/morphology_species.json 有条目；已有《中国动物志》描述 = _data/fauna_species.json 有条目，页面已渲染动物志一节；待补 = 两者皆无，页面显示待补说明并指向属页。")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"rows {len(rows)} {dict(counts)}")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
