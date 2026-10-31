# 现存等翅下目（白蚁）拉丁学名—中文正名对照名录（站点）

多页结构化的 GitHub Pages 站点。将本目录内全部文件放入仓库根目录即可。

## 页面
| 文件 | 页面 |
|---|---|
| `index.md` | 首页：简介（作者/版本/引用格式）+ 页面导航 + JSON-LD |
| `list.md` | 名录：搜索框（中文/拉丁名/次异名/拼音/繁体检索）+ 完整对照表（支系—科—亚科—属—种），属级嵌套目录，可靠锚点 |
| `search.md` | 全文搜索：全站全文检索页（Pagefind 静态索引，含名录、物种页、统计、数据与博客；支持 `?q=` 预填） |
| `papers.md` | 文献检索：按拉丁名/中文名/多个关键词检索 OpenAlex + Crossref，默认限定白蚁（等翅目）文献，自动合并次异名，显示摘要，摘要可机器翻译成中文 / English / Español，导出 GB/T 7714 / BibTeX / RIS；三语 |
| `stats.md` | 统计：科/亚科/属级物种数统计表 |
| `name-issues.md` | 命名差异：名录页下一级（`/list/name-issues/`），把本站名与 GBIF / Catalogue of Life / BSF 的对照结果整理成可筛选清单（名称差异 / 匹配存疑 / 覆盖缺口），支持按类型、来源、关键词筛选与每页 50 条分页，附 CSV 与公开 JSON |
| `data.md` | 数据：机器可读结构化数据（JSON）清单，按支系/科/亚科列出全部 22 个文件并逐文件链接 |
| `download.md` | 下载：自动列出 `downloads/` 文件夹内的全部文件，供直接下载 |
| `guestbook.md` | 留言：Giscus 留言板（GitHub 账号登录） |
| `changelog.md` | 版本记录（`/changelog/`）：从 `dataset/CHANGELOG.md` 生成，逐版本列出变更；可订阅 `changelog.atom` |
| `en/*.md` | 英文版：与上表一一对应的 11 个页面（`en/index.md` … `en/papers.md`、`en/changelog.md`，permalink `/en/…/`） |
| `es/*.md` | 西班牙语版：与上表一一对应的 11 个页面（`es/index.md` … `es/papers.md`、`es/changelog.md`，permalink `/es/…/`） |

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
  - `dataset/data/isoptera-checklist.csv`：3068 行逐条表，22 列（Darwin Core 风格列名，含中文正名、模式产地、分布中英、次异名）
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

站点用到的开源检索 / 统计 / 分发组件都不需要数据库或后端服务：

### 1. 名录检索：拼音 + 繁体（`.github/workflows/build_search_index.py` + `assets/search.js`）
- 索引 `search-index.json` 由脚本从 `list.md`（类群标题与种/亚种条目、页面顺序）与 `_species/`（亚种中文名、次异名）生成，**确定性输出**，可用 `--check` 校验。
- 字段：`l` 拉丁名、`z` 中文名、`r` 阶元、`h` 锚点、`f` 所属科中文名（结果里显示「哪个科」）、`s` 次异名、`p` 物种页 slug，以及三个可选增强字段：`py`（拼音连写，如 `daerwenaobaiyi`）、`pi`（拼音首字母）、`zt`（繁体写法）。
- 增强字段由 CI 安装 **pypinyin**（拼音）与 **OpenCC**（简→繁）后在构建时补上：`pip install pypinyin opencc-python-reimplemented`。本地未装依赖时脚本自动跳过增强字段照常生成基础索引（不报错），所以仓库内的 `search-index.json` 是基础版；部署版由 CI 重新生成。
- 前端 `assets/search.js` 依次匹配：拉丁名 / 中文名 / 次异名 / 繁体 / 拼音全拼 / 拼音首字母；无结果时给出「在全站全文搜索中查找」的跳转入口。命令：`python .github/workflows/build_search_index.py [--write|--check|--no-enrich]`。

