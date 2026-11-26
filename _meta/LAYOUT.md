# 目录与页面地图

> 从 `SITE-INDEX.md` 拆出：只在**知道要改什么、但不确定是哪个目录 / 哪个文件生成**时读这一页。
> 常见的编辑动作已经写在 `SITE-INDEX.md` §0 的三十秒路由表里，先看那张表；这里补的是「每个目录是什么」
> 与「每个页面由谁生成」。

## 1. 目录地图

| 路径 | 是什么 | 手改？ |
| --- | --- | --- |
| `_data/` | 站点数据的唯一来源层：26 个顶层文件 + 14 个分片目录，逐一见 `_meta/DATA-MAP.md` | 按角色分组：源可改、派生 / 缓存勿手改 |
| `_species/` | 3,089 个物种 / 亚种页；**front matter 是唯一真源**，`<!-- AUTO:BEGIN/END -->` 之间是生成的正文 | front matter 可改，AUTO 区块不可改 |
| `_layouts/`、`_includes/` | 4 个布局（`default` / `species` / `post` / `photos`）+ 30 个局部模板（页头页脚、分布图、图片卡、JSON-LD、检索组件…） | 可改 |
| `_includes/lang-path.html` | **URL 去语言前缀的唯一入口**：它写 `path_no_lang`，调用方再 assign 到自己的变量名 | 不要再用 `page.url \| remove_first: '/en'` |
| `assets/` | CSS / JS / 图片 / `geo/` 分布图 GeoJSON / `vendor/`（Leaflet 等） | 可改；改完 `stamp_assets.py` 自动更新缓存戳 |
| `family/`、`subfamily/`、`genus/`、`photos/` | 13 + 18 + 326 个中文分类页，以及按分类单元聚合的图集页 | **生成** |
| `en/`、`es/` | 对应语言的 11 个根页面 + `basics/` + 分类页 / 物种页 / 图集页 | 根页面可改；分类页与物种页**生成** |
| `basics/`、`_posts/` | 基础知识（`index.md` 入口、`morphology.md` 形态篇，正文来自 `_unpublished` 的书稿）；博客文章（模板见 `_tools/新文章模板.md`）。博客 2026-11-26 封存，`_posts/` 现只有一份 `README` 说明 | 可改 |
| `data/`、`downloads/`、`dataset/` | 公开 JSON、对外下载件、带 DOI 的归档数据集 | 各目录的 `metadata.json` / `CHANGELOG.md` / `README.md` / `LICENSE` 可改，其余**生成** |
| `list.md`、`stats.md`、`changelog.md`、`name-issues.md`、`isoptera-data.json`、`search-index.json`、`sitemap.txt`、`papers-index.json` | 三语同名页面的中文版 + 整棵分类树 / 检索索引 / 纯文本站点地图 / 文献缓存 | **生成** |
| `feed.xml`、`feed.json`、`opensearch.xml`、`robots.txt`、`favicon.ico` | 订阅源与站点元文件 | 可改 |
| `_tools/`、`.github/workflows/` | 生成与校验脚本 + 运维文档；CI（`pages.yml` 部署、`validate.yml` 闸门） | `_tools/*.py` 可改，workflow 慎改 |
| `.sources/` | 来源存档账本（`Sxxxx`：元数据 + 逐字摘录 + `used_in`），`.` 开头不发布 | 用 `sources.py add` 写 |
| `.library-vault/`、`_unpublished/` | 文库全文（gitignore、不发布）+ 其 AES 密文备份 | 用 `sources.py library-add` / `library_vault.py pack` |
| `未发布内容/`、`_pending_pages/`、`_drafts/`、`_inbox/`、`_reports/` | 书稿与插图原稿（exclude）、撤下待恢复的页面、草稿素材、工作清单与调研报告 | 可改，均不发布 |
| `_tmp/`、`_langsrc/`、`_site-zh|en|es/`、`_site/`、`.jekyll-cache/` | 本地临时目录与构建中间产物，全部 gitignore | **不要手改也不要提交**；删了可重建（见 `_meta/PIPELINE.md` §5） |
| `_meta/` | 本索引的细节页：DATA-MAP / PIPELINE / LAYOUT / DOCS | 可改，不发布 |
| `README.md`、`CONTRIBUTING.md`、`AGENTS.md`、`SITE-INDEX.md`、`llms.txt` | 仓库文档（`AGENTS.md`、`SITE-INDEX.md` 在 sitemap 里被刻意排除） | 可改 |
| `现存等翅下目 …Comparison List.md` | 2026-10 的**原始单文件名录**（323 属 / 3,004 种），站点数据已更新到 326 / 3,021；脚本只读它的 `## 参考文献` 区块 | 只改参考文献区块（`sitemap: false`） |

