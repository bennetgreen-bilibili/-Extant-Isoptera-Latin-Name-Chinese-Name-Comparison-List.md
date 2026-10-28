# 现存等翅下目（白蚁）拉丁学名—中文正名对照名录（站点）

多页结构化的 GitHub Pages 站点。将本目录内全部文件放入仓库根目录即可。

## 页面
| 文件 | 页面 |
|---|---|
| `index.md` | 首页：简介（作者/版本/引用格式）+ 页面导航 + JSON-LD |
| `list.md` | 名录：搜索框（中文/拉丁名/次异名/拼音/繁体检索）+ 完整对照表（支系—科—亚科—属—种），属级嵌套目录，可靠锚点 |
| `search.md` | 全文搜索：全站全文检索页（Pagefind 静态索引，含名录、物种页、统计、数据与博客；支持 `?q=` 预填） |
| `stats.md` | 统计：科/亚科/属级物种数统计表 |
| `data.md` | 数据：机器可读结构化数据（JSON）清单，按支系/科/亚科列出全部 22 个文件并逐文件链接 |
| `download.md` | 下载：自动列出 `downloads/` 文件夹内的全部文件，供直接下载 |
| `guestbook.md` | 留言：Giscus 留言板（GitHub 账号登录） |
| `en/*.md` | 英文版：与上表一一对应的 8 个页面（`en/index.md` … `en/search.md`，permalink `/en/…/`） |
| `es/*.md` | 西班牙语版：与上表一一对应的 8 个页面（`es/index.md` … `es/search.md`，permalink `/es/…/`） |

> 分布图与文献不再是独立页面：**分布图**内嵌在名录页每个科、属标题下方（每个物种页另有该种自己的种级地图）；**77 条参考文献的 Crossref / DOI 增强视图**内嵌在名录页底部（`#references-doi`）。原来的 `/distribution/`、`/references/` 三语页面已移除。

## 多语言（中文 / English / Español）
- 三种语言一套模板：`_layouts/default.html` 读页面 front matter 的 `lang`（`zh-CN` / `en` / `es`）决定语言前缀、导航、页脚与语言切换；页面路径去掉 `/en`、`/es` 前缀后同构，`hreflang` 与语言切换链接都由它推导。
- 界面文案唯一来源：`_data/i18n.yml`（导航、页脚、页头副标题、语言切换名、回到顶部、页头品牌）。**新增一门语言**只需：① 这里加一个语言键；② `_config.yml` 加 `title_xx`（页头主标题）；③ 建 `xx/` 目录下与根目录一一对应的页面（`lang: xx` + `permalink: /xx/…/`）。模板、hreflang、语言切换、sitemap 脚本都不用改（`build_sitemap_txt.py` 会自动收录新目录）。
- 页面标题：标签页 `<title>` 只显示本页语言（各页 front matter 的 `title`）；页头显示双语标题——主行＝本页语言（`title_zh` / `title_en` / `title_es`），副行＝另一语言（中文页→英文，英文页→中文，西语页→英文），副行只出现在页头。
- 物种页 `_species/` 与文章 `_posts/` 目前只有中文内容：这两类页面不显示语言切换（文章页的 English/Español 切换指向 `/en/blog/`、`/es/blog/`），标题仍是「拉丁学名 + 中文正名」/ 中文标题。
- 西语版说明：`es/list.md` 由 `en/list.md` 生成（8543 行、362 个锚点与英文版完全一致，仅界面文案与若干段科/亚科/支系描述译成西语，参考文献原文保留），新增/改名物种后需与中文版一样同步更新三个 `list.md`；描述性段落为机器翻译初稿，建议母语者校对后再定稿。三个 `list.md` 中每个科/属标题下的分布图 include 与页末的文献 include 由同一套规则插入（见 `_tools/分布图与瓦片使用政策.md`），新增/改名类群时一并补齐。

