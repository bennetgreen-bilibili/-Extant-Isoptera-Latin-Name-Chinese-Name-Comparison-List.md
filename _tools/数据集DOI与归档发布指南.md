# 数据集 DOI 与归档发布指南

> 适用对象：本仓库（现存等翅下目白蚁名录站点）。目标：把站内名录变成**带 DOI、可被引用、被聚合器收录**的数据集，并把 DOI 回填到站内，形成「站点 ↔ 数据集」双向关联。
> 相关文件：`dataset/`（数据集包）、`.github/workflows/build_dataset.py`（生成脚本）、`dataset/metadata.json`（元数据唯一来源）、`_config.yml` 的 `dataset:` 配置块。
> 照着点的操作单（每一步可复制、可勾选、含验收命令）：**《Zenodo发布逐步操作手册.md》**。

---

## 0. 先认清：DOI 带来什么、不带来什么

**DOI 本身不直接带来流量。** 一个没人引用的 DOI 只是一个更长的链接。DOI 真正的价值是三个"可"：

1. **可引用**：论文、报告、科普、Wikipedia 可以正式引它，引用里带着你的名字与版本号；
2. **可收录**：DataCite / OpenAIRE / BASE / CORE / Google Dataset Search / GBIF 会用元数据把它收进索引，这是"曝光"的主要来源；
3. **可回溯**：归档快照固定，别人引用的版本永远能取到（这正是 GitHub Pages 站点做不到的——站点会一直改）。

所以正确的目标不是"弄一个 DOI"，而是：**做一个元数据完整、字段有说明、有许可、有版本的数据集，发到会被收录的仓储，然后从站点和你的文章里链过去。** 本仓库已经把"数据集包 + 元数据 + 站内引用位"准备好，剩下的是账号操作与发布。

---

## 1. 路线选择

| 路线 | 费用 | DOI 前缀 | 适合 | 说明 |
|---|---|---|---|---|
| **Zenodo**（首选） | 免费 | 10.5281 | 通用数据集、长期归档 | CERN 运营，用 DataCite，支持版本 DOI + 概念 DOI、ORCID、GitHub Release 自动归档；上传即发布，元数据可后改（文件 45 天内可改） |
| **GBIF checklist** | 免费 | 10.15468 | 分类名录、生物多样性 | 通过 IPT / GBIF 托管发布 Darwin Core Archive；面向分类学与生物多样性社区，GBIF 的文献追踪会把引用该 DOI 的论文自动关联回数据集 |
| **ScienceDB（科学数据银行）** | 免费 | 常见 10.57760（以记录页为准） | 国内访问与中文用户 | 中科院系统的数据仓储，中文界面、国内访问快，同样分配 DOI（部分记录带 CSTR 标识）；具体字段与流程以站点当年说明为准 |
| **Pensoft BDJ「数据论文」** | 有 APC | 10.3897 | 追求学术曝光 | 把数据集写成 data paper 正式发表，产出文章 DOI + 数据集 DOI，进 Google Scholar / WoS；适合以后想被正式引用时再考虑，费用需自行核实 |
| Figshare / OSF / Dryad | 免费 / 部分付费 | — | 备选 | Dryad 偏生态进化领域且收费；Figshare/OSF 可作镜像 |

**本仓库推荐组合**：Zenodo 主 DOI（通用引用）+ GBIF checklist（分类学社区曝光）+ 站内回填。两者数据同源（都由 `build_dataset.py` 生成），不要手工各改一份。

---

## 2. Zenodo 全流程（含「预留 DOI」，解决"文件里想写 DOI"的顺序问题）

### 2.0 准备数据包（本地 2 分钟）

    python .github/workflows/build_dataset.py --check   # 先确认仓库内产物是最新的
    python .github/workflows/build_dataset.py --write   # 需要时重新生成

产物：`dataset/` 整个目录 + 可直接上传的 `downloads/isoptera-checklist-v2026.10.17.zip`。

### 2.1 账号

1. 用 GitHub 或邮箱注册/登录 <https://zenodo.org>（免费）。
2. 右上角头像 → **Settings → ORCID**：关联 ORCID（有就关联，元数据会带 `nameIdentifier`，DataCite 与 ORCID 双向可见，提升被发现概率）。
3. 如打算用 GitHub 集成：Settings → **GitHub** 里连接账号。

### 2.2 新建上传并「预留 DOI」

1. 右上角 **+ → New upload**。
2. 上传 `downloads/isoptera-checklist-v2026.10.17.zip`（1 个文件，约 0.5 MB）。
3. 在 **Basic information** 的 DOI 一栏点 **"Get a DOI now!"** —— 这会**在发布前预留一个版本 DOI**（注意：删掉草稿会丢失预留 DOI；DOI 只有发布后才真正注册）。
4. 把这个预留 DOI 填进 `dataset/metadata.json` 的 `doi.version`，然后重新生成，用新 zip 覆盖上传的文件：

       python .github/workflows/build_dataset.py --write

   此时 zip 内的 `README.md`、`CITATION.cff`、`datacite-metadata.xml` 都已带上真实 DOI（`README.md` 的 DOI 区块与 BibTeX 由脚本自动渲染）。
