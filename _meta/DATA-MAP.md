# 数据层地图（`_data/` 与其它数据文件）

> 从 `SITE-INDEX.md` 拆出：只在**改数据内容**或**判断某个数据文件能不能手改**时读这一页。
> 定位页面、改标题、看连带关系的入口仍是 `SITE-INDEX.md`；生成链与校验在 `_meta/PIPELINE.md`。

`_data/` 是站点数据的唯一来源层：26 个顶层文件 + 14 个分片目录。14 个大 JSON 已按「一阶元一档」
拆成 `_data/<数据集>/` 分片目录（聚合文件已删除）；布局、读取方式与「改数据改哪个文件」的定位方法
见 §5 与 `_tools/data_shards.md`。

角色标记：**源** = 手写、改这里；**派生** = 脚本生成、勿手改；**缓存** = 外部数据抓取结果，只在需要刷新时手动跑；**配置** = 功能开关。

## 1. 源文件：改内容就改这些

| 文件 | 内容 | 落到哪 |
| --- | --- | --- |
| `taxonomy.json` | 支系 → 科 → 亚科 → 属 的层级与顺序（`id` / 中文名 / 拉丁名 / 父级） | 所有分类页、`/list/`、`data/`、`stats`、`sitemap` |
| `taxon_prose/` | 科 / 亚科正文与插图，三语；按语言、等级分目录，一个分类单元一片 | 科页、亚科页、`/list/sections/` |
| `list_index_blocks.json` | `/list/` 的 H1、导语、按科浏览、参考文献块，三语 | `list.md` 三语 |
| `i18n.yml` | 界面文案，`zh-CN` / `en` / `es` 各 95 个 key | 全站模板 |
| `translation_glossary.yml` | 摘要翻译术语表（学名/术语对齐） | `/papers/` 的翻译提示 |
| `translations_en/`、`translations_es/` | 形态与动物志正文的英/西译文；`meta.json` + 与源数据集同构的分片，键与原数据文件一致 | 分类页、物种页 |
| `etymology/` | 属名词源 + 种加词词源；`meta.json` + `genera/` + `epithets/` | 属页、物种页「词源」 |
| `genus_sources/` | 每个属的形态描述出处（文献 / 书页） | 属页的来源脚注、形态工作清单 |
| `taxon_literature/` | 逐分类单元的文献条目；按等级分目录 | 属页 / 科页的文献区块 |
| `morphology_genera/` | 属级形态描述（补充编写，245 属一属一档） | 属页「形态」 |
| `morphology_species/` | 种级形态描述（400 条，一种一档） | 物种页「形态」 |
| `fauna_families.json`、`fauna_genera.json`、`fauna_keys.json` | 《中国动物志》改写的科 / 属描述与检索表（未拆，仍是单文件） | 分类页 |
| `fauna_species/` | 《中国动物志》改写的种描述；一属一目录、一种一档 | 物种页 |
| `fauna_measure_terms.json`、`fauna_measurements/` | 测量项术语（单文件）与逐种测量值（按属分目录） | 物种页「测量」表 |
| `taxonomy_images.json` | 科 / 亚科的自有插图映射 | 分类页头图 |
| `phylogeny.json` | 系统发育树数据（页面暂缓发布，数据保留） | `_includes/phylogeny.html` |
| `name_issue_reviews.json` | 命名差异的人工裁定 / 复核标记 | 看板的「已复核」状态 |
| `fulltext_hosts.json` | OA 全文抓取的主机放行清单 | `fetch_fulltext.py` |
| `ai_chat.yml` | Cloudflare AI Search 对话气泡开关与脚本地址 | 全站右下角气泡 |
| `analytics.yml` | GoatCounter 统计配置（`count_url` 置空即停用） | 全站页脚 |

## 2. 派生文件：脚本生成，改源文件后重跑

| 文件 | 谁生成 | 内容 / 去处 |
| --- | --- | --- |
| `species_by_genus.json`、`species_by_family.json`、`species_by_subfamily.json` | `build_genus_index.py` | 分类页的物种清单查找表 |
| `name_issues.json` | `build_name_issues.py` | 命名差异看板（与 `data/name-issues.json` 同内容） |
| `changelog.json` | `build_changelog.py` | `/changelog/` 三语页面 |
| `photo_taxa.json` | `build_photo_pages.py` | 哪些分类单元有图集页 |
| `subfamily_maps.json` | `build_occurrence_geojson.py` | 亚科分布图索引 |
| `occurrence_summary.json` | `build_occurrence_geojson.py` | 科 / 属 / 种分布图索引与计数 |
| `build.json` | `stamp_assets.py` | CSS/JS 缓存戳（`?v=`） |
| `taxonomy_crosswalk.json` | `_tools/build_taxonomy_crosswalk.py`（手动） | 分类变更对照表（属级来自 `name_issues.json`） |
| `fulltext_manual.json` | `_tools/fetch_fulltext.py` | 需人工获取的全文清单 |

## 3. 缓存：外部数据，只在刷新时手动跑

| 文件 | 谁生成 | 刷新后必须一起做的事 |
| --- | --- | --- |
| `authority_links/` | `.github/workflows/build_authority_links.py` | 重跑 `build_name_issues.py --write` 并提交 `data/name-issues.json` |
| `bsf_links/` | `.github/workflows/build_bsf_links.py` | 同上 |
| `papers/` | `.github/workflows/build_papers.py`（`papers_refresh.yml`） | 重跑 `build_papers.py --write` 生成 `papers-index.json` |
| `species_photos/` | `.github/workflows/build_species_photos.py`（爬虫 workflow） | 重跑 `build_photo_pages.py`（regen 已含） |
| `references.json` | `build_references.py`（源：根目录单文件的 `## 参考文献`） | 重跑 `build_dataset.py --write` |

