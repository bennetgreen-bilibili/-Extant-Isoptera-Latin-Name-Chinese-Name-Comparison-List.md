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
 11. 命名差异看板产物自洽（条数、CSV 列数、公开副本与 _data 副本一致、
     「名称差异逐对归并」的关系/方向/接收名/补录计数与物种页索引一致、外链 URL 不含空白/引号/锚点残渣）
 12. 「依外部权威库补录的异名」链路一致：_species 的 authority_synonym_* 字段逐条对齐，
     看板的 recorded 标记/计数/反查索引与物种页数据一致，且 search-index.json 能按异名命中；
     之后条目编号顺延（原 12/13）
 13. 订阅源与版本记录齐备：feed.xml / feed.json / opensearch.xml / changelog.atom、
     三语 /changelog/ 页面；sitemap.txt 收录版本记录页但不收录订阅源（只收 HTML 页面）
 14. 全局搜索浮层（#search-overlay）初始 hidden 且样式里有 [hidden] 兜底，
     不会一进页面就常显、关不掉把整站遮住

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
NAME_SYN_CSV = ROOT / "downloads" / "isoptera-synonym-pairs.csv"
# 外链必须是干净的绝对 URL：行尾注释、HTML 引号或 <...> 占位符被拼进来时，
# 页面上「异名 / 接受名」的链接会指向坏地址，甚至提前闭合标签把整格 HTML 弄坏。
BAD_URL_RE = re.compile(r"[\s\"'<>]|#")
OCCURRENCE = ROOT / "_data" / "occurrence_summary.json"
I18N = ROOT / "_data" / "i18n.yml"
CHANGELOG_DATA = ROOT / "_data" / "changelog.json"
CHANGELOG_ATOM = ROOT / "changelog.atom"
# 根目录订阅源页面：permalink 必须与线上路径一致，且用 sitemap: false 挡掉 sitemap.xml
FEED_PAGES = {
    "feed.xml": "/feed.xml",
    "feed.json": "/feed.json",
    "opensearch.xml": "/opensearch.xml",
}
# 三语版本记录页：permalink 必须与 sitemap.txt 收录的 URL 一致
CHANGELOG_PAGES = {
    "changelog.md": "/changelog/",
    "en/changelog.md": "/en/changelog/",
    "es/changelog.md": "/es/changelog/",
}
CHANGELOG_VERSIONS = tuple(sorted(CHANGELOG_PAGES.values()))
# 订阅源 / Atom 是静态产物，不是 HTML 页面，不应出现在 sitemap.txt 里
NON_HTML_ARTIFACTS = ("feed.xml", "feed.json", "opensearch.xml", "changelog.atom")
CHANGELOG_VERSION_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
JSONFEED_VERSION = "https://jsonfeed.org/version/1.1"

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


AUTHORITY_SOURCE_CODES = {"gbif", "col", "bsf"}


def check_authority_synonym_fields(path: Path, fields: dict) -> None:
    """「依外部权威库补录的异名」：条数 / 模式产地 / 来源三个列表必须逐条对齐。

    这些字段写在接受名的 _species 页里，是「把异名记录到对应的接收名下面」的落地数据；
    条数对不上会让物种页渲染出错位的模式产地，也会让看板统计口径失真。
    """
    rel = path.relative_to(ROOT).as_posix()
    names = [x for x in (fields.get("authority_synonyms") or "").split(";") if x.strip()]
    if not names:
        for key in ("authority_synonym_count", "authority_synonym_localities", "authority_synonym_sources"):
            if fields.get(key):
                err(rel, "有 " + key + " 却没有 authority_synonyms")
                break
        return
    try:
        count = int(fields.get("authority_synonym_count") or 0)
    except ValueError:
        count = -1
    if count != len(names):
        err(rel, "authority_synonym_count=%r 与 authority_synonyms 条数 %d 不一致"
            % (fields.get("authority_synonym_count"), len(names)))
    localities = [x for x in (fields.get("authority_synonym_localities") or "").split(";") if x.strip()]
    if len(localities) != len(names):
        err(rel, "authority_synonym_localities 条数 %d 与 authority_synonyms 条数 %d 不一致"
            % (len(localities), len(names)))
    sources = [x for x in (fields.get("authority_synonym_sources") or "").split(";") if x.strip()]
    if len(sources) != len(names):
        err(rel, "authority_synonym_sources 条数 %d 与 authority_synonyms 条数 %d 不一致"
            % (len(sources), len(names)))
    for value in sources:
        for code in re.split(r"[,;]", value):
            code = code.strip().lower()
            if code and code not in AUTHORITY_SOURCE_CODES:
                err(rel, "authority_synonym_sources 含未知来源代码：" + code)


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
        check_authority_synonym_fields(path, fields)
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