5. 回到 Zenodo 页面删除旧文件、上传新 zip。

> 为什么绕这一圈：DOI 是发布时才注册的，但你又希望归档文件里的 README/CFF 写着 DOI。Zenodo 的预留 DOI 正是为此设计的。第一版如果懒得做，也可以发布后拿到 DOI，再「New version」发一版（版本 DOI 会变，概念 DOI 不变）。

### 2.3 填元数据（照抄 `dataset/datacite-metadata.xml` 或 `dataset/metadata.json`）

| Zenodo 字段 | 填什么 |
|---|---|
| Title | `dataset/metadata.json` 的 `title.en`（英文标题，收录效果更好） |
| Description | 英文摘要（`description.en`）；可追加 `<p>项目网站：…</p>` |
| Creators | 班奈特格林；有 ORCID 填 ORCID；affiliation 可填 Independent researcher |
| Publication date | 2026-10-17 |
| Resource type | **Dataset** |
| License | **CC BY 4.0** |
| Keywords | `metadata.json` 的 `keywords.en + keywords.zh` |
| Language | Chinese (zho) |
| Version | 2026.10.17 |
| Related identifiers | 站点 URL（relation: is documented by）；GitHub 仓库（is supplemented by） |
| Funding | 无则留空，不要编 |

### 2.4 发布与回填

1. **Publish**。
2. 记录页会显示两个 DOI：**版本 DOI**（本版唯一）与 **概念 DOI / Concept DOI**（所有版本共用，指向最新版）。把概念 DOI 填进 `metadata.json` 的 `doi.concept`。
3. 回填站内配置 `_config.yml`：

       dataset:
         doi: "10.5281/zenodo.XXXXXXXX"          # 版本 DOI
         concept_doi: "10.5281/zenodo.YYYYYYYY"  # 概念 DOI

   再跑一次 `--write` 让 `CITATION.cff` / `.zenodo.json` 同步，提交并部署。之后：站内「数据」页与首页会出现 DOI 与 APA 引用格式，全站 3086 个页面的页脚出现 DOI 链接，`<link rel="cite-as">` 与首页 JSON-LD 的 `identifier` 自动出现（这些都给 Google Dataset Search / DataCite 提供关联信号）。
4. 可选但推荐：`llms.txt` 里补一行 DOI（该文件是静态文本，脚本不处理）：

       版本 DOI：10.5281/zenodo.XXXXXXXX　概念 DOI：10.5281/zenodo.YYYYYYYY

### 2.5 以后每次更新数据

1. 改数据 → `build_dataset.py --write`（版本号升到新的日期）；
2. Zenodo 记录页 **New version** → 上传新 zip → 发布（新版本 DOI）；
3. `_config.yml` 的 `dataset.doi` 改成新版本 DOI（概念 DOI 不变）。

---

## 3. GBIF checklist 路线（第二个 DOI + 分类学社区曝光）

**为什么值得做**：GBIF 是分类名与分布数据的头号检索入口；GBIF 数据集会分配 DOI（`10.15468` 前缀）；GBIF 的文献追踪会自动把引用该 DOI 的论文挂回数据集页面——这对"被同行看到"非常有效。

**做法（概要）**：

1. 造一个 **Darwin Core Archive**（zip 内含 `taxon.txt`、`meta.xml`、`eml.xml`）：
   - `taxon.txt` 必备：`taxonID`、`scientificName`、`taxonRank`、`parentNameUsageID`、`genus`、`family`、`vernacularName`（中文名放这里）、`taxonRemarks`；
   - `parentNameUsageID` 用物种页 URL 规则构造（亚种指向母种页面）；
   - `eml.xml` 写标题、作者、许可（CC BY 4.0）、引用方式。
2. 用 GBIF 的 **IPT**（Integrated Publishing Toolkit，可自建或使用托管实例）注册资源 → 发布 checklist。
3. 发布后在 GBIF 数据集页拿到 DOI，回填到 `dataset/metadata.json` 的 `relatedIdentifiers`（`IsSupplementedBy` 或 `IsIdenticalTo` 视情况），再 `--write`。

本仓库当前主表列名已按 Darwin Core 风格设计（`taxonID / scientificName / taxonRank / parentNameUsage / genus / family / vernacularName`），改成 `taxon.txt` 只需补 `parentNameUsageID`、把 CSV 改成制表符分隔并加 `meta.xml`/`eml.xml`。可作为数据集 v2 的一步（脚本里加一个 `--dwc` 导出即可）。

**提醒**：名录里"分布"是文字描述，不要包装成精确坐标发布；GBIF checklist 的定位是"名录"，与 occurrence（标本/观测）是两类资源。

---

## 4. 站内回填与曝光动作清单

发布当天（30 分钟）：

