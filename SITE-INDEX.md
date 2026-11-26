# 站点内部索引（SITE-INDEX）

> **先读这页，再按表只打开需要的那几个文件。**
> 仓库里有 3,000+ 个 `.md`、8,500+ 个 `_data` 分片、20 万个磁盘文件，绝大多数是生成产物；真正决定站点
> 内容的源文件不到 50 个。为了「了解项目」通读工作区，既慢，又会把生成产物当成源文件去改。
>
> **分层阅读**（只在需要时打开下一层；本页约 8.5 千字，原来是 2.5 万字）：
>
> | 什么时候读 | 读哪个 |
> | --- | --- |
> | 任何改动：定位文件、判断能不能改、改完连带什么 | 本页 |
> | 知道要改什么，但不确定是哪个目录 / 哪个文件生成的 | `_meta/LAYOUT.md`（目录地图 + 页面 → 源文件） |
> | 改 `_data/` 的内容，或判断某个数据文件是源还是派生 | `_meta/DATA-MAP.md`（逐文件角色 + 分片布局 + 定位方法） |
> | 跑生成链、本地构建、交付前校验 | `_meta/PIPELINE.md`（16 步生成链 + 校验命令） |
> | 查某份说明文档讲什么 | `_meta/DOCS.md` |
>
> 本页手写维护；末尾「现状快照」的计数由 `_tools/build_ai_index.py --write` 刷新。
> `--check` 校验：新增的 `_data` 顶层文件、`_data/<数据集>/` 分片目录、生成脚本、说明文档有没有登记
> （本页与 `_meta/*.md` 一起算，没登记就报错）。
>
> 配套阅读：`AGENTS.md`（硬约定，含来源存档）｜`CONTRIBUTING.md`（流程细节）｜`README.md`（站点功能长文）｜`llms.txt`（对外 AI 说明）

## 0. 三十秒路由表

| 你想做的事 | 改这里 | 然后跑 | 最容易漏 |
| --- | --- | --- | --- |
| 改一个物种的学名 / 中文名 / 命名人 / 模式产地 / 分布 / 异名 | `_species/<slug>.md` 的 front matter | `bash _tools/regen_all.sh` | 学名同时决定 permalink 与 slug，改名要改五处（见 §3.2） |
| 新增 / 删除一个物种或亚种 | 新建 / 删除 `_species/<slug>.md` | `bash _tools/regen_all.sh` | 所属属必须已存在于 `_data/taxonomy.json` |
| 改一个属的位置（科 / 亚科）或增删科、亚科、属 | `_data/taxonomy.json` | `bash _tools/regen_all.sh` | `id` 就是页面 URL，改 id = 旧链接 404 |
| 改科 / 亚科正文（三语） | `_data/taxon_prose/`（分片，见 `_meta/DATA-MAP.md` §5） | `bash _tools/regen_all.sh` | 同时影响 `/family/`、`/subfamily/` 与 `/list/sections/` 合订本 |
| 改 `/list/` 的导语、按科浏览、参考文献块（三语） | `_data/list_index_blocks.json` | `bash _tools/regen_all.sh` | 三语三份都要改，`check_site` 校验锚点同构 |
| 改界面文案（导航、页脚、按钮、语言切换名…） | `_data/i18n.yml` | `python _tools/check_site.py` | `zh-CN` / `en` / `es` 三节 key 必须完全一致（各 94 个） |
| 改页面结构、样式、交互 | `_layouts/`、`_includes/`、`assets/*.css`、`assets/*.js` | `python _tools/check_liquid.py` + `python _tools/check_lang_pages.py --ci` | 三语页面同构；模板里别新增 `site.pages` 遍历 |
| 新增一个页面 | 根目录 + `en/` + `es/` 各一份 | `python _tools/check_site.py` | front matter 的 `title` / `description` / `permalink` / `lang` 四件套 |
| 改 77 条参考文献 | 根目录名录单文件的 `## 参考文献` 区块 | `python .github/workflows/build_references.py --write` | 改完必须重跑 `build_dataset.py --write`（数据集也解析这 77 条） |
| 改数据集元数据 / DOI / 版本 | `dataset/metadata.json` + `_config.yml` 的 `dataset:` | `python .github/workflows/build_dataset.py --write` | 两处要保持一致，`check_site` 会比对版本号 |
| 查某条论断的出处 | `.sources/`（`Sxxxx` 记录） | `python _tools/sources.py check --strict` | 正文里的 `<!-- src:Sxxxx -->` 必须能对上记录 |
| 补属级 / 种级形态描述 | `_data/morphology_genera/`、`_data/morphology_species/`、`_data/fauna_species/`、`_data/fauna_measurements/`（一阶元一档） | `bash _tools/regen_all.sh` | 三语译文在 `_data/translations_en/`、`_data/translations_es/`，缺译文时整节省略、不回退中文 |
| 查命名冲突 / 外部库差异 | `_data/name_issues.json`（派生，勿手改） | `.github/workflows/build_name_issues.py --write` | 人工裁定写在 `_data/name_issue_reviews.json` |
| 发一个新版本（数据集归档） | `dataset/CHANGELOG.md` + `dataset/metadata.json` | `python .github/workflows/build_dataset.py --write` | `dataset/LICENSE` 改动同样会让归档 zip 过期 |
| 只在本地跑站点看效果 | — | 见 `_meta/PIPELINE.md` §4 | Windows 上 Jekyll 必须先进 `_langsrc/<lang>/` 再 build |

