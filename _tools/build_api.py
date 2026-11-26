#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成只读静态 API（`api/v1/**`），让名录能被程序按名、按分类、按 slug 读取。

产物（全部确定性，重复运行零字节变化）：
  api/v1/index.json             版本、许可、引用格式、端点清单、匹配语义
  api/v1/names.json             规范化名称 → 接受名 / 异名 / 中文名 / 属 / 科 的查找表
  api/v1/taxonomy.json          支系 → 科 → 亚科 / 属 的层级与计数（不含种级明细）
  api/v1/species/<slug>.json    3,089 个种与亚种的完整记录（分类、分布、异名、外部对照）

输入（都是仓库内已生成的确定性数据，不联网）：
  dataset/data/isoptera-taxonomy.json   支系→科→亚科→属→种/亚种 的完整树
  dataset/data/isoptera-synonyms.csv    异名 → 接受名长表（页码由 parse_synonym 剥离）
  _data/name_issues.json                GBIF / CoL / BSF 名称对照与人工裁定
  dataset/metadata.json                 版本、许可、DOI、引用

设计约束：
  * GitHub Pages 是静态托管：没有 `?q=` 服务端查询，`names.json` 是完整查找表；
  * 名称匹配在客户端按规范化键完成（NFKC + 折叠空白 + 小写）；
  * 同一键命中多个分类单元时返回 `match: ambiguous` 与 `candidates`，不擅自选一个；
  * 学名只收录名录里的拼写，不引入外部名称，也不改写 `_species/`。

用法：
  python _tools/build_api.py             # 只构建并自检，不写文件
  python _tools/build_api.py --write     # 写入 api/v1/**
  python _tools/build_api.py --check     # 校验仓库内产物与生成结果一致
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_tools"))
from build_dwca import parse_synonym  # noqa: E402

API_VERSION = "1"
SITE = "https://termite-extant-isoptera.org"
API_BASE = f"{SITE}/api/v1"

TAXONOMY_JSON = ROOT / "dataset" / "data" / "isoptera-taxonomy.json"
SYNONYMS_CSV = ROOT / "dataset" / "data" / "isoptera-synonyms.csv"
NAME_ISSUES_JSON = ROOT / "_data" / "name_issues.json"
METADATA_JSON = ROOT / "dataset" / "metadata.json"
OUT_DIR = ROOT / "api" / "v1"

SPACE_RE = re.compile(r"\s+")
PAREN_RE = re.compile(r"\s*\(\s*([^()]*?)\s*\)\s*")
SPECIES_URL_RE = re.compile(r"/species/([^/]+)/?$")

PRIORITY = {
    "accepted": 5,
    "synonym": 4,
    "zh": 3,
    "genus": 2,
    "family": 2,
    "subfamily": 2,
}


def normalize(name: str | None) -> str:
    """查找表的键：全半角归一（NFKC）、折叠空白、去首尾、转小写。"""
    text = unicodedata.normalize("NFKC", name or "")
    text = text.replace("\u00a0", " ")
    return SPACE_RE.sub(" ", text).strip().lower()


def strip_subgenus(name: str) -> str:
    """去掉属名后的亚属括号，便于用「Coptotermes changtaiensis」查到带亚属的异名。"""
    stripped = PAREN_RE.sub(" ", name or "")
    return SPACE_RE.sub(" ", stripped).strip()


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def slug_from_page_url(url: str) -> str:
    match = SPECIES_URL_RE.search(url or "")
    if not match:
        raise SystemExit(f"[build_api] 无法从页面地址取 slug：{url!r}")
    return match.group(1)


