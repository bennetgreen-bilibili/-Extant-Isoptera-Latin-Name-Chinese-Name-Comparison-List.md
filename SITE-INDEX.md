# 站点内部索引（SITE-INDEX）

> **先读这页，再按表只打开需要的那几个文件。**
> 仓库里有 3,000+ 个 `.md`，其中绝大多数是生成产物；真正决定站点内容的源文件不到 50 个。
> 为了「了解项目」而通读整个工作区，既慢，又会把生成产物当成源文件去改。
>
> 本文件手写维护；第 9 节的计数由 `_tools/build_ai_index.py --write` 刷新。
> `--check` 会校验：新增的 `_data` 顶层文件、`_data/<数据集>/` 分片目录、页面、生成脚本、说明文档有没有在这里登记（没登记就报错）。
>
> 配套阅读：`AGENTS.md`（硬约定，含来源存档）｜`CONTRIBUTING.md`（流程细节）｜`README.md`（站点功能长文）｜`llms.txt`（对外 AI 说明）

## 0. 三十秒路由表

| 你想做的事 | 改这里 | 然后跑 | 最容易漏 |
| --- | --- | --- | --- |
| 改一个物种的学名 / 中文名 / 命名人 / 模式产地 / 分布 / 异名 | `_species/<slug>.md` 的 front matter | `bash _tools/regen_all.sh` | 学名同时决定 permalink 与 slug，改名要改五处（见 §5.2） |
| 新增 / 删除一个物种或亚种 | 新建 / 删除 `_species/<slug>.md` | `bash _tools/regen_all.sh` | 所属属必须已存在于 `_data/taxonomy.json` |
| 改一个属的位置（科 / 亚科）或增删科、亚科、属 | `_data/taxonomy.json` | `bash _tools/regen_all.sh` | `id` 就是页面 URL，改 id = 旧链接 404 |
| 改科 / 亚科正文（三语） | `_data/taxon_prose/`（按语言 / 等级分片，见 §4.5） | `bash _tools/regen_all.sh` | 同时影响 `/family/`、`/subfamily/` 与 `/list/sections/` 合订本 |
| 改 `/list/` 的导语、按科浏览、参考文献块（三语） | `_data/list_index_blocks.json` | `bash _tools/regen_all.sh` | 三语三份都要改，`check_site` 校验锚点同构 |
| 改界面文案（导航、页脚、按钮、语言切换名…） | `_data/i18n.yml` | `python _tools/check_site.py` | `zh-CN` / `en` / `es` 三节 key 必须完全一致（各 94 个） |
| 改页面结构、样式、交互 | `_layouts/`、`_includes/`、`assets/*.css`、`assets/*.js` | `python _tools/check_liquid.py` + `python _tools/check_lang_pages.py --ci` | 三语页面同构；模板里别新增 `site.pages` 遍历 |
| 新增一个页面 | 根目录 + `en/` + `es/` 各一份 | `python _tools/check_site.py` | front matter 的 `title` / `description` / `permalink` / `lang` 四件套 |
| 改 77 条参考文献 | 根目录名录单文件的 `## 参考文献` 区块 | `python .github/workflows/build_references.py --write` | 改完必须重跑 `build_dataset.py --write`（数据集也解析这 77 条） |
| 改数据集元数据 / DOI / 版本 | `dataset/metadata.json` + `_config.yml` 的 `dataset:` | `python .github/workflows/build_dataset.py --write` | 两处要保持一致，`check_site` 会比对版本号 |
| 查某条论断的出处 | `.sources/`（`Sxxxx` 记录） | `python _tools/sources.py check --strict` | 正文里的 `<!-- src:Sxxxx -->` 必须能对上记录 |
| 补属级 / 种级形态描述 | `_data/morphology_genera/`、`_data/morphology_species/`、`_data/fauna_species/`、`_data/fauna_measurements/`（一阶元一档，见 §4.5） | `bash _tools/regen_all.sh` | 三语译文在 `_data/translations_en/`、`_data/translations_es/`，缺译文时整节省略、不回退中文 |
| 查命名冲突 / 外部库差异 | `_data/name_issues.json`（派生，勿手改） | `.github/workflows/build_name_issues.py --write` | 人工裁定写在 `_data/name_issue_reviews.json` |
| 发一个新版本（数据集归档） | `dataset/CHANGELOG.md` + `dataset/metadata.json` | `python .github/workflows/build_dataset.py --write` | `dataset/LICENSE` 改动同样会让归档 zip 过期 |
| 只在本地跑站点看效果 | — | 见 §7「本地构建」 | Windows 上 Jekyll 必须先进 `_langsrc/<lang>/` 再 build |