## 4. `_data` 之外的重要数据文件

| 文件 | 谁生成 | 内容 |
| --- | --- | --- |
| `isoptera-data.json` | `build_taxonomy_data.py` | 整棵分类树单文件版（模式种、分布、亚种、页面链接） |
| `data/index.json` + `data/*.json` | `build_taxonomy_data.py` | 按支系 / 科 / 亚科拆分的公开 JSON |
| `search-index.json` | `build_search_index.py` | 名录检索索引（含拼音、繁体；CI 装依赖后生成增强版） |
| `papers-index.json` | `build_papers.py` | 326 个属的论文元数据缓存，`/papers/` 断网兜底 |
| `sitemap.txt` | `build_sitemap_txt.py` | 纯文本站点地图（`sitemap.xml` 由 jekyll-sitemap 生成） |
| `downloads/*.zip`、`downloads/*.csv` | `build_dataset.py`、`build_dwca.py`、`build_name_issues.py` | 对外下载 |
| `CITATION.cff`、`.zenodo.json`、`dataset/*` | `build_dataset.py` | 数据集归档与引用元数据 |

## 5. 分片布局：一阶元一档（`_data/<数据集>/`）

14 个大 JSON 已拆成目录：**目录名 = 数据集名，一个分片文件 = 一个分类单元的一档数据**。仓库里不再有
聚合文件，分片就是唯一真源；完整契约（三语译文子块、Liquid / Python 读取方式对照）见
`_tools/data_shards.md`。状态查询：

```bash
python _tools/data_shards.py --status
```

Python 侧读写统一走 `_tools/shard_io.py`：`load(name)` 给出合并视图、`save(name, root)` 把整份数据
按新布局落成/清理分片、`exists(name)` / `buckets(name, root)` 辅助；模板与脚本都不要自己拼分片路径。

| 数据集 | 分片路径 | 一档是什么 | 分片数 |
| --- | --- | --- | --- |
| `morphology_species` | `_data/morphology_species/<属>/<slug>.json` | 一种形态 | 401 |
| `fauna_species` | `_data/fauna_species/<属>/<slug>.json` | 一种动物志条目 | 435 |
| `fauna_measurements` | `_data/fauna_measurements/<属>/<slug>.json` | 一种测量值 | 255 |
| `morphology_genera` | `_data/morphology_genera/<属>.json` | 一属形态 | 245 |
| `genus_sources` | `_data/genus_sources/<属>.json` | 一属出处 | 326 |
| `taxon_literature` | `_data/taxon_literature/<rank>/<id>.json` + `meta.json`；`<rank>` 为 `family` / `subfamily` / `genus` / `species` | 一阶元文献 | 287 |
| `etymology` | `_data/etymology/meta.json`、`genera/<属>.json`、`epithets/<首字母>.json` | 属名 / 种加词 | 353 |
| `taxon_prose` | `_data/taxon_prose/<lang>/<等级目录>/<id>.json`（等级目录为 `families` / `subfamilies`） | 一科 / 一亚科正文 | 94 |
| `translations_en` / `translations_es` | 见 `_tools/data_shards.md` §2 | 对应原文的一档 | 各 1085 |
| `papers` | `_data/papers/meta.json` + `genera/<属>.json` | 一属论文缓存 | 327 |
| `species_photos` | `_data/species_photos/meta.json` + `species/<属>.json` | 一属 `{拉丁名: …}` | 79 |
| `authority_links` | `_data/authority_links/meta.json` + `taxa/<属>.json` | 一属权威库链接 | 327 |
| `bsf_links` | `_data/bsf_links/meta.json` + `name_map/<属>.json` | 一属 BSF 链接 | 327 |

`<属>` 是 `taxonomy.json` 里的属 id（小写、无空格）；`<slug>` 是物种页 URL 的最后一段。

**定位方法**（先认层级，再开那一个文件）：

- 物种页 `/species/<slug>/`：`<slug>` 取 URL 最后一段，属 id 看 `_species/<slug>.md` 的 `genus_id`，
  即 `_data/<数据集>/<genus_id>/<slug>.json`（`morphology_species`、`fauna_species`、`fauna_measurements`）。
- 属页 `/genus/<id>/`：`_data/morphology_genera/<id>.json`、`_data/genus_sources/<id>.json`；
  `papers`、`species_photos`、`authority_links`、`bsf_links` 各自在 `genera` / `species` / `taxa` / `name_map`
  子目录下按属分文件。
- 科 / 亚科页：`_data/taxon_prose/<lang>/families/<id>.json` 或 `.../subfamilies/<id>.json`；
  文献在 `_data/taxon_literature/family/<id>.json`、`.../subfamily/<id>.json`（属 / 种文献在 `genus/`、`species/`）。
- 词源：属名在 `_data/etymology/genera/<id>.json`，种加词在 `_data/etymology/epithets/<首字母>/<epithet>.json`。

改数据时只改对应分片，**不要重建聚合文件**；单个分片文件不用登记，但 `_data/` 顶层新增数据集目录
必须登记进本文件或 `SITE-INDEX.md`（`python _tools/build_ai_index.py --check` 核对目录名与分片数）。
`data_shards.py --verify-all` 需要拆分前的原始 JSON（`_tmp/shard_orig/`，不入库），CI 只校验目录齐备与
分片数，不在 CI 复跑全量合并。