class NameIndex:
    """收集候选条目，按优先级合并；同优先级命中多个分类单元时标为 ambiguous。"""

    def __init__(self) -> None:
        self.buckets: dict[str, dict[tuple, dict]] = {}

    def add(self, key: str, entry: dict) -> None:
        norm = normalize(key)
        if not norm:
            return
        identity = (entry.get("match"), entry.get("slug") or entry.get("acceptedSlug") or "")
        self.buckets.setdefault(norm, {})[identity] = entry

    def finalize(self) -> dict:
        out: dict[str, dict] = {}
        for key, bucket in self.buckets.items():
            entries = list(bucket.values())
            best = max(PRIORITY[item["match"]] for item in entries)
            top = [item for item in entries if PRIORITY[item["match"]] == best]
            unique: dict[tuple, dict] = {}
            for item in top:
                unique[(item.get("match"), item.get("slug") or item.get("acceptedSlug"))] = item
            if len(unique) > 1 and all(item["match"] == "synonym" for item in unique.values()):
                # 同一个异名同时挂在种与其亚种下（如 Pseudacanthotermes militaris 与
                # P. militaris militaris）不是真的同名冲突：保留层级更高的种。
                slugs = sorted({item["acceptedSlug"] for item in unique.values()}, key=len)
                if all(slug == slugs[0] or slug.startswith(slugs[0] + "-") for slug in slugs):
                    unique = {
                        ident: item
                        for ident, item in unique.items()
                        if item.get("acceptedSlug") == slugs[0]
                    }
            if len(unique) == 1:
                out[key] = next(iter(unique.values()))
            else:
                candidates = []
                for item in sorted(
                    unique.values(),
                    key=lambda row: (row.get("latin") or "", row.get("slug") or row.get("acceptedSlug") or ""),
                ):
                    candidates.append(
                        {k: item[k] for k in ("match", "rank", "latin", "zh", "slug", "accepted", "acceptedSlug")
                         if k in item}
                    )
                out[key] = {"match": "ambiguous", "candidates": candidates}
        return dict(sorted(out.items()))


def citation_from(meta: dict) -> str:
    creators = meta.get("creators") or []
    author = (creators[0] or {}).get("name", "") if creators else ""
    title = (meta.get("title") or {}).get("zh") or ""
    publisher = meta.get("publisher") or ""
    doi = (meta.get("doi") or {}).get("version") or ""
    parts = [part for part in (author, title, publisher) if part]
    text = ". ".join(parts)
    if doi:
        text += f". https://doi.org/{doi}"
    return text


