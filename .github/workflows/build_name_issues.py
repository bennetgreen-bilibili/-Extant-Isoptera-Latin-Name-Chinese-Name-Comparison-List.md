#!/usr/bin/env python3
"""构建「命名差异与待核对」看板数据（/list/name-issues/）。

把已有缓存里的「本站名 vs 外部库」对照结果整理成结构化清单，供页面筛选、下载与程序化访问：

  _data/name_issues.json          页面用（site.data.name_issues）
  data/name-issues.json           公开副本（与 data/references.json 同一做法）
  downloads/isoptera-name-issues.csv  可下载对照表（UTF-8 BOM，Excel 直接打开不花屏）
  downloads/isoptera-synonym-groups.csv  异名→接受名长表（同样 UTF-8 BOM）

数据来源（均为仓库内已提交的缓存，不访问网络）：
  _data/authority_links.json   build_authority_links.py → GBIF / Catalogue of Life / Wikidata 匹配结果与 flags
  _data/bsf_links.json         build_bsf_links.py      → Blattodea Species File 半自动对照
  _species/*.md                front matter（中文正名、科、阶元、页面 slug）

三类问题（group）：
  conflict  名称差异：外部库把本站名当异名（给出接受名）
  match     匹配存疑：模糊匹配 / 多重候选，需要人工判断
  gap       覆盖缺口：仅匹配到上级阶元、外部库未收录、BSF 未检索到

名称差异还会按**接受名（接收名）归并**一份，对应「把异名记录到对应的接收名下面」：

  synonym_groups[]               每个接受名一组：接受名、是否本站也收录、引用它的异名（同一种多来源合并）
  synonyms_by_slug{}             反查索引：站内 slug → 外部库归入该种的异名（物种页「其他数据库」区块用）
  meta.counts.synonym_groups …   归并后的统计口径（组数 / 本站另收 / 异名对数 / 涉及本站名个数）
  downloads/isoptera-synonym-groups.csv  同一份归并结果的长表（一行一对「接受名 ← 异名」）

外链基址读自 _config.yml 的 external.*：按 YAML 规则去掉行尾注释后再拼接，
否则会把「# + /<GBIF usageKey>」这类说明也拼进 URL，页面上的异名/接受名链接会变成坏地址。

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
SYN_CSV_OUT = ROOT / "downloads" / "isoptera-synonym-groups.csv"

GROUP_ORDER = {"conflict": 0, "match": 1, "gap": 2}
SOURCE_ORDER = {"gbif": 0, "col": 1, "bsf": 2}
FM_RE = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<value>.*?)\s*$")
# 接受名去掉命名人后剩下的规范学名：属 + 种 [+ 亚种小写加词]
CANON_RE = re.compile(
    r"^(?P<genus>[A-Z][A-Za-z\-]+)\s+(?P<species>[a-z][A-Za-z\-]+)"
    r"(?:\s+(?P<subspecies>[a-z][A-Za-z\-]+))?"
)
SYN_CSV_COLUMNS = [
    "acceptedName", "acceptedLatin", "acceptedInSite", "acceptedSlug", "acceptedZh",
    "synonymName", "synonymZh", "synonymSlug", "familyZh", "sources",
    "match", "confidence", "synonymUrl", "acceptedUrl",
]


def config_value(key: str) -> str:
    """读 _config.yml 的单行标量，按 YAML 规则去掉行尾注释（空白 + # 之后）。"""
    text = CONFIG.read_text(encoding="utf-8")
    m = re.search(r"^\s*" + re.escape(key) + r":\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        sys.exit("error: 无法从 " + CONFIG.name + " 读取 " + key)
    value = re.split(r"\s+#", m.group(1), maxsplit=1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip().rstrip("/")


def url_base(key: str) -> str:
    """读外链基址，并确认它是干净的绝对 URL（防止行尾注释再次被拼进链接）。"""
    value = config_value(key)
    if not re.match(r"^https?://[^\s\"'#<>]+$", value):
        sys.exit("error: " + CONFIG.name + " 的 " + key + "=%r 不是合法 URL 基址" % value)
    return value


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


def canonical_name(label: str) -> str:
    """把带命名人的接受名压成规范学名：属 + 种 [+ 亚种加词]。

    「Amitermes wheeleri (Desneux, 1906)」→「Amitermes wheeleri」
    「Pericapritermes appellans metata Silvestri, 1914」→「Pericapritermes appellans metata」
    不同来源的接受名写法不完全一致，只有压成规范学名才能把同一个接受名的
    多条异名记录归到一组、并与 _species 的 latin 对齐。
    """
    text = re.sub(r"\s*\([^)]*\)\s*", " ", label or "").strip()
    m = CANON_RE.match(text)
    if not m:
        return (label or "").strip()
    parts = [m.group("genus"), m.group("species")]
    if m.group("subspecies"):
        parts.append(m.group("subspecies"))
    return " ".join(parts)


def annotate_accepted(row: dict, species: dict) -> dict:
    """给「外部库给出接受名」的条目补上接受名的规范学名与站内对应记录。

    这是「把异名记录到对应的接收名下面」的逐条版本：每条名称差异都能落到一个
    接收名（accepted）上；本名录也收录该名时，一并给出它的页面 slug 与中文名。
    """
    accepted = row.get("accepted")
    if not accepted:
        return row
    canonical = canonical_name(accepted)
    sp = species.get(canonical) or {}
    row = dict(row)
    row["accepted_latin"] = canonical
    if sp:
        row["accepted_in_site"] = True
        row["accepted_slug"] = sp.get("slug", "")
        row["accepted_zh"] = sp.get("zh", "")
    return row


def build_synonym_groups(rows: list) -> list:
    """把名称差异（kind=synonym）按接受名归并成组，组内合并多来源的同一异名。"""
    groups: dict = {}
    for row in rows:
        if row["group"] != "conflict" or not row.get("accepted_latin"):
            continue
        group = groups.get(row["accepted_latin"])
        if group is None:
            group = {
                "accepted": row["accepted"],
                "accepted_latin": row["accepted_latin"],
                "accepted_in_site": bool(row.get("accepted_slug")),
                "accepted_slug": row.get("accepted_slug") or None,
                "accepted_zh": row.get("accepted_zh") or None,
                "accepted_links": [],
                "synonyms": [],
            }
            groups[row["accepted_latin"]] = group
        if row.get("accepted_url") and not any(
                link["source"] == row["source"] for link in group["accepted_links"]):
            group["accepted_links"].append({"source": row["source"], "url": row["accepted_url"]})

        synonym = next((item for item in group["synonyms"] if item["latin"] == row["latin"]), None)
        if synonym is None:
            synonym = {
                "latin": row["latin"],
                "zh": row.get("zh", ""),
                "slug": row.get("slug", ""),
                "family_zh": row.get("family_zh", ""),
                "family_latin": row.get("family_latin", ""),
                "sources": [],
                "links": [],
                "match": None,
                "confidence": None,
            }
            group["synonyms"].append(synonym)
        if row["source"] not in synonym["sources"]:
            synonym["sources"].append(row["source"])
        if row.get("url") and not any(
                link["source"] == row["source"] for link in synonym["links"]):
            synonym["links"].append({"source": row["source"], "url": row["url"]})
        if synonym["match"] is None and row.get("match"):
            synonym["match"] = row["match"]
        if synonym["confidence"] is None and row.get("confidence") is not None:
            synonym["confidence"] = row["confidence"]

    ordered = sorted(groups.values(), key=lambda item: item["accepted_latin"].casefold())
    for group in ordered:
        group["accepted_links"].sort(key=lambda link: SOURCE_ORDER[link["source"]])
        group["synonyms"].sort(key=lambda item: item["latin"].casefold())
        for synonym in group["synonyms"]:
            synonym["sources"].sort(key=lambda source: SOURCE_ORDER[source])
            synonym["links"].sort(key=lambda link: SOURCE_ORDER[link["source"]])
    return ordered


def build() -> dict:
    auth = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    bsf = json.loads(BSF.read_text(encoding="utf-8"))
    species = load_species()

    gbif_base = url_base("gbif_species")
    col_base = url_base("col_taxon")
    bsf_base = url_base("bsf_otu")

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
            # BSF 的 label 形如「异名 now 接受名」；接受名另有 accepted 字段，
            # 这里只保留异名本身，免得同一串名字在「外部记录」里出现两次。
            label = rec.get("label") or latin
            rows.append(make_row(
                latin, sp, "bsf", "conflict", "synonym",
                theirs=label.split(" now ", 1)[0].strip() or latin,
                url=rec.get("url"),
                accepted=rec.get("valid_label"),
                accepted_url=(bsf_base + "/" + str(rec.get("valid_otu")) + "/overview")
                if rec.get("valid_otu") else rec.get("url"),
                match=rec.get("match"), verified=verified, note=note))

    rows = [annotate_accepted(r, species) for r in rows]
    rows.sort(key=lambda r: (GROUP_ORDER[r["group"]], r["family_latin"].casefold(),
                             r["latin"].casefold(), SOURCE_ORDER[r["source"]], r["kind"]))

    by_group, by_source, by_kind, by_latin = {}, {}, {}, {}
    for r in rows:
        by_group[r["group"]] = by_group.get(r["group"], 0) + 1
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
        by_latin[r["latin"]] = by_latin.get(r["latin"], 0) + 1

    groups = build_synonym_groups(rows)
    synonyms_by_slug = {
        group["accepted_slug"]: {
            "latin": group["accepted_latin"],
            "zh": group["accepted_zh"],
            "synonyms": group["synonyms"],
        }
        for group in groups
        if group["accepted_slug"]
    }

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
                # 名称差异按接受名（接收名）归并后的口径：条数不变，但「组」才是需要人工决策的单元
                "conflict_species": len({r["latin"] for r in rows if r["group"] == "conflict"}),
                "synonym_groups": len(groups),
                "synonym_groups_in_site": sum(1 for g in groups if g["accepted_in_site"]),
                "synonym_pairs": sum(len(g["synonyms"]) for g in groups),
            },
            "by_latin": {k: by_latin[k] for k in sorted(by_latin)},
        },
        "issues": rows,
        "synonym_groups": groups,
        "synonyms_by_slug": synonyms_by_slug,
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