### 0.1 先定位，再改

- **找某个物种**：`ls _species | grep <slug 关键词>`，或 `grep -l "latin: .*Heterotermes" _species/*.md`；
  拿到文件后只改 front matter，正文交给 `build_species_body.py`。
- **找某个属 / 科**：属的 id 与归属在 `_data/taxonomy.json`；`genus/<id>.md`、`family/<id>.md` 是生成页，
  改位置、改中文名都改 `taxonomy.json`，不要直接编辑页面。
- **找某条论断的出处**：`grep -n "src:S0" <文件>`；记录本身在 `.sources/records/Sxxxx.md`。
- **找某段正文属于哪个数据文件**：科 / 亚科正文 → `_data/taxon_prose/`（按语言 / 等级分片，见 §4.5）；
  `/list/` 导语 → `_data/list_index_blocks.json`；界面字样 → `_data/i18n.yml`；属 / 种形态 →
  `_data/morphology_*/`、`_data/fauna_species/`、`_data/fauna_measurements/`（一阶元一档，见 §4.5；
  三语译文在 `_data/translations_en/`、`_data/translations_es/`，键名与原文数据一致）。
- **判断一个文件能不能改**：先在 §4 / §5.1 查它是不是派生；派生文件的改动一定会被下一次 `regen_all.sh` 覆盖。

## 1. 站点概况

- Jekyll 静态站，GitHub Pages 部署，自定义域名 **https://termite-extant-isoptera.org**（`_config.yml` 的 `url`，`baseurl: ""`）。
- 三语：中文在站点根、英文 `/en/`、西班牙文 `/es/`；一套模板（`_layouts/default.html` 按 front matter 的 `lang` 决定语言）。
- 规模：6 支系、13 科、18 亚科、326 属、3,021 种、68 亚种 = **3,089 条**记录；三语各一套页面，构建约 11,300 页。
- 数据版本 2026.10.30；版本 DOI `10.5281/zenodo.23646836`，概念 DOI `10.5281/zenodo.23646835`（CC BY 4.0）。
- 每次构建：`make_lang_sources.py` 造三份硬链接镜像 → 三个容器并行 Jekyll → `merge_lang_sites.py` 合并；细节见 `CONTRIBUTING.md` §发布构建。

## 2. 目录地图