def build() -> tuple[dict[str, str], dict]:
    tax = read_json(TAXONOMY_JSON)
    meta = read_json(METADATA_JSON)
    issues_data = read_json(NAME_ISSUES_JSON)

    version = tax.get("version") or meta.get("version") or ""
    date_modified = tax.get("dateModified") or ""
    counts = tax.get("counts") or {}

    clade_by_id = {clade["id"]: clade for clade in tax.get("clades") or []}
    subfamily_by_id: dict[str, dict] = {}
    family_by_id = {family["id"]: family for family in tax.get("families") or []}
    for family in tax.get("families") or []:
        for subfamily in family.get("subfamilies") or []:
            subfamily_by_id[subfamily["id"]] = subfamily

    # 异名长表：按接受名页面地址归组，页码与附注由 build_dwca.parse_synonym 拆分。
    synonyms_by_page: dict[str, list[dict]] = {}
    unknown_targets: list[str] = []
    with SYNONYMS_CSV.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            page_url = (row.get("taxonID") or "").strip()
            if not page_url:
                continue
            name, authorship, reference, note = parse_synonym(row.get("synonym") or "")
            record = {
                "asPublished": row.get("synonym") or "",
                "name": name,
                "authorship": authorship,
                "reference": reference,
                "note": note,
                "typeLocality": row.get("synonymTypeLocality") or "",
                "localityAlignment": row.get("localityAlignment") or "",
            }
            synonyms_by_page.setdefault(page_url, []).append(record)
            if not SPECIES_URL_RE.search(page_url):
                unknown_targets.append(page_url)

    issues_by_slug: dict[str, list[dict]] = {}
    for issue in issues_data.get("issues") or []:
        slug = issue.get("slug")
        if slug:
            issues_by_slug.setdefault(slug, []).append(issue)
    authority_review = issues_data.get("species_authority") or {}

    names = NameIndex()
    files: dict[str, str] = {}
    seen_slugs: dict[str, str] = {}

    def register_slug(slug: str, latin: str) -> None:
        if slug in seen_slugs:
            raise SystemExit(f"[build_api] slug 重复：{slug}（{seen_slugs[slug]} / {latin}）")
        seen_slugs[slug] = latin

    def classification(family: dict, genus: dict) -> dict:
        clade = clade_by_id.get(family.get("cladeId") or "") or {}
        subfamily = subfamily_by_id.get(genus.get("subfamilyId") or "")
        return {
            "clade": {"id": clade.get("id", ""), "latin": clade.get("latin", ""), "zh": clade.get("zh", "")},
            "family": {"id": family.get("id", ""), "latin": family.get("latin", ""), "zh": family.get("zh", "")},
            "subfamily": (
                {"id": subfamily.get("id", ""), "latin": subfamily.get("latin", ""), "zh": subfamily.get("zh", "")}
                if subfamily
                else None
            ),
            "genus": {"id": genus.get("id", ""), "latin": genus.get("latin", ""), "zh": genus.get("zh", "")},
        }

    def add_accepted_name(entry_key: str, entry: dict, latin: str, authorship: str = "") -> None:
        names.add(entry_key, entry)
        if authorship:
            names.add(f"{latin} {authorship}", entry)

    def add_synonym_names(record: dict, accepted_latin: str, accepted_slug: str) -> None:
        entry = {
            "match": "synonym",
            "latin": record["name"],
            "authorship": record["authorship"],
            "accepted": accepted_latin,
            "acceptedSlug": accepted_slug,
        }
        names.add(record["name"], entry)
        if record["authorship"]:
            names.add(f"{record['name']} {record['authorship']}", entry)
        stripped = strip_subgenus(record["name"])
        if stripped and stripped != record["name"]:
            names.add(stripped, entry)

    for family in tax.get("families") or []:
        family_cls = {
            "id": family.get("id", ""),
            "latin": family.get("latin", ""),
            "zh": family.get("zh", ""),
            "page": f"{SITE}/family/{family.get('id', '')}/",
        }
        names.add(
            family.get("latin", ""),
            {"match": "family", "rank": "family", "latin": family.get("latin", ""), "zh": family.get("zh", ""),
             "slug": family.get("id", ""), "page": family_cls["page"]},
        )
        names.add(
            family.get("zh", ""),
            {"match": "family", "rank": "family", "latin": family.get("latin", ""), "zh": family.get("zh", ""),
             "slug": family.get("id", ""), "page": family_cls["page"]},
        )
        for subfamily in family.get("subfamilies") or []:
            sub_page = f"{SITE}/subfamily/{subfamily.get('id', '')}/"
            sub_entry = {
                "match": "subfamily", "rank": "subfamily", "latin": subfamily.get("latin", ""),
                "zh": subfamily.get("zh", ""), "slug": subfamily.get("id", ""), "page": sub_page,
            }
            names.add(subfamily.get("latin", ""), sub_entry)
            names.add(subfamily.get("zh", ""), sub_entry)

        for genus in family.get("genera") or []:
            genus_page = f"{SITE}/genus/{genus.get('id', '')}/"
            genus_entry = {
                "match": "genus", "rank": "genus", "latin": genus.get("latin", ""),
                "zh": genus.get("zh", ""), "slug": genus.get("id", ""), "page": genus_page,
            }
            names.add(genus.get("latin", ""), genus_entry)
            names.add(genus.get("zh", ""), genus_entry)

            for species in genus.get("species") or []:
                slug = slug_from_page_url(species.get("pageUrl", ""))
                register_slug(slug, species.get("latin", ""))
                latin = species.get("latin", "")
                zh = species.get("zh", "")
                authorship = species.get("authorship", "")
                record = {
                    "apiVersion": API_VERSION,
                    "version": version,
                    "latin": latin,
                    "zh": zh,
                    "rank": "species",
                    "authorship": authorship,
                    "isTypeSpecies": bool(species.get("isTypeSpecies")),
                    "typeLocality": species.get("typeLocality", ""),
                    "classification": classification(family, genus),
                    "distribution": {
                        "zh": species.get("distributionZh", ""),
                        "en": species.get("distributionEn", ""),
                    },
                    "synonyms": synonyms_by_page.get(species.get("pageUrl", ""), []),
                    "subspecies": [],
                    "pageUrl": species.get("pageUrl", ""),
                    "apiUrl": f"{API_BASE}/species/{slug}.json",
                }

                for sub in species.get("subspecies") or []:
                    sub_slug = slug_from_page_url(sub.get("pageUrl", ""))
                    register_slug(sub_slug, sub.get("latin", ""))
                    sub_record = {
                        "apiVersion": API_VERSION,
                        "version": version,
                        "latin": sub.get("latin", ""),
                        "zh": sub.get("zh", ""),
                        "rank": "subspecies",
                        "authorship": sub.get("authorship", ""),
                        "typeLocality": sub.get("typeLocality", ""),
                        "classification": classification(family, genus),
                        "parent": {"latin": latin, "zh": zh, "slug": slug},
                        "synonyms": synonyms_by_page.get(sub.get("pageUrl", ""), []),
                        "pageUrl": sub.get("pageUrl", ""),
                        "apiUrl": f"{API_BASE}/species/{sub_slug}.json",
                    }
                    sub_checks = issues_by_slug.get(sub_slug)
                    if sub_checks:
                        sub_record["authorityChecks"] = sub_checks
                    files[f"species/{sub_slug}.json"] = dump(sub_record)
                    add_accepted_name(
                        sub.get("latin", ""),
                        {"match": "accepted", "rank": "subspecies", "latin": sub.get("latin", ""),
                         "zh": sub.get("zh", ""), "slug": sub_slug, "page": sub.get("pageUrl", "")},
                        sub.get("latin", ""),
                        sub.get("authorship", ""),
                    )
                    for synonym in sub_record["synonyms"]:
                        add_synonym_names(synonym, sub.get("latin", ""), sub_slug)
                    record["subspecies"].append(
                        {"latin": sub.get("latin", ""), "zh": sub.get("zh", ""),
                         "authorship": sub.get("authorship", ""), "slug": sub_slug,
                         "pageUrl": sub.get("pageUrl", "")}
                    )

                checks = issues_by_slug.get(slug)
                if checks:
                    record["authorityChecks"] = checks
                review = authority_review.get(slug)
                if review:
                    record["authorityReview"] = review
                files[f"species/{slug}.json"] = dump(record)

                add_accepted_name(
                    latin,
                    {"match": "accepted", "rank": "species", "latin": latin, "zh": zh,
                     "slug": slug, "page": species.get("pageUrl", "")},
                    latin,
                    authorship,
                )
                if zh:
                    names.add(zh, {"match": "zh", "rank": "species", "latin": latin, "zh": zh, "slug": slug,
                                   "page": species.get("pageUrl", "")})
                for synonym in record["synonyms"]:
                    add_synonym_names(synonym, latin, slug)

    taxonomy = {
        "apiVersion": API_VERSION,
        "version": version,
        "dateModified": date_modified,
        "counts": counts,
        "clades": [
            {"id": clade.get("id", ""), "latin": clade.get("latin", ""), "zh": clade.get("zh", ""),
             "parentId": clade.get("parentId", "")}
            for clade in tax.get("clades") or []
        ],
        "families": [
            {
                "id": family.get("id", ""),
                "latin": family.get("latin", ""),
                "zh": family.get("zh", ""),
                "cladeId": family.get("cladeId", ""),
                "subfamilies": [
                    {"id": sub.get("id", ""), "latin": sub.get("latin", ""), "zh": sub.get("zh", "")}
                    for sub in family.get("subfamilies") or []
                ],
                "genera": [
                    {
                        "id": genus.get("id", ""),
                        "latin": genus.get("latin", ""),
                        "zh": genus.get("zh", ""),
                        "subfamilyId": genus.get("subfamilyId", ""),
                        "typeSpecies": genus.get("typeSpecies", ""),
                        "counts": genus.get("counts") or {},
                    }
                    for genus in family.get("genera") or []
                ],
            }
            for family in tax.get("families") or []
        ],
    }

    names_map = names.finalize()
    species_count = sum(1 for rel in files if rel.startswith("species/"))
    expected = int(counts.get("species", 0)) + int(counts.get("subspecies", 0))
    if species_count != expected:
        raise SystemExit(f"[build_api] 物种记录 {species_count} 与 counts 的 {expected} 不一致")
    if unknown_targets:
        raise SystemExit("[build_api] 异名指向了未知页面地址：" + "；".join(sorted(set(unknown_targets))[:5]))
    missing_synonym_pages = [page for page in synonyms_by_page if slug_from_page_url(page) not in seen_slugs]
    if missing_synonym_pages:
        raise SystemExit("[build_api] 异名指向的页面没有生成记录：" + "；".join(missing_synonym_pages[:5]))

    index = {
        "name": "extant-isoptera-api",
        "apiVersion": API_VERSION,
        "version": version,
        "dateModified": date_modified,
        "baseUrl": API_BASE + "/",
        "docs": {
            "zh": f"{SITE}/api/",
            "en": f"{SITE}/en/api/",
            "es": f"{SITE}/es/api/",
        },
        "license": meta.get("license") or {},
        "citation": citation_from(meta),
        "counts": counts,
        "endpoints": {
            "names": {"url": f"{API_BASE}/names.json", "entries": len(names_map)},
            "taxonomy": {"url": f"{API_BASE}/taxonomy.json",
                         "families": len(taxonomy["families"])},
            "species": {"urlTemplate": f"{API_BASE}/species/{{slug}}.json", "count": species_count},
            "authorityChecks": {"url": f"{SITE}/data/name-issues.json",
                                "count": len(issues_data.get("issues") or [])},
        },
        "matching": {
            "normalization": "Unicode NFKC, trim, collapse whitespace, lowercase",
            "lookup": "names.json is the whole lookup table; a static host has no query-string endpoint",
            "values": {
                "accepted": "an accepted species or subspecies name in the checklist",
                "synonym": "a synonym; acceptedSlug points to the accepted record",
                "zh": "a Chinese standard name",
                "genus": "a genus",
                "family": "a family",
                "subfamily": "a subfamily",
                "ambiguous": "the key matches more than one taxon; candidates lists them all",
            },
            "absent": "an absent key means the name is not in the checklist",
        },
    }

    files["names.json"] = dump(names_map)
    files["taxonomy.json"] = dump(taxonomy)
    files["index.json"] = dump(index)
    return files, {
        "species": species_count,
        "names": len(names_map),
        "ambiguous": sum(1 for entry in names_map.values() if entry.get("match") == "ambiguous"),
    }