## 结构化数据（按类群拆分）
- 页面：`data.md`（/data/，列出全部文件及白蚁科 18 亚科的逐文件链接）
- 入口：`data/index.json`（分类树 + 全部文件清单）
- `data/mastotermitidae.json`、`data/teletisoptera.json`、`data/kalotermitidae.json`、`data/neoisoptera-excl-termitidae.json`
- `data/termitidae/*.json`（白蚁科 18 亚科，逐亚科文件）
- `search-index.json`（检索索引，供名录页搜索框；由 `.github/workflows/build_search_index.py` 从 `list.md` + `_species/` 生成，见下文「站内检索与开源组件」）

## 归档数据集与 DOI（dataset/）
- 生成脚本：`.github/workflows/build_dataset.py`（只用标准库，确定性输出，可 `--check`）。产物：
  - `dataset/data/isoptera-checklist.csv`：3071 行逐条表，22 列（Darwin Core 风格列名，含中文正名、模式产地、分布中英、次异名）
  - `dataset/data/isoptera-taxonomy.json`：完整分类树（支系—科—亚科—属—种/亚种，含各级计数与页面链接）
  - `dataset/data/isoptera-synonyms.csv`、`isoptera-counts.csv`、`isoptera-references.csv`
  - `dataset/datapackage.json`（字段字典）、`dataset/datacite-metadata.xml`（DataCite 4.6 记录）
  - `dataset/README.md`（其中 AUTO / DOI 两个标记区块由脚本自动填充，标记外手写内容不受影响）、`dataset/LICENSE`、`dataset/CHANGELOG.md`、`dataset/CHECKSUMS.sha256`
  - `downloads/isoptera-checklist-v<版本>.zip`：可直接上传 Zenodo 的归档包（downloads 页自动列出）
  - 仓库根 `CITATION.cff`（GitHub 仓库页「Cite this repository」按钮）与 `.zenodo.json`（Zenodo GitHub 集成）
- 元数据唯一来源：`dataset/metadata.json`（标题、描述、作者、关键词、许可、DOI、相关标识符、来源）。
- 命令：`python .github/workflows/build_dataset.py`（自检）、`--write`（写入）、`--check`（校验仓库内产物是否最新）。
- **铸造成 DOI 后**：把 DOI 填进 `dataset/metadata.json` 的 `doi.version` / `doi.concept` 和 `_config.yml` 的 `dataset.doi` / `dataset.concept_doi`，再跑 `--write`。站内「引用与 DOI」区块、页脚 DOI 链接、`<link rel="cite-as">`、首页 JSON-LD 的 `identifier` 会自动出现，不需要改页面。
- 完整操作流程（Zenodo 预留 DOI 的先后顺序、GBIF checklist 二次发布、ScienceDB 国内路线、Google Dataset Search 收录、常见坑）：见 `_tools/数据集DOI与归档发布指南.md`。
- 逐步操作单（照抄的字段值、可复制命令、发布后验收脚本）：见 `_tools/Zenodo发布逐步操作手册.md`。

## 站内检索与开源组件

站点用到两个开源检索/统计组件，都不需要数据库或后端服务：

### 1. 名录检索：拼音 + 繁体（`.github/workflows/build_search_index.py` + `assets/search.js`）
- 索引 `search-index.json` 由脚本从 `list.md`（类群标题与种/亚种条目、页面顺序）与 `_species/`（亚种中文名、次异名）生成，**确定性输出**，可用 `--check` 校验。
- 字段：`l` 拉丁名、`z` 中文名、`r` 阶元、`h` 锚点、`s` 次异名、`p` 物种页 slug，以及三个可选增强字段：`py`（拼音连写，如 `daerwenaobaiyi`）、`pi`（拼音首字母）、`zt`（繁体写法）。
- 增强字段由 CI 安装 **pypinyin**（拼音）与 **OpenCC**（简→繁）后在构建时补上：`pip install pypinyin opencc-python-reimplemented`。本地未装依赖时脚本自动跳过增强字段照常生成基础索引（不报错），所以仓库内的 `search-index.json` 是基础版；部署版由 CI 重新生成。
- 前端 `assets/search.js` 依次匹配：拉丁名 / 中文名 / 次异名 / 繁体 / 拼音全拼 / 拼音首字母；无结果时给出「在全站全文搜索中查找」的跳转入口。命令：`python .github/workflows/build_search_index.py [--write|--check|--no-enrich]`。

