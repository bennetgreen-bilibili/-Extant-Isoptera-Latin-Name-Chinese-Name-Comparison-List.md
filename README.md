# 现存等翅下目（白蚁）拉丁学名—中文正名对照名录（站点）

多页结构化的 GitHub Pages 站点。将本目录内全部文件放入仓库根目录即可。

## 页面
| 文件 | 页面 |
|---|---|
| `index.md` | 首页：简介（作者/版本/引用格式）+ 页面导航 + JSON-LD |
| `list.md` | 名录：搜索框（中文/拉丁名/次异名检索）+ 完整对照表（支系—科—亚科—属—种），属级嵌套目录，可靠锚点 |
| `stats.md` | 统计：科/亚科/属级物种数统计表 |
| `data.md` | 数据：机器可读结构化数据（JSON）清单，按支系/科/亚科列出全部 22 个文件并逐文件链接 |
| `download.md` | 下载：自动列出 `downloads/` 文件夹内的全部文件，供直接下载 |
| `guestbook.md` | 留言：Giscus 留言板（GitHub 账号登录） |
| `en/*.md` | 英文版：与上表一一对应的 7 个页面（`en/index.md` … `en/guestbook.md`，permalink `/en/…/`） |
| `es/*.md` | 西班牙语版：与上表一一对应的 7 个页面（`es/index.md` … `es/guestbook.md`，permalink `/es/…/`） |

## 多语言（中文 / English / Español）
- 三种语言一套模板：`_layouts/default.html` 读页面 front matter 的 `lang`（`zh-CN` / `en` / `es`）决定语言前缀、导航、页脚与语言切换；页面路径去掉 `/en`、`/es` 前缀后同构，`hreflang` 与语言切换链接都由它推导。
- 界面文案唯一来源：`_data/i18n.yml`（导航、页脚、页头副标题、语言切换名、回到顶部、页头品牌）。**新增一门语言**只需：① 这里加一个语言键；② `_config.yml` 加 `title_xx`（页头主标题）；③ 建 `xx/` 目录下与根目录一一对应的页面（`lang: xx` + `permalink: /xx/…/`）。模板、hreflang、语言切换、sitemap 脚本都不用改（`build_sitemap_txt.py` 会自动收录新目录）。
- 页面标题：标签页 `<title>` 只显示本页语言（各页 front matter 的 `title`）；页头显示双语标题——主行＝本页语言（`title_zh` / `title_en` / `title_es`），副行＝另一语言（中文页→英文，英文页→中文，西语页→英文），副行只出现在页头。
- 物种页 `_species/` 与文章 `_posts/` 目前只有中文内容：这两类页面不显示语言切换（文章页的 English/Español 切换指向 `/en/blog/`、`/es/blog/`），标题仍是「拉丁学名 + 中文正名」/ 中文标题。
- 西语版说明：`es/list.md` 由 `en/list.md` 生成（7939 行、362 个锚点与英文版完全一致，仅界面文案与 74 段科/亚科/支系描述译成西语，参考文献原文保留），新增/改名物种后需与中文版一样同步更新三个 `list.md`；描述性段落为机器翻译初稿，建议母语者校对后再定稿。

## 结构化数据（按类群拆分）
- 页面：`data.md`（/data/，列出全部文件及白蚁科 18 亚科的逐文件链接）
- 入口：`data/index.json`（分类树 + 全部文件清单）
- `data/mastotermitidae.json`、`data/teletisoptera.json`、`data/kalotermitidae.json`、`data/neoisoptera-excl-termitidae.json`
- `data/termitidae/*.json`（白蚁科 18 亚科，逐亚科文件）
- `search-index.json`（检索索引，供名录页搜索框）

## 归档数据集与 DOI（dataset/）
- 生成脚本：`.github/workflows/build_dataset.py`（只用标准库，确定性输出，可 `--check`）。产物：
  - `dataset/data/isoptera-checklist.csv`：3071 行逐条表，22 列（Darwin Core 风格列名，含中文正名、模式产地、分布中英、次异名）
  - `dataset/data/isoptera-taxonomy.json`：完整分类树（支系—科—亚科—属—种/亚种，含各级计数与页面链接）
  - `dataset/data/isoptera-synonyms.csv`、`isoptera-counts.csv`、`isoptera-references.csv`
  - `dataset/datapackage.json`（字段字典）、`dataset/datacite-metadata.xml`（DataCite 4.6 记录）
  - `dataset/README.md`（其中 AUTO / DOI 两个标记区块由脚本自动填充，标记外手写内容不受影响）、`dataset/LICENSE`、`dataset/CHANGELOG.md`、`dataset/CHECKSUMS.sha256`
  - `downloads/isoptera-checklist-v<版本>.zip`：可直接上传 Zenodo 的归档包（downloads 页自动列出）
  - `dataset/dwc-a/` + `downloads/isoptera-checklist-dwca-v<版本>.zip`：**GBIF checklist 发布用** Darwin Core Archive（`taxon.txt` 3767 行 = 接受名 3071 + 次异名 696、`vernacularname.txt` 3071 行、`meta.xml`、`eml.xml` 通过 GBIF Metadata Profile 1.1 校验）；与 Zenodo 包同源但不进 Zenodo zip
  - 仓库根 `CITATION.cff`（GitHub 仓库页「Cite this repository」按钮）与 `.zenodo.json`（Zenodo GitHub 集成）