def write_files(files: dict[str, str]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for rel, text in sorted(files.items()):
        path = OUT_DIR / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    # 删除重命名 / 删除物种后留下的旧记录，避免 API 里出现已不存在的分类单元。
    keep = {rel for rel in files}
    for path in sorted(OUT_DIR.rglob("*.json")):
        rel = path.relative_to(OUT_DIR).as_posix()
        if rel not in keep:
            path.unlink()
    for path in sorted(OUT_DIR.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def check(files: dict[str, str]) -> int:
    if not OUT_DIR.is_dir():
        print(f"[build_api] 缺少 {OUT_DIR.relative_to(ROOT).as_posix()}/，先跑 --write", file=sys.stderr)
        return 1
    existing = {path.relative_to(OUT_DIR).as_posix() for path in OUT_DIR.rglob("*.json")}
    errors: list[str] = []
    for rel in sorted(set(files) - existing):
        errors.append(f"缺少 {rel}")
    for rel in sorted(existing - set(files)):
        errors.append(f"多出 {rel}")
    for rel in sorted(set(files) & existing):
        actual = (OUT_DIR / rel).read_text(encoding="utf-8")
        if actual != files[rel]:
            errors.append(f"内容过期 {rel}")
    if errors:
        for error in errors[:20]:
            print(f"[build_api] {error}", file=sys.stderr)
        if len(errors) > 20:
            print(f"[build_api] ……另有 {len(errors) - 20} 条", file=sys.stderr)
        return 1
    print(f"[build_api] api/v1 与生成结果一致（{len(files)} 个文件）")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="生成只读静态 API（api/v1/**）")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="写入 api/v1/**")
    group.add_argument("--check", action="store_true", help="校验仓库内产物是否最新")
    args = parser.parse_args()

    files, stats = build()
    if args.write:
        write_files(files)
        print(f"[build_api] 已写入 {len(files)} 个文件：{stats['species']} 条物种记录、"
              f"{stats['names']} 个名称键（其中 {stats['ambiguous']} 个歧义）")
        return 0
    if args.check:
        return check(files)

    print(f"[build_api] 自检通过：{stats['species']} 条物种记录、{stats['names']} 个名称键"
          f"（{stats['ambiguous']} 个歧义）；未写文件（用 --write）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