### 2. 全文搜索：Pagefind（`.github/workflows/pages.yml` + `assets/search-page.js`）
- [Pagefind](https://pagefind.app/) 在 Jekyll 构建**之后**扫描 `_site` 生成静态索引 `_site/pagefind/`（CI 步骤：`pip install "pagefind[extended]==1.5.2"` → `python -m pagefind --site _site`）。
- 必须用 **extended** 版：普通版不带中文/日文分词，中文检索效果差。
- 页面 `search.md` / `en/search.md` / `es/search.md` 的 front matter 里有 `pagefind: true`，`_layouts/default.html` 据此加载 `/pagefind/pagefind-ui.css`、`pagefind-ui.js` 与 `assets/search-page.js`；`bundlePath` 与 `baseUrl` 都带上站点 `baseurl`，因此站点部署在子路径下也能用。
- 本地预览（`jekyll serve`）没有跑 Pagefind，搜索页会显示「索引尚未生成」的回退提示，其余功能不受影响；不生成索引时代码不会报错。
- 索引产物不进仓库（由 CI 生成、随 artifact 部署），因此仓库不变大。

### 3. 访问统计：GoatCounter（已启用，站点代码 `bennetgreen`）
- 开源、无 Cookie、可自托管的访问统计，面板：<https://bennetgreen.goatcounter.com>。
- 配置在 `_data/analytics.yml`，两个字段对应 goatcounter.com 给出的官方片段：`count_url` → `data-goatcounter="https://bennetgreen.goatcounter.com/count"`，`script_src` → `src="https://gc.zgo.at/count.js"`。**把 `count_url` 置空即停用**，页面完全不输出统计脚本。
- `count_local: true` 时才统计本地预览（默认 `false`，线上不受影响）。自托管时把两个字段改成自己的域名即可。
- 统计脚本只上报页面路径、不写 Cookie；如需向访客明示，可在页脚或独立页面加一句声明。

### 4. 引用与导出（`_includes/citation.html` + `assets/site.js`）
- 三个数据页（`data.md` / `en/data.md` / `es/data.md`）通过 `{% include citation.html %}` 插入「引用与导出」区块：GB/T 7714 风格与 BibTeX 各一段，带「复制」按钮（`setupCitations()`，含 `document.execCommand` 回退）；另有 CITATION.cff、DataCite XML、数据集 README 的导入入口。
- 文案与 DOI/版本号全部取自 `_config.yml` 的 `site.dataset`，铸造新 DOI 或改版本后无需改该文件。

## 外部数据与增强视图（GBIF / Catalogue of Life / Wikidata / BSF / iNaturalist / Crossref）

在原有名录之外，站点把「外部数据」接进来：物种页增加外链与一致性提示，名录页内嵌科/属分布图并在页末整合参考文献增强视图，每个物种页另有种级分布图，并输出更完整的结构化数据。所有外部数据都由 `.github/workflows/` 下的脚本抓取、缓存进仓库并随构建部署；**外部信息只用于外链、对照与展示，绝不写回 `_species/` 或站内分类数据**。

| 功能 | 生成脚本 | 数据缓存 | 页面/模板 |
|---|---|---|---|
| 其它数据库外链 + 一致性提示 | `.github/workflows/build_authority_links.py` | `_data/authority_links.json` | `_includes/species-authority.html`、物种页、`/data/#authority` |
| 世界名录对照（Blattodea Species File） | `.github/workflows/build_bsf_links.py` | `_data/bsf_links.json` + `_tools/bsf对照/工作表.csv` | 物种页「其他数据库」区块 |
| 开放图片图集（CC0 / CC BY / CC BY-SA） | `.github/workflows/build_species_photos.py` | `_data/species_photos.json` | `_includes/species-gallery.html`、PhotoSwipe 灯箱 |
| 分布图（GBIF occurrence → GeoJSON） | `.github/workflows/build_occurrence_geojson.py` | `assets/geo/{family,genus,species}/**` + `_data/occurrence_summary.json` | 名录页科/属标题下方、物种页种级地图（`_includes/distribution-map.html`） |
| 文献增强（Crossref，可选 BHL） | `.github/workflows/build_references.py` | `_data/references.json`（+ 公开副本 `data/references.json`） | 名录页底部 `#references-doi`（`_includes/references.html`） |
| schema.org 实体图 | 模板内生成（无需脚本） | `_data/authority_links.json`、`_data/bsf_links.json` | `_includes/species-jsonld.html`、首页 Dataset JSON-LD |

| 覆盖情况（截至最近一次抓取） | 数量 |
|---|---|
| GBIF 可外链 / 共 3071 | 2967（96.6%；接受名 2957、异名 10、仅上级阶元 104） |
| Catalogue of Life 可外链 | 2996（97.6%；异名 6、仅上级阶元 59、未收录 16） |
| Wikidata 条目（P225） | 2875（93.6%） |
| 与两库接受名完全一致 / 带提示 | 2896（94.3%） / 175 |
| Blattodea Species File 对照 | 有效名 2963、异名 3、待核对 62、未检索到 43（共 3071；抽查 20/20 页可通过） |
| 开放许可照片 | 202 个物种、875 张（iNaturalist 758 + Wikimedia Commons 117） |
| 参考文献（Crossref） | 47/77 条带 DOI，其中 47 条已按 DOI 取回 Crossref 记录；12 条有候选待人工核对 |
| 分布图 | 13 个科级 + 属级 + 种级 GeoJSON（`assets/geo/{family,genus,species}/`），仅名录现生类群，化石记录已剔除 |

### 1. 其它数据库外链与「本站名 vs 外部接受名」一致性提示
- 每个物种页的「其他数据库」区块给出 GBIF Backbone、Catalogue of Life（ChecklistBank）、Wikidata、Blattodea Species File 的链接、状态（接受名/异名/存疑/未收录）与匹配置信度。
- **只提示、不改数据**：外部库把本站名视为异名时显示接受名与对方记录链接，并注明本站数据保持原样；与两库接受名一致时显示 ✔；仅模糊匹配或未收录时给黄色提示。
- GBIF 外链有门槛（`matchType=EXACT`，或 `FUZZY` 且 `confidence ≥ 95`，且阶元为种/亚种），避免把属级近似当成本种。
- 逐条对照表：`downloads/isoptera-authority-crossref.csv`（GBIF/COL ID、状态、接受名、Wikidata QID、差异标记），`/data/#authority` 有说明与下载入口。
- 方法与判定规则见 `_tools/外部权威库与一致性核对.md`。

### 2. 世界名录对照（Blattodea Species File）
- BSF（<https://cockroach.speciesfile.org>，已并入原 Isoptera Species File）覆盖蜚蠊与白蚁，含命名、文献、模式标本、分布与图片；站点由 TaxonWorks / TaxonPages（MIT）构建，可深链到 OTU：`/otus/<OTU>/overview`。
- 它没有稳定公开 API，因此采用**半自动**流程：脚本按学名自动匹配 OTU 并给出「自动匹配」徽章；人工核对工作表（`_tools/bsf对照/工作表.csv`）复核后 `--import` 回来才显示「已人工核对」。未检索到/不确定的条目也如实标注。
- 复核流程见 `_tools/bsf对照/操作说明.md`。

### 3. 开放图片图集（iNaturalist + Wikimedia Commons）
- 只收 **CC0 / CC BY / CC BY-SA** 三种许可（拒绝 NC/ND/PD 等），逐张生成「作者 · 许可（链接） · 来源」署名；PhotoSwipe 5（MIT，本地托管）灯箱，无 JS 时可点开原图。
- 图片热链回原站、不复制入库；没有自由许可照片的物种不显示该区块。
- 细节与刷新方式见 `_tools/图片授权与署名说明.md`。

### 4. 分布图（GBIF occurrence → GeoJSON + Leaflet，内嵌在名录与物种页）
- 预生成 **科级 13 个、属级每个属、种级每个种** 的 1° 网格 GeoJSON（`assets/geo/{family,genus,species}/*.geojson`），名录页每个科/属标题下方与每个物种页用**本地托管**的 Leaflet（BSD-2）渲染；地图只在滚动进视口时创建，不预取瓦片。
- 只统计本名录收录的现生类群：GBIF 中不属于本名录的物种（含全部化石种、琥珀化石）被排除，`basisOfRecord` 为 `FOSSIL_SPECIMEN` / `MATERIAL_CITATION` 的记录也被剔除——地图上不会再混入化石产地。
- 数据是「仅有记录」的 occurrence 聚合，不代表实际分布边界；每个属都取全 GBIF 中的带坐标记录（上限 30000 条作为安全阈值），采样偏差在名录页顶部「分布图怎么读」与 `_tools/分布图与瓦片使用政策.md` 中说明。
- 种级地图在种页面按需创建（不预取瓦片），因此即使 3000 多个种页也不会把公共瓦片当免费 CDN。

### 5. 文献增强（Crossref + 可选 BHL，已整合进名录页底部）
- 把名录文末 77 条参考文献按 DOI 补全为 Crossref 书目记录，生成 GB/T 7714 式、APA、Vancouver 三种引用与 BibTeX / RIS / CSL-JSON；原文没有 DOI 的条目**不臆造 DOI**，只给候选供人工核对。
- 增强视图直接内嵌在名录页底部（`#references-doi`），三个 `list.md` 各用 `{% include references.html %}` 引入，支持一键复制、导出 CSL-JSON；BHL 原始描述扫描为可选增强（需免费 `BHL_API_KEY`，见 `_tools/参考文献与DOI补全说明.md`）。
- 权威条目仍是名录页文末的编号列表（正文上标的 (1)…(77) 都指向它），增强视图只是它的展开。

### 6. 结构化数据（JSON-LD 实体图）
- 物种页输出 schema.org `Taxon`（含 `scientificName`、`taxonRank`、中文 `alternateName`、`parentTaxon`、`identifier`）与 `BreadcrumbList`；`sameAs` 指向 GBIF / Catalogue of Life / Wikidata / BSF 条目，`isPartOf` 指向首页的 Dataset 实体。
- 首页三语 `Dataset` JSON-LD 增加了固定 `@id`，因此 `Dataset ← isPartOf ← Taxon` 构成同一实体图，便于搜索引擎与学术聚合器识别。字段缺失（如没有 Wikidata 条目）时自动省略，不输出空数组。

### 外部数据的刷新与 CI
- 全部缓存已提交进仓库，构建时不需要现场抓 3000+ 次 API。CI 在 Jekyll 构建前：① 离线校验各缓存（`--check` / `--verify`，坏 JSON 会立刻暴露但不阻断部署）；② 对权威库外链做一次 ≤120 秒的「过期条目」增量刷新（失败不阻断部署，部署版可能比仓库缓存新）。
- 手动全量刷新（建议每月或换 Catalogue of Life 年度版本后执行）：
```bash
python .github/workflows/build_authority_links.py --write --refresh-all   # GBIF / COL / Wikidata
python .github/workflows/build_bsf_links.py --write --refresh            # Blattodea Species File（≈2 req/s）
python .github/workflows/build_species_photos.py --write --refresh       # iNaturalist + Commons
python .github/workflows/build_references.py --write                    # Crossref（可加 --bhl）
python .github/workflows/build_occurrence_geojson.py --write --refresh   # GBIF 分布图
```
- 各脚本都支持 `--check`（离线校验）与断点续跑；缓存文件变大是正常的（`_data/` 下最大的是权威库与图片缓存）。

## 其它
- `_config.yml`：启用 jekyll-seo-tag 与 jekyll-sitemap
- **标题规则**：标签页 `<title>` 只显示本页语言，不做双语拼接；双语只出现在页头（主行 + 副行，见上文「多语言」）。因此各页 front matter 只需一个 `title`，不再有 `title_alt`。
- `robots.txt`：允许主流搜索引擎与 AI 爬虫抓取
- `sitemap.xml`：站点地图，由 jekyll-sitemap 插件在构建时自动生成（含全部页面、文章与物种页）
- `sitemap.txt`：纯文本格式站点地图（每行一个绝对 URL，共 3096 条：24 个页面（中文 8 + 英文 8 + 西语 8）+ 1 篇文章 + 3071 个物种页；Google/Bing 均支持该格式），由 `.github/workflows/build_sitemap_txt.py` 从仓库源文件生成，CI 在 Jekyll 构建前自动重跑（位于 `_inbox` 转换之后，故 `_inbox` 自动转成的文章也会收录进部署版）。增删页面/物种页后本地执行 `python .github/workflows/build_sitemap_txt.py` 同步，`--check` 只校验不写文件
- `llms.txt`：llmstxt.org 规范的站点说明
- `assets/search.js`、`assets/search-page.js`、`assets/custom.css`：名录搜索框 / 全文搜索页脚本与样式

## 下载 / 留言
- **下载页**（`download.md` / `en/download.md`）：把要提供下载的文件放进仓库 `downloads/` 文件夹即可，页面用 Jekyll `site.static_files` 自动列出，无需改页面。占位文件 `downloads/.gitkeep` 可删除。
- **留言页**（`guestbook.md` / `en/guestbook.md`）：使用 Giscus（GitHub Discussions 留言）。
  1. 在仓库 Settings → General → Features 勾选 **Discussions** 并保存（仓库需为公开仓库）。
  2. 打开 https://giscus.app/ ，填写仓库 `bennetgreen-bilibili/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md`。
  3. 在 Discussion Category 里选择一个分类（如 General / Announcements）。
  4. 复制生成的 `data-category` 与 `data-category-id`，替换 `guestbook.md` 和 `en/guestbook.md` 中对应的占位值。

## 物种页（每个物种/亚种一个独立页面）
- `_species/*.md`：Jekyll 集合（collection），共 3071 个文件（3008 种 + 63 亚种），每个物种/亚种一页，URL 为 `/species/<slug>/`（slug 为拉丁学名小写、空格转连字符，如 `mastotermes-darwiniensis`）。
- **物种页是三语单页**：不设 `/en/species/`、`/es/species/` 副本，一个物种一页，页内同时承载中文/英文/西班牙文信息——固定标签写作「中文主 + `.fact-en`（英文）+ `.fact-es`（西文）」（如 `模式产地 Type locality Localidad tipo`），分布字段同时给出中文记录与英文记录（数据本身只有这两列），学名与中文正名在同一 H1。三语站的名录页都链接到这些共享物种页。
- `_layouts/species.html`：物种页模板（面包屑 + 学名/中文正名 + 模式产地/分布速览 + 同属内链）；面包屑「名录」带英文/西文小字，页面不显示语言切换（同一页服务三种语言）。
- `list.md` / `en/list.md` / `es/list.md`：名录中每个物种名已链接到对应物种页（三语共用同一批 URL）。
- 在 `_config.yml` 中通过 `collections.species` 注册（`output: true`，`permalink: /species/:name/`）。
- 物种页正文由 `.github/workflows/build_species_body.py` 生成（见下文「物种页正文」）。
- 物种页底部有「同属其他种」内链区块：列出同属全部物种（最多 40 个，超出部分链接到 `/list/#<属id>`），用于增加站内抓取路径；数据来自 `_data/species_by_genus.json`，由 `.github/workflows/build_genus_index.py` 在 CI 构建时自动重新生成。本地新增/改名物种后，先执行 `python .github/workflows/build_genus_index.py` 再构建。
- 如需新增/修改物种页内容，直接编辑对应 `_species/<slug>.md` 的正文（front matter 已含学名、中文正名、分类层级与模式种标记）。

## 物种页正文（自动生成）
- 生成器：`.github/workflows/build_species_body.py`。把 front matter（学名、中文正名、命名人年份、模式产地、分布、异名、亚种）+ `isoptera-data.json`（属内种数、模式属模式种）+ `data/index.json`（科/亚科计数、数据文件路径）写成每个物种页的正文：**摘要 / 分类位置 / 分布 / 次异名 / 亚种**（每页 800–3900 字，3071 条摘要句互不相同）。
- 内容只写在 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 两个标记之间。标记**外**的文字可以随意手写（生态习性、照片说明、考证），脚本永远不会覆盖。
- 手写多语言内容也放在标记外：正文直接写中文段落，非中文内容用 `lang` 标注，例如 `<div class="fact-es" lang="es">…</div>`、`<div class="fact-en" lang="en">…</div>`（`.fact-en` / `.fact-es` 为灰色小字样式，见 `assets/custom.css`）。自动生成的正文与章节标题目前只有中文；若要连正文一起三语，需要改 `build_species_body.py`（会重写 3071 页，属大改动）。
- 幂等：脚本重复运行零改动，因此更新数据后重新生成时，**只有源数据真正变了的页面才会产生 diff**。
- 用法：`python .github/workflows/build_species_body.py`（只统计、不写文件）、`--write`（写回 `_species/*.md`）、`--sample <slug>...`（打印生成结果）、`--check-idempotent`。
- CI 中位于 `pages.yml` 的「Build species page bodies」步骤，在 Jekyll 构建前执行，保证数据变更后正文同步。
- 生成内容完全来自仓库内已有字段，不做外部事实补全；分布、模式产地等地名沿用原始数据写法。

## 搜索引擎收录推送（IndexNow）
- 根目录 `182d630ef67e7551ab41b920fcdba760.txt` 是 IndexNow 的 key 验证文件：文件名就是 key，内容也必须恰好是同一串 key。**不要改名、不要删、不要改内容**，否则 IndexNow 会拒收提交。
- `.github/workflows/indexnow.py` 在 `pages.yml` 的 `indexnow` job（`needs: deploy`）里执行：部署完成后读取线上 sitemap，把本次提交改动到的页面 URL 批量 POST 到 `https://api.indexnow.org/indexnow`（Bing / Yandex / Seznam / Naver / Yep 共享端点），让它们分钟级重新抓取。
- 默认只推送**本次改动涉及的 URL**（`--changed`，用 `git diff HEAD^` 映射：`_species/x.md → /species/x/`、`list.md → /list/`、`en/x.md → /en/x/`、`es/x.md → /es/x/`、`_posts/2026-10-22-welcome.md → /blog/2026/10/22/welcome/`…）。若改动涉及模板/配置（`_layouts/`、`_data/`、`assets/`、`_config.yml`），自动退化为提交整个 sitemap。
- 该 step 设了 `continue-on-error: true`：推送失败只会标黄，不会让部署失败。
- 手动执行：`python .github/workflows/indexnow.py --dry-run`（只解析不提交）、`--changed --dry-run`、`--sitemap <本地或线上 sitemap 路径>`。
- Google 不支持 IndexNow（sitemap ping 也已停用），Google 侧依靠 `sitemap.xml` + 站内链接 + 时间；百度/必应中国的站长平台 API 需要 token，暂未接入。