- 元数据唯一来源：`dataset/metadata.json`（标题、描述、作者、关键词、许可、DOI、相关标识符、来源）。
- 命令：`python .github/workflows/build_dataset.py`（自检）、`--write`（写入）、`--check`（校验仓库内产物是否最新）。
- **铸造成 DOI 后**：把 DOI 填进 `dataset/metadata.json` 的 `doi.version` / `doi.concept` 和 `_config.yml` 的 `dataset.doi` / `dataset.concept_doi`，再跑 `--write`。站内「引用与 DOI」区块、页脚 DOI 链接、`<link rel="cite-as">`、首页 JSON-LD 的 `identifier` 会自动出现，不需要改页面。
- 完整操作流程（Zenodo 预留 DOI 的先后顺序、GBIF checklist 二次发布、ScienceDB 国内路线、Google Dataset Search 收录、常见坑）：见 `_tools/数据集DOI与归档发布指南.md`。
- 逐步操作单（照抄的字段值、可复制命令、发布后验收脚本）：见 `_tools/Zenodo发布逐步操作手册.md`。
- GBIF checklist（第二 DOI，10.15468）逐步操作单（发布资格/背书、IPT 上传、元数据照抄表、回填与验收）：见 `_tools/GBIF-checklist发布逐步操作手册.md`。

## 其它
- `_config.yml`：启用 jekyll-seo-tag 与 jekyll-sitemap
- **标题规则**：标签页 `<title>` 只显示本页语言，不做双语拼接；双语只出现在页头（主行 + 副行，见上文「多语言」）。因此各页 front matter 只需一个 `title`，不再有 `title_alt`。
- `robots.txt`：允许主流搜索引擎与 AI 爬虫抓取
- `sitemap.xml`：站点地图，由 jekyll-sitemap 插件在构建时自动生成（含全部页面、文章与物种页）
- `sitemap.txt`：纯文本格式站点地图（每行一个绝对 URL，共 3093 条：21 个页面（中文 7 + 英文 7 + 西语 7）+ 1 篇文章 + 3071 个物种页；Google/Bing 均支持该格式），由 `.github/workflows/build_sitemap_txt.py` 从仓库源文件生成，CI 在 Jekyll 构建前自动重跑（位于 `_inbox` 转换之后，故 `_inbox` 自动转成的文章也会收录进部署版）。增删页面/物种页后本地执行 `python .github/workflows/build_sitemap_txt.py` 同步，`--check` 只校验不写文件
- `llms.txt`：llmstxt.org 规范的站点说明
- `assets/search.js`、`assets/custom.css`：搜索框脚本与样式

## 下载 / 留言
- **下载页**（`download.md` / `en/download.md`）：把要提供下载的文件放进仓库 `downloads/` 文件夹即可，页面用 Jekyll `site.static_files` 自动列出，无需改页面。占位文件 `downloads/.gitkeep` 可删除。
- **留言页**（`guestbook.md` / `en/guestbook.md`）：使用 Giscus（GitHub Discussions 留言）。
  1. 在仓库 Settings → General → Features 勾选 **Discussions** 并保存（仓库需为公开仓库）。
  2. 打开 https://giscus.app/ ，填写仓库 `bennetgreen-bilibili/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md`。
  3. 在 Discussion Category 里选择一个分类（如 General / Announcements）。
  4. 复制生成的 `data-category` 与 `data-category-id`，替换 `guestbook.md` 和 `en/guestbook.md` 中对应的占位值。

## 物种页（每个物种/亚种一个独立页面）
- `_species/*.md`：Jekyll 集合（collection），共 3071 个文件（3008 种 + 63 亚种），每个物种/亚种一页，URL 为 `/species/<slug>/`（slug 为拉丁学名小写、空格转连字符，如 `mastotermes-darwiniensis`）。
- `_layouts/species.html`：物种页模板（面包屑 + 学名/中文正名 + 模式产地/分布速览 + 同属内链）。
- `list.md` / `en/list.md`：名录中每个物种名已链接到对应物种页。
- 在 `_config.yml` 中通过 `collections.species` 注册（`output: true`，`permalink: /species/:name/`）。
- 物种页正文由 `.github/workflows/build_species_body.py` 生成（见下文「物种页正文」）。
- 物种页底部有「同属其他种」内链区块：列出同属全部物种（最多 40 个，超出部分链接到 `/list/#<属id>`），用于增加站内抓取路径；数据来自 `_data/species_by_genus.json`，由 `.github/workflows/build_genus_index.py` 在 CI 构建时自动重新生成。本地新增/改名物种后，先执行 `python .github/workflows/build_genus_index.py` 再构建。
- 如需新增/修改物种页内容，直接编辑对应 `_species/<slug>.md` 的正文（front matter 已含学名、中文正名、分类层级与模式种标记）。

## 物种页正文（自动生成）
- 生成器：`.github/workflows/build_species_body.py`。把 front matter（学名、中文正名、命名人年份、模式产地、分布、异名、亚种）+ `isoptera-data.json`（属内种数、模式属模式种）+ `data/index.json`（科/亚科计数、数据文件路径）写成每个物种页的正文：**摘要 / 分类位置 / 分布 / 次异名 / 亚种**（每页 800–3900 字，3071 条摘要句互不相同）。
- 内容只写在 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 两个标记之间。标记**外**的文字可以随意手写（生态习性、照片说明、考证），脚本永远不会覆盖。
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