def check_name_issue_urls(where: str, url: str) -> None:
    if url and BAD_URL_RE.search(url):
        err(where, "外链 URL 不干净（疑似把 _config.yml 行尾注释拼进链接）：" + url[:120])


def check_name_issues(fields_by_slug: dict) -> None:
    for path in (NAME_ISSUES, NAME_ISSUES_PUBLIC, NAME_ISSUES_CSV, NAME_SYN_CSV):
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
        check_name_issue_urls("_data/name_issues.json", row.get("url") or "")
        check_name_issue_urls("_data/name_issues.json", row.get("accepted_url") or "")
        if row.get("accepted") and not row.get("accepted_latin"):
            err("_data/name_issues.json", "有接受名却没有 accepted_latin（异名没记录到接收名下面）：" + row["latin"])
            break
        if row.get("accepted_slug") and not (SPECIES_DIR / (row["accepted_slug"] + ".md")).is_file():
            err("_data/name_issues.json", "accepted_slug 找不到对应物种页：" + row["accepted_slug"])
            break
    if read(NAME_ISSUES) != read(NAME_ISSUES_PUBLIC):
        err("data/name-issues.json", "公开副本与 _data/name_issues.json 不一致")
    header = read(NAME_ISSUES_CSV).splitlines()[0]
    if len(header.split(",")) != 17:
        err("downloads/isoptera-name-issues.csv", "表头列数为 %d，应为 17" % len(header.split(",")))
    syn_header = read(NAME_SYN_CSV).splitlines()[0]
    if len(syn_header.split(",")) != 15:
        err("downloads/isoptera-synonym-pairs.csv", "表头列数为 %d，应为 15" % len(syn_header.split(",")))

    # 名称差异逐对归并：关系 / 方向 / 接收名 / 补录 必须与缓存和 _species 数据一致
    counts = meta.get("counts") or {}
    pairs = data.get("synonym_pairs") or []
    authority = data.get("species_authority") or {}
    conflicts = [row for row in issues if row.get("group") == "conflict"]
    if counts.get("conflict_pairs") != len(pairs):
        err("_data/name_issues.json", "counts.conflict_pairs=%s 与 synonym_pairs 对数 %d 不一致"
            % (counts.get("conflict_pairs"), len(pairs)))
    if counts.get("conflict_species") != len({row.get("latin") for row in conflicts}):
        err("_data/name_issues.json", "counts.conflict_species 与名称差异涉及的本站名个数不一致")
    relation_total = {"synonym": 0, "combination": 0}
    direction_total = {"external": 0, "site": 0, "disputed": 0}
    recordable = recorded = disputed = 0
    expected_reverse = {}
    pair_keys = set()
    for pair in pairs:
        our, external = pair.get("our") or {}, pair.get("external") or {}
        if not our.get("latin") or not external.get("latin") or not pair.get("sources"):
            err("_data/name_issues.json", "名称差异对缺少本站名/外部名/来源：" + str(pair)[:120])
            break
        key = (our["latin"], external["latin"])
        if key in pair_keys:
            err("_data/name_issues.json", "名称差异对重复：%s ↔ %s" % key)
        pair_keys.add(key)
        for link in (pair.get("our_links") or []) + (pair.get("external_links") or []):
            check_name_issue_urls("_data/name_issues.json", link.get("url") or "")
        relation, direction = pair.get("relation"), pair.get("direction")
        if relation not in ("synonym", "combination"):
            err("_data/name_issues.json", "未知关系类型：%r（%s）" % (relation, our["latin"]))
            continue
        if direction not in ("external", "site", "disputed"):
            err("_data/name_issues.json", "未知方向：%r（%s）" % (direction, our["latin"]))
            continue
        relation_total[relation] += 1
        direction_total[direction] += 1
        receiving = pair.get("receiving") or {}
        if direction == "external":
            if receiving.get("latin") != external["latin"]:
                err("_data/name_issues.json", "方向 external 的接收名应为外部接受名：%s" % our["latin"])
        elif direction == "site":
            if receiving.get("latin") != our["latin"] or not receiving.get("in_site"):
                err("_data/name_issues.json", "方向 site 的接收名应为本站名：%s" % our["latin"])
        elif receiving:
            err("_data/name_issues.json", "方向待定的对不应有接收名：%s" % our["latin"])
        if receiving.get("slug") and not (SPECIES_DIR / (receiving["slug"] + ".md")).is_file():
            err("_data/name_issues.json", "接收名的 slug 找不到物种页：" + receiving["slug"])
        if pair.get("disputed"):
            disputed += 1
        if pair.get("recordable"):
            recordable += 1
        if pair.get("recorded"):
            recorded += 1
            # 已补录必须方向明确、真异名，且真的写进了接受名物种页的 authority_synonyms
            if direction != "external" or relation != "synonym":
                err("_data/name_issues.json", "已补录的对必须是「真异名 + 外部库名为接收名」：%s" % our["latin"])
            accepted_slug = receiving.get("slug")
            accepted_fields = fields_by_slug.get(accepted_slug) if accepted_slug else None
            accepted_auth = [
                item.strip() for item in ((accepted_fields or {}).get("authority_synonyms") or "").split(";")
                if item.strip()
            ]
            if not any(item == our["latin"] or item.startswith(our["latin"] + " ") for item in accepted_auth):
                err("_data/name_issues.json",
                    "标为已补录但接受名物种页的 authority_synonyms 里没有它：%s" % our["latin"])
            if our.get("slug") and accepted_slug:
                expected_reverse[our["slug"]] = accepted_slug
    for name, actual in (("pairs_relation_synonym", relation_total["synonym"]),
                         ("pairs_relation_combination", relation_total["combination"]),
                         ("pairs_direction_external", direction_total["external"]),
                         ("pairs_direction_site", direction_total["site"]),
                         ("pairs_direction_disputed", direction_total["disputed"]),
                         ("pairs_disputed", disputed), ("pairs_recordable", recordable),
                         ("pairs_recorded", recorded)):
        if counts.get(name) != actual:
            err("_data/name_issues.json", "counts.%s=%s 与逐对统计 %d 不一致" % (name, counts.get(name), actual))
    issue_pairs = {(row.get("latin"), row.get("accepted_latin")) for row in conflicts if row.get("accepted_latin")}
    if issue_pairs != pair_keys:
        err("_data/name_issues.json", "名称差异条目与 synonym_pairs 不是一一对应：%s"
            % sorted(issue_pairs.symmetric_difference(pair_keys))[:3])
    for row in conflicts:
        pair = next((p for p in pairs
                     if (p["our"]["latin"], p["external"]["latin"]) == (row.get("latin"), row.get("accepted_latin"))), None)
        if pair and (row.get("relation"), row.get("direction"), bool(row.get("recorded"))) != (
                pair["relation"], pair["direction"], bool(pair["recorded"])):
            err("_data/name_issues.json", "条目的 relation/direction/recorded 与对不一致：%s" % row.get("latin"))
            break

    # 物种页索引（incoming / outgoing）必须与对一致、且 slug 都有对应物种页
    expected_authority = {}
    for pair in pairs:
        if pair["direction"] == "external":
            receiving = pair.get("receiving") or {}
            slug = (receiving.get("slug") if receiving.get("in_site") else None)
            if slug:
                entry = expected_authority.setdefault(slug, {"incoming": set(), "outgoing": set()})
                entry["incoming"].add(pair["our"]["latin"])
        else:
            entry = expected_authority.setdefault(pair["our"]["slug"], {"incoming": set(), "outgoing": set()})
            entry["outgoing"].add(pair["external"]["latin"])
    for slug, expected in expected_authority.items():
        if not (SPECIES_DIR / (slug + ".md")).is_file():
            err("_data/name_issues.json", "species_authority 的 slug 找不到物种页：" + slug)
            continue
        actual = authority.get(slug) or {}
        incoming = {item.get("latin") for item in (actual.get("incoming") or [])}
        outgoing = {item.get("latin") for item in (actual.get("outgoing") or [])}
        if incoming != expected["incoming"] or outgoing != expected["outgoing"]:
            err("_data/name_issues.json", "species_authority[%s] 与对不一致" % slug)
    for slug in set(authority) - set(expected_authority):
        err("_data/name_issues.json", "species_authority 多出条目：" + slug)

    reverse = data.get("synonym_of_slug") or {}
    reverse_map = {slug: rec.get("accepted_slug") for slug, rec in reverse.items()}
    if reverse_map != expected_reverse:
        err("_data/name_issues.json", "synonym_of_slug 与已补录对不一致：%s"
            % sorted(set(reverse_map).symmetric_difference(expected_reverse))[:3])
    if expected_reverse and SEARCH_INDEX.is_file():
        entries = json.loads(read(SEARCH_INDEX))
        by_page = {entry.get("p"): entry for entry in entries if entry.get("p")}
        for pair in pairs:
            if not pair.get("recorded"):
                continue
            slug = (pair.get("receiving") or {}).get("slug")
            haystack = (by_page.get(slug) or {}).get("s") or ""
            if pair["our"]["latin"] not in haystack:
                err("search-index.json", "检索索引里 %s 没有记录异名 %s（名录搜索无法按次异名命中）"
                    % (slug, pair["our"]["latin"]))