def synonym_csv_text(payload: dict) -> str:
    """异名归并长表：一行一对「接受名（接收名）← 异名」。"""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(SYN_CSV_COLUMNS)
    for group in payload["synonym_groups"]:
        for synonym in group["synonyms"]:
            writer.writerow([
                group["accepted"], group["accepted_latin"],
                "yes" if group["accepted_in_site"] else "no",
                group["accepted_slug"] or "", group["accepted_zh"] or "",
                synonym["latin"], synonym["zh"], synonym["slug"], synonym["family_zh"],
                ";".join(synonym["sources"]), synonym["match"] or "",
                synonym["confidence"] if synonym["confidence"] is not None else "",
                synonym["links"][0]["url"] if synonym["links"] else "",
                group["accepted_links"][0]["url"] if group["accepted_links"] else "",
            ])
    return buf.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description="构建命名差异看板数据")
    parser.add_argument("--write", action="store_true", help="写入四个产物")
    parser.add_argument("--check", action="store_true", help="校验仓库内产物是否最新")
    args = parser.parse_args()

    for required in (AUTHORITY, BSF, CONFIG):
        if not required.is_file():
            sys.exit("error: 找不到 " + str(required.relative_to(ROOT)))

    payload = build()
    js = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
    csv_content = csv_text(payload)
    synonym_csv_content = synonym_csv_text(payload)
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
    print("名称差异按接受名归并：{groups} 组（本站另有收录 {in_site} 组）· {pairs} 对异名 · "
          "涉及本站名 {species} 个".format(
              groups=counts["synonym_groups"], in_site=counts["synonym_groups_in_site"],
              pairs=counts["synonym_pairs"], species=counts["conflict_species"]))

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
        if not SYN_CSV_OUT.is_file():
            problems.append(str(SYN_CSV_OUT.relative_to(ROOT)))
        elif SYN_CSV_OUT.read_text(encoding="utf-8-sig") != synonym_csv_content:
            problems.append(str(SYN_CSV_OUT.relative_to(ROOT)))
        if problems:
            print("error: 以下产物已过期，请运行 --write：" + "、".join(problems), file=sys.stderr)
            return 1
        print("校验通过：四个产物与生成结果一致")
        return 0

    if args.write:
        DATA_OUT.write_text(js, encoding="utf-8", newline="\n")
        PUBLIC_OUT.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC_OUT.write_text(js, encoding="utf-8", newline="\n")
        CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
        CSV_OUT.write_text(csv_content, encoding="utf-8-sig", newline="\n")
        SYN_CSV_OUT.write_text(synonym_csv_content, encoding="utf-8-sig", newline="\n")
        print("已写入 _data/name_issues.json、data/name-issues.json、"
              "downloads/isoptera-name-issues.csv、downloads/isoptera-synonym-groups.csv")
    else:
        print("未写入（加 --write 写入文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
