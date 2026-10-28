#!/usr/bin/env python3
"""构建名录站内搜索索引 search-index.json（含拼音、繁体字段）。

索引条目字段（按顺序输出）：
  l  拉丁学名 / 拉丁类群名
  z  中文名（种、亚种为中文正名）
  r  阶元：支系 / 科 / 亚科 / 属 / 种 / 亚种
  h  所属属（或类群自身）的锚点 id，用于回跳 /list/#<h>
  s  次异名（仅种、亚种；以 " ; " 分隔；无则省略）
  p  物种页 slug（仅种、亚种），用于跳转 /species/<p>/
  py 中文名的拼音连写（无声调，仅小写字母），供拼音检索
  pi 中文名的拼音首字母连写，供首字母检索
  zt 中文名的繁体写法（OpenCC s2t），供繁体检索

数据来源（不引入任何外部数据）：
  list.md                  类群标题 <h2>~<h5> 与种/亚种条目（条目顺序 = 页面顺序）
  _species/*.md            亚种条目的中文名 / 层级 / 次异名（次异名取页面「## 次异名」小节的斜体名）

拼音与繁体字段为可选增强：
  pip install pypinyin opencc-python-reimplemented
缺少依赖时照常生成基础字段（l z r h s p），并在 stderr 提示，退出码仍为 0。
站点部署时由 CI 安装依赖后重新生成，部署后的索引含拼音与繁体字段。
脚本自带自检：种/亚种条目数须与 _species/ 页面数一致，且每条记录都能在名录标题里找到属锚点，
因此增删物种后无需改动脚本。

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
LIST_MD = ROOT / "list.md"
SPECIES_DIR = ROOT / "_species"
INDEX_JSON = ROOT / "search-index.json"

RANK_BY_LEVEL = {2: "支系", 3: "科", 4: "亚科", 5: "属"}
# _species front matter 的 rank 写作英文 species / subspecies
RANK_BY_FRONT_MATTER = {"species": "种", "subspecies": "亚种"}
SKIP_IDS = {"toc", "references"}

HEADING_RE = re.compile(r'^<h([2-5]) id="([^"]+)">(.+?)</h[2-5]>\s*$')
TITLE_SPLIT_RE = re.compile(r"^([^\x00-\x7f][^\x00-\x7f\s]*)\s+([\x00-\x7f].*)$")
SPECIES_RE = re.compile(
    r"^(?:\\\*)?\[\*(?P<latin>[^*]+)\* (?P<zh>[^\]]+?)\]"
    r"\(\{\{ site\.base_url \}\}/species/(?P<slug>[^/]+)/\)\s*$"
)
SYNONYM_RE = re.compile(r"^\d+\.\s+\*(?P<name>[^*]+)\*")
FM_RE = re.compile(r'^(?P<key>[a-z_]+):\s*(?P<value>.*?)\s*$')


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


SUBGENUS_RE = re.compile(r"^(?P<genus>[A-Z][a-z]+) \((?P<subgenus>[A-Za-z]+)\) (?P<rest>[a-z].*)$")


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


def split_heading_title(text: str) -> tuple[str, str]:
    """把「中文名 LATIN」标题拆成中文名与拉丁名。"""
    m = TITLE_SPLIT_RE.match(text.strip())
    if not m:
        sys.exit(f"error: 无法拆分标题：{text!r}")
    return m.group(1), m.group(2).strip()


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

def build(species_fields: dict[str, dict[str, str]], species_synonyms: dict[str, list[str]]) -> list[dict]:
    entries: list[dict] = []
    genus_id = ""
    current: dict[str, dict] = {}  # parent_slug -> [subspecies entries]
    for path, fm in sorted(species_fields.items()):
        if fm.get("rank") == "subspecies":
            current.setdefault(fm.get("parent_slug", ""), []).append(
                {
                    "l": fm.get("latin", ""),
                    "z": fm.get("zh", ""),
                    "r": "亚种",
                    "h": fm.get("genus_id", ""),
                }
            )

    # 支系（h2）条目统一排在最前，其余按页面顺序：与页面目录一致，便于检索结果排序稳定
    for line in LIST_MD.read_text(encoding="utf-8").splitlines():
        heading = HEADING_RE.match(line)
        if heading and heading.group(1) == "2" and heading.group(2) not in SKIP_IDS:
            zh, latin = split_heading_title(heading.group(3))
            entries.append({"l": latin, "z": zh, "r": RANK_BY_LEVEL[2], "h": heading.group(2)})

    for line in LIST_MD.read_text(encoding="utf-8").splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            level, anchor, title = int(heading.group(1)), heading.group(2), heading.group(3)
            if anchor in SKIP_IDS or level == 2:
                continue
            zh, latin = split_heading_title(title)
            entries.append({"l": latin, "z": zh, "r": RANK_BY_LEVEL[level], "h": anchor})
            if level == 5:
                genus_id = anchor
            continue

        species = SPECIES_RE.match(line)
        if not species:
            continue
        latin, zh, slug = species.group("latin"), species.group("zh").strip(), species.group("slug")
        entry: dict = {"l": latin, "z": zh, "r": "种", "h": genus_id}
        synonyms = expand_synonyms(species_synonyms.get(slug) or [])
        if synonyms:
            entry["s"] = " ; ".join(synonyms)
        entry["p"] = slug
        entries.append(entry)

        for sub in sorted(current.get(slug, []), key=lambda e: e["l"]):
            sub_entry = dict(sub)
            sub_synonyms = expand_synonyms(species_synonyms.get(sub["l"].lower().replace(" ", "-")) or [])
            if sub_synonyms:
                sub_entry["s"] = " ; ".join(sub_synonyms)
            sub_entry["p"] = sub["l"].lower().replace(" ", "-")
            entries.append(sub_entry)

    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="构建 search-index.json")
    parser.add_argument("--write", action="store_true", help="写入 search-index.json")
    parser.add_argument("--check", action="store_true", help="校验磁盘索引与生成结果一致")
    parser.add_argument("--no-enrich", action="store_true", help="跳过拼音 / 繁体字段")
    args = parser.parse_args()

    if not LIST_MD.is_file():
        sys.exit(f"error: 找不到 {LIST_MD.name}")

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