| 路径 | 是什么 | 手改？ | 进 `_site`？ |
| --- | --- | --- | --- |
| `_data/` | 站点数据的唯一来源层（26 个顶层文件 + 14 个分片目录，逐一见 §4） | 见 §4 的分组 | 否（`_` 开头不发布） |
| `_species/` | 3,089 个物种 / 亚种页；**front matter 是唯一真源**，`<!-- AUTO:BEGIN/END -->` 之间是生成的正文 | front matter 可改，AUTO 区块不可改 | 是（经 `species` collection 输出） |
| `_layouts/` | 4 个布局：`default.html`（全站）、`species.html`、`post.html`、`photos.html` | 可改 | 否 |
| `_includes/` | 30 个局部模板（页头页脚片段、分布图、图片卡、JSON-LD、引用块、检索组件…）；**URL 去语言前缀只走 `_includes/lang-path.html`**（它写 `path_no_lang`，各调用方再 assign 到自己的变量名），不要再用 `page.url \| remove_first: '/en'` | 可改 | 否 |
| `assets/` | CSS / JS / 图片 / `geo/` 分布图 GeoJSON / `vendor/`（Leaflet 等） | 可改；改完 `stamp_assets.py` 自动更新缓存戳 | 是 |
| `family/`、`subfamily/`、`genus/` | 13 + 18 + 326 个分类页（中文） | **生成** | 是 |
| `en/`、`es/` | 对应语言的 11 个根页面 + `basics/` + `family/` + `subfamily/` + `genus/` + `species/` + `photos/` | 根页面可改；分类页与物种页**生成** | 是 |
| `basics/` | 基础知识：`index.md`（入口）、`morphology.md`（形态篇，正文来自 `_unpublished` 的书稿） | 可改 | 是 |
| `photos/` | 按分类单元聚合的完整图集页（`family/`、`subfamily/`、`genus/`、`species/` 四个子目录） | **生成** | 是 |
| `data/` | 公开的机器可读 JSON：`index.json`、按支系/科拆分文件、`termitidae/` 18 个亚科文件、`name-issues.json`、`references.json` | **生成**（`references.json` / `name-issues.json` 是副本） | 是 |
| `dataset/` | 带 DOI 的归档数据集：`data/*.csv`、`data/*.json`、`datapackage.json`、`datacite-metadata.xml`、`dwca/`、`README.md`、`LICENSE`、`CHANGELOG.md`、`metadata.json` | `metadata.json`、`CHANGELOG.md`、`README.md` 手写部分、`LICENSE` 可改，其余**生成** | 是（`sitemap: false`） |
| `downloads/` | 对外下载文件（CSV / Darwin Core zip / 归档 zip） | **生成** | 是 |
| `_posts/` | 博客文章（目前 1 篇，`blog.md` 自动列出） | 可改（模板见 `_tools/新文章模板.md`） | 是 |
| `_tools/` | 生成与校验脚本 + 运维说明文档（15 篇 `.md`，见 §8） | 可改 | 否 |
| `.github/workflows/` | 生成脚本（多数在这里）+ CI 工作流（`pages.yml` 部署、`validate.yml` 闸门） | 慎改 | 否 |
| `.sources/` | 来源存档账本（`Sxxxx` 记录：元数据 + 逐字摘录 + `used_in`） | 用 `sources.py add` 写 | 否（`.` 开头不发布） |
| `.library-vault/` | `_unpublished/文库/` 的 AES 密文备份，克隆即恢复 | 用 `library_vault.py pack` | 否 |
| `_unpublished/` | **全文库**：本机 5 本书 + 9 篇论文的全文（gitignore、不发布） | 用 `sources.py library-add` 入库 | 否 |
| `未发布内容/` | 书稿 docx / 插图原稿等工作文件（`_config.yml` 的 `exclude` 挡住） | 可改 | 否 |
| `_pending_pages/` | 已从站点撤下、保留待恢复的页面（生物学篇、系统发育树） | 按各自 README 恢复 | 否 |
| `_drafts/`、`_inbox/` | 草稿与待处理素材 | 可改 | 否 |
| `_reports/` | 工作清单与调研报告（14 篇 `.md` + 5 个 CSV，见 §8） | 可改 | 否 |
| `_tmp/` | 本地临时目录（脚本清单、断点缓存），已 gitignore | 随便写 | 否 |
| `_langsrc/`、`_site-zh` / `_site-en` / `_site-es` / `_site/` | 构建中间产物与切片，全部 gitignore | **不要手改也不要提交** | 否 |
| `list.md`、`stats.md`、`changelog.md`、`name-issues.md` | 三语同名页面的中文版 | **生成**（`changelog.md` / `name-issues.md` 也由脚本重写） | 是 |
| `isoptera-data.json`、`search-index.json`、`sitemap.txt`、`papers-index.json` | 整棵分类树 / 检索索引 / 纯文本站点地图 / 文献缓存 | **生成** | 是 |
| `feed.xml`、`feed.json`、`opensearch.xml`、`robots.txt`、`favicon.ico` | 订阅源与站点元文件 | 可改 | 是 |
| `README.md`、`CONTRIBUTING.md`、`AGENTS.md`、`SITE-INDEX.md`、`llms.txt` | 仓库文档（`AGENTS.md`、`SITE-INDEX.md` 在 sitemap 里被刻意排除） | 可改 | 是（静态复制） |
| `现存等翅下目 …Comparison List.md` | 2026-10 的**原始单文件名录**（323 属 / 3,004 种），站点数据已更新到 326 / 3,021；脚本只读它的 `## 参考文献` 区块 | 只改参考文献区块 | 是（`sitemap: false`） |

