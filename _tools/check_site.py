#!/usr/bin/env python3
"""站点与数据一致性校验：PR / 推送前的闸门（只读，不写文件）。

覆盖那些"坏了但不会报错、只会在线上悄悄错"的不变量：

  1. _config.yml 的 url + baseurl 与 base_url 一致；版本号与 dataset/metadata.json 一致
  2. 全部 JSON 可解析（_data/、data/、search-index.json、isoptera-data.json）
  3. 分布图产物与 occurrence_summary.json 一一对应（无孤儿 / 缺失），GeoJSON 合法
  4. _species/ front matter 必备字段齐全、slug 唯一
  5. 三语 list.md 同构：物种链接集合、标题锚点集合完全一致
  6. 名录页内部锚点全部有对应标题（不会点进去落空）
  7. 物种页面包屑 / 同属链接的 family_id、genus_id 都能在名录里找到
  8. 批次计数一致：_species 页数 = 检索索引种/亚种条数 = sitemap 物种 URL 数 = 名录物种链接数
  9. sitemap.txt 无重复、URL 以 base_url 开头、收录 /list/name-issues/ 三语页面
 10. _data/i18n.yml 三语 key 集合一致
 11. 命名差异看板产物自洽（条数、CSV 列数、公开副本与 _data 副本一致）

另外输出"提醒"级问题（不阻断）：中文正名重复、缺分布/模式产地、名录标题层级跳级。

用法：
  python _tools/check_site.py            # 只看错误与提醒
  python _tools/check_site.py --ci       # 额外输出 GitHub Actions 注解
  python _tools/check_site.py --quiet    # 只输出错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "_config.yml"
SPECIES_DIR = ROOT / "_species"
LIST_FILES = {"zh-CN": ROOT / "list.md", "en": ROOT / "en" / "list.md", "es": ROOT / "es" / "list.md"}
SITEMAP = ROOT / "sitemap.txt"
SEARCH_INDEX = ROOT / "search-index.json"
METADATA = ROOT / "dataset" / "metadata.json"
NAME_ISSUES = ROOT / "_data" / "name_issues.json"
NAME_ISSUES_PUBLIC = ROOT / "data" / "name-issues.json"
NAME_ISSUES_CSV = ROOT / "downloads" / "isoptera-name-issues.csv"
OCCURRENCE = ROOT / "_data" / "occurrence_summary.json"
I18N = ROOT / "_data" / "i18n.yml"

REQUIRED_FIELDS = ("latin", "zh", "rank", "family_zh", "family_latin", "family_id", "genus_id")
HEADING_RE = re.compile(r'<h([2-5]) id="([^"]+)">')
SPECIES_LINK_RE = re.compile(r"\{\{ site\.base_url \}\}/species/([^/\s\"]+)/")
ANCHOR_RE = re.compile(r"\]\(#([^)\s]+)\)")
HREF_ANCHOR_RE = re.compile(r'href="#([^"\s]+)"')
FM_RE = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<value>.*?)\s*$")
KNOWN_ANCHORS = {"references-doi"}

errors: list = []
warnings: list = []


def err(where: str, msg: str) -> None:
    errors.append((where, msg))


def warn(where: str, msg: str) -> None:
    warnings.append((where, msg))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").lstrip("\ufeff")


def check_config() -> str:
    text = read(CONFIG)
    values = {}
    for key in ("url", "baseurl", "base_url"):
        m = re.search(r"^" + key + r":\s*(.+?)\s*$", text, re.MULTILINE)
        if not m:
            err("_config.yml", "缺少 " + key)
            continue
        values[key] = m.group(1).strip().strip("'\"").rstrip("/")
    if len(values) == 3 and values["base_url"] != values["url"] + values["baseurl"]:
        err("_config.yml", "base_url 与 url + baseurl 不一致：%s != %s" % (values["base_url"], values["url"] + values["baseurl"]))
    m = re.search(r"^dataset:\s*\n(?:.*\n)*?\s{2}version:\s*\"?([^\"\n]+)\"?", text)
    if m and METADATA.is_file():
        meta_version = json.loads(read(METADATA)).get("version")
        if meta_version and m.group(1).strip() != meta_version:
            err("_config.yml", "site.dataset.version（%s）与 dataset/metadata.json（%s）不一致" % (m.group(1).strip(), meta_version))
    return values.get("base_url", "")


def check_json() -> None:
    for path in sorted(ROOT.glob("_data/*.json")) + sorted(ROOT.glob("data/*.json")):
        try:
            json.loads(read(path))
        except Exception as exc:
            err(path.relative_to(ROOT).as_posix(), "JSON 解析失败：" + str(exc)[:120])
    for path in (SEARCH_INDEX, ROOT / "isoptera-data.json"):
        if path.is_file():
            try:
                json.loads(read(path))
            except Exception as exc:
                err(path.name, "JSON 解析失败：" + str(exc)[:120])


def check_geo() -> None:
    if not OCCURRENCE.is_file():
        err("_data/occurrence_summary.json", "文件不存在")
        return
    summary = json.loads(read(OCCURRENCE))
    listed = set()
    for item in summary.get("families") or []:
        listed.add(item["file"])
    for item in summary.get("genera") or []:
        listed.add(item["file"])
    for item in (summary.get("species") or {}).values():
        listed.add(item["file"])
    disk = {p.relative_to(ROOT).as_posix() for p in (ROOT / "assets" / "geo").rglob("*.geojson")}
    missing = sorted(listed - disk)
    orphan = sorted(disk - listed)
    if missing:
        err("assets/geo", "%d 个 summary 引用但磁盘缺失的 GeoJSON，例如 %s" % (len(missing), missing[:3]))
    if orphan:
        err("assets/geo", "%d 个磁盘存在但 summary 未引用的 GeoJSON，例如 %s" % (len(orphan), orphan[:3]))
    for rel in sorted(listed & disk):
        try:
            json.loads(read(ROOT / rel))
        except Exception as exc:
            err(rel, "GeoJSON 解析失败：" + str(exc)[:80])


def parse_front_matter(path: Path) -> dict:
    text = read(path)
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fields = {}
    for line in text[4:end].splitlines():
        m = FM_RE.match(line)
        if not m:
            continue
        value = m.group("value")
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1].replace('\\"', '"')
        fields[m.group("key")] = value
    return fields


def check_species() -> tuple[dict, dict]:
    fields_by_slug = {}
    zh_names = {}
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fields = parse_front_matter(path)
        slug = path.stem
        if not fields:
            err(path.relative_to(ROOT).as_posix(), "front matter 缺失或未闭合")
            continue
        missing = [k for k in REQUIRED_FIELDS if not fields.get(k)]
        if missing:
            err(path.relative_to(ROOT).as_posix(), "缺少字段 " + "、".join(missing))
        if slug in fields_by_slug:
            err(path.relative_to(ROOT).as_posix(), "slug 重复")
        fields_by_slug[slug] = fields
        zh = fields.get("zh", "")
        if zh:
            zh_names.setdefault(zh, []).append(slug)
        if not fields.get("type_locality"):
            warn(path.relative_to(ROOT).as_posix(), "缺模式产地 type_locality")
        if not (fields.get("distribution_zh") or fields.get("distribution_en")):
            warn(path.relative_to(ROOT).as_posix(), "缺分布 distribution")
    dups = {k: v for k, v in zh_names.items() if len(v) > 1}
    for zh, slugs in sorted(dups.items()):
        warn("_species", "中文正名重复：%s（%s）" % (zh, "、".join(slugs)))
    return fields_by_slug, zh_names


def check_lists() -> tuple[dict, dict]:
    species_sets, heading_sets, ids_by_lang = {}, {}, {}
    zh_ids = set()
    for lang, path in LIST_FILES.items():
        if not path.is_file():
            err(path.relative_to(ROOT).as_posix(), "文件不存在")
            continue
        text = read(path)
        links = SPECIES_LINK_RE.findall(text)
        headings = HEADING_RE.findall(text)
        ids = {h[1] for h in headings}
        ids_by_lang[lang] = ids
        species_sets[lang] = set(links)
        heading_sets[lang] = ids
        # 内部锚点：](#id) 与 href="#id"
        anchors = set(ANCHOR_RE.findall(text)) | set(HREF_ANCHOR_RE.findall(text))
        dangling = sorted(a for a in anchors if a not in ids and a not in KNOWN_ANCHORS)
        if dangling:
            err(path.relative_to(ROOT).as_posix(), "%d 个锚点找不到目标，例如 %s" % (len(dangling), dangling[:3]))
        # 标题层级跳级（h3 -> h5，无 h4）：已知结构（无亚科的科直接进属），只提醒
        seq = [(int(lvl), anchor) for lvl, anchor in headings]
        skips = 0
        for i in range(1, len(seq)):
            if seq[i][0] - seq[i - 1][0] >= 2:
                skips += 1
        if skips:
            warn(path.relative_to(ROOT).as_posix(), "%d 处标题层级跳级（h3→h5，无亚科的科），axe heading-order 会提示" % skips)
        if lang == "zh-CN":
            zh_ids = ids
    if len(species_sets) == 3:
        base = species_sets["zh-CN"]
        for lang in ("en", "es"):
            missing = sorted(base - species_sets[lang])
            extra = sorted(species_sets[lang] - base)
            if missing or extra:
                err(LIST_FILES[lang].relative_to(ROOT).as_posix(),
                    "与中文名录的物种链接不一致：缺少 %d、多出 %d（示例 %s）" % (len(missing), len(extra), (missing + extra)[:3]))
    if len(heading_sets) == 3:
        base = heading_sets["zh-CN"]
        for lang in ("en", "es"):
            missing = sorted(base - heading_sets[lang])
            extra = sorted(heading_sets[lang] - base)
            if missing or extra:
                err(LIST_FILES[lang].relative_to(ROOT).as_posix(),
                    "与中文名录的标题锚点不一致：缺少 %d、多出 %d（示例 %s）" % (len(missing), len(extra), (missing + extra)[:3]))
    # 物种页面包屑 / 同属链接的锚点必须存在
    bad = 0
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fields = parse_front_matter(path)
        for key in ("family_id", "genus_id"):
            anchor = fields.get(key)
            if anchor and anchor not in zh_ids:
                bad += 1
                if bad <= 5:
                    err(path.relative_to(ROOT).as_posix(), key + "=" + anchor + " 在名录中找不到锚点")
    if bad > 5:
        err("_species", "共 %d 处分类锚点在名录中不存在" % bad)
    return species_sets, ids_by_lang


def check_counts(fields_by_slug: dict, species_sets: dict) -> None:
    page_count = len(fields_by_slug)
    index = json.loads(read(SEARCH_INDEX))
    index_species = sum(1 for e in index if e.get("r") in ("种", "亚种"))
    sitemap_urls = read(SITEMAP).splitlines()
    sitemap_species = [u for u in sitemap_urls if "/species/" in u]
    zh_links = len(species_sets.get("zh-CN", set()))
    per_rank = {}
    for fields in fields_by_slug.values():
        per_rank[fields.get("rank")] = per_rank.get(fields.get("rank"), 0) + 1
    want = {"种": 0, "亚种": 0}
    for fields in fields_by_slug.values():
        if fields.get("rank") == "species":
            want["种"] += 1
        elif fields.get("rank") == "subspecies":
            want["亚种"] += 1
    # 名录页只列种（亚种挂在 _species 与 species 页，不单独出现在名录列表里）
    if zh_links != want["种"]:
        err("list.md", "物种链接数 %d 与 front matter 中 rank=species 的页面数 %d 不一致" % (zh_links, want["种"]))
    if len(sitemap_species) != page_count:
        err("sitemap.txt", "物种 URL 数 %d 与 _species 页面数 %d 不一致" % (len(sitemap_species), page_count))
    if index_species != page_count:
        err("search-index.json", "种/亚种条数 %d 与 _species 页面数 %d 不一致" % (index_species, page_count))


def check_sitemap(base_url: str) -> None:
    if not SITEMAP.is_file():
        err("sitemap.txt", "文件不存在")
        return
    urls = read(SITEMAP).splitlines()
    if len(urls) != len(set(urls)):
        err("sitemap.txt", "存在重复 URL")
    bad = [u for u in urls if not u.startswith(base_url + "/")]
    if bad:
        err("sitemap.txt", "%d 个 URL 不以 base_url 开头，例如 %s" % (len(bad), bad[:3]))
    for rel in ("/list/name-issues/", "/en/list/name-issues/", "/es/list/name-issues/"):
        if base_url + rel not in urls:
            err("sitemap.txt", "未收录新页面 " + rel)
    for page in ("name-issues.md", "en/name-issues.md", "es/name-issues.md"):
        if not (ROOT / page).is_file():
            err(page, "命名差异看板页面缺失")


def check_i18n() -> None:
    if not I18N.is_file():
        return
    per_lang: dict = {}
    current = None
    for line in read(I18N).splitlines():
        m = re.match(r"^([a-z]{2})(?:-[A-Z]{2})?:\s*$", line)
        if m:
            current = line.split(":")[0].strip()
            per_lang[current] = set()
            continue
        if current and re.match(r"^\s{2}[a-z_]+:", line):
            per_lang[current].add(line.strip().split(":")[0])
    if len(per_lang) < 2:
        return
    langs = sorted(per_lang)
    base = per_lang[langs[0]]
    for lang in langs[1:]:
        missing = sorted(base - per_lang[lang])
        extra = sorted(per_lang[lang] - base)
        if missing or extra:
            err("_data/i18n.yml", "%s 与 %s 的 key 不一致：缺少 %s、多出 %s" % (langs[0], lang, missing[:5], extra[:5]))


def check_name_issues() -> None:
    for path in (NAME_ISSUES, NAME_ISSUES_PUBLIC, NAME_ISSUES_CSV):
        if not path.is_file():
            err(path.relative_to(ROOT).as_posix(), "文件不存在（运行 .github/workflows/build_name_issues.py --write）")
            return
    data = json.loads(read(NAME_ISSUES))
    meta = data.get("meta") or {}
    issues = data.get("issues") or []
    total = (meta.get("counts") or {}).get("total")
    if total != len(issues):
        err("_data/name_issues.json", "meta.counts.total=%s 与 issues 条数 %d 不一致" % (total, len(issues)))
    by_group = (meta.get("counts") or {}).get("by_group") or {}
    if sum(by_group.values()) != len(issues):
        err("_data/name_issues.json", "by_group 合计 %d 与 issues 条数 %d 不一致" % (sum(by_group.values()), len(issues)))
    for row in issues:
        if not row.get("latin") or not row.get("source") or not row.get("group") or not row.get("kind"):
            err("_data/name_issues.json", "条目缺少必要字段：" + str(row)[:120])
            break
    if read(NAME_ISSUES) != read(NAME_ISSUES_PUBLIC):
        err("data/name-issues.json", "公开副本与 _data/name_issues.json 不一致")
    header = read(NAME_ISSUES_CSV).splitlines()[0]
    if len(header.split(",")) != 17:
        err("downloads/isoptera-name-issues.csv", "表头列数为 %d，应为 17" % len(header.split(",")))


def main() -> int:
    parser = argparse.ArgumentParser(description="站点与数据一致性校验")
    parser.add_argument("--ci", action="store_true", help="输出 GitHub Actions 注解")
    parser.add_argument("--quiet", action="store_true", help="只输出错误")
    args = parser.parse_args()

    if not (ROOT / "list.md").is_file():
        sys.exit("error: 请在仓库根目录运行（找不到 list.md）")

    base_url = check_config()
    check_json()
    check_geo()
    fields_by_slug, _ = check_species()
    species_sets, _ = check_lists()
    check_counts(fields_by_slug, species_sets)
    check_sitemap(base_url)
    check_i18n()
    check_name_issues()

    if args.ci:
        for where, msg in errors:
            print("::error file=%s::%s" % (where, msg))
        for where, msg in warnings:
            print("::warning file=%s::%s" % (where, msg))

    if warnings and not args.quiet:
        print("提醒 %d 条（不阻断）：" % len(warnings))
        for where, msg in warnings[:15]:
            print("  - %s：%s" % (where, msg))
        if len(warnings) > 15:
            print("  …… 另有 %d 条" % (len(warnings) - 15))

    if errors:
        print("\n错误 %d 条：" % len(errors))
        for where, msg in errors[:40]:
            print("  [ERROR] %s: %s" % (where, msg))
        if len(errors) > 40:
            print("  …… 另有 %d 条" % (len(errors) - 40))
        return 1

    print("校验通过：%d 个物种页、三语名录同构、计数一致、sitemap / i18n / 命名差异产物自洽（提醒 %d 条）" % (len(fields_by_slug), len(warnings)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