def check_search_overlay() -> None:
    """全局搜索浮层：初始必须隐藏、且能正常关闭（否则整站被遮罩挡住、点 × 也没反应）。

    浮层用 hidden 属性做开关（assets/search-widget.js 只切 hidden）。但
    .search-overlay{display:flex} 是作者样式，会盖掉浏览器 UA 样式表里的
    [hidden]{display:none}；一旦缺少 !important 的 [hidden] 兜底规则，浮层一进页面
    就常显、close() 把 hidden 设回 true 也关不掉 —— 线上表现就是"弹窗跳在页面上无法
    关闭、网站无法使用"。
    """
    css_path = ROOT / "assets" / "custom.css"
    if not css_path.is_file():
        err("assets/custom.css", "全局搜索浮层的样式文件缺失")
        return
    # 浮层标签可能放在 _layouts 或 _includes 里：扫全部模板，找到 #search-overlay 的标签
    found = []
    for folder in ("_layouts", "_includes"):
        for path in sorted((ROOT / folder).glob("*.html")):
            text = read(path)
            for tag in re.findall(r'<div\b[^>]*\bid="search-overlay"[^>]*>', text):
                found.append((path.relative_to(ROOT).as_posix(), tag))
    if not found:
        err("_layouts/default.html", '找不到全局搜索浮层 #search-overlay 的标签')
    for where, tag in found:
        if not re.search(r"\shidden\b", tag):
            err(where, '浮层 #search-overlay 的初始状态必须是 hidden 属性（不能默认显示）')
    css = read(css_path)
    m = re.search(r"\.search-overlay\[hidden\]\s*\{([^}]*)\}", css)
    if not m:
        err("assets/custom.css", "缺少 .search-overlay[hidden] 兜底规则，浮层会一进页面就常显且关不掉")
    elif not re.search(r"display\s*:\s*none\s*!important", m.group(1)):
        err("assets/custom.css", ".search-overlay[hidden] 必须写 display:none!important（普通声明会被 .search-overlay 的 display:flex 按优先级压掉）")


