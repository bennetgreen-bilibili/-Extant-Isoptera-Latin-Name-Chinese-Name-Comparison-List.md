#!/usr/bin/env python3
"""构建名录站内搜索索引 search-index.json（含拼音、繁体字段）。

条目字段（按顺序输出）：
  l  拉丁学名 / 拉丁类群名
  z  中文名（种、亚种为中文正名）
  r  阶元：支系 / 科 / 亚科 / 属 / 种 / 亚种
  h  分类单元自身的锚点 id（种、亚种为所属属的 id），前端按页范围求交
  f  所属科中文名（检索结果里显示"属于哪个科"；支系与科条目省略）
  s  次异名（仅种、亚种；以 " ; " 分隔；无则省略）
  dz 分布（中文记录，仅种、亚种；无则省略）
  de 分布（英文记录，仅种、亚种；无则省略）
  t  模式产地（仅种、亚种；无则省略）
  sl 次异名的模式产地（仅种、亚种；无则省略）
  p  物种页 slug（仅种、亚种），前端跳 /species/<p>/
  u  中转页路径（支系 / 科 / 亚科 / 属），前端跳 /list/#<id> 或 /family|/subfamily|/genus/<id>/
  py 中文名的拼音连写（无声调，仅小写字母），供拼音检索
  pi 中文名的拼音首字母连写，供首字母检索
  zt 中文名的繁体写法（OpenCC s2t），供繁体检索

  dz / de / t / sl 供科、亚科、属页的局部检索（assets/taxon-search.js）按产地查种，
  数据直接取 _species/*.md 的 front matter，不再另建索引文件；它们只增字段、
  不改条目顺序，所以 --check 的确定性比对不受影响。

数据来源：
  _data/taxonomy.json   支系 → 科 → 亚科 → 属 的层级与锚点 id（条目顺序即分类顺序）
  _species/*.md         种与亚种的拉丁名 / 中文名 / 所属属 / 次异名 / 模式产地 / 分布

/list/ 已改为索引页、不再逐条罗列物种，所以索引不再解析 list.md，改由上面两个数据源生成；
名录页只负责按支系列出科并链到科页、亚科页、属页。

拼音与繁体字段为可选增强：
  pip install pypinyin opencc-python-reimplemented
缺少依赖时照常生成基础字段，并在 stderr 提示，退出码仍为 0。

自检：种 / 亚种条目数须与 _species/ 页面数一致，且每条种、亚种所属的属必须存在于
taxonomy.json 的属表里——增删物种后无需改动脚本。

用法：
  python .github/workflows/build_search_index.py             # 只报告统计与自检
  python .github/workflows/build_search_index.py --write     # 写入 search-index.json
  python .github/workflows/build_search_index.py --check     # 校验磁盘索引与生成结果一致
  python .github/workflows/build_search_index.py --no-enrich # 跳过拼音 / 繁体（离线或未装依赖时）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_JSON = ROOT / "_data" / "taxonomy.json"
SPECIES_DIR = ROOT / "_species"
INDEX_JSON = ROOT / "search-index.json"

RANK_BY_FRONT_MATTER = {"species": "种", "subspecies": "亚种"}
SYNONYM_RE = re.compile(r"^(?:\d+\.|-)\s+\*(?P<name>[^*]+)\*")
WS_RE = re.compile(r"\s+")
FM_RE = re.compile(r'^(?P<key>[a-z_]+):\s*(?P<value>.*?)\s*$')
SUBGENUS_RE = re.compile(r"^(?P<genus>[A-Z][a-z]+) \((?P<subgenus>[A-Za-z]+)\) (?P<rest>[a-z].*)$")


# ---------------------------------------------------------------- 读取来源

def parse_front_matter(path: Path) -> dict[str, str]:
    """解析 _species/*.md 的 front matter（字段均为单行标量，不引入 PyYAML）。"""
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    if not text.startswith("---"):
        sys.exit(f"error: {path.name} 缺少 front matter")
    end = text.find("\n---", 3)
    if end < 0:
        sys.exit(f"error: {path.name} 的 front matter 未闭合")
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        m = FM_RE.match(line)
        if not m or m.group("key") == "layout":
            continue
        value = m.group("value")
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        fields[m.group("key")] = value
    return fields


def parse_synonyms(path: Path) -> list[str]:
    """从物种页「## 次异名」小节提取斜体学名（保持原始顺序）。"""
    text = path.read_text(encoding="utf-8")
    start = text.find("\n## 次异名")
    if start < 0:
        return []
    body = text[start:]
    stop = body.find("\n## ", 3)
    if stop >= 0:
        body = body[:stop]
    names: list[str] = []
    for line in body.splitlines():
        m = SYNONYM_RE.match(line.strip())
        if m:
            names.append(m.group("name").strip())
    return names


def clean(value: str | None) -> str:
    """front matter 的产地 / 分布写成单行标量，这里只压平空白，不改写内容。"""
    return WS_RE.sub(" ", value or "").strip()


def expand_synonyms(names: list[str]) -> list[str]:
    """带亚属括注的异名同时收录「属 + 种」与「属 (亚属) + 种」两种写法（旧文献两种都有）。"""
    expanded: list[str] = []
    for name in names:
        m = SUBGENUS_RE.match(name)
        if m:
            expanded.append(f"{m.group('genus')} {m.group('rest')}")
            expanded.append(name)
        else:
            expanded.append(name)
    return expanded


# ---------------------------------------------------------------- 拼音 / 繁体

def build_enrichers() -> tuple:
    """返回 (pinyin_fn, traditional_fn)，任一依赖缺失则为 None。"""
    pinyin_fn = None
    traditional_fn = None

    try:
        from pypinyin import lazy_pinyin  # type: ignore

        def pinyin_fn(text: str) -> tuple[str, str]:
            syllables = [s.lower() for s in lazy_pinyin(text)]
            letters = [re.sub(r"[^a-z]", "", s) for s in syllables]
            letters = [s for s in letters if s]
            return "".join(letters), "".join(s[0] for s in letters)

    except ImportError:
        print("提示：未安装 pypinyin，跳过拼音字段（pip install pypinyin）", file=sys.stderr)

    try:
        from opencc import OpenCC  # type: ignore

        cc = OpenCC("s2t")
        traditional_fn = cc.convert

    except ImportError:
        print(
            "提示：未安装 opencc-python-reimplemented，跳过繁体字段"
            "（pip install opencc-python-reimplemented）",
            file=sys.stderr,
        )

    return pinyin_fn, traditional_fn


def enrich(entry: dict, pinyin_fn, traditional_fn, cache: dict) -> dict:
    """给条目补 py / pi / zt 字段（同一中文名只算一次）。"""
    zh = entry["z"]
    cached = cache.get(zh)
    if cached is None:
        py = pi = zt = None
        if pinyin_fn is not None:
            py, pi = pinyin_fn(zh)
        if traditional_fn is not None:
            zt = traditional_fn(zh)
        cached = (py, pi, zt)
        cache[zh] = cached
    py, pi, zt = cached
    if py:
        entry["py"] = py
    if pi and pi != py:
        entry["pi"] = pi
    if zt and zt != zh:
        entry["zt"] = zt
    return entry


# ---------------------------------------------------------------- 构建索引

def build(species_fields: dict[str, dict[str, str]],
          species_synonyms: dict[str, list[str]]) -> list[dict]:
    """按 classification 顺序展开 taxonomy.json，挂上 _species/ 里的种与亚种。"""
    taxonomy = json.loads(TAXONOMY_JSON.read_text(encoding="utf-8"))
    families = {family["id"]: family for family in taxonomy["families"]}
    genera = {genus["id"]: genus for genus in taxonomy["genera"]}
    subfamily_ids = {sub["id"] for sub in taxonomy["subfamilies"]}

    species_by_genus: dict[str, list[tuple[str, dict[str, str]]]] = {}
    subspecies_by_parent: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for slug, fields in sorted(species_fields.items()):
        if not fields.get("latin"):
            continue
        rank = fields.get("rank") or "species"
        if rank == "subspecies":
            parent = fields.get("parent_slug") or ""
            subspecies_by_parent.setdefault(parent, []).append((slug, fields))
        else:
            species_by_genus.setdefault(fields.get("genus_id") or "", []).append((slug, fields))

    def sort_key(item: tuple[str, dict[str, str]]) -> str:
        return item[1].get("latin", "").lower()

    def taxon_entry(fields: dict[str, str], slug: str, rank: str,
                    genus_id: str, family_zh: str) -> dict:
        entry = {
            "l": fields.get("latin", ""),
            "z": fields.get("zh") or fields.get("title", ""),
            "r": rank,
            "h": genus_id,
        }
        if family_zh:
            entry["f"] = family_zh
        names = expand_synonyms(species_synonyms.get(slug) or [])
        if names:
            entry["s"] = " ; ".join(names)
        # 产地类字段：让科 / 亚科 / 属页的局部检索也能按「模式产地 / 分布」查种
        for key, field in (("dz", "distribution_zh"), ("de", "distribution_en"),
                           ("t", "type_locality"), ("sl", "synonym_localities")):
            value = clean(fields.get(field))
            if value:
                entry[key] = value
        entry["p"] = slug
        return entry

    def genus_block(genus_id: str, family_zh: str) -> None:
        genus = genera.get(genus_id)
        if not genus:
            return
        entries.append({
            "l": genus["latin"],
            "z": genus["zh"],
            "r": "属",
            "h": genus_id,
            "f": family_zh,
            "u": "/genus/%s/" % genus_id,
        })
        for slug, fields in sorted(species_by_genus.get(genus_id) or [], key=sort_key):
            entries.append(taxon_entry(fields, slug, "种", genus_id, family_zh))
            for sub_slug, sub_fields in sorted(subspecies_by_parent.get(slug) or [], key=sort_key):
                entries.append(taxon_entry(sub_fields, sub_slug, "亚种", genus_id, family_zh))

    entries: list[dict] = []
    for clade in taxonomy["clades"]:
        entries.append({
            "l": clade["latin"],
            "z": clade["zh"],
            "r": "支系",
            "h": clade["id"],
            "u": "/list/#%s" % clade["id"],
            "c": clade["zh"],
        })

    for clade in taxonomy["clades"]:
        for family_id in clade["families"]:
            family = families.get(family_id)
            if not family:
                continue
            family_zh = family["zh"]
            entries.append({
                "l": family["latin"],
                "z": family_zh,
                "r": "科",
                "h": family_id,
                "u": "/family/%s/" % family_id,
            })
            subfamilies = [sub for sub in taxonomy["subfamilies"] if sub["family"] == family_id]
            for sub in sorted(subfamilies, key=lambda item: item["latin"].lower()):
                entries.append({
                    "l": sub["latin"],
                    "z": sub["zh"],
                    "r": "亚科",
                    "h": sub["id"],
                    "f": family_zh,
                    "u": "/subfamily/%s/" % sub["id"],
                })
                for genus_id in sub["genera"]:
                    genus_block(genus_id, family_zh)
            for genus_id in family["genera"]:
                genus = genera.get(genus_id)
                if genus and (genus.get("subfamily") or "") in subfamily_ids:
                    continue
                genus_block(genus_id, family_zh)

    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="构建 search-index.json")
    parser.add_argument("--write", action="store_true", help="写入 search-index.json")
    parser.add_argument("--check", action="store_true", help="校验磁盘索引与生成结果一致")
    parser.add_argument("--no-enrich", action="store_true", help="跳过拼音 / 繁体字段")
    args = parser.parse_args()

    if not TAXONOMY_JSON.is_file():
        sys.exit(f"error: 找不到 {TAXONOMY_JSON.name}，先跑 _tools/extract_taxon_data.py")

    species_fields: dict[str, dict[str, str]] = {}
    species_synonyms: dict[str, list[str]] = {}
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path)
        slug = path.stem
        species_fields[slug] = fm
        synonyms = parse_synonyms(path)
        if synonyms:
            species_synonyms[slug] = synonyms

    entries = build(species_fields, species_synonyms)

    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["r"]] = counts.get(entry["r"], 0) + 1

    # 自检（不写死任何数量，数据增删后照样通过）：
    #   1) 种、亚种条目数必须与 _species/ 下的页面数一致；
    #   2) 每条种/亚种记录所属的属必须能在名录标题里找到对应锚点。
    expected = {"种": 0, "亚种": 0}
    for fields in species_fields.values():
        rank = RANK_BY_FRONT_MATTER.get(fields.get("rank", ""))
        if rank in expected:
            expected[rank] += 1
    for rank, total in expected.items():
        if counts.get(rank, 0) != total:
            sys.exit(f"error: {rank}条目 {counts.get(rank, 0)} 与 _species/ 页面数 {total} 不一致")
    genus_anchors = {entry["h"] for entry in entries if entry["r"] == "属"}
    missing = [entry["l"] for entry in entries
               if entry["r"] in ("种", "亚种") and entry["h"] not in genus_anchors]
    if missing:
        sys.exit(f"error: {len(missing)} 条记录找不到属锚点，例如：{'、'.join(missing[:5])}")

    if not args.no_enrich:
        pinyin_fn, traditional_fn = build_enrichers()
        cache: dict = {}
        entries = [enrich(dict(entry), pinyin_fn, traditional_fn, cache) for entry in entries]

    payload = json.dumps(entries, ensure_ascii=False, separators=(",", ":"))

    enriched = sum(1 for entry in entries if "py" in entry)
    print(
        f"条目 {len(entries)}（" + " / ".join(f"{k} {v}" for k, v in counts.items()) + "）"
        f"，拼音 {enriched}，繁体 {sum(1 for e in entries if 'zt' in e)}，"
        f"次异名 {sum(1 for e in entries if 's' in e)}，字节 {len(payload.encode('utf-8'))}"
    )

    if args.check:
        if not INDEX_JSON.is_file():
            sys.exit(f"error: {INDEX_JSON.name} 不存在")
        on_disk = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
        if on_disk == entries:
            print("校验通过：磁盘索引与生成结果一致")
            return 0
        print("校验失败：磁盘索引与生成结果不一致（用 --write 更新）", file=sys.stderr)
        return 1

    if args.write:
        INDEX_JSON.write_text(payload, encoding="utf-8")
        print(f"已写入 {INDEX_JSON.name}")
    else:
        print("未写入（加 --write 写入文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())