## 3. 页面 → 源文件

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
| 博客 `/blog/` | `blog.md` | `en/blog.md` | `es/blog.md` | Jekyll 自动列出 `_posts/` |
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

## 4. 数据层 `_data/`（26 个顶层文件 + 14 个分片目录）

14 个大 JSON 已按「一阶元一档」拆成 `_data/<数据集>/` 分片目录（聚合文件已删除）；布局、读取方式与
「改数据改哪个文件」的定位方法见 §4.5 与 `_tools/data_shards.md`。

角色标记：**源** = 手写、改这里；**派生** = 脚本生成、勿手改；**缓存** = 外部数据抓取结果，只在需要刷新时手动跑；**配置** = 功能开关。

### 4.1 源文件：改内容就改这些

| 文件 | 内容 | 落到哪 |
| --- | --- | --- |
| `taxonomy.json` | 支系 → 科 → 亚科 → 属 的层级与顺序（`id` / 中文名 / 拉丁名 / 父级） | 所有分类页、`/list/`、`data/`、`stats`、`sitemap` |
| `taxon_prose/` | 科 / 亚科正文与插图，三语；按语言、等级分目录，一个分类单元一片 | 科页、亚科页、`/list/sections/` |
| `list_index_blocks.json` | `/list/` 的 H1、导语、按科浏览、参考文献块，三语 | `list.md` 三语 |
| `i18n.yml` | 界面文案，`zh-CN` / `en` / `es` 各 94 个 key | 全站模板 |
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

### 4.2 派生文件：脚本生成，改源文件后重跑

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

### 4.3 缓存：外部数据，只在刷新时手动跑

| 文件 | 谁生成 | 刷新后必须一起做的事 |
| --- | --- | --- |
| `authority_links/` | `.github/workflows/build_authority_links.py` | 重跑 `build_name_issues.py --write` 并提交 `data/name-issues.json` |
| `bsf_links/` | `.github/workflows/build_bsf_links.py` | 同上 |
| `papers/` | `.github/workflows/build_papers.py`（`papers_refresh.yml`） | 重跑 `build_papers.py --write` 生成 `papers-index.json` |
| `species_photos/` | `.github/workflows/build_species_photos.py`（爬虫 workflow） | 重跑 `build_photo_pages.py`（regen 已含） |
| `references.json` | `build_references.py`（源：根目录单文件的 `## 参考文献`） | 重跑 `build_dataset.py --write` |

### 4.4 `_data` 之外的重要数据文件