def check_feeds_and_changelog(base_url: str) -> None:
    """订阅源与版本记录：静态产物、Jekyll 页面、sitemap.txt 三者必须互相对得上。"""
    # 1. 版本记录数据与 Atom feed（由 _tools/build_changelog.py 生成；是否最新由 validate.yml 重新生成后比对 git status）
    if not CHANGELOG_DATA.is_file():
        err("_data/changelog.json", "文件不存在（运行 python _tools/build_changelog.py --write）")
    else:
        try:
            data = json.loads(read(CHANGELOG_DATA))
        except Exception as exc:
            err("_data/changelog.json", "JSON 解析失败：" + str(exc)[:120])
        else:
            versions = data.get("versions") or []
            if not versions:
                err("_data/changelog.json", "versions 为空（应从 dataset/CHANGELOG.md 解析到至少一个版本）")
            for item in versions:
                version = str(item.get("version") or "")
                if not CHANGELOG_VERSION_RE.match(version):
                    err("_data/changelog.json", "版本号 %r 不是 YYYY.MM.DD 形式" % version)
    if not CHANGELOG_ATOM.is_file():
        err("changelog.atom", "文件不存在（运行 python _tools/build_changelog.py --write）")
    else:
        atom = read(CHANGELOG_ATOM)
        if not atom.startswith("<?xml"):
            err("changelog.atom", "文件不以 <?xml 开头")
        for tag in ("<feed", "<entry"):
            if tag not in atom:
                err("changelog.atom", "缺少 " + tag + " 元素")

    # 2. 根目录订阅源页面：必须留在根目录由 Jekyll 渲染，permalink 固定，且不进入 sitemap.xml
    for name, permalink in FEED_PAGES.items():
        path = ROOT / name
        if not path.is_file():
            err(name, "文件不存在")
            continue
        fields = parse_front_matter(path)
        if not fields:
            err(name, "front matter 缺失或未闭合")
            continue
        if fields.get("permalink") != permalink:
            err(name, "permalink 应为 %s，实际为 %r" % (permalink, fields.get("permalink")))
        if fields.get("sitemap") != "false":
            err(name, "缺少 sitemap: false（订阅源不应被 sitemap.xml 收录）")
    feed_json = ROOT / "feed.json"
    if feed_json.is_file():
        text = read(feed_json)
        if JSONFEED_VERSION not in text:
            err("feed.json", "缺少 JSON Feed 1.1 版本声明 " + JSONFEED_VERSION)
        if '"items"' not in text:
            err("feed.json", '缺少 "items" 数组')

    # 3. sitemap.txt：收录三语版本记录页，但不收录订阅源 / Atom 等非 HTML 产物
    if SITEMAP.is_file():
        urls = read(SITEMAP).splitlines()
        for rel in CHANGELOG_VERSIONS:
            if base_url + rel not in urls:
                err("sitemap.txt", "未收录版本记录页 " + rel)
        listed = [name for name in NON_HTML_ARTIFACTS if any(u.endswith("/" + name) for u in urls)]
        if listed:
            err("sitemap.txt", "不应收录非 HTML 产物：" + "、".join(listed))

    # 4. 三语版本记录页：permalink 必须与 sitemap.txt 里的 URL 一致
    for name, permalink in CHANGELOG_PAGES.items():
        path = ROOT / name
        if not path.is_file():
            err(name, "版本记录页不存在")
            continue
        fields = parse_front_matter(path)
        if not fields:
            err(name, "front matter 缺失或未闭合")
            continue
        if fields.get("permalink") != permalink:
            err(name, "permalink 应为 %s，实际为 %r" % (permalink, fields.get("permalink")))


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
    check_feeds_and_changelog(base_url)
    check_i18n()
    check_name_issues(fields_by_slug)
    check_search_overlay()

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

    print("校验通过：%d 个物种页、三语名录同构、计数一致、sitemap / i18n / 命名差异产物与订阅源 / 版本记录自洽（提醒 %d 条）" % (len(fields_by_slug), len(warnings)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