### 2. 全文搜索：Pagefind（`.github/workflows/pages.yml` + `assets/search-page.js`）
- [Pagefind](https://pagefind.app/) 在 Jekyll 构建**之后**扫描 `_site` 生成静态索引 `_site/pagefind/`（CI 步骤：`pip install "pagefind[extended]==1.5.2"` → `python -m pagefind --site _site`）。
- 必须用 **extended** 版：普通版不带中文/日文分词，中文检索效果差。
- 页面 `search.md` / `en/search.md` / `es/search.md` 的 front matter 里有 `pagefind: true`，`_layouts/default.html` 据此加载 `/pagefind/pagefind-ui.css`、`pagefind-ui.js` 与 `assets/search-page.js`；`bundlePath` 与 `baseUrl` 都带上站点 `baseurl`，因此站点部署在子路径下也能用。
- 本地预览（`jekyll serve`）没有跑 Pagefind，搜索页会显示「索引尚未生成」的回退提示，其余功能不受影响；不生成索引时代码不会报错。
- 索引产物不进仓库（由 CI 生成、随 artifact 部署），因此仓库不变大。
- 物种页的「同属其他种」内链区块带 `data-pagefind-ignore`：它只用于站内抓取路径，**不进全文索引**。该区块每页最多列 40 个同属学名 / 中文名，一旦进索引，每个物种页都「含有」整属的种名，搜一个种名就会带出同属一大片无关页面。`_tools/check_site.py` 第 15 项会在该属性被误删时拦下。

### 3. 访问统计：GoatCounter（已启用，站点代码 `bennetgreen`）
- 开源、无 Cookie、可自托管的访问统计，面板：<https://bennetgreen.goatcounter.com>。
- 配置在 `_data/analytics.yml`，两个字段对应 goatcounter.com 给出的官方片段：`count_url` → `data-goatcounter="https://bennetgreen.goatcounter.com/count"`，`script_src` → `src="https://gc.zgo.at/count.js"`。**把 `count_url` 置空即停用**，页面完全不输出统计脚本。
- `count_local: true` 时才统计本地预览（默认 `false`，线上不受影响）。自托管时把两个字段改成自己的域名即可。
- 统计脚本只上报页面路径、不写 Cookie；如需向访客明示，可在页脚或独立页面加一句声明。

### 4. 引用与导出（`_includes/citation.html` + `assets/site.js`）
- 三个数据页（`data.md` / `en/data.md` / `es/data.md`）通过 `{% include citation.html %}` 插入「引用与导出」区块：GB/T 7714 风格与 BibTeX 各一段，带「复制」按钮（`setupCitations()`，含 `document.execCommand` 回退）；另有 CITATION.cff、DataCite XML、数据集 README 的导入入口。
- 文案与 DOI/版本号全部取自 `_config.yml` 的 `site.dataset`，铸造新 DOI 或改版本后无需改该文件。

### 5. 全局搜索浮层：Ctrl/⌘+K（`assets/search-widget.js`）
- 任何页面按 Ctrl/⌘+K（或点导航右侧搜索按钮）打开浮层，直接调 Pagefind 的 JS API（`/pagefind/pagefind.js`）异步搜索，Enter 打开第一条结果，Esc 关闭，另有「查看全部结果 → /search/?q=」。
- 索引不存在（本地 `jekyll serve`）时自动回退：不报错，浮层里只保留跳转入口。
- 浮层文案来自 `_data/i18n.yml` 的 `search_overlay_*` 三语 key，由 `_layouts/default.html` 以 data 属性传给脚本。
- 物种页的 `<main>` 与 `<h1>` 带 `data-pagefind-filter`（科 / 阶元）与 `data-pagefind-meta`（拉丁名 / 中文名），索引里可据此过滤与展示。

### 6. 搜索词回流（GoatCounter 事件，无 Cookie）
- 名录检索框（`assets/search.js`）与全文搜索页（`assets/search-page.js`）在用户停手 1.5 秒、词长 ≥ 2 时上报一次 GoatCounter 事件（`path=/list?q=…` / `/search?q=…`, `event: true`），同词每次会话只报一次。
- 用途：知道读者实际在找什么（缺哪些中文名 / 异名），指导数据补全；不需要新服务、不写 Cookie。

### 7. 文献检索器：`/papers/`（三语，`assets/papers.js` + `.github/workflows/build_papers.py`）
- 页面：`papers.md` / `en/papers.md` / `es/papers.md`，permalink `/papers/`、`/en/papers/`、`/es/papers/`；导航「文献 / Papers / Artículos」进入。
- 检索：输入拉丁学名、中文名或**多个关键词**（空格分隔，全部匹配；短语加引号），浏览器直接查 **OpenAlex**（主）与 **Crossref**（辅，按 DOI/标题去重合并）。默认追加白蚁（等翅目 + 常见属名）范围过滤，避免关键词检索跑出无关文献；可取消「仅白蚁文献」，或勾选「全文检索」把关键词匹配扩大到全文。常见中英术语会自动互扩（分子↔molecular、系统发育↔phylogeny、肠道↔gut 等）。自动合并 `search-index.json` 里的次异名；可筛「仅中文文献 / 只看有摘要」，按相关度 / 最新 / 被引排序。
- 摘要：OpenAlex `abstract_inverted_index` 按词位置还原；Crossref JATS 摘要去标签补缺；单条缺摘要时可点「尝试获取摘要」再查 Crossref / Semantic Scholar。**只使用开放元数据，不抓出版社页面 / PDF，也不抓知网**；摘要版权归原作者 / 出版方，页面注明来源。
- 摘要翻译：结果卡带「目标语言（中文 / English / Español）+ 翻译摘要」控件，**纯前端直连 MyMemory**（CORS 开放、无密钥、单次 500 字符、按访客 IP 约 5000 字符/天）；按 420 字节分块翻译、已知学名以 `[[n]]` 占位保护后还原、译文写入 `localStorage` 缓存。额度用尽依次回退站点邮箱额度与 Google 非官方接口，都失败时给 Google / Bing 外部翻译链接。可在 `#papers-app` 配 `data-translate-url`（+ `data-translate-key`）改用自建 LibreTranslate 兼容服务。
- 引用导出：每条结果可复制 GB/T 7714、BibTeX、RIS；外链预填 Google Scholar / CNKI / 万方 / 百度学术 / BHL / OpenAlex / Crossref。
- 缓存：`build_papers.py` 按 323 个属查询 OpenAlex（每属 12 条）并补 Crossref 摘要，生成 `_data/papers.json`（物种页静态渲染）与公开副本 `papers-index.json`（`/papers/` 断网兜底）；两者字节一致，`--check` 离线校验。物种页「相关文献」显示本属 top 3 与完整摘要。
- 覆盖率：本次缓存 1540 条中 1053 条有摘要（68.4%），页面会明确显示「暂无摘要」并给出 DOI / OpenAlex / 外部平台链接；不保证 100%。
- 额度与回退：OpenAlex 无 API key 时按出口 IP 共享每日免费额度；额度用尽会 429，`build_papers.py` 自动回退 Crossref（摘要覆盖率会降低）。设置 `OPENALEX_API_KEY` 可走自己的额度；也可用 `--crossref-only` 直接只用 Crossref。
- 刷新：`python .github/workflows/build_papers.py --write`（只补缺失 / 过期）、`--force`（全部重查）、`--refresh --stale-days 180 --time-budget 300`；断点缓存在 `_tmp/papers-cache.json`（不提交）。方法、许可与限制见 `_tools/文献检索器说明.md`。
- 定时刷新：`.github/workflows/papers_refresh.yml` 每天 03:47 UTC 用 GitHub Secret `OPENALEX_API_KEY` 增量刷新（默认 30 天 / 300 秒预算），自动提交 `_data/papers.json` 与 `papers-index.json` 并触发 Pages；手动触发可勾选 `force` 全量重查。**没有 key 时不要开启每日定时**（只会走 Crossref 回退，且 runner 共享 IP 仍可能 429）。


## 外部数据与增强视图（GBIF / Catalogue of Life / Wikidata / BSF / iNaturalist / Crossref）

在原有名录之外，站点把「外部数据」接进来：物种页增加外链与一致性提示，名录页内嵌科/属分布图并在页末整合参考文献增强视图，每个物种页另有种级分布图，并输出更完整的结构化数据。所有外部数据都由 `.github/workflows/` 下的脚本抓取、缓存进仓库并随构建部署；**外部信息只用于外链、对照与展示，绝不写回 `_species/` 或站内分类数据**。

| 功能 | 生成脚本 | 数据缓存 | 页面/模板 |
|---|---|---|---|
| 其它数据库外链 + 一致性提示 | `.github/workflows/build_authority_links.py` | `_data/authority_links.json` | `_includes/species-authority.html`、物种页、`/data/#authority` |
| 世界名录对照（Blattodea Species File） | `.github/workflows/build_bsf_links.py` | `_data/bsf_links.json` + `_tools/bsf对照/工作表.csv` | 物种页「其他数据库」区块 |
| 开放图片图集（CC0 / CC BY / CC BY-SA / 公有领域） | `.github/workflows/build_species_photos.py` + `.github/workflows/crawl_species_photos_loop.py`（循环爬取，`.github/workflows/species_photos_crawl.yml` 每天自动跑） | `_data/species_photos.json` | `_includes/species-gallery.html`、PhotoSwipe 灯箱 |
| 分布图（GBIF occurrence → GeoJSON） | `.github/workflows/build_occurrence_geojson.py` | `assets/geo/{family,genus,species}/**` + `_data/occurrence_summary.json` | 名录页科/属标题下方、物种页种级地图（`_includes/distribution-map.html`） |
| 文献增强（Crossref，可选 BHL） | `.github/workflows/build_references.py` | `_data/references.json`（+ 公开副本 `data/references.json`） | 名录页底部 `#references-doi`（`_includes/references.html`） |
| schema.org 实体图 | 模板内生成（无需脚本） | `_data/authority_links.json`、`_data/bsf_links.json` | `_includes/species-jsonld.html`、首页 Dataset JSON-LD |
| 命名差异看板（名称差异 / 匹配存疑 / 覆盖缺口 + 逐对关系/方向/补录） | `.github/workflows/build_name_issues.py` | `_data/name_issues.json` + 公开副本 `data/name-issues.json`；人工核对备注 `_data/name_issue_reviews.json` | `/list/name-issues/` 及英/西语版、`downloads/isoptera-name-issues.csv`、`downloads/isoptera-synonym-pairs.csv`、物种页「其他数据库」区块（incoming / outgoing） |

| 覆盖情况（截至最近一次抓取） | 数量 |
|---|---|
| GBIF 可外链 / 共 3068 | 2963（96.6%；接受名 2956、异名 7、仅上级阶元 105） |
| Catalogue of Life 可外链 | 2995（97.6%；接受名 2995、仅上级阶元 57、未收录 16） |
| Wikidata 条目（P225） | 2872（93.6%） |
| 与两库接受名完全一致 / 带提示 | 2899（94.5%） / 169 |
| Blattodea Species File 对照 | 有效名 2968、异名 0、待核对 58、未检索到 42（共 3068；抽查 20/20 页可通过） |
| 开放许可照片 | 205 个物种、891 张（iNaturalist 769 + Wikimedia Commons 122） |
| 参考文献（Crossref） | 47/77 条带 DOI，其中 47 条已按 DOI 取回 Crossref 记录；12 条有候选待人工核对 |
| 分布图 | 13 个科级 + 254 个属级 + 1,180 个种级 GeoJSON（`assets/geo/{family,genus,species}/`），87,075 条 GBIF 带坐标记录（访问日期 2026-10-28）；仅名录现生类群，化石种与 `FOSSIL_SPECIMEN` / `MATERIAL_CITATION` 记录已剔除 |

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
- 只收 **CC0 / CC BY / CC BY-SA / 公有领域（Public domain、PD-… 模板）**，逐张生成「作者 · 许可（链接） · 来源」署名；瀑布流版式、图注常显，PhotoSwipe 5（MIT，本地托管）灯箱，无 JS 时可点开原图。
- 图片热链回原站、不复制入库；没有符合许可的照片的物种不显示该区块。
- **循环爬取**：`python .github/workflows/crawl_species_photos_loop.py --round-budget 900` 会一轮接一轮地补，每轮限时、轮间休息，连续几轮没进度就自动停；`_data/species_photos.json` 本身就是断点缓存，随时可以中断。GitHub Actions 工作流 `.github/workflows/species_photos_crawl.yml` 每天 03:17 UTC 自动跑一次，也可以手动触发（可选只抓某个源、或忽略缓存重扫许可）。
- 公有领域文件常常没有作者信息，本站如实写「author not stated」而**不猜测作者**；细节与刷新方式见 `_tools/图片授权与署名说明.md`。

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

### 7. 命名差异与待核对看板（/list/name-issues/）

- 位置：名录页（`/list/`）下一级，三语各一页；从名录页搜索框下方与每个物种页「其他数据库」区块底部进入。
- 内容：把 `_data/authority_links.json` 与 `_data/bsf_links.json` 里需要人工注意的对照结果整理成清单，按三类分组：**名称差异**（外部库把本站名当异名，给出接受名）、**匹配存疑**（模糊匹配 / BSF 多重候选）、**覆盖缺口**（仅上级阶元 / 未收录 / 未检索到）；当前 289 条，涉及 194 个种/亚种。
- 逐对归并（「把异名记录到对应的接收名下面」）：7 条名称差异整理成 **7 对「本站名 ↔ 外部库主张的接受名」**（同一对多库只算一次），逐对判定两件事：
  - **关系**：加词不同 = 「异名」0 对；同种异属（只是换了属）= 「组合差异」7 对——组合差异不算异名。GBIF 常把本站采用的属并入旧属、把本站名写成它认为的「接受名」，方向容易写反，所以不能一律按外部接受名归并。
  - **方向（接收名）**：逐库按**物种级**结论投票（仅上级阶元 / 模糊匹配 / 未收录都不计票）。真异名：没有任何库说本站名是接受名 → 外部接受名为接收名；组合差异：多数库采用本站名 → **本站名为接收名**，否则「方向待定」。当前 7 对里：外部名为接收名 0 对、本站名为接收名 6 对、方向待定 1 对（6 对存在库间分歧）。
  - 页末「名称差异逐对归并」表与 `downloads/isoptera-synonym-pairs.csv`（15 列）给出每对的关系、方向、各库判定与补录状态；物种页「其他数据库」区块按 incoming / outgoing 两侧列出（本种接收了哪些异名 / 外部库把本名放在哪个名字下）。数字随缓存刷新而变，页面与 `meta.counts` 为准。
- **补录规则与现状（当前 0 对）**：只有「真异名 + 方向明确为外部库名为接收名 + 至少两个分类数据库一致认定」（`recordable`）才允许补录；GBIF Backbone 对滞后组合仍标 ACCEPTED 时只作「方向有分歧」提示，不否决。此前看板标「已补录」的 3 对已在 2026.10.30 版**正式合并**（异名物种页删除，名录与各数据文件不再单列，命名人与模式产地并入接受名的次异名列表，`synonym_count` 各加 1），因此当前既无「可补录」也无「已补录」条目：
  - *Amitermes californicus* → *Amitermes wheeleri*（GBIF / CoL / BSF 一致）
  - *Coptotermes guizhouensis* → *Coptotermes formosanus*（CoL / BSF 一致；GBIF 仍标接受名）
  - *Nasutitermes dasyopsis* → *Nasutitermes nigriceps*（CoL / BSF 一致；GBIF 仍标接受名）
  「依外部权威库补录的异名」机制仍在（接受名 front matter 的 `authority_synonym_count` / `authority_synonyms` / `authority_synonym_localities` / `authority_synonym_sources`，来源代码 gbif/col/bsf），用于「异名另有独立记录、是否合并待定」的情形；正式合并后，异名只写进接受名的 `synonyms` / `synonym_localities`，`search-index.json` 仍可按异名命中接受名。原留待人工核对的 *Pericapritermes metatus* → *P. appellans metata* 已在同日按 CoL 的接受名改为亚种；另有 3 对组合差异（*Velocitermes aporeticus* → *Diversitermes aporeticus*、*Parvitermes mexicanus* → *Nasutitermes mexicanus*、*Parvitermes bacchanalis* → *Obtusitermes bacchanalis*）以及 *Megagnathotermes katangensis* → *Polyspathotermes katangensis*（CoL / BSF 接受该组合，GBIF Backbone 尚未收录）也按外部接受名改正，详见 `dataset/CHANGELOG.md`。
- **拼写变体与人工核对（当前 5 条）**：看板里的模糊匹配不一定是本站拼错——外部库可能少一个字母（*Cortaritermes silvestrii* → *silvestri*、*Niuginitermes variratae* → *variatae*、*Euhamitermes chhotanii* → *chhotannii*），或者 GBIF Backbone 尚未收录新名而把它模糊匹配到另一个有效种（*Incisitermes mariae* → *I. marianus*）；还有一条是外部库仍用旧组合（*Ruptitermes franciscoi* 被 GBIF 归为 *Anoplotermes franciscoi* 的同物异名，但后者只是 2015 年新组合的基础异名，并非独立物种）。这 5 条经与原始描述逐条核对，本站名正确、**不改名**；核对结论写进 `_data/name_issue_reviews.json`（`verified` / `note`），`build_name_issues.py` 生成看板时套用（页面与 CSV 标「已人工核对」并给出依据），不改站内分类数据，也不写回外部库缓存。详见 `_tools/外部权威库与一致性核对.md` 第 4.3 节。
- 交互：按类型与来源筛选、关键词检索（拉丁名 / 中文名 / 外部名 / 科名）、每页 50 条分页，状态写进 URL（`?group=&source=&q=&page=`）可分享；无 JS 时展示全部条目。
- 产物：`_data/name_issues.json`（页面用；`synonym_pairs` = 逐对关系/方向/票数，`species_authority` = 物种页 incoming/outgoing 索引，`synonym_of_slug` = 已补录异名的反查）、`data/name-issues.json`（公开副本，程序化访问）、`downloads/isoptera-name-issues.csv`（17 列，含外部记录 URL 与人工核对状态）、`downloads/isoptera-synonym-pairs.csv`（15 列，一行一对）。
- 生成：`python .github/workflows/build_name_issues.py [--write|--check]`，确定性输出，CI 在 Jekyll 构建前执行；脚本只整理缓存并**读取** `_species` 的 `authority_synonym_*` 判断哪些异名已补录，不改动任何站内分类数据（补录本身是直接编辑接受名的 front matter）。外链基址读 `_config.yml` 的 `external.*` 并去掉 YAML 行尾注释（否则「# + /<GBIF usageKey>」会被拼进 URL，页面上异名/接受名的链接会变成坏地址甚至破坏 HTML），`_tools/check_site.py` 也会校验产物里没有这类脏 URL。

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

## 订阅与分发（Atom / JSON Feed / OpenSearch / 版本记录）
- `feed.xml`（Atom，博客文章）与 `feed.json`（JSON Feed 1.1）由 Jekyll 页面模板直接输出（`permalink: /feed.xml`、`/feed.json`，`sitemap: false`），不依赖插件；`_layouts/default.html` 的 `<head>` 里有 `<link rel="alternate">` 自动发现。
- `changelog.atom`：由 `_tools/build_changelog.py` 从 `dataset/CHANGELOG.md` 生成（确定性输出，`--check` 校验），逐版本列出归档变更；人读版在 `/changelog/`（三语，`_data/changelog.json` 驱动）。
- `opensearch.xml`：OpenSearch 描述文档，浏览器可把本站加为搜索引擎（检索地址 `/search/?q=…`）。
- `index.md`（三语）输出 `WebSite` + `SearchAction` JSON-LD（与已有 Dataset 实体并存），便于搜索引擎识别站内搜索框。

## 物种级引用与打印
- 物种页底部有「引用本种 / Cite this species」折叠块（`_layouts/species.html`），提供 GB/T 7714、BibTeX、RIS 三种字符串，一键复制；内容全部由 front matter + `site.dataset` 现场拼出，无需逐页生成。
- `assets/custom.css` 有完整 `@media print`：隐藏导航 / 页脚 / 搜索浮层 / 目录侧栏 / 地图控件 / 灯箱 / 分页控件，白底黑字、表格边框、标题与卡片避免跨页截断、正文外链后附 URL；打印前 `assets/site.js` 会展开引用折叠块。

## 可访性与贡献入口
- 每页首个元素是 `.skip-link`（跳到 `#main-content`），样式在 `assets/custom.css`；地图容器已有 `role` / `aria-label`。
- 每个物种页底部（`_includes/species-authority.html` 末尾，不依赖外部库是否匹配到该种）有「报告错误」入口，预填 GitHub Issue Form（`.github/ISSUE_TEMPLATE/name-correction.yml`）的标题与学名 / 中文名 / 页面 URL。
- `.github/PULL_REQUEST_TEMPLATE.md`、`CONTRIBUTING.md` 明确三语同步、生成脚本顺序与提交前校验。

## 校验与巡检（GitHub Actions）
| 工作流 | 触发 | 内容 |
|---|---|---|
| `validate.yml` | PR + push main | 跑 `_tools/check_site.py` 结构检查，再重跑全部生成脚本并用 `git status --porcelain` 断言「已提交产物与脚本输出一致」 |
| `pages.yml` 内的 `verify` job | deploy 后 | 线上抽查 14 个 URL（状态 200 + 关键内容，含 `/list/name-issues/`、`/changelog/`、`/feed.xml`、`/pagefind/pagefind.js`），失败即红 |
| `linkcheck.yml` | 每周一 cron + 手动 | Jekyll 构建后 lychee 两步：`--offline` 校验站内链接与锚点；在线检查外链（排除 iNat / 维基图床 / doi.org，见 `lychee.toml`）；失败开 issue |
| `a11y.yml` | PR + 每周一 cron | 构建后本地起服务，用 `@axe-core/cli` 扫首页 / 名录 / 物种页 / 搜索页；先 `continue-on-error` 观察 heading-order 基线 |
| `species_photos_crawl.yml` | 每天 | 图片循环抓取（原有） |

## 其它
- `_config.yml`：启用 jekyll-seo-tag 与 jekyll-sitemap
- **标题规则**：标签页 `<title>` 只显示本页语言，不做双语拼接；双语只出现在页头（主行 + 副行，见上文「多语言」）。因此各页 front matter 只需一个 `title`，不再有 `title_alt`。
- **数据校验闸门**：`_tools/check_site.py`（只读，纯标准库）检查三语 `list.md` 同构、名录内部锚点、物种页面包屑锚点、批次计数（`_species` 页数 = 检索索引种/亚种条数 = sitemap 物种 URL 数 = 名录物种链接数）、sitemap 与 i18n、命名差异产物自洽，并把「中文重名 / 缺分布 / 标题层级跳级」列为提醒。用法：`python _tools/check_site.py`（加 `--ci` 输出 GitHub Actions 注解）。`.github/workflows/validate.yml` 在 PR 与推送到 main 时运行它，并重新生成全部派生产物后用 `git status --porcelain` 断言「已提交的产物与脚本输出一致」；`pages.yml` 在构建前也跑一次结构检查，数据有错就不部署。
- `robots.txt`：允许主流搜索引擎与 AI 爬虫抓取。**注意**：爬虫只读域名根 `https://bennetgreen-bilibili.github.io/robots.txt`，而本仓库的文件发布在 `…/-Extant-…-List.md/robots.txt` 这个子路径下，因此这份规则目前不生效（域名根 404 等价于全站允许，无副作用）；要让它生效需另建 `bennetgreen-bilibili.github.io` 用户站仓库。sitemap 请在 Search Console 直接提交
- `sitemap.xml`：站点地图，由 jekyll-sitemap 插件在构建时自动生成（含全部页面、文章与物种页）；工具页（`dataset/`、`dataset/CHANGELOG.html`、`assets/vendor/leaflet/`、Google 验证文件、根目录那份中文长文件名单文件版）已在 `_config.yml` 的 `defaults` 里用 `sitemap: false` 排除，两种格式的 URL 集合因此一致（均为 3099 条）
- `sitemap.txt`：纯文本格式站点地图（每行一个绝对 URL，共 3099 条：30 个页面（中文 10 + 英文 10 + 西语 10）+ 1 篇文章 + 3068 个物种页；Google/Bing 均支持该格式），由 `.github/workflows/build_sitemap_txt.py` 从仓库源文件生成，CI 在 Jekyll 构建前自动重跑（位于 `_inbox` 转换之后，故 `_inbox` 自动转成的文章也会收录进部署版）。增删页面/物种页后本地执行 `python .github/workflows/build_sitemap_txt.py` 同步，`--check` 只校验不写文件
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
- `_species/*.md`：Jekyll 集合（collection），共 3068 个文件（3004 种 + 64 亚种），每个物种/亚种一页，URL 为 `/species/<slug>/`（slug 为拉丁学名小写、空格转连字符，如 `mastotermes-darwiniensis`）。
- **物种页是三语单页**：不设 `/en/species/`、`/es/species/` 副本，一个物种一页，页内同时承载中文/英文/西班牙文信息——固定标签写作「中文主 + `.fact-en`（英文）+ `.fact-es`（西文）」（如 `模式产地 Type locality Localidad tipo`），分布字段同时给出中文记录与英文记录（数据本身只有这两列），学名与中文正名在同一 H1。三语站的名录页都链接到这些共享物种页。
- `_layouts/species.html`：物种页模板（面包屑 + 学名/中文正名 + 模式产地/分布速览 + 同属内链）；面包屑「名录」带英文/西文小字，页面不显示语言切换（同一页服务三种语言）。
- `list.md` / `en/list.md` / `es/list.md`：名录中每个物种名已链接到对应物种页（三语共用同一批 URL）。
- 在 `_config.yml` 中通过 `collections.species` 注册（`output: true`，`permalink: /species/:name/`）。
- 物种页正文由 `.github/workflows/build_species_body.py` 生成（见下文「物种页正文」）。
- 物种页底部有「同属其他种」内链区块：列出同属全部物种（最多 40 个，超出部分链接到 `/list/#<属id>`），用于增加站内抓取路径；数据来自 `_data/species_by_genus.json`，由 `.github/workflows/build_genus_index.py` 在 CI 构建时自动重新生成。本地新增/改名物种后，先执行 `python .github/workflows/build_genus_index.py` 再构建。
- 如需新增/修改物种页内容，直接编辑对应 `_species/<slug>.md` 的正文（front matter 已含学名、中文正名、分类层级与模式种标记）。

## 物种页正文（自动生成）
- 生成器：`.github/workflows/build_species_body.py`。把 front matter（学名、中文正名、命名人年份、模式产地、分布、异名、依外部权威库补录的异名、亚种）+ `isoptera-data.json`（属内种数、模式属模式种）+ `data/index.json`（科/亚科计数、数据文件路径）写成每个物种页的正文：**摘要 / 分类位置 / 分布 / 次异名 / 亚种**（每页 800–3900 字，3068 条摘要句互不相同）。
- 内容只写在 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 两个标记之间。标记**外**的文字可以随意手写（生态习性、照片说明、考证），脚本永远不会覆盖。
- 手写多语言内容也放在标记外：正文直接写中文段落，非中文内容用 `lang` 标注，例如 `<div class="fact-es" lang="es">…</div>`、`<div class="fact-en" lang="en">…</div>`（`.fact-en` / `.fact-es` 为灰色小字样式，见 `assets/custom.css`）。自动生成的正文与章节标题目前只有中文；若要连正文一起三语，需要改 `build_species_body.py`（会重写 3068 页，属大改动）。
- 幂等：脚本重复运行零改动，因此更新数据后重新生成时，**只有源数据真正变了的页面才会产生 diff**。
- 用法：`python .github/workflows/build_species_body.py`（只统计、不写文件）、`--write`（写回 `_species/*.md`）、`--sample <slug>...`（打印生成结果）、`--check-idempotent`。
- CI 中位于 `pages.yml` 的「Build species page bodies」步骤，在 Jekyll 构建前执行，保证数据变更后正文同步。
- 生成内容完全来自仓库内已有字段，不做外部事实补全；分布、模式产地等地名沿用原始数据写法。
- 「次异名」一节的结构：原始文献次异名（`synonyms` / `synonym_localities` / `synonym_count`）在前，编号列表；若 front matter 另有 `authority_synonym_count` / `authority_synonyms` / `authority_synonym_localities` / `authority_synonym_sources`，再接一个「依外部权威库补录的异名」小节（项目符号列表，逐条给出模式产地与来源）。补录数据只影响该小节与检索索引，不改 `synonym_count`；2026.10.30 版已把此前 3 对「已补录」异名正式并入 `synonyms`（`synonym_count` 各加 1），当前没有只存在于该小节的条目。

## 搜索引擎收录推送（IndexNow）
- 根目录 `182d630ef67e7551ab41b920fcdba760.txt` 是 IndexNow 的 key 验证文件：文件名就是 key，内容也必须恰好是同一串 key。**不要改名、不要删、不要改内容**，否则 IndexNow 会拒收提交。
- `.github/workflows/indexnow.py` 在 `pages.yml` 的 `indexnow` job（`needs: deploy`）里执行：部署完成后读取线上 sitemap，把本次提交改动到的页面 URL 批量 POST 到 `https://api.indexnow.org/indexnow`（Bing / Yandex / Seznam / Naver / Yep 共享端点），让它们分钟级重新抓取。
- 默认只推送**本次改动涉及的 URL**（`--changed`，用 `git diff HEAD^` 映射：`_species/x.md → /species/x/`、`list.md → /list/`、`en/x.md → /en/x/`、`es/x.md → /es/x/`、`_posts/2026-10-22-welcome.md → /blog/2026/10/22/welcome/`…）。若改动涉及模板/配置（`_layouts/`、`_data/`、`assets/`、`_config.yml`），自动退化为提交整个 sitemap。
- 该 step 设了 `continue-on-error: true`：推送失败只会标黄，不会让部署失败。
- 手动执行：`python .github/workflows/indexnow.py --dry-run`（只解析不提交）、`--changed --dry-run`、`--sitemap <本地或线上 sitemap 路径>`。
- Google 不支持 IndexNow（sitemap ping 也已停用），Google 侧依靠 `sitemap.xml` + 站内链接 + 时间；百度/必应中国的站长平台 API 需要 token，暂未接入。