### 0.1 先定位，再改

- **找某个物种**：`ls _species | grep <slug 关键词>`，或 `grep -l "latin: .*Heterotermes" _species/*.md`；
  拿到文件后只改 front matter，正文交给 `build_species_body.py`。
- **找某个属 / 科**：属的 id 与归属在 `_data/taxonomy.json`；`genus/<id>.md`、`family/<id>.md` 是生成页，
  改位置、改中文名都改 `taxonomy.json`，不要直接编辑页面。
- **找某条论断的出处**：`grep -n "src:S0" <文件>`；记录本身在 `.sources/records/Sxxxx.md`。
- **找某段正文属于哪个数据文件**：科 / 亚科正文 → `_data/taxon_prose/`；`/list/` 导语 →
  `_data/list_index_blocks.json`；界面字样 → `_data/i18n.yml`；属 / 种形态 → `_data/morphology_*/`、
  `_data/fauna_species/`、`_data/fauna_measurements/`（分片路径见 `_meta/DATA-MAP.md` §5）。
- **判断一个文件能不能改**：先在 `_meta/DATA-MAP.md` §2 / §3 与下面 §3.1 查它是不是派生；派生文件的改动一定会被下一次 `regen_all.sh` 覆盖。

### 0.2 搜索纪律（比多读文档更省时间）

磁盘上有 20 万个文件，其中 99% 是生成产物与临时件：`_langsrc/`（26.6k）、`_site-zh|en|es/`（各 5.3k）、
`_tmp/`（173k）、`_data/` 分片（8.5k）、`_species/`（3.1k）。全仓 `grep` / `glob` 会先走进这些目录，
打满扫描预算后截断，结果常常是「没有匹配」而不是「真的不存在」。**一律把路径限定到目标目录：**

| 要找 | 做法 |
| --- | --- |
| 物种文件 | `grep -l "关键词" _species/*.md`（3,089 个文件，秒级） |
| 属 / 科 / 亚科 | `grep -n '"heterotermes"' _data/taxonomy.json`，或按 id 直接开 `_data/<数据集>/<id>.json` |
| 分片数据 | 按 `_meta/DATA-MAP.md` §5 的路径直接打开，不要 grep `_data/` 全目录 |
| 正文出处引用 | `grep -n "src:S0" <目标文件>` |
| 模板 / 脚本 / 工作流 | `_includes/`、`_layouts/`、`_tools/`、`.github/workflows/` |
| 说明文档 | `_meta/DOCS.md` 有全表，按标题挑一份读 |

`_langsrc/`、`_site-*`、`_site/`、`.jekyll-cache/`、`_tmp/` 里的内容都能重新生成，里面没有任何源信息，**不要在它们里面找东西**。

## 1. 站点概况

