#!/usr/bin/env python3
"""构建「命名差异与待核对」看板数据（/list/name-issues/）。

把已有缓存里的「本站名 vs 外部库」对照结果整理成结构化清单，供页面筛选、下载与程序化访问：

  _data/name_issues.json          页面用（site.data.name_issues）
  data/name-issues.json           公开副本（与 data/references.json 同一做法）
  downloads/isoptera-name-issues.csv  可下载对照表（UTF-8 BOM，Excel 直接打开不花屏）

数据来源（均为仓库内已提交的缓存，不访问网络）：
  _data/authority_links.json   build_authority_links.py → GBIF / Catalogue of Life / Wikidata 匹配结果与 flags
  _data/bsf_links.json         build_bsf_links.py      → Blattodea Species File 半自动对照
  _species/*.md                front matter（中文正名、科、阶元、页面 slug）

三类问题（group）：
  conflict  名称差异：外部库把本站名当异名（给出接受名）
  match     匹配存疑：模糊匹配 / 多重候选，需要人工判断
  gap       覆盖缺口：仅匹配到上级阶元、外部库未收录、BSF 未检索到

只做整理，不改动任何站内分类数据；排序固定（先冲突、再存疑、再缺口，科内按学名），
输出确定性，可用 --check 校验仓库内产物是否最新。

用法：
  python .github/workflows/build_name_issues.py           # 只统计
  python .github/workflows/build_name_issues.py --write   # 写入三个产物
  python .github/workflows/build_name_issues.py --check   # 校验仓库内产物是否最新
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "_config.yml"
SPECIES_DIR = ROOT / "_species"
AUTHORITY = ROOT / "_data" / "authority_links.json"
BSF = ROOT / "_data" / "bsf_links.json"
DATA_OUT = ROOT / "_data" / "name_issues.json"
PUBLIC_OUT = ROOT / "data" / "name-issues.json"
CSV_OUT = ROOT / "downloads" / "isoptera-name-issues.csv"

GROUP_ORDER = {"conflict": 0, "match": 1, "gap": 2}
SOURCE_ORDER = {"gbif": 0, "col": 1, "bsf": 2}
FM_RE = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<value>.*?)\s*$")


def config_value(key: str) -> str:
    text = CONFIG.read_text(encoding="utf-8")
    m = re.search(r"^\s*" + re.escape(key) + r":\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        sys.exit("error: 无法从 " + CONFIG.name + " 读取 " + key)
    return m.group(1).strip().strip("'\"").rstrip("/")


def parse_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    if not text.startswith("---"):
        sys.exit("error: " + path.name + " 缺少 front matter")
    end = text.find("\n---", 3)
    if end < 0:
        sys.exit("error: " + path.name + " 的 front matter 未闭合")
    fields = {}
    for line in text[3:end].splitlines():
        m = FM_RE.match(line)
        if not m or m.group("key") == "layout":
            continue
        value = m.group("value")
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        fields[m.group("key")] = value
    return fields


def load_species() -> dict:
    out = {}
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path)
        latin = fm.get("latin", "")
        if not latin:
            continue
        out[latin] = {
            "zh": fm.get("zh", ""),
            "rank": "亚种" if fm.get("rank") == "subspecies" else "种",
            "family_zh": fm.get("family_zh", ""),
            "family_latin": fm.get("family_latin", ""),
            "slug": path.stem,
        }
    return out


def make_row(latin, sp, source, group, kind, theirs="", url=None, accepted=None,
             accepted_url=None, match=None, confidence=None, verified=False, note=""):
    return {
        "latin": latin,
        "zh": sp.get("zh", ""),
        "slug": sp.get("slug", ""),
        "rank": sp.get("rank", ""),
        "family_zh": sp.get("family_zh", ""),
        "family_latin": sp.get("family_latin", ""),
        "source": source,
        "group": group,
        "kind": kind,
        "theirs": theirs or "",
        "url": url or None,
        "accepted": accepted or None,
        "accepted_url": accepted_url or None,
        "match": match or None,
        "confidence": confidence if isinstance(confidence, int) else None,
        "verified": bool(verified),
        "note": (note or "").strip(),
    }


def build() -> dict:
    auth = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    bsf = json.loads(BSF.read_text(encoding="utf-8"))
    species = load_species()

    gbif_base = config_value("gbif_species")
    col_base = config_value("col_taxon")
    bsf_base = config_value("bsf_otu")

    rows = []
    for latin in sorted(auth.get("taxa", {})):
        rec = auth["taxa"][latin]
        sp = species.get(latin, {})
        flags = rec.get("flags") or []
        gbif = rec.get("gbif") or {}
        col = rec.get("col") or {}

        if "gbif_synonym" in flags:
            acc = gbif.get("accepted") or {}
            rows.append(make_row(
                latin, sp, "gbif", "conflict", "synonym",
                theirs=gbif.get("name", ""),
                url=gbif_base + "/" + str(gbif.get("key")) if gbif.get("key") else None,
                accepted=acc.get("name"),
                accepted_url=gbif_base + "/" + str(acc.get("key")) if acc.get("key") else None,
                match=gbif.get("match"), confidence=gbif.get("confidence")))
        if "col_synonym" in flags:
            acc = col.get("accepted") or {}
            rows.append(make_row(
                latin, sp, "col", "conflict", "synonym",
                theirs=col.get("label") or latin,
                url=col_base + "/" + str(col.get("id")) if col.get("id") else None,
                accepted=acc.get("label"),
                accepted_url=col_base + "/" + str(acc.get("id")) if acc.get("id") else None,
                match="exact", confidence=None))
        if "gbif_fuzzy" in flags:
            rows.append(make_row(
                latin, sp, "gbif", "match", "fuzzy",
                theirs=gbif.get("name", ""),
                url=gbif_base + "/" + str(gbif.get("key")) if gbif.get("key") else None,
                match=gbif.get("match"), confidence=gbif.get("confidence")))
        if "gbif_higherrank" in flags:
            rows.append(make_row(
                latin, sp, "gbif", "gap", "higherrank",
                theirs=gbif.get("name", ""),
                match=gbif.get("match"), confidence=gbif.get("confidence")))
        if "col_higherrank" in flags:
            rows.append(make_row(
                latin, sp, "col", "gap", "higherrank",
                theirs=col.get("label") or "",
                match="higherrank"))
        if "col_missing" in flags:
            rows.append(make_row(latin, sp, "col", "gap", "missing"))

    bsf_verified_total = 0
    for latin in sorted(bsf.get("name_map", {})):
        rec = bsf["name_map"][latin]
        sp = species.get(latin, {})
        status = rec.get("status")
        verified = bool(rec.get("verified"))
        if verified:
            bsf_verified_total += 1
        note = rec.get("notes") or ""
        if status == "ambiguous":
            rows.append(make_row(latin, sp, "bsf", "match", "ambiguous",
                                 match=rec.get("match"), verified=verified, note=note))
        elif status == "missing":
            rows.append(make_row(latin, sp, "bsf", "gap", "missing",
                                 verified=verified, note=note))
        elif status == "synonym":
            rows.append(make_row(
                latin, sp, "bsf", "conflict", "synonym",
                theirs=rec.get("label") or latin,
                url=rec.get("url"),
                accepted=rec.get("valid_label"),
                accepted_url=(bsf_base + "/" + str(rec.get("valid_otu")) + "/overview")
                if rec.get("valid_otu") else rec.get("url"),
                match=rec.get("match"), verified=verified, note=note))

    rows.sort(key=lambda r: (GROUP_ORDER[r["group"]], r["family_latin"].casefold(),
                             r["latin"].casefold(), SOURCE_ORDER[r["source"]], r["kind"]))

    by_group, by_source, by_kind, by_latin = {}, {}, {}, {}
    for r in rows:
        by_group[r["group"]] = by_group.get(r["group"], 0) + 1
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
        by_latin[r["latin"]] = by_latin.get(r["latin"], 0) + 1

    payload = {
        "meta": {
            "title": "Isoptera checklist — name discrepancies and review queue",
            "scope": "本站每一物种/亚种与 GBIF Backbone、Catalogue of Life、Blattodea Species File 的对照结果中，"
                     "需要人工注意的条目；只提示，不改动站内分类数据。",
            "method": "由 .github/workflows/build_name_issues.py 从 _data/authority_links.json 与 "
                      "_data/bsf_links.json 生成；匹配规则见 _tools/外部权威库与一致性核对.md。",
            "cache_dates": {
                "authority": (auth.get("meta") or {}).get("generated"),
                "bsf": (bsf.get("meta") or {}).get("generated"),
            },
            "counts": {
                "total": len(rows),
                "by_group": by_group,
                "by_source": by_source,
                "by_kind": by_kind,
                "species_total": len(species),
                "species_with_issue": len({r["latin"] for r in rows}),
                "bsf_verified": bsf_verified_total,
            },
            "by_latin": {k: by_latin[k] for k in sorted(by_latin)},
        },
        "issues": rows,
    }
    return payload


def csv_text(payload: dict) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["scientificName", "chineseName", "rank", "familyZh", "familyLatin",
                     "source", "group", "kind", "ourName", "externalName", "acceptedName",
                     "match", "confidence", "externalUrl", "acceptedUrl", "verified", "note"])
    for r in payload["issues"]:
        writer.writerow([r["latin"], r["zh"], r["rank"], r["family_zh"], r["family_latin"],
                         r["source"], r["group"], r["kind"], r["latin"], r["theirs"],
                         r["accepted"] or "", r["match"] or "",
                         r["confidence"] if r["confidence"] is not None else "",
                         r["url"] or "", r["accepted_url"] or "",
                         "yes" if r["verified"] else "no", r["note"]])
    return buf.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description="构建命名差异看板数据")
    parser.add_argument("--write", action="store_true", help="写入三个产物")
    parser.add_argument("--check", action="store_true", help="校验仓库内产物是否最新")
    args = parser.parse_args()

    for required in (AUTHORITY, BSF, CONFIG):
        if not required.is_file():
            sys.exit("error: 找不到 " + str(required.relative_to(ROOT)))

    payload = build()
    js = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
    csv_content = csv_text(payload)
    counts = payload["meta"]["counts"]

    print("条目 {total}（冲突 {conflict} / 存疑 {match} / 缺口 {gap}）；来源 "
          "GBIF {gbif} · COL {col} · BSF {bsf}；涉及物种 {species_with_issue}/{species_total}；"
          "BSF 已人工核对 {bsf_verified}".format(
              total=counts["total"], conflict=counts["by_group"].get("conflict", 0),
              match=counts["by_group"].get("match", 0), gap=counts["by_group"].get("gap", 0),
              gbif=counts["by_source"].get("gbif", 0), col=counts["by_source"].get("col", 0),
              bsf=counts["by_source"].get("bsf", 0),
              species_with_issue=counts["species_with_issue"],
              species_total=counts["species_total"], bsf_verified=counts["bsf_verified"]))

    if args.check:
        problems = []
        if not DATA_OUT.is_file():
            problems.append(str(DATA_OUT.relative_to(ROOT)))
        elif DATA_OUT.read_text(encoding="utf-8") != js:
            problems.append(str(DATA_OUT.relative_to(ROOT)))
        if not PUBLIC_OUT.is_file():
            problems.append(str(PUBLIC_OUT.relative_to(ROOT)))
        elif PUBLIC_OUT.read_text(encoding="utf-8") != js:
            problems.append(str(PUBLIC_OUT.relative_to(ROOT)))
        if not CSV_OUT.is_file():
            problems.append(str(CSV_OUT.relative_to(ROOT)))
        elif CSV_OUT.read_text(encoding="utf-8-sig") != csv_content:
            problems.append(str(CSV_OUT.relative_to(ROOT)))
        if problems:
            print("error: 以下产物已过期，请运行 --write：" + "、".join(problems), file=sys.stderr)
            return 1
        print("校验通过：三个产物与生成结果一致")
        return 0

    if args.write:
        DATA_OUT.write_text(js, encoding="utf-8", newline="\n")
        PUBLIC_OUT.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC_OUT.write_text(js, encoding="utf-8", newline="\n")
        CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
        CSV_OUT.write_text(csv_content, encoding="utf-8-sig", newline="\n")
        print("已写入 _data/name_issues.json、data/name-issues.json、downloads/isoptera-name-issues.csv")
    else:
        print("未写入（加 --write 写入文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