| 文件 | 谁生成 | 内容 |
| --- | --- | --- |
| `isoptera-data.json` | `build_taxonomy_data.py` | 整棵分类树单文件版（模式种、分布、亚种、页面链接） |
| `data/index.json` + `data/*.json` | `build_taxonomy_data.py` | 按支系 / 科 / 亚科拆分的公开 JSON |
| `search-index.json` | `build_search_index.py` | 名录检索索引（含拼音、繁体；CI 装依赖后生成增强版） |
| `papers-index.json` | `build_papers.py` | 326 个属的论文元数据缓存，`/papers/` 断网兜底 |
| `sitemap.txt` | `build_sitemap_txt.py` | 纯文本站点地图（`sitemap.xml` 由 jekyll-sitemap 生成） |
| `downloads/*.zip`、`downloads/*.csv` | `build_dataset.py`、`build_dwca.py`、`build_name_issues.py` | 对外下载 |
| `CITATION.cff`、`.zenodo.json`、`dataset/*` | `build_dataset.py` | 数据集归档与引用元数据 |

### 4.5 分片布局：一阶元一档（`_data/<数据集>/`）

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
必须登记进本文件（`python _tools/build_ai_index.py --check` 核对目录名与分片数）。
`data_shards.py --verify-all` 需要拆分前的原始 JSON（`_tmp/shard_orig/`，不入库），CI 只校验目录齐备与
分片数，不在 CI 复跑全量合并。

## 5. 改动的连带影响（最容易漏的地方）

### 5.1 派生文件清单：不要手改

`list.md`、`en/list.md`、`es/list.md`、`en/list/sections.md`、`es/list/sections.md`、
`family/*.md`、`subfamily/*.md`、`genus/*.md`、`en/` 与 `es/` 下的全部分类页与物种页、
`photos/**`、`stats.md`、`en/stats.md`、`es/stats.md`、`isoptera-data.json`、`data/*.json`、
`search-index.json`、`sitemap.txt`、`changelog.md`、`changelog.atom`、`name-issues.md`、
`dataset/data/*`、`dataset/datapackage.json`、`dataset/datacite-metadata.xml`、`dataset/CHECKSUMS.sha256`、
`downloads/*.zip`、`_data/` 里 §4.2 与 §4.3 列出的文件（§4.1 的 `_data/<数据集>/` 分片是源文件，不在此列）。

`_species/*.md` 只有 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 之外的内容可以手改；
标记之间由 `build_species_body.py` 按 front matter 重写。

`dataset/README.md` 的 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 之间同理，标记外的手写内容不受影响。

### 5.2 连带关系表

| 改动 | 连带要处理 | 校验会卡在哪 |
| --- | --- | --- |
| 改物种学名（`latin` / `title` / `permalink` / slug / 文件名） | 五处一起改；属页清单、检索、CSV、数据集都会跟着变 | `check_site` 第 7 项（物种页必须出现在属页上） |
| 新增物种 | 所属属的 id 必须在 `taxonomy.json`；`rank` / `type` / `subfamily_id` 按实际填 | `check_site` 第 7、8 项 |
| 改 `taxonomy.json` 的 id | 页面 URL、锚点、`search-index.json` 的 `h` 字段、数据集里的链接全变 | `sitemap.txt` / 链接检查 / `check_lang_pages` |
| 改 `_species` 的 `authority_synonym_*` | 按顺序重跑 `build_species_body.py` → `build_search_index.py` → `build_name_issues.py` | `check_site` 第 12 项（三处一致性） |
| 刷新权威库缓存 | `build_name_issues.py --write` + `data/name-issues.json` 同提交 | CI「生成产物过期」 |
| 改 `i18n.yml` | 三个语言节同时增删；模板里用到的 key 不能少 | `check_site` 第 10 项 |
| 改页面文案（标题 / 描述） | `en/`、`es/` 对应页同改；`description` 里的冒号要加引号 | `check_lang_pages --ci`；YAML 解析失败会静默吞掉整块 front matter |
| 加一个页面 | front matter `title` / `description` / `permalink` / `lang` + 三语 + 导航入口 | `check_lang_pages --ci`；漏收录看 `check_site` 第 9 项（sitemap） |
| 改 `dataset/CHANGELOG.md` 或 `dataset/LICENSE` | 归档 zip 内容过期 | `build_dataset.py --check` |
| 改 `_config.yml` 的 `url` / `base_url` / `baseurl` | 三处必须一致（`baseurl` 为空时写 `""`） | `check_site` 第 1 项 |
| 改版本号 / DOI | `dataset/metadata.json` 与 `_config.yml` 的 `dataset:` 两处 | `check_site` 第 1 项 |
| 改 `assets/*.css` / `*.js` | `stamp_assets.py` 自动改 `_data/build.json` | 无需手改，但别忘提交 |
| 改模板 | 三语同构；**不要**新增 `site.pages` / `site.documents` 遍历；**不要** `assign` 整棵大 `_data` 哈希 | `check_liquid` / `check_lang_pages` |