- Jekyll 静态站，GitHub Pages 部署，自定义域名 **https://termite-extant-isoptera.org**（`_config.yml` 的 `url`，`baseurl: ""`）。
- 三语：中文在站点根、英文 `/en/`、西班牙文 `/es/`；一套模板（`_layouts/default.html` 按 front matter 的 `lang` 决定语言）。
- 规模：6 支系、13 科、18 亚科、326 属、3,021 种、68 亚种 = **3,089 条**记录；三语各一套页面，构建约 11,300 页。
- 数据版本 2026.11.21；版本 DOI `10.5281/zenodo.23646836`，概念 DOI `10.5281/zenodo.23646835`（CC BY 4.0）。
- 每次构建：`make_lang_sources.py` 造三份硬链接镜像 → 三个容器并行 Jekyll → `merge_lang_sites.py` 合并；细节见 `CONTRIBUTING.md` §发布构建、`_meta/PIPELINE.md` §4。

## 2. 数据层速查

`_data/` 的逐文件角色（源 / 派生 / 缓存）、分片布局与定位方法在 **`_meta/DATA-MAP.md`**，改数据前读那一页即可。
这里只记三条判断：

- **源**（可改）：`taxonomy.json`、`list_index_blocks.json`、`i18n.yml`、`translation_glossary.yml`、`fauna_*.json`、
  `taxonomy_images.json`、`phylogeny.json`、`name_issue_reviews.json`、`fulltext_hosts.json`、`ai_chat.yml`、`analytics.yml`，
  以及 14 个分片目录（`taxon_prose/`、`translations_en|es/`、`etymology/`、`genus_sources/`、`taxon_literature/`、
  `morphology_*`、`fauna_*` 等）。
- **派生**（勿手改）：`species_by_*`、`name_issues.json`、`changelog.json`、`photo_taxa.json`、`subfamily_maps.json`、
  `occurrence_summary.json`、`build.json`、`taxonomy_crosswalk.json`、`fulltext_manual.json`。
- **缓存**（只在刷新时跑）：`authority_links/`、`bsf_links/`、`papers/`、`species_photos/`、`references.json`。

## 3. 改动的连带影响（最容易漏的地方）

### 3.1 派生文件清单：不要手改

`list.md`、`en/list.md`、`es/list.md`、`en/list/sections.md`、`es/list/sections.md`、
`family/*.md`、`subfamily/*.md`、`genus/*.md`、`en/` 与 `es/` 下的全部分类页与物种页、
`photos/**`、`stats.md`、`en/stats.md`、`es/stats.md`、`isoptera-data.json`、`data/*.json`、
`search-index.json`、`sitemap.txt`、`sitemap-core.xml`、`changelog.md`、`changelog.atom`、`name-issues.md`、
`dataset/data/*`、`dataset/datapackage.json`、`dataset/datacite-metadata.xml`、`dataset/CHECKSUMS.sha256`、
`downloads/*.zip`、`_data/` 里 `_meta/DATA-MAP.md` §2 与 §3 列出的文件（§1 的分片是源文件，不在此列）。

`_species/*.md` 只有 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 之外的内容可以手改；
标记之间由 `build_species_body.py` 按 front matter 重写。
`dataset/README.md` 的 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 之间同理，标记外的手写内容不受影响。

### 3.2 连带关系表

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

## 4. 现状快照（自动生成，勿手改）

<!-- AUTO:INDEX:BEGIN -->
| 项目 | 数量 |
| --- | --- |
| 支系 / 科 / 亚科 / 属 | 6 / 13 / 18 / 326 |
| 种 / 亚种 / 记录合计 | 3021 / 68 / 3089 |
| 物种页 `_species/*.md` | 3089 |
| 科页 / 亚科页 / 属页（中文） | 13 / 18 / 326 |
| `_data/` 顶层文件 | 26 |
| `_data/` 分片目录（数据集 / 分片文件） | 14 / 8870 |
| `build_*.py` 脚本（`_tools/` + `.github/workflows/`） | 21 |
| 说明文档（`_tools/*.md` / `_reports/**/*.md`） | 15 / 17 |

> 数字由 `_tools/build_ai_index.py --write` 从 `_data/taxonomy.json`、`_species/`、各页面目录与文件系统直接统计，改完数据请重跑 `_tools/regen_all.sh`。
<!-- AUTO:INDEX:END -->