- [ ] `_config.yml`：`dataset.doi` / `dataset.concept_doi`
- [ ] `dataset/metadata.json`：`doi.version` / `doi.concept` → `--write`
- [ ] `llms.txt`：补 DOI 行（静态文件，手动）
- [ ] 提交、等 Pages 部署，打开 `/data/` 与首页确认 DOI、APA 引用格式已显示
- [ ] Google Search Console：重新提交 `sitemap.xml`（含新页面时）
- [ ] Google **Dataset Search**：确认 Zenodo 记录可被检索（Zenodo 本身是被支持的仓储；站内 JSON-LD 的 `identifier`/`sameAs` 是补充信号）
- [ ] **DataCite Commons**（<https://commons.datacite.org/>）用 DOI 查一次，确认元数据已登记
- [ ] **ORCID**：把数据集加进 Works（有 ORCID 的话）
- [ ] 在博客文章 / B 站简介 / 相关科普里引用 DOI 并链接到 `/data/`

长期（真正决定曝光）：

- [ ] 论文、报告、图鉴里引用 DOI（哪怕只是"名录参考"）
- [ ] 给 GBIF / Wikipedia / Wikidata 相关条目补链接（有合适条目时）
- [ ] 每次数据更新发新版本（版本 DOI 会累积 citations，概念 DOI 始终指向最新）

---

## 5. 常见坑

1. **把整个网站 zip 当数据集**：几千个页面文件、无字段说明，聚合器不会收录，审稿人也不会用。→ 只发 `dataset/` 里的数据文件（本仓库已按此打包）。
2. **没有 README / 字段字典 / 许可**：DataCite 元数据再全，用户拿到文件也读不懂；CC BY 4.0 必须明确。→ 已含 `README.md`、`datapackage.json`、`LICENSE`。
3. **DOI 指向"活的网站"而不是归档快照**：内容和版本会漂移，引用不可复现。→ DOI 指向 Zenodo 归档包，站点只做检索入口。
4. **把中文正当作学名**：数据集必须声明"不构成命名行为（no nomenclatural act）"，并说明中文名是编者层。→ 已在 README 与 DataCite 描述中声明。
5. **版本 DOI / 概念 DOI 用错**：论文里应引**版本 DOI**（可复现），需要"永远最新"的场合用概念 DOI。站内两个都展示。
6. **发布后才发现漏字段**：Zenodo 发布后文件只能改 45 天，元数据可改但版本记录会留痕。→ 发布前跑 `--check` 并过一遍 `datacite-metadata.xml`。
7. **关键词堆砌、描述机翻**：会被判定为低质量。→ 用现在的中英双语描述即可，别再堆词。
8. **两份数据不一致**：Zenodo、GBIF、站点各改一份。→ 唯一来源是仓库 + 生成脚本，任何改动都 `--write` 后重新归档。
9. **预留 DOI 后删草稿**：预留 DOI 会丢，只能重新预留。
10. **只发 DOI 不建关联**：少了站内 3000+ 页面的链接、`cite-as` 与 JSON-LD 信号，等于放弃一半曝光。

---

## 6. 验收清单

- [ ] `python .github/workflows/build_dataset.py --check` 通过（产物与生成结果一致）
- [ ] `dataset/README.md` 的 AUTO 区块有文件清单与 SHA-256；DOI 区块显示真实 DOI
- [ ] `.zenodo.json` / `CITATION.cff` 的 DOI 与 `_config.yml` 一致
- [ ] Zenodo 记录页：Resource type = Dataset、License = CC BY 4.0、Related identifiers 含站点与仓库
- [ ] 站内 `/data/`、`/en/data/`、首页均显示 DOI 与引用格式；页脚有 DOI 链接
- [ ] `https://doi.org/<DOI>` 可解析；DataCite Commons 能查到元数据
- [ ] GBIF（若发布）：dataset 页有 DOI，taxon 页能检索到名录

---

## 7. 本仓库相关文件索引

| 文件 | 作用 |
|---|---|
| `.github/workflows/build_dataset.py` | 生成数据集包（`--write` / `--check` / `--strict`） |
| `dataset/metadata.json` | 元数据唯一来源（标题、描述、作者、关键词、许可、DOI、相关标识符） |
| `dataset/datacite-metadata.xml` | 照抄填 Zenodo / ScienceDB / DataCite 表单 |
| `dataset/datapackage.json` | 字段字典（Frictionless Data Package） |
| `dataset/README.md` | 归档包说明（AUTO / DOI 区块由脚本填充） |
| `dataset/CHECKSUMS.sha256` | 数据文件校验和 |
| `downloads/isoptera-checklist-v2026.10.17.zip` | 直接上传 Zenodo 的归档包 |
| `.zenodo.json` | Zenodo GitHub 集成元数据（若用 Release 自动归档） |
| `CITATION.cff`（仓库根） | GitHub「Cite this repository」按钮 |
| `_config.yml` `dataset:` 块 | 铸造后只改这里，站内自动显示 DOI |
