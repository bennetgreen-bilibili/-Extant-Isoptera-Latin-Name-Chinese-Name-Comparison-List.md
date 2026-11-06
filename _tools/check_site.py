#!/usr/bin/env python3
"""站点与数据一致性校验：PR / 推送前的闸门（只读，不写文件）。

覆盖那些"坏了但不会报错、只会在线上悄悄错"的不变量：

  1. _config.yml 的 url + baseurl 与 base_url 一致；版本号与 dataset/metadata.json 一致
  2. 全部 JSON 可解析（_data/、data/、search-index.json、isoptera-data.json）
  3. 分布图产物与索引一一对应（无孤儿 / 缺失），GeoJSON 合法：索引 = occurrence_summary.json
     （科 / 属 / 种）+ subfamily_maps.json（亚科）；实现见 _tools/check_geo.py
  4. _species/ front matter 必备字段齐全、slug 唯一
  5. 三语 /list/ 索引页同构：标题锚点集合（支系 + by-family + references）完全一致，
     且与 _data/taxonomy.json 的支系 id 对齐；索引页不再含 /species/ 链接
  6. 索引页内部锚点全部有对应标题（不会点进去落空）；13 科都有 /family/<id>/ 入口
  7. 层级页面齐备：taxonomy.json 里每个科 / 亚科 / 属都有对应页面，属页 front matter
     的 family_id 在科表内，属页列出的物种 slug 都存在，且每个物种页都出现在其属页上
  8. 批次计数一致：_species 页数 = 检索索引种/亚种条数 = sitemap 物种 URL 数；
     检索索引的属条目数 = taxonomy.json 的属数
  8b. /en/list/sections/、/es/list/sections/ 覆盖全部 13 科 + 18 亚科的锚点
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
 15. 物种页「同属其他种」区块带 data-pagefind-ignore：该区块只是内链，不进 Pagefind
     全文索引，否则一个属的 40 个种名会塞进属内每一页，搜一个种名冒出整属的无关结果
  16. 文献检索器：三语 /papers/ 页面、sitemap、papers.json / papers-index.json
      字节一致、属覆盖与摘要字段自洽
  17. 摘要翻译术语表（_data/translation_glossary.yml）：结构、字段、重复项与 post 守卫，
      且三语 /papers/ 页面都接入了 _includes/papers-glossary.html

另外输出"提醒"级问题（不阻断）：中文正名重复、缺分布/模式产地。

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

# 分布图产物的不变量只有一份实现（_tools/check_geo.py），这里只负责把结果转成
# 本脚本的 errors 列表与 --ci 注解，避免两处各写一遍后再次漂移。
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_geo as geo_artifacts  # noqa: E402  （必须先插入 sys.path 才能导入同级脚本）

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "_config.yml"
SPECIES_DIR = ROOT / "_species"
LIST_FILES = {"zh-CN": ROOT / "list.md", "en": ROOT / "en" / "list.md", "es": ROOT / "es" / "list.md"}
SITEMAP = ROOT / "sitemap.txt"
SEARCH_INDEX = ROOT / "search-index.json"
TAXONOMY_JSON = ROOT / "_data" / "taxonomy.json"
SECTION_PAGES = {"en": ROOT / "en" / "list" / "sections.md", "es": ROOT / "es" / "list" / "sections.md"}
PAPERS_DATA = ROOT / "_data" / "papers.json"
PAPERS_PUBLIC = ROOT / "papers-index.json"
PAPERS_PAGES = (
    ("papers.md", "/papers/"),
    ("en/papers.md", "/en/papers/"),
    ("es/papers.md", "/es/papers/"),
)
METADATA = ROOT / "dataset" / "metadata.json"
NAME_ISSUES = ROOT / "_data" / "name_issues.json"
NAME_ISSUES_PUBLIC = ROOT / "data" / "name-issues.json"
NAME_ISSUES_CSV = ROOT / "downloads" / "isoptera-name-issues.csv"
NAME_SYN_CSV = ROOT / "downloads" / "isoptera-synonym-pairs.csv"
# 外链必须是干净的绝对 URL：行尾注释、HTML 引号或 <...> 占位符被拼进来时，
# 页面上「异名 / 接受名」的链接会指向坏地址，甚至提前闭合标签把整格 HTML 弄坏。
BAD_URL_RE = re.compile(r"[\s\"'<>]|#")
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
HEADING_RE = re.compile(r'<h([2-6]) id="([^"]+)"')
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
    """分布图产物：索引（occurrence_summary + subfamily_maps）与磁盘一一对应。"""
    report = geo_artifacts.collect(ROOT)
    for problem in report["problems"]:
        err("_data", problem)
    if report["missing"]:
        err("assets/geo", "%d 个索引引用但磁盘缺失的 GeoJSON，例如 %s"
            % (len(report["missing"]), report["missing"][:3]))
    if report["orphan"]:
        err("assets/geo", "%d 个磁盘存在但索引未引用的 GeoJSON，例如 %s"
            % (len(report["orphan"]), report["orphan"][:3]))
    for rel, msg in report["invalid"]:
        err(rel, "GeoJSON 解析失败：" + msg[:80])


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


FAUNA_KEY_RE = re.compile(r"site\.data\.(fauna_[a-z_]+)")
FAUNA_SITES = ("family", "genus", "species", "subfamily", "_layouts", "_includes", "_pages")


def check_fauna_keys() -> None:
    """形态描述段落引用的数据键必须真实存在。

    site.data.fauna_genera 就是 Jekyll 按 _data/fauna_genera.json 暴露的键；拼成单数时
    Liquid 的 {% if fz %} 恒不成立，整段形态描述静默消失——不报错、不留空洞，只有页面
    diff 才看得出来（本仓库真踩过：builder 曾写 fauna_genus / fauna_family）。
    """
    used: dict = {}
    paths = [ROOT / "index.md"] + [ROOT / "list.md"]
    for site in FAUNA_SITES:
        base = ROOT / site
        if base.is_dir():
            paths.extend(sorted(base.rglob("*.md")) + sorted(base.rglob("*.html")))
    for path in paths:
        if not path.is_file():
            continue
        for key in FAUNA_KEY_RE.findall(read(path)):
            used.setdefault(key, set()).add(path.relative_to(ROOT).as_posix())
    data_dir = ROOT / "_data"
    for key, pages in sorted(used.items()):
        if (data_dir / (key + ".json")).is_file():
            continue
        err("_data", "%d 个页面/布局引用 site.data.%s，但 _data/%s.json 不存在："
                     "Liquid 里恒为空、形态描述不会渲染（例如 %s）"
            % (len(pages), key, key, ", ".join(sorted(pages)[:3])))
    for path in sorted(data_dir.glob("fauna_*.json")):
        if path.stem not in used:
            warn("_data/" + path.name, "已提交，但没有任何页面或布局引用 site.data.%s" % path.stem)


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


def load_taxonomy() -> dict:
    """分类层级数据（支系 → 科 → 亚科 → 属）与各级页面的锚点 id 来源。"""
    if not TAXONOMY_JSON.is_file():
        sys.exit("error: 找不到 _data/taxonomy.json（先跑 _tools/extract_taxon_data.py）")
    return json.loads(read(TAXONOMY_JSON))


def check_lists(taxonomy: dict, fields_by_slug: dict) -> dict:
    """三语索引页同构 + 层级页面一一对应 + 每个物种都能从属页点到。

    /list/ 现在是索引页：只列支系与各科的入口，物种条目一律在属页。旧的
    「名录物种链接集合 == 标题锚点集合」不变量已随页面改版退场，这里换成三条更贴
    结构的检查：索引页不含物种链接、每个科都有入口、每个物种都挂在自己的属页下。
    """
    clade_ids = [clade["id"] for clade in taxonomy["clades"]]
    family_ids = {fam["id"] for fam in taxonomy["families"]}
    subfamily_ids = {sub["id"] for sub in taxonomy["subfamilies"]}
    genus_ids = {genus["id"] for genus in taxonomy["genera"]}
    index_ids = set(clade_ids) | {"by-family", "references"}

    ids_by_lang: dict = {}
    for lang, path in LIST_FILES.items():
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            err(rel, "文件不存在")
            continue
        text = read(path)
        ids = {m[1] for m in HEADING_RE.findall(text)}
        ids_by_lang[lang] = ids
        links = SPECIES_LINK_RE.findall(text)
        if links:
            err(rel, "名录索引页仍含 %d 个物种链接（例如 %s）；种条目应放在所属属页"
                % (len(links), links[0]))
        missing = sorted(index_ids - ids)
        if missing:
            err(rel, "缺少标题锚点：" + "、".join(missing))
        extra = sorted(ids - index_ids)
        if extra:
            err(rel, "多出标题锚点 %s：索引页只列支系，科 / 亚科 / 属各有独立页面"
                % "、".join(extra[:5]))
        anchors = set(ANCHOR_RE.findall(text)) | set(HREF_ANCHOR_RE.findall(text))
        dangling = sorted(a for a in anchors if a not in ids and a not in KNOWN_ANCHORS)
        if dangling:
            err(rel, "%d 个锚点找不到目标，例如 %s" % (len(dangling), dangling[:3]))
        fam_links = set(re.findall(r"/family/([a-z0-9-]+)/", text))
        absent = sorted(family_ids - fam_links)
        if absent:
            err(rel, "按科浏览缺 %d 个科页入口：%s" % (len(absent), "、".join(absent[:5])))
        stray_genus = sorted(genus_ids & set(re.findall(r"/genus/([a-z0-9-]+)/", text)))
        if stray_genus:
            err(rel, "索引页不该直链属页（例如 /genus/%s/）：属条目在属页" % stray_genus[0])

    if len(ids_by_lang) == 3:
        base = ids_by_lang["zh-CN"]
        for lang in ("en", "es"):
            missing = sorted(base - ids_by_lang[lang])
            extra = sorted(ids_by_lang[lang] - base)
            if missing or extra:
                err(LIST_FILES[lang].relative_to(ROOT).as_posix(),
                    "与中文索引页的标题锚点不一致：缺少 %d、多出 %d（示例 %s）"
                    % (len(missing), len(extra), (missing + extra)[:3]))

    # 每个分类单元都要有自己的页面（页面由 build_taxonomy_pages.py 生成）
    for rank, ids in (("family", family_ids), ("subfamily", subfamily_ids), ("genus", genus_ids)):
        absent = sorted(t for t in ids if not (ROOT / rank / (t + ".md")).is_file())
        if absent:
            err(rank, "%d 个分类单元缺页面：%s" % (len(absent), "、".join(absent[:5])))

    # 属页 front matter 的 family_id 必须真实存在
    bad_parent = []
    for genus_id in sorted(genus_ids):
        path = ROOT / "genus" / (genus_id + ".md")
        if not path.is_file():
            continue
        fam = parse_front_matter(path).get("family_id")
        if fam not in family_ids:
            bad_parent.append("%s→%s" % (genus_id, fam))
    if bad_parent:
        err("genus", "%d 个属页的 family_id 不在 taxonomy.json 里：%s"
            % (len(bad_parent), "、".join(bad_parent[:5])))

    # 物种页与属页的挂接：每个物种 / 亚种都出现在其所属属页的列表里
    genus_text = {path.stem: read(path) for path in sorted((ROOT / "genus").glob("*.md"))}
    linked: set = set()
    for text in genus_text.values():
        linked.update(SPECIES_LINK_RE.findall(text))
    stray = sorted(linked - set(fields_by_slug))
    if stray:
        err("genus", "%d 个属页链接了不存在的物种页：%s" % (len(stray), "、".join(stray[:5])))
    unlisted, misplaced = [], []
    for slug, fields in sorted(fields_by_slug.items()):
        if slug not in linked:
            unlisted.append(slug)
            continue
        genus_id = fields.get("genus_id") or ""
        if genus_id and ("/species/%s/" % slug) not in genus_text.get(genus_id, ""):
            misplaced.append("%s→%s" % (slug, genus_id))
    if unlisted:
        err("genus", "%d 个物种页没有出现在任何属页的物种列表里（例如 %s）"
            % (len(unlisted), "、".join(unlisted[:5])))
    if misplaced:
        err("genus", "%d 个物种页没有挂在 front matter 指定的属页下（例如 %s）"
            % (len(misplaced), "、".join(misplaced[:5])))
    return ids_by_lang


def check_section_pages(taxonomy: dict) -> None:
    """英 / 西译文页（/en/list/sections/、/es/list/sections/）须覆盖全部科与亚科小节。"""
    want = {fam["id"] for fam in taxonomy["families"]} | {sub["id"] for sub in taxonomy["subfamilies"]}
    for lang, path in SECTION_PAGES.items():
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            err(rel, "译文页不存在（由 _tools/build_list_index.py 生成）")
            continue
        ids = {m[1] for m in HEADING_RE.findall(read(path))}
        missing = sorted(want - ids)
        if missing:
            err(rel, "%d 个科 / 亚科缺小节：%s" % (len(missing), "、".join(missing[:5])))


def check_counts(fields_by_slug: dict, taxonomy: dict) -> None:
    page_count = len(fields_by_slug)
    index = json.loads(read(SEARCH_INDEX))
    index_species = sum(1 for e in index if e.get("r") in ("种", "亚种"))
    index_genera = sum(1 for e in index if e.get("r") == "属")
    sitemap_urls = read(SITEMAP).splitlines()
    # /species/<slug>/photos/ 是「全部图片」页（.github/workflows/build_photo_pages.py），
    # 属于物种的附属页，不计入「每个 _species 页面恰好一条物种 URL」这个等式。
    sitemap_species = [u for u in sitemap_urls if "/species/" in u and not u.endswith("/photos/")]
    if len(sitemap_species) != page_count:
        err("sitemap.txt", "物种 URL 数 %d 与 _species 页面数 %d 不一致" % (len(sitemap_species), page_count))
    if index_species != page_count:
        err("search-index.json", "种/亚种条数 %d 与 _species 页面数 %d 不一致" % (index_species, page_count))
    if index_genera != len(taxonomy["genera"]):
        err("search-index.json", "属条目 %d 与 taxonomy.json 的属数 %d 不一致"
            % (index_genera, len(taxonomy["genera"])))
    # 科 / 亚科 / 属页的局部检索按产地查种（assets/taxon-search.js 的 dz / de / t / sl），
    # 这些字段一旦整体消失，检索框就退化成只能搜名字，故在这里拦下。
    no_type = [e.get("l") for e in index if e.get("r") in ("种", "亚种") and not e.get("t")]
    if no_type:
        err("search-index.json", "%d 条种/亚种缺模式产地字段 t，例如 %s"
            % (len(no_type), "、".join(no_type[:3])))
    no_dist = [e.get("l") for e in index
               if e.get("r") in ("种", "亚种") and e.get("p")
               and (fields_by_slug.get(e["p"], {}).get("distribution_zh") or "").strip()
               and not e.get("dz")]
    if no_dist:
        err("search-index.json", "%d 条有分布但缺分布字段 dz，例如 %s"
            % (len(no_dist), "、".join(no_dist[:3])))


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


GLOSSARY = ROOT / "_data" / "translation_glossary.yml"
GLOSSARY_INCLUDE = ROOT / "_includes" / "papers-glossary.html"


def parse_glossary(path: Path):
    """解析 translation_glossary.yml 的受限子集（块式 mapping / sequence），返回 (data, problems)。"""
    data = {"version": None, "extra_names": [], "mask": [], "post_zh": []}
    problems = []
    section = None
    item = None
    subkey = None
    for no, raw in enumerate(read(path).splitlines(), 1):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        body = line.strip()
        if indent == 0:
            if body in ("extra_names:", "mask:", "post_zh:"):
                section, item, subkey = body[:-1], None, None
                continue
            if body.startswith("version:"):
                try:
                    data["version"] = int(body.split(":", 1)[1].strip())
                except ValueError:
                    problems.append("第 %d 行 version 不是整数" % no)
                continue
            problems.append("第 %d 行未知顶层键：%s" % (no, body))
            continue
        if indent == 2 and body.startswith("- "):
            item = {}
            subkey = None
            if section is None:
                problems.append("第 %d 行列表项不在已知区段内" % no)
                continue
            data[section].append(item)
            body = body[2:].strip()
            if ":" not in body:
                problems.append("第 %d 行列表项缺少 key: value" % no)
                continue
            key, value = body.split(":", 1)
            item[key.strip()] = value.strip()
            continue
        if indent == 4 and item is not None:
            if ":" not in body:
                problems.append("第 %d 行缺少冒号" % no)
                continue
            key, value = body.split(":", 1)
            key, value = key.strip(), value.strip()
            if value == "":
                if key not in ("when", "unless"):
                    problems.append("第 %d 行 %s 缺少值" % (no, key))
                item[key] = []
                subkey = key
            else:
                item[key] = value
                subkey = None
            continue
        if indent == 6 and body.startswith("- ") and item is not None and subkey:
            item[subkey].append(body[2:].strip())
            continue
        problems.append("第 %d 行无法识别（缩进 %d）：%s" % (no, indent, body[:40]))
    return data, problems


def check_glossary() -> None:
    """中英互译术语表：结构、字段、重复项与 post 守卫，以及三语页面是否接入。"""
    if not GLOSSARY.is_file():
        err("_data/translation_glossary.yml", "术语表缺失（摘要翻译会退回只有名录）")
        return
    data, problems = parse_glossary(GLOSSARY)
    for problem in problems:
        err("_data/translation_glossary.yml", problem)
    if data["version"] is None:
        err("_data/translation_glossary.yml", "缺 version（改术语表必须 +1，旧译文缓存才会失效）")
    mask, posts, extra = data["mask"], data["post_zh"], data["extra_names"]
    cjk = re.compile(r"[\u4e00-\u9fff]")
    if len(mask) < 10 or len(posts) < 5:
        err("_data/translation_glossary.yml", "条目过少（mask %d / post %d），疑似被误删" % (len(mask), len(posts)))
    found = {item.get("en"): item.get("zh") for item in mask}
    required_mask = {
        "head capsule": "头壳", "antenna": "触角", "mandible": "上颚", "mouthparts": "口器",
        "tarsus": "跗节", "tergite": "背板", "sternite": "腹板", "pronotum": "前胸背板",
        "gizzard": "砂囊", "enteric valve": "肠瓣",
    }
    for en, zh in required_mask.items():
        if found.get(en) != zh:
            err("_data/translation_glossary.yml", "缺少关键形态术语 %s → %s（当前 %s）" % (en, zh, found.get(en)))
    posts_map = {item.get("from"): item.get("to") for item in posts}
    for frm, to in {"头舱": "头壳", "工人": "工蚁", "殖民地": "巢群"}.items():
        if posts_map.get(frm) != to:
            err("_data/translation_glossary.yml", "缺少关键纠错 %s → %s" % (frm, to))
    seen = set()
    for i, item in enumerate(mask):
        en, zh = item.get("en"), item.get("zh")
        if not en or not zh:
            err("_data/translation_glossary.yml", "mask[%d] 缺 en/zh" % i)
            continue
        if not en.isascii():
            err("_data/translation_glossary.yml", "mask[%d] en 含非 ASCII：%s" % (i, en))
        if not cjk.search(zh):
            err("_data/translation_glossary.yml", "mask[%d] zh 不含中文：%s" % (i, zh))
        if en.lower() in seen:
            err("_data/translation_glossary.yml", "mask 重复：%s" % en)
        seen.add(en.lower())
    seen = set()
    for i, item in enumerate(posts):
        frm, to, when = item.get("from"), item.get("to"), item.get("when")
        if not frm or not to:
            err("_data/translation_glossary.yml", "post_zh[%d] 缺 from/to" % i)
            continue
        if frm in seen:
            err("_data/translation_glossary.yml", "post_zh 重复 from：%s" % frm)
        seen.add(frm)
        if frm == to:
            err("_data/translation_glossary.yml", "post_zh[%d] from 与 to 相同：%s" % (i, frm))
        if not isinstance(when, list) or not when:
            err("_data/translation_glossary.yml", "post_zh[%d] 缺 when 守卫（会误伤其他语境）" % i)
    for i, item in enumerate(extra):
        if not item.get("latin") or not item.get("zh"):
            err("_data/translation_glossary.yml", "extra_names[%d] 缺 latin/zh" % i)
    if not GLOSSARY_INCLUDE.is_file():
        err("_includes/papers-glossary.html", "术语表 JSON 桥接文件缺失")
    else:
        include_body = read(GLOSSARY_INCLUDE)
        if 'id="papers-glossary"' not in include_body:
            err("_includes/papers-glossary.html", '缺 id="papers-glossary"（前端读不到）')
        if "site.data.translation_glossary" not in include_body:
            err("_includes/papers-glossary.html", "没有输出 site.data.translation_glossary")
    for page, _url in PAPERS_PAGES:
        path = ROOT / page
        if path.is_file() and "{% include papers-glossary.html %}" not in read(path):
            err(page, "缺少 {% include papers-glossary.html %}（术语表不会进入页面）")


def check_papers(base_url: str) -> None:
    """文献检索器：三语页面、sitemap、缓存文件与摘要字段。"""
    sitemap = read(SITEMAP).splitlines() if SITEMAP.is_file() else []
    for page, url in PAPERS_PAGES:
        path = ROOT / page
        if not path.is_file():
            err(page, "文献检索页面缺失")
            continue
        body = read(path)
        if 'id="papers-app"' not in body:
            err(page, "缺少 #papers-app 容器（assets/papers.js 不会初始化）")
        for control in ("papers-scope", "papers-fulltext"):
            if ('id="%s"' % control) not in body:
                err(page, "缺少 #%s 控件（白蚁范围 / 全文检索无法切换）" % control)
        for label in ("T.papers_scope", "T.papers_fulltext"):
            if label not in body:
                err(page, "缺少 %s 文案（i18n key 未接入）" % label)
        if 'data-lang="' not in body:
            err(page, "缺少 #papers-app 的 data-lang（摘要翻译的默认目标语言无法确定）")
        if ("permalink: " + url) not in body:
            err(page, "permalink 应为 " + url)
        if (base_url + url) not in sitemap:
            err("sitemap.txt", "未收录文献检索页面 " + url)

    bridge = ROOT / "_includes" / "papers-i18n.html"
    if not bridge.is_file():
        err("_includes/papers-i18n.html", "文案桥接文件缺失（assets/papers.js 只能用英文默认值）")
    else:
        bridge_body = read(bridge)
        for key in ('"translate"', '"translateTo"', '"translateProgress"',
                    '"translateQuota"', '"translateMachine"', '"langZh"', '"langEs"'):
            if key not in bridge_body:
                err("_includes/papers-i18n.html", "缺少 %s 字段（摘要翻译文案无法本地化）" % key)

    if not PAPERS_DATA.is_file():
        err(PAPERS_DATA.relative_to(ROOT).as_posix(), "文件不存在（运行 .github/workflows/build_papers.py --write）")
        return
    if not PAPERS_PUBLIC.is_file():
        err(PAPERS_PUBLIC.relative_to(ROOT).as_posix(), "公开副本不存在（运行 build_papers.py --write）")
    else:
        if PAPERS_PUBLIC.read_bytes() != PAPERS_DATA.read_bytes():
            err(PAPERS_PUBLIC.relative_to(ROOT).as_posix(), "与 _data/papers.json 字节不一致")

    try:
        document = json.loads(read(PAPERS_DATA))
    except json.JSONDecodeError as exc:
        err(PAPERS_DATA.relative_to(ROOT).as_posix(), "JSON 不可解析：%s" % exc)
        return
    if not isinstance(document, dict):
        err(PAPERS_DATA.relative_to(ROOT).as_posix(), "顶层不是对象")
        return

    expected_genera = {
        str(e.get("h"))
        for e in (json.loads(read(SEARCH_INDEX)) if SEARCH_INDEX.is_file() else [])
        if isinstance(e, dict) and e.get("r") == "属" and e.get("h")
    }
    meta = document.get("meta") or {}
    genera = document.get("genera") or {}
    if not isinstance(genera, dict):
        err(PAPERS_DATA.relative_to(ROOT).as_posix(), "genera 不是对象")
        return
    missing = sorted(expected_genera - set(genera))
    extra = sorted(set(genera) - expected_genera)
    if missing:
        err(PAPERS_DATA.relative_to(ROOT).as_posix(), "缺少属条目 %d 个：%s" % (len(missing), missing[:5]))
    if extra:
        err(PAPERS_DATA.relative_to(ROOT).as_posix(), "多出属条目 %d 个：%s" % (len(extra), extra[:5]))

    total = with_abstract = with_doi = 0
    for gid, entry in genera.items():
        if not isinstance(entry, dict):
            err(PAPERS_DATA.relative_to(ROOT).as_posix(), "%s: 条目不是对象" % gid)
            continue
        if not entry.get("latin"):
            err(PAPERS_DATA.relative_to(ROOT).as_posix(), "%s: 缺 latin" % gid)
        if not isinstance(entry.get("fetched_at"), str):
            err(PAPERS_DATA.relative_to(ROOT).as_posix(), "%s: 缺 fetched_at" % gid)
        papers = entry.get("papers")
        if not isinstance(papers, list):
            err(PAPERS_DATA.relative_to(ROOT).as_posix(), "%s: papers 不是数组" % gid)
            continue
        if len(papers) > int(meta.get("per_genus") or 12):
            err(PAPERS_DATA.relative_to(ROOT).as_posix(), "%s: 文献数超过 per_genus" % gid)
        seen = set()
        for idx, paper in enumerate(papers):
            where = "%s[%d]" % (gid, idx)
            if not isinstance(paper, dict):
                err(PAPERS_DATA.relative_to(ROOT).as_posix(), where + ": 不是对象")
                continue
            pid = paper.get("id") or paper.get("doi") or paper.get("title")
            if not pid:
                err(PAPERS_DATA.relative_to(ROOT).as_posix(), where + ": 缺 id/doi/title")
            if pid in seen:
                err(PAPERS_DATA.relative_to(ROOT).as_posix(), where + ": 重复条目")
            seen.add(pid)
            if not paper.get("title"):
                err(PAPERS_DATA.relative_to(ROOT).as_posix(), where + ": 缺 title")
            abstract = paper.get("abstract", "")
            if not isinstance(abstract, str):
                err(PAPERS_DATA.relative_to(ROOT).as_posix(), where + ": abstract 不是字符串")
                abstract = ""
            if paper.get("abstract_chars") != len(abstract):
                err(PAPERS_DATA.relative_to(ROOT).as_posix(), where + ": abstract_chars 与摘要长度不一致")
            if paper.get("doi") and paper.get("doi_url") != ("https://doi.org/" + str(paper.get("doi"))):
                err(PAPERS_DATA.relative_to(ROOT).as_posix(), where + ": doi_url 与 doi 不一致")
            if abstract:
                with_abstract += 1
            if paper.get("doi"):
                with_doi += 1
            total += 1

    counts = meta.get("counts") or {}
    expected_counts = {
        "genera": len(expected_genera),
        "papers": total,
        "with_abstract": with_abstract,
        "with_doi": with_doi,
    }
    for key, value in expected_counts.items():
        if counts.get(key) != value:
            err(PAPERS_DATA.relative_to(ROOT).as_posix(), "meta.counts.%s=%s，实际 %s" % (key, counts.get(key), value))


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
        expected_recordable = (direction == "external" and relation == "synonym"
                               and len((pair.get("votes") or {}).get("synonym") or []) >= 2)
        if bool(pair.get("recordable")) != expected_recordable:
            err("_data/name_issues.json", "recordable 判定与规则不一致：%s（应为 %s）"
                % (our["latin"], expected_recordable))
        if pair.get("recordable"):
            recordable += 1
        if pair.get("recorded"):
            recorded += 1
            # 已补录必须方向明确、真异名，且真的写进了接受名物种页的 authority_synonyms
            if direction != "external" or relation != "synonym":
                err("_data/name_issues.json", "已补录的对必须是「真异名 + 外部库名为接收名」：%s" % our["latin"])
            if len((pair.get("votes") or {}).get("synonym") or []) < 2:
                err("_data/name_issues.json", "已补录的对至少要有两个分类数据库认定是异名：%s" % our["latin"])
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


def check_species_siblings_not_indexed() -> None:
    """物种页「同属其他种」区块不得进入 Pagefind 全文索引。

    Pagefind 只索引 <main data-pagefind-body> 里的文字（见 _layouts/default.html），
    而「同属其他种」在 3000+ 个物种页上各列出最多 40 条同属学名 / 中文名内链。
    一旦这些名字进了索引，每个物种页都「含有」整属的种名：搜一个种名会连同属的一大堆
    无关页面一起返回，搜索结果被淹没。给该区块加 data-pagefind-ignore 让 Pagefind
    整块跳过即可（页面上的内链、SEO 抓取路径都不受影响，只是不参与全文检索）。
    """
    layout = ROOT / "_layouts" / "species.html"
    if not layout.is_file():
        err("_layouts/species.html", "物种页布局不存在")
        return
    text = read(layout)
    tags = re.findall(r'<section\b[^>]*\bclass="[^"]*\bspecies-siblings\b[^"]*"[^>]*>', text)
    if not tags:
        err("_layouts/species.html", '找不到「同属其他种」区块（<section class="species-siblings">）')
        return
    for tag in tags:
        if not re.search(r"\sdata-pagefind-ignore\b", tag):
            err("_layouts/species.html",
                "「同属其他种」区块缺少 data-pagefind-ignore：同属种名会进入 Pagefind 全文索引，"
                "搜索一个种名会多出同属其他种的一大批页面（每页最多 40 条内链）")


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
    check_fauna_keys()
    fields_by_slug, _ = check_species()
    taxonomy = load_taxonomy()
    check_lists(taxonomy, fields_by_slug)
    check_section_pages(taxonomy)
    check_counts(fields_by_slug, taxonomy)
    check_sitemap(base_url)
    check_papers(base_url)
    check_glossary()
    check_feeds_and_changelog(base_url)
    check_i18n()
    check_name_issues(fields_by_slug)
    check_search_overlay()
    check_species_siblings_not_indexed()

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

    print("校验通过：%d 个物种页、三语索引页同构、科/亚科/属页面齐备、计数一致、sitemap / i18n / 命名差异产物与订阅源 / 版本记录自洽（提醒 %d 条）" % (len(fields_by_slug), len(warnings)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
