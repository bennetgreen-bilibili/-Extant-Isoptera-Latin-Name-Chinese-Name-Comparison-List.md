#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate taxonomic hub pages (family / subfamily / genus) in three languages.

Why this exists
---------------
The site has 3,089 species pages but, before this script, their only "parent" was the
single 450 KB /list/ page. Search engines therefore saw almost no intermediate
classification level: crawl depth 2 for every species, no page that answers
"what is genus X" / "which genera are in family Y".

This script reads the front matter of every _species/*.md (same minimal YAML parser as
build_genus_index.py, no PyYAML dependency) and writes one page per taxon **per language**:

    family/<id>.md                13 pages   zh-CN  /family/<id>/
    subfamily/<id>.md             18 pages   zh-CN  /subfamily/<id>/
    genus/<id>.md                326 pages   zh-CN  /genus/<id>/
    en/family/<id>.md             13 pages   en     /en/family/<id>/
    en/subfamily/<id>.md          18 pages   en     /en/subfamily/<id>/
    en/genus/<id>.md             326 pages   en     /en/genus/<id>/
    es/family/<id>.md             13 pages   es     /es/family/<id>/
    es/subfamily/<id>.md          18 pages   es     /es/subfamily/<id>/
    es/genus/<id>.md             326 pages   es     /es/genus/<id>/

2026-11: the three languages used to be interleaved on one page (`<span class="fact-en">`
+ `<span class="fact-es">`, greyed out by CSS). They are now three separate pages, each
rendering **one** language only — see _tmp/lang-split-CONTRACT.md. Every page keeps:
a short unique summary (BreadcrumbList comes from _includes/breadcrumb-jsonld.html via the
breadcrumb list in front matter), a local search box scoped to that taxon, a distribution
map (reusing _includes/distribution-map.html), the family/subfamily prose from
_data/taxon_prose.json, and the child list.

The prose (形态/分布/经济意义) lives in _data/taxon_prose.json for all three languages and
is its canonical home; the hub page links back to the /list/ anchor. Copying it is
deliberate: /list/ is a single 450 KB page, so "白蚁科的形态特征" had no citable, shareable
landing page of its own before this.

Data that has no translation yet
--------------------------------
en/es pages read their per-taxon text from _data/translations_en.json /
_data/translations_es.json (schema in the contract, §5; produced by another step). When a
page's data exists in Chinese but has no translated entry, the section is omitted by the
includes (never backfilled with Chinese) and the front matter gets
`translation_pending: true`, which makes _layouts/default.html show the one-line note from
_includes/translation-missing.html. The flag clears itself as soon as the translation data
covers the key, so this script stays idempotent.

The subfamily maps (assets/geo/subfamily/<id>.geojson, _data/subfamily_maps.json) are
merged here from the committed per-genus maps: build_occurrence_geojson.py pulls GBIF
records per genus and has no subfamily level, and merging offline keeps this script
deterministic and network-free.

It also writes _data/taxonomy_images.json, used by _layouts/default.html as the og:image
fallback for species pages (per-family photo) and by the hub pages themselves.

Pages are generated deterministically and idempotently: sorted keys, LF endings, files
whose content did not change are left untouched. Run it after build_species_body.py and
before build_sitemap_txt.py (see .github/workflows/pages.yml).

Usage:
    python .github/workflows/build_taxonomy_pages.py           # write
    python .github/workflows/build_taxonomy_pages.py --check   # verify without writing
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "_species"
IMAGES_DIR = ROOT / "assets" / "images"
PROSE_JSON = ROOT / "_data" / "taxon_prose.json"
PHOTO_TAXA_JSON = ROOT / "_data" / "photo_taxa.json"
DATA_OUT = ROOT / "_data" / "taxonomy_images.json"
ETYMOLOGY_JSON = ROOT / "_data" / "etymology.json"

# 三种语言与它们的 URL / 目录前缀（契约 §2、§7）
LANGS = ("zh-CN", "en", "es")
LANG_PREFIX = {"zh-CN": "", "en": "/en", "es": "/es"}

# 每种语言的产物目录：zh 沿用 family/ 等；en/es 写到 en/family/、es/family/ 等
OUT_DIRS = {}
for _lang in LANGS:
    _root = ROOT if not LANG_PREFIX[_lang] else ROOT / LANG_PREFIX[_lang].strip("/")
    OUT_DIRS[_lang] = {rank: _root / rank for rank in ("family", "subfamily", "genus")}
del _lang, _root

DEFAULT_IMAGE = "/assets/images/mastotermitidae.jpg"
RANK_LABEL = {"family": "Family", "subfamily": "Subfamily", "genus": "Genus"}
SB = "{{ site.base_url }}"
DATASET_ID = "{{ site.base_url }}/#dataset"
DATASET_VERSION = "{{ site.dataset.version }}"
DATASET_DATE = "{{ site.dataset.version | replace: '.', '-' }}"

# description 必须落在 150-160 字符之间（Bing 对过短的描述降权）。zh 一直如此；en/es 在
# 拆分后同样按 150-160 生成——比契约里允许的 140-180 更严，因此每条外文描述都是
# 「core 模板 + 短尾」拼到窗口内，不靠放宽下限过关。
DESC_MIN = 150
DESC_MAX = 160

# 三语固定文案。zh-CN 的字句沿用拆分前的原文（对外引用、/list/ 锚点与既有 description
# 都建立在它上面）；en/es 是本次拆页新增的译法，标题词序跟 /en/list/sections/、
# /es/list/sections/ 一致（拉丁名在前、中文专名在后，中文专名作为对照保留）。
COPY = {
    "zh-CN": {
        "checklist": "名录",
        "checklist_index": "名录索引",
        "data": "数据与下载",
        "home": "首页",
        "back_checklist": "← 返回名录索引",
        "parent_level": "上一级",
        "crumbs_label": "分类位置",
        "this_rank": {"family": "本科", "subfamily": "本亚科", "genus": "本属"},
        "rank_noun": {"family": "科", "subfamily": "亚科", "genus": "属"},
        "about": {"family": "科级介绍", "subfamily": "亚科级介绍", "genus": "属级介绍"},
        "distribution": "分布图",
        "etymology": "词源",
        "type_species": "模式种",
        "search_scope": {"family": "本科", "subfamily": "本亚科", "genus": "本属"},
        "search_placeholder": "如 白蚁 / Amitermes / 澳大利亚",
    },
    "en": {
        "checklist": "Checklist",
        "checklist_index": "Checklist index",
        "data": "Data &amp; downloads",
        "home": "Home",
        "back_checklist": "← Back to the checklist",
        "parent_level": "Parent level",
        "crumbs_label": "Taxonomic position",
        "this_rank": {"family": "This family", "subfamily": "This subfamily", "genus": "This genus"},
        "rank_noun": {"family": "family", "subfamily": "subfamily", "genus": "genus"},
        "about": {"family": "About the family", "subfamily": "About the subfamily",
                  "genus": "About the genus"},
        "distribution": "Distribution map",
        "etymology": "Etymology",
        "type_species": "Type species",
        "search_scope": {"family": "this family", "subfamily": "this subfamily", "genus": "this genus"},
        "search_placeholder": "e.g. termite / Amitermes / Australia",
    },
    "es": {
        "checklist": "Listado",
        "checklist_index": "Índice del listado",
        "data": "Datos y descargas",
        "home": "Inicio",
        "back_checklist": "← Volver al listado",
        "parent_level": "Nivel superior",
        "crumbs_label": "Posición taxonómica",
        "this_rank": {"family": "Esta familia", "subfamily": "Esta subfamilia",
                      "genus": "Este género"},
        "rank_noun": {"family": "familia", "subfamily": "subfamilia", "genus": "género"},
        "about": {"family": "Acerca de la familia", "subfamily": "Acerca de la subfamilia",
                  "genus": "Acerca del género"},
        "distribution": "Mapa de distribución",
        "etymology": "Etimología",
        "type_species": "Especie tipo",
        "search_scope": {"family": "esta familia", "subfamily": "esta subfamilia",
                         "genus": "este género"},
        "search_placeholder": "p. ej. termita / Amitermes / Australia",
    },
}

# 计数名词的单复数（契约：en/es 页面里的标题、统计行都用它）
WORDS = {
    "zh-CN": {"subfamily": "亚科", "genus": "属", "species": "种", "subspecies": "亚种"},
    "en": {"subfamily": ("subfamily", "subfamilies"), "genus": ("genus", "genera"),
           "species": ("species", "species"), "subspecies": ("subspecies", "subspecies")},
    "es": {"subfamily": ("subfamilia", "subfamilias"), "genus": ("género", "géneros"),
           "species": ("especie", "especies"), "subspecies": ("subespecie", "subespecies")},
}

# 页面标题（front matter title）。zh 沿用原文；en/es 把拉丁名放前、中文正名放括注里。
TITLE_FMT = {
    "zh-CN": {"family": "%s %s 分类名录", "subfamily": "%s %s 属与物种名录",
              "genus": "%s %s 物种名录"},
    "en": {"family": "Family %s (%s) checklist", "subfamily": "Subfamily %s (%s) checklist",
           "genus": "Genus %s (%s) checklist"},
    "es": {"family": "Familia %s (%s) — listado", "subfamily": "Subfamilia %s (%s) — listado",
           "genus": "Género %s (%s) — listado"},
}

# h1 的阶元前缀（en/es）。zh 页的 h1 是「中文名 + 拉丁名」，不加前缀。
HEAD_PREFIX = {
    "en": {"family": "Family", "subfamily": "Subfamily", "genus": "Genus"},
    "es": {"family": "Familia", "subfamily": "Subfamilia", "genus": "Género"},
}

# 「本节是本站为这一级分类维护的常设说明……」：段落里的链接用 %(list)s。
INTRO_SRC = {
    "zh-CN": '<p class="taxon-src">本节是本站为这一级分类维护的常设说明，随分类修订在本页更新；'
             '名录索引见<a href="%(list)s">名录</a>。</p>\n',
    "en": '<p class="taxon-src">This section is the standing account the site maintains for '
          'this rank and is updated on this page as the classification is revised; the '
          'checklist index is in the <a href="%(list)s">Checklist</a>.</p>\n',
    "es": '<p class="taxon-src">Esta sección es la explicación permanente que el sitio mantiene '
          'para este nivel y se actualiza en esta página conforme se revisa la clasificación; '
          'el índice del listado está en el <a href="%(list)s">Listado</a>.</p>\n',
}

# 词源脚注（词根据 Brown 1956, S0018）
ETYM_SRC = {
    "zh-CN": '<p class="taxon-src">本节词源为拆解式整理，词根据 Brown (1956)。</p>\n',
    "en": '<p class="taxon-src">The etymologies in this section are analytical breakdowns; '
          'the roots follow Brown (1956).</p>\n',
    "es": '<p class="taxon-src">Las etimologías de esta sección son descomposiciones '
          'analíticas; las raíces siguen a Brown (1956).</p>\n',
}

# Short neutral tails used only to pad a description up to the 150-character target.
# They are appended after the rank-specific pool, shortest last, and never repeated.
FILLERS = [
    "详见名录索引。",
    "按分类系统逐级排列。",
    "数据来自 CC BY 4.0 数据集。",
    "并附中文正名与引用格式。",
    "亦可从名录对应章节进入。",
    "页面持续更新。",
]

# en/es 的长度梯度补尾句。每句以空格开头（外文句之间必须有空格，计数也含这个空格）。
# 长度从 11 到 65 之间间隔不超过 10，因此无论模板把描述留在 150 以下的哪一段，都能用
# 1-2 句把它推进 150-160 窗口（见 fit_localized）。句子本身只说页面事实，不重复内容。
LOCAL_TAILS = {
    "en": [
        " See below.",
        " See the list below.",
        " See the checklist index.",
        " See the index below.",
        " Counts are listed below.",
        " Counts are per genus.",
        " Counts follow the dataset.",
        " Names follow the checklist.",
        " See the checklist for the full list.",
        " Counts follow the site dataset (CC BY 4.0).",
        " Counts and names follow the checklist used on this site.",
    ],
    "es": [
        " Ver abajo.",
        " Ver el listado.",
        " Ver el índice del listado.",
        " Ver el listado completo.",
        " Los recuentos van abajo.",
        " Los recuentos son por género.",
        " Los nombres siguen el listado.",
        " Ver el listado para el detalle.",
        " Los recuentos siguen el listado del sitio.",
        " Los recuentos siguen el conjunto de datos del sitio (CC BY 4.0).",
    ],
}

# 图注里的中文标签（数据里是「摄影」「图自」「已缩放」这类模板词，不是学名）。
# zh 页原样输出；en/es 页换成本页语言的标签，许可链接的 deed.zh 也换成 deed.en / deed.es，
# 学名、摄影者、许可与来源链接一律不动（授权信息必须逐字保留）。
FIG_LABELS = {
    "en": [
        (" · 摄影 ", " · Photo: "),
        (" · 图自 ", " · Image from "),
        (" · 图源 ", " · Source: "),
        (" · 摄影者放弃版权（", " · Photographer waived copyright ("),
        ("（补充材料）", " (supplementary material)"),
        ("（iNaturalist，已缩放）", " (iNaturalist, scaled)"),
        ("deed.zh", "deed.en"),
        ("（", " ("),
        ("）", ")"),
        ("，", ", "),
    ],
    "es": [
        (" · 摄影 ", " · Foto: "),
        (" · 图自 ", " · Imagen de "),
        (" · 图源 ", " · Fuente: "),
        (" · 摄影者放弃版权（", " · El fotógrafo renunció a los derechos de autor ("),
        ("（补充材料）", " (material complementario)"),
        ("（iNaturalist，已缩放）", " (iNaturalist, ampliada)"),
        ("deed.zh", "deed.es"),
        ("（", " ("),
        ("）", ")"),
        ("，", ", "),
    ],
}


def localize_figure(lang, block):
    """图注标签按页面语言替换；zh 页原样返回。"""
    if lang == "zh-CN":
        return block
    for old, new in FIG_LABELS[lang]:
        block = block.replace(old, new)
    return block

# en/es 的语义补句池（按秩级分开，顺序即优先顺序）
LOCAL_POOL = {
    "en": {
        "family": [
            " The page lists the family's subfamilies and genera in taxonomic order.",
            " Each genus opens its own page; each species opens the species page.",
            " Morphology, distribution and economic significance are summarized above.",
            " Species pages give type locality, map, congeners and citation formats.",
        ],
        "subfamily": [
            " Every genus of the subfamily is listed below with its species totals.",
            " Genus and species pages give distribution maps and citation formats.",
            " Morphology and economic significance are summarized above.",
        ],
        "genus": [
            " Every species and subspecies of the genus is listed below.",
            " Species pages give type locality, distribution, congeners and citation formats.",
            " Morphology and etymology are summarized above.",
        ],
    },
    "es": {
        "family": [
            " La página ordena las subfamilias y los géneros de la familia.",
            " Cada género abre su página; cada especie abre la suya.",
            " La morfología, la distribución y la importancia económica se resumen arriba.",
            " Las páginas de especie dan localidad tipo, mapa, congéneres y formatos de cita.",
        ],
        "subfamily": [
            " Cada género de la subfamilia aparece abajo con sus recuentos de especies.",
            " Las páginas de género y especie dan mapas de distribución y formatos de cita.",
            " La morfología y la importancia económica se resumen arriba.",
        ],
        "genus": [
            " Abajo se listan todas las especies y subespecies del género.",
            " Las páginas de especie dan localidad tipo, distribución, congéneres y formatos de cita.",
            " La morfología y la etimología se resumen arriba.",
        ],
    },
}

FM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)[ \t]*:[ \t]*(.*)$")
FIGURE_RE = re.compile(r'<figure class="taxa-illustration">.*?</figure>', re.S)
IMG_RE = re.compile(r"/assets/images/([a-z0-9\-]+)\.(?:jpg|png)")
HEADING_RE = re.compile(r'<h([2-5])\s+id="([a-z0-9\-]+)"[^>]*>.*?</h\1>', re.S)
INCLUDE_MAP_RE = re.compile(r"^[ \t]*\{%\s*include\s+distribution-map\.html.*?%\}[ \t]*$", re.M)
TAG_ONLY_RE = re.compile(r"^[ \t]*<[^>]+>[ \t]*$")
CJK_RE = re.compile(u"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]")
# 阈值与 _tools/check_lang_pages.py 的 E014 一致（≥12 连续汉字视为残留中文句子）：
# 只有真的会被判成句子的长串才插断行点，普通 6–11 字正名一律原样输出。
CJK_RUN_RE = re.compile(u"[\u4e00-\u9fff]{12,}")


def break_long_cjk(text):
    """长中文专名插断行机会（`<wbr>`）。

    数据集里有一个音译得很长的中文正名（14 个汉字，如「阿尔米尔萨特尔西尔韦斯特里白蚁」）。
    外文页的正文检查把「≥12 连续汉字」当成残留中文句子，长专名会误报；`<wbr>` 只在渲染层
    提供断行点，不增加、不替换任何字符（浏览器也不复制它），名字本身逐字不变。
    短于 E014 阈值的正名不插，免得 326 个属页的每条物种链接都多出一个无意义的断行点。
    """
    return CJK_RUN_RE.sub(lambda m: m.group(0)[:6] + "<wbr>" + m.group(0)[6:], text)
GEO_DIR = ROOT / "assets" / "geo"
GEO_FAMILY = GEO_DIR / "family"
GEO_GENUS = GEO_DIR / "genus"
GEO_SUBFAMILY = GEO_DIR / "subfamily"
SUBFAMILY_MAPS_OUT = ROOT / "_data" / "subfamily_maps.json"


def parse_front_matter(text):
    """Minimal YAML parser for the flat, single-line front matter used here."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = {}
    for line in text[3:end].splitlines():
        m = FM_RE.match(line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
            raw = raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        elif len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
            raw = raw[1:-1].replace("''", "'")
        data[key] = raw
    return data


# _data/taxon_prose.json 的语言键是 zh / en / es（站点语言键是 zh-CN），必须映射，
# 否则 zh 页会一个科/亚科的正文都取不到。
PROSE_LANG = {"zh-CN": "zh", "en": "en", "es": "es"}


def load_prose(lang="zh-CN"):
    """Read one language of _data/taxon_prose.json, written by _tools/extract_taxon_data.py."""
    if not PROSE_JSON.is_file():
        sys.exit("missing %s — run _tools/extract_taxon_data.py" % PROSE_JSON.name)
    data = json.loads(PROSE_JSON.read_text(encoding="utf-8"))
    return data.get(PROSE_LANG.get(lang, lang)) or {}


def list_figures(lang="zh-CN"):
    """Map taxon id -> <figure> block for one language.

    The block is kept verbatim so the caption and photo credit stay attached to the photo
    (they are CC BY-NC / CC BY-NC-SA from iNaturalist and must keep their attribution).
    """
    prose = load_prose(lang)
    figures = {}
    for bucket in ("families", "subfamilies"):
        for taxon_id, entry in (prose.get(bucket) or {}).items():
            if entry.get("figure"):
                figures[taxon_id] = entry["figure"]
    return figures


def html_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def reflow(lines):
    """Re-join the hard-wrapped lines of one /list/ paragraph.

    Chinese may break anywhere, so a newline inside a paragraph is not a space; between
    two Latin tokens it is ("Termes Linnaeus," + "1758；" -> "Termes Linnaeus, 1758；").
    """
    out = ""
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if not out:
            out = line
        elif CJK_RE.match(out[-1]) or CJK_RE.match(line[0]):
            out += line
        else:
            out += " " + line
    return out


def list_sections(lang="zh-CN"):
    """Map taxon id -> list of prose paragraphs for families and subfamilies, one language.

    The prose used to be copied out of /list/; since /list/ became an index page it lives
    in _data/taxon_prose.json, and these hub pages are now its canonical home.
    """
    prose = load_prose(lang)
    sections = {}
    for bucket in ("families", "subfamilies"):
        for taxon_id, entry in (prose.get(bucket) or {}).items():
            paragraphs = entry.get("paragraphs") or []
            if paragraphs:
                sections[taxon_id] = paragraphs
    return sections


def parse_cells(path):
    """Read the 1 degree grid of one committed taxon map -> {(lon, lat): records}."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}, ""
    cells = {}
    for feature in data.get("features") or []:
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        if len(coords) < 2:
            continue
        key = (round(float(coords[0]), 3), round(float(coords[1]), 3))
        count = int((feature.get("properties") or {}).get("n") or 0)
        cells[key] = cells.get(key, 0) + count
    props = data.get("properties") or {}
    return cells, str(props.get("generated") or "")


def render_geojson(properties, cells):
    """Same byte layout as build_occurrence_geojson.render_geojson (review-friendly)."""
    body = ",\n".join(
        "    " + json.dumps(
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]},
             "properties": {"n": cells[(lon, lat)]}},
            ensure_ascii=False, separators=(",", ":"))
        for lon, lat in sorted(cells, key=lambda key: (key[1], key[0]))
    )
    return (
        "{\n"
        '"type":"FeatureCollection",\n'
        '"properties":%s,\n'
        '"features":[\n%s\n'
        "]\n"
        "}\n"
    ) % (json.dumps(properties, ensure_ascii=False, separators=(",", ":")), body)


def image_path(taxon_id):
    for name in ("%s.jpg" % taxon_id, "%s.png" % taxon_id, "%s-1.jpg" % taxon_id):
        if (IMAGES_DIR / name).is_file():
            return "/assets/images/" + name
    return None


def plural(n, unit):
    return "%d %s" % (n, unit)


def num_phrase(n, one, many):
    """English/Spanish count with the singular/plural forms of doc §4."""
    return "%d %s" % (n, one if n == 1 else many)


def count_unit(lang, n, key):
    """`4 亚科` / `4 subfamilies` / `4 subfamilias`."""
    if lang == "zh-CN":
        return plural(n, WORDS[lang][key])
    one, many = WORDS[lang][key]
    return num_phrase(n, one, many)


def count_phrase(lang, species, subspecies):
    """`7 种、1 亚种` / `7 species, 1 subspecies` / `7 especies, 1 subespecie`."""
    if lang == "zh-CN":
        parts = [plural(species, "种")]
        if subspecies:
            parts.append(plural(subspecies, "亚种"))
        return "、".join(parts)
    parts = [count_unit(lang, species, "species")]
    if subspecies:
        parts.append(count_unit(lang, subspecies, "subspecies"))
    return ", ".join(parts)


def join_words(lang, parts):
    """`a, b and c` / `a, b y c`。"""
    if len(parts) <= 1:
        return "".join(parts)
    if lang == "en":
        return ", ".join(parts[:-1]) + " and " + parts[-1]
    return ", ".join(parts[:-1]) + " y " + parts[-1]


def count_phrase_full(lang, subfamilies, genera, species, subspecies):
    """`3 个亚科、12 个属、300 个种、5 个亚种` / `3 subfamilies, 12 genera and 300 species`。"""
    if lang == "zh-CN":
        parts = []
        if subfamilies:
            parts.append(plural(subfamilies, "个亚科"))
        parts.append(plural(genera, "个属"))
        parts.append(plural(species, "个种"))
        if subspecies:
            parts.append(plural(subspecies, "个亚种"))
        return "、".join(parts)
    parts = []
    if subfamilies:
        parts.append(count_unit(lang, subfamilies, "subfamily"))
    parts.append(count_unit(lang, genera, "genus"))
    parts.append(count_unit(lang, species, "species"))
    if subspecies:
        parts.append(count_unit(lang, subspecies, "subspecies"))
    return join_words(lang, parts)


def fit_description(core, pool, fillers=None):
    """zh：Append sentences from pool/fillers while keeping the result within 150-160 chars.

    Bing's SEO report flags descriptions shorter than ~150 characters; the site target is
    150-160 characters (character count, not bytes), so padding stops as soon as the text
    reaches 150 and never crosses 160.
    """
    desc = core
    for sentence in pool:
        if len(desc) >= DESC_MIN:
            break
        if len(desc) + len(sentence) <= DESC_MAX:
            desc += sentence
    for sentence in (fillers or FILLERS):
        if len(desc) >= DESC_MIN:
            break
        if len(desc) + len(sentence) <= DESC_MAX:
            desc += sentence
    return desc


def fit_localized(core, pool, max_extra=3):
    """en/es：core + 至多 max_extra 句 pool，落进 150-160 窗口（外文句自带前置空格）。

    模板与短尾各有几种长度，广度优先试到落进窗口为止；落不进时返回原 core，由
    main() 末尾的长度校验报错，绝不静默放宽。core 里带拉丁学名，所以描述天然唯一。
    """
    if len(core) > DESC_MAX:
        return core
    if DESC_MIN <= len(core) <= DESC_MAX:
        return core
    found = [None]

    def walk(desc, start, used):
        if found[0] is not None:
            return
        if DESC_MIN <= len(desc) <= DESC_MAX:
            found[0] = desc
            return
        if used >= max_extra:
            return
        for idx in range(start, len(pool)):
            nxt = desc + pool[idx]
            if len(nxt) <= DESC_MAX:
                walk(nxt, idx + 1, used + 1)

    walk(core, 0, 0)
    return found[0] if found[0] is not None else core


def load_photo_taxa():
    """有开放许可照片的分类单元：_data/photo_taxa.json（build_photo_pages.py 生成）。

    科 / 亚科 / 属页只在真的有照片时才挂图片小节、并在 front matter 里写
    has_photos: true —— _layouts/default.html 据此决定要不要加载 PhotoSwipe，
    否则 326 个属页会白下载一套灯箱脚本。文件不存在（例如先跑本脚本）时按空处理。
    """
    if not PHOTO_TAXA_JSON.is_file():
        return {rank: {} for rank in ("family", "subfamily", "genus", "species")}
    data = json.loads(PHOTO_TAXA_JSON.read_text(encoding="utf-8"))
    return {rank: data.get(rank) or {} for rank in ("family", "subfamily", "genus", "species")}


def load_data_keys():
    """中文数据里有哪些页面的条目 —— 用来判断外文页是否缺译文（→ translation_pending）。"""
    keys = {}
    for name in ("fauna_families", "fauna_genera", "fauna_keys", "morphology_genera"):
        path = ROOT / "_data" / (name + ".json")
        keys[name] = set(json.loads(path.read_text(encoding="utf-8"))) if path.is_file() else set()
    return keys


def load_translations():
    """en/es 译文（另一环节产出，可能尚未就位）。缺失按空处理，页面因此整节省略。"""
    out = {}
    for lang in ("en", "es"):
        path = ROOT / "_data" / ("translations_%s.json" % lang)
        if not path.is_file():
            out[lang] = {}
            continue
        try:
            out[lang] = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            out[lang] = {}
    return out


def main():
    write = "--check" not in sys.argv

    figures = {lang: list_figures(lang) for lang in LANGS}
    photo_taxa = load_photo_taxa()
    data_keys = load_data_keys()
    translations = load_translations()
    families, subfamilies, genera = {}, {}, {}
    per_genus = {}
    species_total = subspecies_total = 0

    for path in sorted(SPECIES_DIR.glob("*.md")):
        slug = path.stem
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        if not fm.get("latin") or not fm.get("family_id") or not fm.get("genus_id"):
            sys.exit("bad front matter in %s" % path.name)
        rank = str(fm.get("rank", "species")).lower()
        is_ssp = rank == "subspecies"
        fid = fm["family_id"].strip()
        sid = (fm.get("subfamily_id") or "").strip()
        gid = fm["genus_id"].strip()

        fam = families.setdefault(fid, {
            "id": fid, "zh": fm["family_zh"].strip(), "latin": fm["family_latin"].strip(),
            "subfamilies": [], "species": 0, "subspecies": 0, "genera": {},
        })
        if is_ssp:
            fam["subspecies"] += 1
        else:
            fam["species"] += 1
        fam["genera"][gid] = True

        if sid:
            sub = subfamilies.setdefault(sid, {
                "id": sid, "zh": fm["subfamily_zh"].strip(), "latin": fm["subfamily_latin"].strip(),
                "family": fid, "species": 0, "subspecies": 0, "genera": {},
            })
            if is_ssp:
                sub["subspecies"] += 1
            else:
                sub["species"] += 1
            sub["genera"][gid] = True
            if sid not in fam["subfamilies"]:
                fam["subfamilies"].append(sid)

        gen = genera.setdefault(gid, {
            "id": gid, "zh": fm["genus_zh"].strip(), "latin": fm["genus_latin"].strip(),
            "family": fid, "subfamily": sid,
            "species": 0, "subspecies": 0, "rows": [], "type_species": "",
        })
        if is_ssp:
            gen["subspecies"] += 1
        else:
            gen["species"] += 1
        if str(fm.get("type", "")).lower() == "true":
            gen["type_species"] = fm["latin"].strip()
        gen["rows"].append({
            "slug": slug, "latin": fm["latin"].strip(), "zh": (fm.get("zh") or "").strip(),
            "author_year": (fm.get("author_year") or "").strip(), "rank": rank,
            "type": str(fm.get("type", "")).lower() == "true",
        })
        if is_ssp:
            subspecies_total += 1
        else:
            species_total += 1

    if species_total != 3021 or subspecies_total != 68:
        sys.exit("unexpected counts: %d species / %d subspecies (expected 3021 / 68)"
                 % (species_total, subspecies_total))
    if len(families) != 13 or len(subfamilies) != 18 or len(genera) != 326:
        sys.exit("unexpected taxa: %d families / %d subfamilies / %d genera"
                 % (len(families), len(subfamilies), len(genera)))

    # 科 / 亚科介绍：三语正文都在 _data/taxon_prose.json；属小节只有地图与物种链接，没有正文。
    intros = {lang: list_sections(lang) for lang in LANGS}
    for lang in LANGS:
        missing = [tid for tid in list(families) + list(subfamilies) if tid not in intros[lang]]
        if missing:
            sys.exit("taxon_prose.json has no %s prose for: %s" % (lang, ", ".join(sorted(missing))))

    # 属级词源：_data/etymology.json 的 genera 键（词根据 Brown 1956, S0018）
    etym_genera = {}
    if ETYMOLOGY_JSON.is_file():
        etym_genera = json.loads(ETYMOLOGY_JSON.read_text(encoding="utf-8")).get("genera") or {}

    for gen in genera.values():
        gen["rows"].sort(key=lambda r: (0 if r["rank"] != "subspecies" else 1,
                                        r["latin"].casefold(), r["slug"]))
    for fam in families.values():
        fam["subfamilies"].sort()
        fam["genera"] = sorted(fam["genera"])
    for sub in subfamilies.values():
        sub["genera"] = sorted(sub["genera"])

    # 亚科级分布图：GBIF 的抓取是按属做的，没有亚科层级；这里把本亚科各属已提交的
    # 1° 网格地图按坐标合并，得到一份可直接给 distribution-map.html 用的单文件。
    subfamily_maps, geo_outputs = [], {}
    for sid in sorted(subfamilies):
        sub = subfamilies[sid]
        cells, generated = {}, ""
        for gid in sub["genera"]:
            path = GEO_GENUS / (gid + ".geojson")
            if not path.is_file():
                continue
            part, stamp = parse_cells(path)
            for key, count in part.items():
                cells[key] = cells.get(key, 0) + count
            generated = stamp or generated
        if not cells:
            continue
        fam = families[sub["family"]]
        props = {
            "level": "subfamily",
            "subfamily": sub["latin"],
            "subfamily_zh": sub["zh"],
            "subfamily_id": sid,
            "family": fam["latin"],
            "family_zh": fam["zh"],
            "family_id": fam["id"],
            "records": sum(cells.values()),
            "cells": len(cells),
            "genera": len(sub["genera"]),
            "species": sub["species"],
            "grid": "1 degree",
            "taxon_scope": "checklist_extant",
            "generated": generated,
            "source": ("merged by build_taxonomy_pages.py from the per-genus 1 degree maps of "
                       "this subfamily; original records: GBIF occurrence search API "
                       "(assets/geo/genus/*.geojson, generated %s)" % generated),
        }
        geo_outputs[GEO_SUBFAMILY / (sid + ".geojson")] = render_geojson(props, cells)
        subfamily_maps.append({
            "id": sid, "zh": sub["zh"], "latin": sub["latin"],
            "family_id": fam["id"], "family_zh": fam["zh"],
            "records": props["records"], "cells": props["cells"],
            "species": sub["species"], "genera": len(sub["genera"]),
            "file": "assets/geo/subfamily/%s.geojson" % sid,
        })
    subfamily_map_ids = {entry["id"] for entry in subfamily_maps}

    images = {"_meta": {"families": len(families), "subfamilies": len(subfamilies),
                        "default": DEFAULT_IMAGE},
              "family": {}, "subfamily": {}}
    for fid in families:
        path = image_path(fid)
        if path:
            images["family"][fid] = path
    for sid in subfamilies:
        path = image_path(sid)
        if path:
            images["subfamily"][sid] = path

    def display_latin(latin):
        return latin.capitalize() if latin.isupper() else latin

    def zh_latin_link(lang, href, zh, latin):
        """站内分类群链接：中文页「中文正名 <i>拉丁名</i>」，外文页「<i>拉丁名</i> 中文正名」。

        外文页把拉丁名放前面，与本页物种/属列表的排法一致（`<i>Amitermitinae</i> 弓白蚁亚科`），
        免得同一页里同一个亚科出现两种词序。
        """
        if lang == "zh-CN":
            return '<a href="%s">%s <i>%s</i></a>' % (href, zh, display_latin(latin))
        return '<a href="%s"><i>%s</i> %s</a>' % (href, display_latin(latin), zh)

    def lp_url(lang, path):
        """站内链接：`{{ site.base_url }}` + 语言前缀 + 路径（契约 §4）。"""
        return SB + LANG_PREFIX[lang] + path

    def taxon_link(lang, taxon_id, rank):
        return lp_url(lang, "/" + rank + "/" + taxon_id + "/")

    def taxon_name(lang, zh, latin):
        """链接 / 面包屑里的「拉丁名 + 中文正名」；zh 页沿用原来只写中文名的做法。"""
        if lang == "zh-CN":
            return zh
        return "%s %s" % (display_latin(latin), zh)

    def stats_line(lang, fam=None, sub=None, gen=None):
        bits = []
        if fam:
            if fam["subfamilies"]:
                bits.append(count_unit(lang, len(fam["subfamilies"]), "subfamily"))
            bits.append(count_unit(lang, len(fam["genera"]), "genus"))
            bits.append(count_phrase(lang, fam["species"], fam["subspecies"]))
        elif sub:
            bits.append(count_unit(lang, len(sub["genera"]), "genus"))
            bits.append(count_phrase(lang, sub["species"], sub["subspecies"]))
        else:
            bits.append(count_phrase(lang, gen["species"], gen["subspecies"]))
        return " · ".join(bits)

    def list_heading(lang, key, n):
        """`亚科（4）` / `Subfamilies (4)` / `Subfamilias (4)`（单复数按 doc §4，标题首字母大写）。"""
        if lang == "zh-CN":
            return "%s（%d）" % (WORDS[lang][key], n)
        one, many = WORDS[lang][key]
        word = one if n == 1 else many
        return "%s (%d)" % (word[0].upper() + word[1:], n)

    def species_heading(lang, gen):
        """`物种（7 种、1 亚种）` / `Species (7)` / `Species (7 species, 1 subspecies)`。

        中文标题里的「种」是量词，不冗余；英文/西文标题已写 Species，`Species (7
        species)` 是同词并列，所以无亚种时外语只给数字，有亚种时用整句计数
        （只有这一种写法能同时交代两个数字，不必再造短语）。
        """
        n, m = gen["species"], gen["subspecies"]
        if lang == "zh-CN":
            return "物种（%s）" % count_phrase(lang, n, m)
        head = {"en": "Species", "es": "Especies"}[lang]
        if not m:
            return "%s (%d)" % (head, n)
        return "%s (%s)" % (head, count_phrase(lang, n, m))

    def meta_line(lang, rank, fam=None, sub=None, gen=None):
        """Page-header count line in one language only.

        The subfamily / genus pages prefix the family name; the Latin name is never
        translated, and the Chinese family name stays as the name-comparison counterpart.
        """
        if rank == "family":
            stats = stats_line(lang, fam=fam)
        elif rank == "subfamily":
            stats = stats_line(lang, sub=sub)
        else:
            stats = stats_line(lang, gen=gen)
        if rank == "family":
            return '<p class="taxon-meta">%s</p>\n' % stats
        latin = display_latin(fam["latin"])
        prefix = {
            "zh-CN": "%s %s" % (fam["zh"], fam["latin"]),
            "en": "Family <i>%s</i>" % latin,
            "es": "Familia <i>%s</i>" % latin,
        }[lang]
        return '<p class="taxon-meta">%s · %s</p>\n' % (prefix, stats)

    def page_h1(lang, rank, zh, latin):
        if lang == "zh-CN":
            return "%s <i>%s</i>" % (zh, display_latin(latin))
        return "%s <i>%s</i> · %s" % (HEAD_PREFIX[lang][rank], display_latin(latin), zh)

    def crumb_nav(lang, rank, fam=None, sub=None, gen=None):
        c = COPY[lang]
        parts = ['<a href="%s">%s</a>' % (lp_url(lang, "/list/"), c["checklist"])]
        if fam:
            parts.append('<a href="%s">%s</a>'
                         % (lp_url(lang, "/family/%s/" % fam["id"]),
                            taxon_name(lang, fam["zh"], fam["latin"])))
        if sub:
            parts.append('<a href="%s">%s</a>'
                         % (lp_url(lang, "/subfamily/%s/" % sub["id"]),
                            taxon_name(lang, sub["zh"], sub["latin"])))
        if gen:
            if lang == "zh-CN":
                label = "%s <i>%s</i>" % (gen["zh"], display_latin(gen["latin"]))
            else:
                label = "<i>%s</i> %s" % (display_latin(gen["latin"]), gen["zh"])
            parts.append('<a href="%s">%s</a>' % (lp_url(lang, "/genus/%s/" % gen["id"]), label))
        return ('<nav class="taxon-crumbs" aria-label="%s">' % c["crumbs_label"]
                + " › ".join(parts) + ' › <span>%s</span></nav>' % c["this_rank"][rank])

    def html_list(items):
        return "<ul class=\"taxon-list\">" + "".join(items) + "</ul>"

    def genus_item(lang, gid):
        gen = genera[gid]
        return ('<li><a href="%s"><i>%s</i> %s</a> <span class="taxon-count">%s</span></li>'
                % (lp_url(lang, "/genus/%s/" % gid), gen["latin"], gen["zh"],
                   count_phrase(lang, gen["species"], gen["subspecies"])))

    def species_items(lang, gen):
        mark_text = COPY[lang]["type_species"]
        out = []
        for row in gen["rows"]:
            mark = (' <span class="taxon-type" title="%s">★ %s</span>' % (mark_text, mark_text)
                    if row["type"] else "")
            # 外文页的正文检查把 ≥12 连续汉字当成残留中文句子；极长的中文正名插 <wbr> 断行。
            name = break_long_cjk(row["zh"]) if lang != "zh-CN" else row["zh"]
            if row["rank"] == "subspecies":
                out.append('<li class="taxon-sub"><a href="%s"><i>%s</i> %s %s</a>%s</li>'
                           % (lp_url(lang, "/species/%s/" % row["slug"]), row["latin"],
                              row["author_year"], name, mark))
            else:
                out.append('<li><a href="%s"><i>%s</i> %s %s</a>%s</li>'
                           % (lp_url(lang, "/species/%s/" % row["slug"]), row["latin"],
                              row["author_year"], name, mark))
        return out

    def taxon_jsonld(lang, rank, taxon_id, latin, zh, parent):
        payload = {
            "@context": "https://schema.org",
            "@type": "Taxon",
            "@id": taxon_link(lang, taxon_id, rank) + "#taxon",
            "name": display_latin(latin),
            "alternateName": [zh],
            "taxonRank": RANK_LABEL[rank],
            "url": taxon_link(lang, taxon_id, rank),
            # 只用 @id 引用首页 / 数据页定义的那个 Dataset 实体，**不要带 @type**：
            # 带 @type 而只有 @id 时，Google 会把每个科/亚科/属页都算成一个 Dataset 条目，
            # 报「未填写字段 name / description / license / creator」（2026-11 的 Search Console 现象）。
            "isPartOf": {"@id": DATASET_ID},
            "version": DATASET_VERSION,
            "dateModified": DATASET_DATE,
        }
        if parent:
            payload["parentTaxon"] = parent
        return ('<script type="application/ld+json">\n'
                + json.dumps(payload, ensure_ascii=False, indent=1) + "\n</script>")

    def figure_html(lang, taxon_id):
        block = (figures[lang] or {}).get(taxon_id) or figures["zh-CN"].get(taxon_id)
        if not block or not image_path(taxon_id):
            return ""
        return "\n" + localize_figure(lang, block) + "\n"

    def desc_zh(rank, fam=None, sub=None, gen=None):
        if rank == "family":
            core = ("%s（%s）是现存等翅下目（Isoptera）下的一个科，本站收录 %s。"
                    % (fam["zh"], fam["latin"],
                       count_phrase_full("zh-CN", len(fam["subfamilies"]), len(fam["genera"]),
                                         fam["species"], fam["subspecies"])))
            pool = [
                "本页按分类系统列出该科的全部%s与属，并汇总各级物种数量。" % ("亚科" if fam["subfamilies"] else ""),
                "点击任一属可查看其全部物种与亚种，点击物种可查看模式产地、分布地图、同属物种与 GB/T 7714、BibTeX、RIS 引用格式。",
                "科的形态特征、分布格局与经济意义见本页上文。",
            ]
            if not fam["subfamilies"]:
                pool[0] = "本页按分类系统列出该科的全部属，并汇总各级物种数量。"
            return fit_description(core, pool)
        if rank == "subfamily":
            parent = families[sub["family"]]
            core = ("%s（%s）是%s（%s）下的一个亚科，本站收录 %s。"
                    % (sub["zh"], sub["latin"], parent["zh"], parent["latin"],
                       count_phrase_full("zh-CN", 0, len(sub["genera"]), sub["species"],
                                         sub["subspecies"])))
            pool = [
                "本页列出该亚科下属的全部属及其物种数量，逐级链接到属页面与物种页面。",
                "物种页包含拉丁学名与命名人年份、中文正名、模式产地、分布地图、同属物种、参考文献与引用格式。",
                "亚科的形态、分布与经济意义见本页上文。",
            ]
            return fit_description(core, pool)
        parent = families[gen["family"]]
        where = ""
        if gen["subfamily"]:
            where = "，隶属%s（%s）" % (subfamilies[gen["subfamily"]]["zh"],
                                         subfamilies[gen["subfamily"]]["latin"])
        core = ("%s（%s）是%s（%s）下的一个属%s，本站收录 %s。"
                % (gen["zh"], gen["latin"], parent["zh"], parent["latin"], where,
                   count_phrase("zh-CN", gen["species"], gen["subspecies"])))
        pool = [
            "本页列出该属的全部物种与亚种%s，物种页含模式产地、分布地图与同属物种。" % ("，并标注模式种" if gen["type_species"] else ""),
            "每一条目均可跳转到对应的物种页面，查看拉丁学名、命名人年份、中文正名、参考文献与引用格式。",
            "属的分类位置见名录索引与上级科、亚科页面。",
        ]
        return fit_description(core, pool)

    def desc_foreign(lang, rank, fam=None, sub=None, gen=None):
        """en/es 的 description：同样是 150-160 字符、全站唯一（Lead 要求外文页同口径）。

        每个阶元准备 4 句长度不同的 core（同一事实、不同句法），再用 LOCAL_POOL /
        LOCAL_FILLERS 的短句把长度补进窗口：中文按字计、英文按字符计，固定模板的长度
        随学名长短浮动，所以必须靠多种长度的模板 + 补尾句组合，不能靠放宽下限。
        """
        pool = LOCAL_POOL[lang][rank] + LOCAL_TAILS[lang]
        if rank == "family":
            counts = count_phrase_full(lang, len(fam["subfamilies"]), len(fam["genera"]),
                                       fam["species"], fam["subspecies"])
            if lang == "en":
                cores = [
                    "The family %s (%s) is one of the extant termite families (Isoptera); "
                    "the site records %s." % (display_latin(fam["latin"]), fam["zh"], counts),
                    "Family %s (%s), one of the extant termite families (Isoptera); "
                    "the site records %s." % (display_latin(fam["latin"]), fam["zh"], counts),
                    "The family %s (%s), in the extant termites (Isoptera); the site records %s."
                    % (display_latin(fam["latin"]), fam["zh"], counts),
                    "Termite family %s (%s), treated on this site; the site records %s."
                    % (display_latin(fam["latin"]), fam["zh"], counts),
                ]
            else:
                cores = [
                    "La familia %s (%s) es una de las familias de termitas actuales (Isoptera); "
                    "el sitio registra %s." % (display_latin(fam["latin"]), fam["zh"], counts),
                    "Familia %s (%s), una de las familias de termitas actuales (Isoptera); "
                    "el sitio registra %s." % (display_latin(fam["latin"]), fam["zh"], counts),
                    "La familia %s (%s), entre las termitas actuales (Isoptera); el sitio "
                    "registra %s." % (display_latin(fam["latin"]), fam["zh"], counts),
                    "Familia de termitas %s (%s), tratada en este sitio; el sitio registra %s."
                    % (display_latin(fam["latin"]), fam["zh"], counts),
                ]
        elif rank == "subfamily":
            parent = families[sub["family"]]
            counts = count_phrase_full(lang, 0, len(sub["genera"]), sub["species"],
                                       sub["subspecies"])
            if lang == "en":
                cores = [
                    "The subfamily %s (%s) belongs to the family %s (%s); the site records %s."
                    % (display_latin(sub["latin"]), sub["zh"], display_latin(parent["latin"]), parent["zh"], counts),
                    "Subfamily %s (%s) of the family %s (%s); the site records %s."
                    % (display_latin(sub["latin"]), sub["zh"], display_latin(parent["latin"]), parent["zh"], counts),
                    "The subfamily %s (%s), in the family %s (%s); the site records %s."
                    % (display_latin(sub["latin"]), sub["zh"], display_latin(parent["latin"]), parent["zh"], counts),
                    "Subfamily %s (%s), family %s (%s); the site records %s."
                    % (display_latin(sub["latin"]), sub["zh"], display_latin(parent["latin"]), parent["zh"], counts),
                ]
            else:
                cores = [
                    "La subfamilia %s (%s) pertenece a la familia %s (%s); el sitio registra %s."
                    % (display_latin(sub["latin"]), sub["zh"], display_latin(parent["latin"]), parent["zh"], counts),
                    "Subfamilia %s (%s) de la familia %s (%s); el sitio registra %s."
                    % (display_latin(sub["latin"]), sub["zh"], display_latin(parent["latin"]), parent["zh"], counts),
                    "La subfamilia %s (%s), en la familia %s (%s); el sitio registra %s."
                    % (display_latin(sub["latin"]), sub["zh"], display_latin(parent["latin"]), parent["zh"], counts),
                    "Subfamilia %s (%s), familia %s (%s); el sitio registra %s."
                    % (display_latin(sub["latin"]), sub["zh"], display_latin(parent["latin"]), parent["zh"], counts),
                ]
        else:
            parent = families[gen["family"]]
            where = ""
            if gen["subfamily"]:
                s = subfamilies[gen["subfamily"]]
                if lang == "en":
                    where = ", in the subfamily %s (%s)" % (s["latin"], s["zh"])
                else:
                    where = ", en la subfamilia %s (%s)" % (s["latin"], s["zh"])
            counts = count_phrase(lang, gen["species"], gen["subspecies"])
            if lang == "en":
                cores = [
                    "The genus %s (%s) belongs to the family %s (%s)%s; the site records %s."
                    % (display_latin(gen["latin"]), gen["zh"], display_latin(parent["latin"]), parent["zh"], where, counts),
                    "Genus %s (%s), in the family %s (%s)%s; the site records %s."
                    % (display_latin(gen["latin"]), gen["zh"], display_latin(parent["latin"]), parent["zh"], where, counts),
                    "The genus %s (%s) is placed in the family %s (%s)%s; the site records %s."
                    % (display_latin(gen["latin"]), gen["zh"], display_latin(parent["latin"]), parent["zh"], where, counts),
                    "Genus %s (%s); family %s (%s)%s; the site records %s."
                    % (display_latin(gen["latin"]), gen["zh"], display_latin(parent["latin"]), parent["zh"], where, counts),
                ]
            else:
                cores = [
                    "El género %s (%s) pertenece a la familia %s (%s)%s; el sitio registra %s."
                    % (display_latin(gen["latin"]), gen["zh"], display_latin(parent["latin"]), parent["zh"], where, counts),
                    "Género %s (%s), de la familia %s (%s)%s; el sitio registra %s."
                    % (display_latin(gen["latin"]), gen["zh"], display_latin(parent["latin"]), parent["zh"], where, counts),
                    "El género %s (%s) se sitúa en la familia %s (%s)%s; el sitio registra %s."
                    % (display_latin(gen["latin"]), gen["zh"], display_latin(parent["latin"]), parent["zh"], where, counts),
                    "Género %s (%s); familia %s (%s)%s; el sitio registra %s."
                    % (display_latin(gen["latin"]), gen["zh"], display_latin(parent["latin"]), parent["zh"], where, counts),
                ]
        for core in cores:
            if len(core) > DESC_MAX:
                continue
            fitted = fit_localized(core, pool)
            if DESC_MIN <= len(fitted) <= DESC_MAX:
                return fitted
        return min(cores, key=len)

    def desc_for(lang, rank, fam=None, sub=None, gen=None):
        if lang == "zh-CN":
            return desc_zh(rank, fam=fam, sub=sub, gen=gen)
        return desc_foreign(lang, rank, fam=fam, sub=sub, gen=gen)

    def page_title(lang, rank, zh, latin):
        if lang == "zh-CN":
            return TITLE_FMT[lang][rank] % (zh, latin)
        return TITLE_FMT[lang][rank] % (display_latin(latin), zh)

    def front_matter(lang, title, description, permalink, breadcrumb, image, family_id,
                     last_modified="2026-10-30", has_map=False, taxon_search=False,
                     has_photos=False, translation_pending=False):
        lines = ["---", "layout: default", "title: " + json.dumps(title, ensure_ascii=False),
                 "description: " + json.dumps(description, ensure_ascii=False),
                 "lang: " + lang,
                 # 单语言页标记：_layouts/default.html 用它替代原来的 lang_only
                 # （语言切换器、hreflang 只对「人工翻好的整页」判断，不再看 lang_only）。
                 "single_lang: true",
                 "author: 班奈特格林",
                 "family_id: " + family_id,
                 "last_modified_at: " + last_modified,
                 "permalink: " + LANG_PREFIX[lang] + permalink, "sitemap: true"]
        if has_map:
            lines.append("has_map: true")
        if taxon_search:
            lines.append("taxon_search: true")
        if has_photos:
            lines.append("has_photos: true")
        if translation_pending:
            lines.append("translation_pending: true")
        if image:
            lines.append("image: " + json.dumps(image))
        lines.append("breadcrumb:")
        for crumb in breadcrumb:
            lines.append("  - name: " + json.dumps(crumb[0], ensure_ascii=False))
            lines.append("    url: " + json.dumps(crumb[1]))
        lines.append("---")
        return "\n".join(lines) + "\n"

    def breadcrumb_for(lang, rank, fam=None, sub=None, gen=None):
        crumbs = [(COPY[lang]["checklist"], LANG_PREFIX[lang] + "/list/")]
        if fam:
            crumbs.append((taxon_name(lang, fam["zh"], fam["latin"]),
                           LANG_PREFIX[lang] + "/family/%s/" % fam["id"]))
        if sub:
            crumbs.append((taxon_name(lang, sub["zh"], sub["latin"]),
                           LANG_PREFIX[lang] + "/subfamily/%s/" % sub["id"]))
        if gen:
            if lang == "zh-CN":
                name = "%s %s" % (gen["zh"], gen["latin"])
            else:
                name = "%s %s" % (display_latin(gen["latin"]), gen["zh"])
            crumbs.append((name, LANG_PREFIX[lang] + "/genus/%s/" % gen["id"]))
        return crumbs

    def footer_nav(lang, rank, taxon_id, up=None):
        """上下级导航：名录索引是唯一入口，逐级可以往回走（链接一律带语言前缀）。"""
        c = COPY[lang]
        links = ['<a href="%s">%s</a>' % (lp_url(lang, "/list/"), c["checklist_index"])]
        if up:
            links.append(up)
        links.append('<a href="%s">%s</a>' % (lp_url(lang, "/data/"), c["data"]))
        sep = "：" if lang == "zh-CN" else ": "
        back = ('<p class="taxon-more">%s%s%s</p>'
                % (c["parent_level"], sep, " · ".join(links)))
        return (back + '\n<p class="taxon-back"><a href="%s">%s</a> · <a href="%s">%s</a></p>'
                % (lp_url(lang, "/list/"), c["back_checklist"], lp_url(lang, "/"), c["home"]))

    def genus_up(lang, gen):
        """属页的上一级：有亚科就指亚科页，否则指科页。"""
        if gen["subfamily"]:
            sub = subfamilies[gen["subfamily"]]
            return zh_latin_link(lang, lp_url(lang, "/subfamily/%s/" % sub["id"]),
                                 sub["zh"], sub["latin"])
        fam = families[gen["family"]]
        return zh_latin_link(lang, lp_url(lang, "/family/%s/" % fam["id"]),
                             fam["zh"], fam["latin"])

    def has_geo(rank, taxon_id):
        if rank == "subfamily":
            return taxon_id in subfamily_map_ids
        directory = {"family": GEO_FAMILY, "genus": GEO_GENUS}[rank]
        return (directory / (taxon_id + ".geojson")).is_file()

    def distribution_section(lang, rank, taxon_id):
        if not has_geo(rank, taxon_id):
            return ""
        return ('<section class="taxon-section taxon-distribution" data-pagefind-ignore>\n'
                '<h2>%s</h2>\n'
                '{%% include distribution-map.html mode="%s" id="%s" %%}\n'
                '</section>\n' % (COPY[lang]["distribution"], rank, taxon_id))

    def photo_section(rank, taxon_id):
        """图片小节：6 张预览 + 「查看全部 N 张」→ /<LP>/<rank>/<id>/photos/。

        照片本体由 _includes/taxon-photos.html 渲染（它自己按 page.lang 分支、链接带
        语言前缀），这里只决定要不要出现，避免没有照片的分类单元留下一个空占位。
        """
        if not photo_taxa[rank].get(taxon_id):
            return ""
        return ('<section class="taxon-section taxon-photos-section" data-pagefind-ignore>\n'
                '{%% include taxon-photos.html kind="%s" id="%s" limit=6 more="1" %%}\n'
                '</section>\n' % (rank, taxon_id))

    def intro_section(lang, rank, taxon_id):
        paragraphs = intros[lang].get(taxon_id) or []
        if not paragraphs:
            return ""
        body = "".join("<p>%s</p>\n" % html_escape(p) for p in paragraphs)
        return ('<section class="taxon-section taxon-intro">\n<h2>'
                + COPY[lang]["about"][rank] + '</h2>\n'
                + body
                + (INTRO_SRC[lang] % {"list": lp_url(lang, "/list/")})
                + '</section>\n')

    def genus_intro(lang, gen, mapped):
        fam = families[gen["family"]]
        fam_link = zh_latin_link(lang, lp_url(lang, "/family/%s/" % fam["id"]),
                                 fam["zh"], fam["latin"])
        sub_link = None
        if gen["subfamily"]:
            sub = subfamilies[gen["subfamily"]]
            sub_link = zh_latin_link(lang, lp_url(lang, "/subfamily/%s/" % sub["id"]),
                                     sub["zh"], sub["latin"])
        counts = count_phrase(lang, gen["species"], gen["subspecies"])
        if lang == "zh-CN":
            text = "本属隶属" + fam_link
            if sub_link:
                text += "下的" + sub_link
            text += "，本站收录 %s。" % counts
            paragraphs = [text]
        elif lang == "en":
            text = "This genus belongs to the family " + fam_link
            if sub_link:
                text += ", in the subfamily " + sub_link
            text += "; the site records %s." % counts
            paragraphs = [text]
        else:
            text = "Este género pertenece a la familia " + fam_link
            if sub_link:
                text += ", en la subfamilia " + sub_link
            text += "; el sitio registra %s." % counts
            paragraphs = [text]
        if gen["type_species"]:
            paragraphs.append("%s<i>%s</i>%s" % (
                {"zh-CN": "模式种：", "en": "Type species: ", "es": "Especie tipo: "}[lang],
                gen["type_species"], {"zh-CN": "。", "en": ".", "es": "."}[lang]))
        if mapped:
            paragraphs.append({
                "zh-CN": "本页附有本属的分布图（GBIF 记录按 1° 网格汇总）；"
                         "点开物种条目可查看各自模式产地、分布与参考文献。",
                "en": "This page includes a distribution map for the genus (GBIF records "
                      "aggregated on a 1° grid); open a species entry to see its type "
                      "locality, distribution, and references.",
                "es": "Esta página incluye un mapa de distribución del género (registros de "
                      "GBIF agregados en una cuadrícula de 1°); abra una entrada de especie "
                      "para ver su localidad tipo, distribución y referencias.",
            }[lang])
        else:
            paragraphs.append({
                "zh-CN": "GBIF 中暂无本属带坐标的记录，本页因此不附图；"
                         "点开物种条目仍可查看各自模式产地与参考文献。",
                "en": "GBIF has no georeferenced records for this genus, so this page has no "
                      "map; open a species entry to see its type locality and references.",
                "es": "GBIF no tiene registros con coordenadas para este género, por lo que "
                      "esta página no incluye mapa; abra una entrada de especie para ver su "
                      "localidad tipo y referencias.",
            }[lang])
        body = "".join("<p>%s</p>\n" % text for text in paragraphs)
        return ('<section class="taxon-section taxon-intro" data-pagefind-ignore>\n'
                '<h2>%s</h2>\n' % COPY[lang]["about"]["genus"]
                + body + "</section>\n")

    # 数据键必须与 _data/ 里的文件名一致：_data/fauna_families.json → site.data.fauna_families。
    # 曾按单数拼成 fauna_family / fauna_genus，与文件名不匹配 → fz 恒为 nil，
    # 整段形态描述永远不渲染（且不报错），只有页面 diff 会露馅。
    FAUNA_DATA_KEY = {"family": "fauna_families", "genus": "fauna_genera", "species": "fauna_species"}

    def fauna_section(lang, kind, taxon_id):
        """据《中国动物志·昆虫纲 第十七卷 等翅目》(2000) 改写而来的形态描述。

        数据在 _data/fauna_<复数>.json，键为页面 URL；没有对应条目时不输出任何内容。
        en/es 章从 _data/translations_<lang>.json 的同名桶取译文，取不到时整节省略
        （不回退中文）。include 内不再做语言判断，只渲染传进去的那份数据。
        """
        url = "/%s/%s/" % (kind, taxon_id)
        if lang == "zh-CN":
            source = 'site.data.%s["%s"]' % (FAUNA_DATA_KEY[kind], url)
        else:
            source = 'site.data.translations_%s.%s["%s"]' % (
                lang, FAUNA_DATA_KEY[kind], url)
        # 英文页另送 _data/fauna_*.json 里原有的英文摘要（`en` 字段）：那条摘要本来就是
        # 用英文写的，译文桶不重复收录，若不单独传进来，拆页后全站就再也看不到它。
        # 中文与西语页不传（各自语言没有对应内容，不拿英文兜底）。
        # 摘要先在页面里 assign 成变量再传：Jekyll 的 include 标签对未加引号的参数值只认
        # [\w.-]+，把 site.data.x["/family/y/"].en 这种带引号方括号的查找直接写进参数会被
        # 判为语法错误（整页 500）。顺带也保证 fza 为 nil 时 include 里 if 判断照常成立。
        abstract_assign = ""
        extra = ""
        if lang == "en":
            abstract_assign = '{%%- assign fza = site.data.%s["%s"].en -%%}' % (
                FAUNA_DATA_KEY[kind], url)
            extra = " abstract=fza"
        return ('%s{%%- assign fz = %s -%%}'
                '{%%- if fz %%}\n{%% include fauna-%s.html fauna=fz%s %%}\n{%%- endif %%}\n'
                % (abstract_assign, source, kind, extra))

    # 2025-11: 中国动物志的检索表已撤下，只保留 Hellemans et al. (2024) 的目级/白蚁科
    # 亚科表与 Krishna et al. (2013) 的木白蚁科世界分属表。以下三页之外不再输出检索表，
    # 免得 326 个属页各留一个空的 include。
    KEYS_PAGES = {"/list/", "/family/kalotermitidae/", "/family/termitidae/"}

    def keys_section(lang, kind, taxon_id):
        """形态检索表：仅保留非中国动物志来源的表（目级、白蚁科亚科、木白蚁科世界分属）。

        数据在 _data/fauna_keys.json（键为页面 URL），来源逐表标注。检索表按「组」折叠
        显示，终端一律链到站内页面。没有保留表的页面不输出任何内容。
        en/es 页取 translations_<lang>.json 的 fauna_keys 桶，缺译文时整节省略。
        """
        url = "/%s/%s/" % (kind, taxon_id)
        if url not in KEYS_PAGES:
            return ""
        if lang == "zh-CN":
            source = 'site.data.fauna_keys["%s"]' % url
        else:
            source = 'site.data.translations_%s.fauna_keys["%s"]' % (lang, url)
        return ('{%%- assign fk = %s -%%}'
                '{%%- if fk %%}\n{%% include fauna-keys.html fk=fk %%}\n{%%- endif %%}\n'
                % source)

    def genus_morphology_section():
        """属级形态描述：有《中国动物志》条目时由 fauna_section 渲染，否则由
        _includes/genus-morphology.html 给出「待补」占位与原始描述出处。"""
        return '{% include genus-morphology.html %}\n'

    def literature_section():
        """人工整理的研究记述（_data/taxon_literature.json，按 page.url 取）。"""
        return '{% include taxon-literature.html %}\n'

    def genus_map_note(lang, gen):
        fam = families[gen["family"]]
        fam_latin = display_latin(fam["latin"])
        if lang == "zh-CN":
            links = ['<a href="%s">%s的科级分布图</a>' % (lp_url(lang, "/family/%s/" % fam["id"]),
                                                          fam["zh"])]
        elif lang == "en":
            links = ['<a href="%s">the family map for <i>%s</i></a>'
                     % (lp_url(lang, "/family/%s/" % fam["id"]), fam_latin)]
        else:
            links = ['<a href="%s">el mapa de la familia <i>%s</i></a>'
                     % (lp_url(lang, "/family/%s/" % fam["id"]), fam_latin)]
        if gen["subfamily"]:
            sub = subfamilies[gen["subfamily"]]
            sub_latin = display_latin(sub["latin"])
            if lang == "zh-CN":
                links.append('<a href="%s">%s的亚科级分布图</a>'
                             % (lp_url(lang, "/subfamily/%s/" % sub["id"]), sub["zh"]))
            elif lang == "en":
                links.append('<a href="%s">the subfamily map for <i>%s</i></a>'
                             % (lp_url(lang, "/subfamily/%s/" % sub["id"]), sub_latin))
            else:
                links.append('<a href="%s">el mapa de la subfamilia <i>%s</i></a>'
                             % (lp_url(lang, "/subfamily/%s/" % sub["id"]), sub_latin))
        if lang == "zh-CN":
            note = ("GBIF 中暂无该属带坐标的记录，因此本页没有属级地图；可参考%s。"
                    % "或".join(links))
        elif lang == "en":
            note = ("GBIF has no georeferenced records for this genus, so this page has no "
                    "genus-level map; see %s." % " or ".join(links))
        else:
            note = ("GBIF no tiene registros con coordenadas para este género, por lo que esta "
                    "página no incluye un mapa de nivel de género; consulte %s."
                    % " o ".join(links))
        return ('<section class="taxon-section taxon-distribution" data-pagefind-ignore>\n'
                '<h2>%s</h2>\n<p class="taxon-map-empty">%s</p>\n</section>\n'
                % (COPY[lang]["distribution"], note))

    def search_box(lang, rank, anchors, species, subspecies):
        """页内局部检索框（assets/taxon-search.js）。

        data-lang / data-lang-prefix 让脚本按本页语言出结果标签、并把结果链到同语言页面；
        data-index 仍指向站根唯一的 search-index.json（en/es 暂无独立索引）。
        """
        scope = COPY[lang]["search_scope"][rank]
        noun = COPY[lang]["rank_noun"][rank]
        if lang == "zh-CN":
            label = "在本%s范围内检索（%d 个种与亚种）：名字、分布或模式产地" % (
                noun, species + subspecies)
            hint = ('按名字与产地筛选本%s登记的分类单元；全站网页请用'
                    '<a href="%s">全文搜索</a>。' % (noun, lp_url(lang, "/search/")))
        elif lang == "en":
            label = ("Search within %s (%s): name, distribution, or type locality"
                     % (scope, count_phrase(lang, species, subspecies)))
            hint = ('Filter the taxa recorded under %s by name and locality; for the whole '
                    'site use the <a href="%s">full-text search</a>.'
                    % (scope, lp_url(lang, "/search/")))
        else:
            label = ("Buscar en %s (%s): nombre, distribución o localidad tipo"
                     % (scope, count_phrase(lang, species, subspecies)))
            hint = ('Filtre por nombre y localidad los taxones registrados en %s; para todo '
                    'el sitio use la <a href="%s">búsqueda de texto completo</a>.'
                    % (scope, lp_url(lang, "/search/")))
        return (
            '<div class="taxon-search" data-pagefind-ignore data-lang="%s" '
            'data-lang-prefix="%s" data-anchors="%s" data-index="%s/search-index.json" '
            'data-search-page="%s">\n'
            '<label class="taxon-search-label" for="taxon-search-input">%s</label>\n'
            '<input type="search" id="taxon-search-input" class="taxon-search-input" '
            'placeholder="%s" autocomplete="off" spellcheck="false" '
            'role="combobox" aria-expanded="false" aria-controls="taxon-search-results" '
            'aria-autocomplete="list">\n'
            '<p class="taxon-search-status" hidden></p>\n'
            '<ul class="taxon-search-results" hidden></ul>\n'
            '<p class="taxon-search-hint">%s</p>\n'
            '</div>\n'
            % (lang, LANG_PREFIX[lang], ",".join(anchors), SB, lp_url(lang, "/search/"),
               label, COPY[lang]["search_placeholder"], hint))

    def etymology_section(lang, gid):
        """属级词源（每页只渲染本页语言），来自 _data/etymology.json（词根据 Brown 1956, S0018）。

        en/es 只在对应字段非空时输出——缺失时整段跳过，绝不拿中文顶替。
        """
        entry = (etym_genera or {}).get(gid)
        if not entry:
            return ""
        text = html_escape((entry.get(lang) or "").strip())
        if not text:
            return ""
        return ('<section class="taxon-section taxon-etymology" data-pagefind-ignore>\n'
                '<h2>%s</h2>\n<p>%s</p>\n<!-- src:S0018 -->\n%s</section>\n'
                % (COPY[lang]["etymology"], text, ETYM_SRC[lang]))

    def translation_pending(lang, kind, taxon_id):
        """本页中文数据有、本语言译文缺 → 页面末尾挂一句提示（不回退中文）。

        只看「这一节本来会不会渲染」：fauna 条目、属级形态改写稿、检索表三类。
        科/亚科正文（taxon_prose.json）由本脚本直接按语言取，不缺。
        """
        if lang == "zh-CN":
            return False
        url = "/%s/%s/" % (kind, taxon_id)
        buckets = []
        if kind == "family":
            buckets.append("fauna_families")
        else:
            buckets.append("fauna_genera")
            buckets.append("morphology_genera")
        buckets.append("fauna_keys")
        translated = translations.get(lang) or {}
        for bucket in buckets:
            if url not in data_keys[bucket]:
                continue
            if not ((translated.get(bucket) or {}).get(url)):
                return True
        return False

    outputs = {}
    for lang in LANGS:
        for fid in sorted(families):
            fam = families[fid]
            parent = {"@type": "Taxon", "name": "Isoptera", "alternateName": ["现存等翅下目"],
                      "taxonRank": "Infraorder"}
            sections = []
            if fam["subfamilies"]:
                items = []
                for sid in fam["subfamilies"]:
                    sub = subfamilies[sid]
                    items.append('<li><a href="%s"><i>%s</i> %s</a> '
                                 '<span class="taxon-count">%s</span></li>'
                                 % (lp_url(lang, "/subfamily/%s/" % sid), sub["latin"], sub["zh"],
                                    count_phrase_full(lang, 0, len(sub["genera"]), sub["species"],
                                                      sub["subspecies"])))
                sections.append("<h2>" + list_heading(lang, "subfamily", len(fam["subfamilies"]))
                                + "</h2>" + html_list(items))
            genus_items = [genus_item(lang, gid) for gid in fam["genera"]]
            sections.append("<h2>" + list_heading(lang, "genus", len(fam["genera"]))
                            + "</h2>" + html_list(genus_items))
            body = (
                '<article class="taxon-page">\n'
                + crumb_nav(lang, "family", fam=fam) + "\n"
                + '<header class="taxon-header">\n'
                + '<h1>%s</h1>\n' % page_h1(lang, "family", fam["zh"], fam["latin"])
                + meta_line(lang, "family", fam=fam)
                + "</header>\n"
                + search_box(lang, "family", [fid] + fam["subfamilies"] + fam["genera"],
                             fam["species"], fam["subspecies"])
                + figure_html(lang, fid)
                + distribution_section(lang, "family", fid)
                + photo_section("family", fid)
                + intro_section(lang, "family", fid)
                + fauna_section(lang, "family", fid)
                + keys_section(lang, "family", fid)
                + literature_section()
                + "\n".join('<section class="taxon-section">\n' + s + "\n</section>"
                            for s in sections) + "\n"
                + footer_nav(lang, "family", fid) + "\n</article>\n"
                + taxon_jsonld(lang, "family", fid, fam["latin"], fam["zh"], parent)
            )
            desc = desc_for(lang, "family", fam=fam)
            outputs[OUT_DIRS[lang]["family"] / (fid + ".md")] = (
                front_matter(lang, page_title(lang, "family", fam["zh"], fam["latin"]), desc,
                             "/family/%s/" % fid, breadcrumb_for(lang, "family", fam=fam),
                             image_path(fid), fid,
                             has_map=has_geo("family", fid), taxon_search=True,
                             has_photos=bool(photo_taxa["family"].get(fid)),
                             translation_pending=translation_pending(lang, "family", fid))
                + body)

        for sid in sorted(subfamilies):
            sub = subfamilies[sid]
            fam = families[sub["family"]]
            parent = {"@type": "Taxon", "name": display_latin(fam["latin"]),
                      "alternateName": [fam["zh"]], "taxonRank": "Family",
                      "url": lp_url(lang, "/family/%s/" % fam["id"])}
            sections = []
            items = [genus_item(lang, gid) for gid in sub["genera"]]
            sections.append("<h2>" + list_heading(lang, "genus", len(sub["genera"]))
                            + "</h2>" + html_list(items))
            body = (
                '<article class="taxon-page">\n'
                + crumb_nav(lang, "subfamily", fam=fam, sub=sub) + "\n"
                + '<header class="taxon-header">\n'
                + '<h1>%s</h1>\n' % page_h1(lang, "subfamily", sub["zh"], sub["latin"])
                + meta_line(lang, "subfamily", fam=fam, sub=sub)
                + "</header>\n"
                + search_box(lang, "subfamily", [sid] + sub["genera"],
                             sub["species"], sub["subspecies"])
                + figure_html(lang, sid)
                + distribution_section(lang, "subfamily", sid)
                + photo_section("subfamily", sid)
                + intro_section(lang, "subfamily", sid)
                + keys_section(lang, "subfamily", sid)
                + literature_section()
                + "\n".join('<section class="taxon-section">\n' + s + "\n</section>"
                            for s in sections) + "\n"
                + footer_nav(lang, "subfamily", sid,
                             zh_latin_link(lang, lp_url(lang, "/family/%s/" % fam["id"]),
                                           fam["zh"], fam["latin"])) + "\n</article>\n"
                + taxon_jsonld(lang, "subfamily", sid, sub["latin"], sub["zh"], parent)
            )
            desc = desc_for(lang, "subfamily", sub=sub)
            outputs[OUT_DIRS[lang]["subfamily"] / (sid + ".md")] = (
                front_matter(lang, page_title(lang, "subfamily", sub["zh"], sub["latin"]), desc,
                             "/subfamily/%s/" % sid,
                             breadcrumb_for(lang, "subfamily", fam=fam, sub=sub),
                             image_path(sid), fam["id"],
                             has_map=has_geo("subfamily", sid), taxon_search=True,
                             has_photos=bool(photo_taxa["subfamily"].get(sid)),
                             translation_pending=translation_pending(lang, "subfamily", sid))
                + body)

        for gid in sorted(genera):
            gen = genera[gid]
            fam = families[gen["family"]]
            if gen["subfamily"]:
                sub = subfamilies[gen["subfamily"]]
                parent = {"@type": "Taxon", "name": display_latin(sub["latin"]),
                          "alternateName": [sub["zh"]], "taxonRank": "Subfamily",
                          "url": lp_url(lang, "/subfamily/%s/" % sub["id"])}
            else:
                parent = {"@type": "Taxon", "name": display_latin(fam["latin"]),
                          "alternateName": [fam["zh"]], "taxonRank": "Family",
                          "url": lp_url(lang, "/family/%s/" % fam["id"])}
            sections = ['<h2>' + species_heading(lang, gen) + '</h2>'
                        + html_list(species_items(lang, gen))]
            mapped = has_geo("genus", gid)
            body = (
                '<article class="taxon-page">\n'
                + crumb_nav(lang, "genus", fam=fam, sub=subfamilies.get(gen["subfamily"]),
                            gen=gen) + "\n"
                + '<header class="taxon-header">\n'
                + '<h1>%s</h1>\n' % page_h1(lang, "genus", gen["zh"], gen["latin"])
                + meta_line(lang, "genus", fam=fam, gen=gen)
                + "</header>\n"
                + search_box(lang, "genus", [gid], gen["species"], gen["subspecies"])
                + figure_html(lang, gid)
                + (distribution_section(lang, "genus", gid) if mapped
                   else genus_map_note(lang, gen))
                + photo_section("genus", gid)
                + genus_intro(lang, gen, mapped)
                + etymology_section(lang, gid)
                + fauna_section(lang, "genus", gid)
                + genus_morphology_section()
                + keys_section(lang, "genus", gid)
                + literature_section()
                + "\n".join('<section class="taxon-section">\n' + s + "\n</section>"
                            for s in sections) + "\n"
                + footer_nav(lang, "genus", gid, genus_up(lang, gen)) + "\n</article>\n"
                + taxon_jsonld(lang, "genus", gid, gen["latin"], gen["zh"], parent)
            )
            desc = desc_for(lang, "genus", gen=gen)
            outputs[OUT_DIRS[lang]["genus"] / (gid + ".md")] = (
                front_matter(lang, page_title(lang, "genus", gen["zh"], gen["latin"]), desc,
                             "/genus/%s/" % gid,
                             breadcrumb_for(lang, "genus", fam=fam,
                                            sub=subfamilies.get(gen["subfamily"]), gen=gen),
                             image_path(gen["family"]), fam["id"],
                             has_map=mapped, taxon_search=True,
                             has_photos=bool(photo_taxa["genus"].get(gid)),
                             translation_pending=translation_pending(lang, "genus", gid))
                + body)

    # 生成后的机械校验：描述长度/唯一、外文页无三语残留、外文页链接带前缀。
    # 这些和 _tools/check_lang_pages.py 重复是有意的——生成器自己做一次，跑 --check 时
    # 不必再等站点级检查才发现问题。
    problem = False
    descs = {}
    for path, content in sorted(outputs.items()):
        rel = path.relative_to(ROOT)
        fm = parse_front_matter(content)
        lang = fm.get("lang", "zh-CN")
        desc = fm.get("description", "")
        if not (DESC_MIN <= len(desc) <= DESC_MAX):
            print("BAD desc length %d (allowed %d-%d): %s (%s)"
                  % (len(desc), DESC_MIN, DESC_MAX, rel, desc))
            problem = True
        if desc in descs:
            print("DUP desc: %s and %s" % (descs[desc], rel))
            problem = True
        descs[desc] = rel
        for mark in ("fact-en", "fact-es", "EN —", "ES —"):
            if mark in content:
                print("three-language leftover %r: %s" % (mark, rel))
                problem = True
        if lang == "zh-CN":
            continue
        body = content.split("\n---\n", 1)[1] if "\n---\n" in content else content
        for ch in "。；，、！？「」：（）":
            if ch in body:
                print("Chinese punctuation %r on a %s page: %s" % (ch, lang, rel))
                problem = True
                break
        for pat in ("site.base_url }}/family/", "site.base_url }}/subfamily/",
                    "site.base_url }}/genus/", "site.base_url }}/species/",
                    "site.base_url }}/list/", "site.base_url }}/data/"):
            if pat in body:
                print("link without language prefix %r: %s" % (pat, rel))
                problem = True
                break

    if problem:
        sys.exit("refusing to write: page checks above")

    changed = 0
    for path, content in sorted(outputs.items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        changed += 1
        if write:
            with path.open("w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)
    stale = 0
    for lang in LANGS:
        for rank, out_dir in OUT_DIRS[lang].items():
            expected = {p.name for p in outputs if p.parent == out_dir}
            if out_dir.is_dir():
                for path in sorted(out_dir.glob("*.md")):
                    if path.name not in expected:
                        stale += 1
                        print("stale page: %s" % path.relative_to(ROOT))
                        if write:
                            path.unlink()

    geo_changed = 0
    for path, content in sorted(geo_outputs.items()):
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        geo_changed += 1
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    geo_stale = 0
    if GEO_SUBFAMILY.is_dir():
        for path in sorted(GEO_SUBFAMILY.glob("*.geojson")):
            if path in geo_outputs:
                continue
            geo_stale += 1
            print("stale map: %s" % path.relative_to(ROOT))
            if write:
                path.unlink()

    payload = json.dumps(images, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    data_changed = not DATA_OUT.is_file() or DATA_OUT.read_text(encoding="utf-8") != payload
    if data_changed and write:
        DATA_OUT.write_text(payload, encoding="utf-8", newline="\n")

    maps_payload = json.dumps({
        "_meta": {"subfamilies": len(subfamily_maps),
                  "note": "亚科级 1° 网格分布图：由 build_taxonomy_pages.py 合并本亚科各属地图生成"},
        "subfamilies": subfamily_maps,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    maps_changed = (not SUBFAMILY_MAPS_OUT.is_file()
                    or SUBFAMILY_MAPS_OUT.read_text(encoding="utf-8") != maps_payload)
    if maps_changed and write:
        SUBFAMILY_MAPS_OUT.parent.mkdir(parents=True, exist_ok=True)
        SUBFAMILY_MAPS_OUT.write_text(maps_payload, encoding="utf-8", newline="\n")

    total = len(outputs)
    n_changed = changed + (1 if data_changed else 0) + (1 if maps_changed else 0) + geo_changed
    print("taxonomy hub pages: %d pages (%d per language: 13 family / 18 subfamily / 326 genus), "
          "%d stale" % (total, total // len(LANGS), stale))
    print("description length %d-%d chars, all unique"
          % (min(len(d) for d in descs), max(len(d) for d in descs)))
    print("subfamily maps: %d of 18 subfamilies have merged geometry, %d changed, %d stale"
          % (len(subfamily_maps), geo_changed, geo_stale))
    print("%s: %d file(s) changed%s" % (DATA_OUT.relative_to(ROOT), n_changed,
                                        "" if write else " (--check: nothing written)"))
    if not write and (changed or data_changed or maps_changed or geo_changed or geo_stale or stale):
        sys.exit("generated files are out of date; rerun without --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