## 2. 页面 → 源文件

| 页面 | 中文 | English | Español | 谁生成 / 依赖 |
| --- | --- | --- | --- | --- |
| 首页 `/` | `index.md` | `en/index.md` | `es/index.md` | 手写；JSON-LD 来自 `_includes/dataset-jsonld.html` |
| 名录索引 `/list/` | `list.md` | `en/list.md` | `es/list.md` | `build_list_index.py`（`taxonomy.json` + `list_index_blocks.json` + `taxon_prose/`） |
| 索引页合订本 `/en/list/sections/`、`/es/list/sections/` | — | `en/list/sections.md` | `es/list/sections.md` | 同上 |
| 命名差异 `/list/name-issues/` | `name-issues.md` | `en/name-issues.md` | `es/name-issues.md` | `build_name_issues.py` → `_data/name_issues.json`；前端 `assets/name-issues.js` |
| 全文搜索 `/search/` | `search.md` | `en/search.md` | `es/search.md` | `assets/search-page.js` + Pagefind（构建时生成）+ `search-index.json`（名录检索） |
| 文献检索 `/papers/` | `papers.md` | `en/papers.md` | `es/papers.md` | `assets/papers.js` + `_data/papers/` + `papers-index.json`（断网兜底） |
| 统计 `/stats/` | `stats.md` | `en/stats.md` | `es/stats.md` | `build_taxonomy_data.py` |
| 数据 `/data/` | `data.md` | `en/data.md` | `es/data.md` | 手写清单 + `build_taxonomy_data.py` 产出 `data/*.json` |
| 下载 `/download/` | `download.md` | `en/download.md` | `es/download.md` | 手写；列出 `downloads/` 里的静态文件 |
| 博客 `/blog/`（2026-11-26 封存，不发布） | — | — | — | 三语页面与唯一一篇文章在 `_pending_pages/blog/`，恢复见该目录 README |
| 版本记录 `/changelog/` | `changelog.md` | `en/changelog.md` | `es/changelog.md` | `build_changelog.py`（源：`dataset/CHANGELOG.md`） |
| 留言 `/guestbook/` | `guestbook.md` | `en/guestbook.md` | `es/guestbook.md` | Giscus |
| 基础知识 `/basics/` | `basics/index.md` | `en/basics/index.md` | `es/basics/index.md` | 手写 |
| 形态篇 `/basics/morphology/` | `basics/morphology.md` | `en/basics/morphology.md` | `es/basics/morphology.md` | 手写（书稿在 `未发布内容/`） |
| 科页 `/family/<id>/` | `family/<id>.md` | `en/family/<id>.md` | `es/family/<id>.md` | `build_taxonomy_pages.py` |
| 亚科页 `/subfamily/<id>/` | `subfamily/<id>.md` | `en/subfamily/<id>.md` | `es/subfamily/<id>.md` | `build_taxonomy_pages.py` |
| 属页 `/genus/<id>/` | `genus/<id>.md` | `en/genus/<id>.md` | `es/genus/<id>.md` | `build_taxonomy_pages.py` |
| 物种页 `/species/<slug>/` | `_species/<slug>.md` | `en/species/<slug>.md` | `es/species/<slug>.md` | front matter 手写；正文 `build_species_body.py` |
| 图集页 `/photos/…/` | `photos/{family,subfamily,genus,species}/<id>.md` | `en/photos/…` | `es/photos/…` | `build_photo_pages.py` |

> URL 规则：分类页与物种页的路径全部由 `_data/taxonomy.json` 的 id / `_species/<slug>.md` 的 slug 决定；
> 页面内的锚点 id 也取自这些 id（`_tools/checklist_headings.py` 登记非分类学锚点）。