## 6. 生成链（`_tools/regen_all.sh`）

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
| 8 | `build_sitemap_txt.py` | 页面清单 → `sitemap.txt` |
| 9 | `build_search_index.py --write --no-enrich` | → `search-index.json`（基础版；CI 部署时生成增强版） |
| 10 | `build_dataset.py --write` | → `dataset/`、`downloads/*.zip`、`CITATION.cff`、`.zenodo.json` |
| 11 | `_tools/build_dwca.py --write` | `dataset/data/*` → `dataset/dwca/` + DwC-A zip |
| 12 | `_tools/build_changelog.py --write` | `dataset/CHANGELOG.md` → `changelog.md` 三语、`changelog.atom`、`_data/changelog.json` |
| 13 | `build_name_issues.py --write` | 缓存 + `_species` → `_data/name_issues.json`、`data/name-issues.json`、CSV |
| 14 | `_tools/stamp_assets.py` | `assets/*.css`、`assets/*.js` 内容哈希 → `_data/build.json` |
| 15 | `_tools/check_lang_pages.py --ci` | 三语页面齐备 / 混语残留 / 站内链语言前缀 |
| 16 | `_tools/build_ai_index.py --write` | 刷新本文件第 9 节的计数（含 `_data/` 顶层文件与分片目录） |

**不在 regen 链里的手动脚本**（只在需要时跑，且会联网）：

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

## 7. 校验与构建

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
| `python _tools/build_ai_index.py --check` | 本索引的计数是否最新、新增文件是否登记 |

**本地构建**（Windows 上 Jekyll 3.10 必须先进目录再 build，否则 layout 路径会拼错）：

```bash
python _tools/make_lang_sources.py
cd _langsrc/zh && jekyll build --destination ../../_site-zh   # en / es 同理
cd ../.. && python _tools/merge_lang_sites.py
```

**交付前**：`check_site.py --ci` + `check_liquid.py` + `sources.py check --strict` 全绿，且生成产物已提交（CI 会断言 `git status --porcelain` 为空）。

## 8. 其它文档索引

