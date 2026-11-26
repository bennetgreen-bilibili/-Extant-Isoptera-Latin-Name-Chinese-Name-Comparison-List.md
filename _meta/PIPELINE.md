# 生成链、校验与本地构建

> 从 `SITE-INDEX.md` 拆出：只在**跑生成链 / 本地构建 / 交付前校验**时读这一页。
> 文件定位、数据层结构仍看 `SITE-INDEX.md` 与 `_meta/DATA-MAP.md`。

## 1. 生成链（`_tools/regen_all.sh`）

顺序固定、整条链幂等（连跑两次第二次零字节变化）。改完源文件后只需一条命令：

```bash
bash _tools/regen_all.sh
```

| 步骤 | 脚本 | 输入 → 输出 |
| --- | --- | --- |
| 1 | `_tools/extract_taxon_data.py --check` | 校验 `taxonomy.json` / `taxon_prose/` / `list_index_blocks.json` 自洽 |
| 2 | `_tools/build_list_index.py` | 三份数据 → `list.md`、`en/list.md`、`es/list.md`、`*/list/sections.md` |
| 3 | `_tools/build_taxonomy_data.py --write` | `taxonomy.json` + `_species` → `isoptera-data.json`、`data/`、三语 `stats.md` |
| 4 | `build_genus_index.py` | `_species` → `_data/species_by_{genus,family,subfamily}.json` |
| 5 | `build_species_body.py --write` | `_species` front matter → 物种页正文 + `en/species/` + `es/species/` |
| 6 | `build_photo_pages.py` | `species_photos/` → `photos/` 三语图集页 + `photo_taxa.json` |
| 7 | `build_taxonomy_pages.py` | `taxonomy.json` + `taxon_prose/` + `_species` → `family/`、`subfamily/`、`genus/` 三语 |
| 8 | `build_sitemap_txt.py` + `build_sitemap_core.py` | 页面清单 → `sitemap.txt`（整份）；分类层级页 → `sitemap-core.xml`（三语 首页 + 名录索引 + 科/亚科/属聚合页，先在 GSC 提交的那一份） |
| 9 | `build_search_index.py --write --no-enrich` | → `search-index.json`（基础版；CI 部署时生成增强版） |
| 10 | `build_dataset.py --write` | → `dataset/`、`downloads/*.zip`、`CITATION.cff`、`.zenodo.json` |
| 11 | `_tools/build_dwca.py --write` | `dataset/data/*` → `dataset/dwca/` + DwC-A zip |
| 12 | `_tools/build_changelog.py --write` | `dataset/CHANGELOG.md` → `changelog.md` 三语、`changelog.atom`、`_data/changelog.json` |
| 13 | `build_name_issues.py --write` | 缓存 + `_species` → `_data/name_issues.json`、`data/name-issues.json`、CSV |
| 14 | `_tools/build_api.py --write` | `dataset/data/*` + `_data/name_issues.json` → `api/v1/`（名称查找表、分类索引、3089 条物种记录） |
| 15 | `_tools/stamp_assets.py` | `assets/*.css`、`assets/*.js` 内容哈希 → `_data/build.json` |
| 16 | `_tools/check_lang_pages.py --ci` | 三语页面齐备 / 混语残留 / 站内链语言前缀 |
| 17 | `_tools/build_ai_index.py --write` | 刷新 `SITE-INDEX.md` 现状快照的计数（含 `_data/` 顶层文件与分片目录） |

## 2. 不在 regen 链里的手动脚本

只在需要时跑，且会联网：

| 脚本 | 用途 |
| --- | --- |
| `build_authority_links.py` / `build_bsf_links.py` | 刷新 GBIF / Catalogue of Life / Wikidata / BSF 缓存 |
| `build_papers.py` | 刷新 `/papers/` 的 OpenAlex 缓存（`papers_refresh.yml` 定期跑） |
| `build_species_photos.py` | 抓取开放许可照片（爬虫 workflow） |
| `build_references.py` | 从单文件「参考文献」区块补 Crossref / DOI / BHL |
| `build_occurrence_geojson.py` | 刷新 GBIF 1° 网格分布图数据 |
| `_tools/build_taxonomy_crosswalk.py` | 分类变更对照表 |
| `_tools/fetch_fulltext.py` | 抓取合法 OA 全文进文库 |
| `_tools/library_scan.py` / `_tools/library_vault.py` | 文库扫描 / 加密备份 |

## 3. 校验

| 命令 | 查什么 |
| --- | --- |
| `python _tools/check_site.py --ci` | 结构与数据一致性 18 项 + 分片布局（JSON、三语同构、页面齐备、计数、sitemap、i18n、命名差异、JSON-LD…） |
| `python _tools/data_shards.py --status` | 14 个分片数据集的目录 / 分片数 / 聚合文件残留状态 |
| `python _tools/check_liquid.py` | Liquid 语法（成对标签、参数个数、注释内部也会解析） |
| `python _tools/check_lang_pages.py --ci` | 三语页面契约（漏页、混语残留、站内链缺语言前缀） |
| `python _tools/sources.py check --strict` | 来源存档完整性（id、摘录、`used_in`、正文 `src:` 引用） |
| `python _tools/check_publish_surface.py --tracked` | 不该发布的文件（pdf / docx / 日志 / `未发布内容/`）有没有被跟踪 |
| `python _tools/translations_merge.py --all --check-only` | 译文覆盖率与数字对账 |
| `python .github/workflows/build_dataset.py --check` | 归档数据集是否与源一致（逐成员比对） |
| `python _tools/build_api.py --check` | `api/v1/` 是否与当前数据一致（缺文件 / 多文件 / 字节过期） |
| `python _tools/build_ai_index.py --check` | 索引计数是否最新、新增文件是否登记（`SITE-INDEX.md` + `_meta/*.md` 一起算） |

## 4. 本地构建

Windows 上 Jekyll 3.10 必须先进目录再 build，否则 layout 路径会拼错：

```bash
python _tools/make_lang_sources.py
cd _langsrc/zh && jekyll build --destination ../../_site-zh   # en / es 同理
cd ../.. && python _tools/merge_lang_sites.py
```

**交付前**：`check_site.py --ci` + `check_liquid.py` + `sources.py check --strict` 全绿，且生成产物已提交
（CI 会断言 `git status --porcelain` 为空）。

## 5. 构建产物的位置

`_langsrc/`、`_site-zh|en|es/`、`_site/`、`.jekyll-cache/`、`_tmp/` 都是**可再生成的**，已在 `.gitignore`：

- 它们不属于源文件，改站时不要读、不要搜（会撑爆上下文，见 `SITE-INDEX.md` §0.2 搜索纪律）。
- 目录被删掉后跑一次 `python _tools/make_lang_sources.py` + 上面的 build 即可重建。
- `_tmp/` 里有两样不能删：`_tmp/vault.key`（文库备份口令）与 `_tmp/shard_orig/`（分片拆分前的原始 JSON，
  `data_shards.py --verify-all` 要用）。