| 文档 | 讲什么 |
| --- | --- |
| `AGENTS.md` | 硬约定：来源存档、存档格式、红线（编造 / 摘录不逐字 / 全文进仓库） |
| `CONTRIBUTING.md` | 数据流、三语同步、生成顺序、发布构建、提交前校验 |
| `README.md` | 站点功能长文：每个页面、检索、外部库、JSON-LD、数据集、部署细节 |
| `llms.txt` | 面向外部 AI 的站点说明（页面对照、数据入口、引用格式） |
| `_tools/data_shards.md` | `_data` 一阶元一档分片布局、读取方式对照、改分片数据怎么定位 |
| `_tools/数据集DOI与归档发布指南.md` | 数据集 DOI、Zenodo / GBIF / ScienceDB 路线 |
| `_tools/Zenodo发布逐步操作手册.md` | 照抄式发布操作单（字段值、命令、验收） |
| `_tools/Zenodo新版描述-2026.10.30.md` | 当前版本的 Zenodo 描述文案 |
| `_tools/分布图与瓦片使用政策.md` | 分布图流水线、1° 网格聚合、化石过滤、瓦片政策 |
| `_tools/外部权威库与一致性核对.md` | GBIF / CoL / Wikidata / BSF 外链与判定规则 |
| `_tools/文献检索器说明.md` | `/papers/` 的数据来源、查询与导出 |
| `_tools/原文归档工作流说明.md` | 合法 OA 全文下载进文库的流程 |
| `_tools/参考文献与DOI补全说明.md` | 77 条参考文献的 Crossref / 格式增强 |
| `_tools/图片授权与署名说明.md` | 图片图集的许可策略与署名规则 |
| `_tools/图片版权核查与处理清单.md` | `assets/images/` 插图的逐张核查结果 |
| `_tools/开源功能与工作流扩展建议.md` | 可加功能清单（读者收益 × 可维护性 × 工作量） |
| `_tools/物种介绍选题清单.md` | 按真实搜索需求排的选题清单 |
| `_tools/新文章模板.md` | 博客文章 front matter 模板 |
| `_tools/manual_fulltext.md` | 待人工获取全文清单（自动生成，勿手改） |
| `_reports/library-reading/SOP.md` | 文库阅读与摘录的工作流 |
| `_reports/library-reading/taxonomy-crosswalk.md` | 分类变更对照表（可读版） |
| `_reports/library-reading/book-outlines/README.md` | 各书的章节大纲 |
| `_reports/library-reading/facts/README.md` | 已抽取的事实条目 |
| `_reports/genus-morphology-gaps.md` | 属级形态描述缺口（哪些属还没有描述） |
| `_reports/genus-morphology-worklist.md` | 属级形态补写清单 |
| `_reports/genus-missing-literature.md` | 待补文献线索 |
| `_reports/genus-literature-candidates.md` | 属级文献候选汇总 |
| `_reports/species-morphology-coverage.md` | 种级形态描述覆盖率 |
| `_reports/species-morphology-worklist.md` | 物种形态补写清单（配套同名 `.csv`） |
| `_reports/species-morphology-no-source.md` | 文库中对不上号的待补种 |
| `_reports/species-morphology-bd-review.md` | B/C 类种级形态复核方法与结果 |
| `_reports/species-morphology-bd-disposition.csv` | B/C 类逐种处置表 |
| `_reports/species-morphology-dispatch.md` | 剩余 2177 种 + 46 属的补全派单（批次、渠道、工时） |
| `_reports/species-morphology-dispatch.csv` | 派单逐条明细（每种的 BSF 入口、目标文献、获取渠道） |
| `_reports/域名迁移可行性评估-2026-11-12.md` | 换域名的判断依据 |
| `_reports/域名迁移操作手册-2026-11-12.md` | 域名迁移步骤 |
| `_reports/域名迁移验收-2026-11-14.md` | 301 现状与收尾 |

## 9. 现状快照（自动生成，勿手改）

<!-- AUTO:INDEX:BEGIN -->
| 项目 | 数量 |
| --- | --- |
| 支系 / 科 / 亚科 / 属 | 6 / 13 / 18 / 326 |
| 种 / 亚种 / 记录合计 | 3021 / 68 / 3089 |
| 物种页 `_species/*.md` | 3089 |
| 科页 / 亚科页 / 属页（中文） | 13 / 18 / 326 |
| `_data/` 顶层文件 | 26 |
| `_data/` 分片目录（数据集 / 分片文件） | 14 / 8428 |
| `build_*.py` 脚本（`_tools/` + `.github/workflows/`） | 20 |
| 说明文档（`_tools/*.md` / `_reports/**/*.md`） | 15 / 16 |

> 数字由 `_tools/build_ai_index.py --write` 从 `_data/taxonomy.json`、`_species/`、各页面目录与文件系统直接统计，改完数据请重跑 `_tools/regen_all.sh`。
<!-- AUTO:INDEX:END -->
