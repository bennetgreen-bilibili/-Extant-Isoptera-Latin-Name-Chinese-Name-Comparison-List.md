# 现存等翅下目（白蚁）拉丁学名—中文正名对照名录 · 归档数据集

**Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names — archived dataset**

**版本 Version**：2026.10.30　·　**记录 Records**：3089 条（3021 种 + 68 亚种）　·　**许可 License**：CC BY 4.0　·　**语言 Languages**：中文 · English

<!-- DOI:BEGIN -->
**DOI**：[10.5281/zenodo.23646836](https://doi.org/10.5281/zenodo.23646836)（概念 DOI / 全部版本：10.5281/zenodo.23646835）

**引用格式 Citation（中文 / APA 7）**

> 班奈特格林. (2026). 《现存等翅下目（白蚁）拉丁学名—中文正名对照名录（2026.10.30 正式版）》(版本 2026.10.30) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23646836

**Citation (English, APA 7)**

> Bennet Green. (2026). Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names (version 2026.10.30) (Version 2026.10.30) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23646836

**BibTeX**

```bibtex
@misc{extantisopterachecklist2026,
  author    = {班奈特格林},
  title     = {Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names (version 2026.10.30)},
  year      = {2026},
  version   = {2026.10.30},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.23646836},
  url       = {https://doi.org/10.5281/zenodo.23646836}
}
```
<!-- DOI:END -->

## 这是什么 What this is

本包是「现存等翅下目（白蚁）拉丁学名—中文正名对照名录」的**可引用归档版本**：把项目网站上的名录整理为机器可读、字段完整、可被 DOI 长期引用的数据文件。

数据集覆盖现存等翅下目（Isoptera，白蚁）**全部现生类群**：13 科、18 亚科、326 属、3021 种、68 亚种，共 **3089 条分类单元记录**。每条记录包含：

- 拉丁学名（属名 + 种加词 [+ 亚种加词]）与命名人、年份；
- **中文正名**（本数据集的核心增值内容）；
- 分类等级（species / subspecies）、母种（亚种）与完整分类位置（支系—科—亚科—属，中拉双语）；
- 模式种标记、模式产地、分布（中文 / 英文）；
- 次异名及其模式产地（单独长表）；
- 指向项目网站上对应物种页的永久链接。

配套提供 **77 条参考文献**（带 DOI 者随条目给出，见 `data/isoptera-references.csv`），便于核对名录所依据的分类学与生物学文献。

## 数据集内容 Contents

本目录所有文件均由仓库来源自动生成（主表、分类树、异名表等由 `.github/workflows/build_dataset.py` 生成，`dwca/` 子目录由 `_tools/build_dwca.py` 生成，均只用 Python 标准库），字段字典见 `datapackage.json`。

<!-- AUTO:BEGIN -->
> 构建提示 Build notes：43 个分类单元的次异名与模式产地条数不等，无法逐条对齐（见 isoptera-synonyms.csv 的 localityAlignment / localitySource / localityCounts 列；这些行的 synonymTypeLocality 留空表示「未逐条对齐」，完整产地串仍在 isoptera-checklist.csv 的 synonymLocalities 列）

## 文件清单 Files

| 文件 File | 内容 Content | 记录数 Rows | 字节 Bytes | SHA-256 |
|---|---|---|---|---|
| `data/isoptera-checklist.csv` | 逐条分类单元表（Darwin Core 风格列名；含中文正名、模式产地、分布、次异名） | 3089 | 1374319 | `0d4688268fd0356b…` |
| `data/isoptera-taxonomy.json` | 完整分类树（支系—科—亚科—属—种/亚种，含各级计数与页面链接） | 3089 | 1530514 | `2fefeebcd7bbbe0d…` |
| `data/isoptera-synonyms.csv` | 次异名长表（一行一次异名，含其模式产地） | 704 | 148261 | `b8f4c57b9de98ff2…` |
| `data/isoptera-counts.csv` | 科/亚科级分类单元计数 | 31 | 2216 | `76fce47f5eedeaa0…` |
| `data/isoptera-references.csv` | 参考文献清单（有 DOI 者随条目给出） | 77 | 14186 | `ae7befd446eaac7b…` |

统计 Counts：6 支系 · 13 科 · 18 亚科 · 326 属 · 3021 种 · 68 亚种，合计 3089 条分类单元记录（每条均含中文正名）；参考文献 77 条，其中 46 条带 DOI。

版本 Version：2026.10.30　生成 Generator：.github/workflows/build_dataset.py（可由仓库来源完全重建）　本区块由脚本自动生成，请勿手工编辑；标记外的手写内容不受影响。
<!-- AUTO:END -->

## 与项目网站的关系 Relationship to the project website

- 项目网站（检索、统计、3089 个物种页）：<https://termite-extant-isoptera.org/>
- 网站上的在线 JSON 数据（按类群拆分的 22 个文件）：<https://termite-extant-isoptera.org/data/>
- 源码与更新历史：<https://github.com/bennetgreen-bilibili/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md>

**引用请优先引本包的 DOI（永久、带版本）**；网站适合检索与浏览，DOI 归档版本适合论文引用与长期保存。

## 编制方法与数据来源 Provenance and methods

分类框架以 Krishna 等《Treatise on the Isoptera of the world》(2013) 与 Hellemans 等 (2024, *Nature Communications* 15:6724) 的现生类群分类为主，属、种与异名信息参考 termitologia.net、GBIF、《中国动物志》《白蚁学》等资料以及文末 77 篇文献。

- **拉丁学名与异名**：沿用上述文献与数据库的写法，未作分类学修订。
- **中文正名**：由编者拟定或沿用既有译名。中文名不是命名法规管的学名，不同作者可能有不同译法；正式使用（如论文、报告、科普）前建议对照原始文献或与作者确认。
- **分布**：沿用原始数据中的记录，未逐条核实；格式与粒度因来源而异（国家、地区或具体产地）。
- **模式产地**：沿用原始数据写法，未统一为现代行政区划。

数据可由仓库来源完全重建：脚本读取 3089 个物种页 front matter 与站点分类树，同一版本重跑得到逐字节一致的结果（`--check` 可校验）。

## 字段说明 Fields

完整字段字典（名称、类型、中英文说明）见 `datapackage.json` 的 `resources[].schema.fields`。主表 `data/isoptera-checklist.csv` 主要列：

| 列 Column | 说明 Description |
|---|---|
| taxonID | 站点物种页 URL，同时作为本数据集的分类单元标识符 |
| scientificName / authorship | 拉丁学名 / 命名人与年份 |
| taxonRank | species 或 subspecies |
| parentNameUsage | 亚种所属的种 |
| genus / subfamily / family / clade | 分类位置（拉丁） |
| genusZh / subfamilyZh / familyZh / cladeZh | 分类位置（中文） |
| vernacularName | 中文正名 |
| isTypeSpecies | 是否模式种（yes / no） |
| typeLocality | 模式产地 |
| distributionZh / distributionEn | 分布（中 / 英） |
| synonymCount / synonyms / synonymLocalities | 次异名条数、次异名、次异名模式产地 |
| pageUrl | 对应站点页面 URL |

## 格式与编码 Formats

- CSV：UTF-8（**无 BOM**）、RFC 4180 换行（CRLF）、逗号分隔、首行表头。用 Excel 打开如中文乱码，请用「数据 → 从文本/CSV」并指定 UTF-8。
- JSON：UTF-8，`indent=1`，`ensure_ascii=False`（中文可读）。
- XML：DataCite Metadata Schema 4.6，可直接参考其字段在 DataCite / Zenodo / ScienceDB 等平台录入元数据。
- 归档包 `isoptera-checklist-v2026.10.30.zip`：本目录全部文件的确定性打包（固定时间戳，重跑字节一致）。

读取示例：

    import pandas as pd

    df = pd.read_csv("data/isoptera-checklist.csv", encoding="utf-8")
    df[df["vernacularName"].notna()].head()

    # 某属全部种（含亚种）
    df[df["genus"] == "Coptotermes"][["scientificName", "vernacularName", "distributionZh"]]

## Darwin Core Archive（DwC-A）

`dwca/` 是同一套数据按 **Darwin Core Archive** 组织的版本，供 GBIF Data Validator、IPT、`python-dwca-reader`、R 包 `finch` 等工具直接读取；打包好的归档包在 `downloads/isoptera-checklist-v2026.10.30-dwca.zip`，四个文件都在 zip 根目录。

| 文件 File | 作用 Role |
|---|---|
| `dwca/meta.xml` | metafile：core 的 `rowType` 为 `dwc:Taxon`（含 `<id index="0"/>`），另有一个 `VernacularName` 扩展（含 `<coreid index="0"/>`） |
| `dwca/taxon.csv` | core 表，4134 行 = 接受名 3446（13 科 + 18 亚科 + 326 属 + 3021 种 + 68 亚种）+ 异名 688 |
| `dwca/vernacularname.csv` | 中文正名扩展，3446 行，`language` 用 ISO 639-1 的 `zh` |
| `dwca/eml.xml` | EML 2.1.1 / GBIF Metadata Profile 资源元数据（标题、摘要、许可、关键词、联系人） |
| `dwca/CHECKSUMS.sha256` | 上述四个文件的 SHA-256 |

core 表的列（与 `meta.xml` 的 `index` 一一对应）：`taxonID`、`scientificName`、`scientificNameAuthorship`、`taxonRank`、`taxonomicStatus`、`acceptedNameUsageID`、`parentNameUsageID`、`kingdom`、`phylum`、`class`、`order`、`family`、`subfamily`、`genus`、`higherClassification`、`nomenclaturalCode`、`vernacularName`、`taxonRemarks`。

**标识符与阶元约定（发布后不要改）**

- `taxonID` 一律是站点 URL：科 `/family/{id}/`、亚科 `/subfamily/{id}/`、属 `/genus/{id}/`、种与亚种用各自页面地址、异名 `/taxon/synonym/{slug}-{hash6}/`。它们会成为外部数据库引用的外键，**slug 一旦发布就不应再改**（非改不可时要留 301）。
- 阶元只用 `family / subfamily / genus / species / subspecies`。支系（clade）不是林奈阶元，不单独出行，写进 `higherClassification`（如 `Animalia | Arthropoda | Insecta | Blattodea | Isoptera | Neoisoptera`）。
- 亚科与亚种保留原阶元、不压平：GBIF 的 `taxonRank` 推荐值只有 kingdom / phylum / class / order / family / genus / species 七级，Validator 可能对这两级给出提示——这是刻意的取舍，宁可提示也不丢分类信息。
- 异名行的 `scientificName` 去掉原文献页码（页码进 `taxonRemarks`），命名人进 `scientificNameAuthorship`，并用 `acceptedNameUsageID` 指回接受名；页面上没有的名称不编造 URL。
- 异名里带亚属的写法统一成 `Eutermes (Eutermes) latinasus`（括号内不加空格）：原始文献有「Hodotermes ( Anacanthotermes ) koenigi」这种带空格的写法，紧贴或带空格都要切成同一形态，否则 GBIF 只会把它当成未解析全名。同一「学名 + 命名人」只保留一行（同一条异名有时同时挂在两个接受名下）。
- `nomenclaturalCode` 全部写 `ICZN`：不写这一列时 GBIF 报 “nomenclatural code inferred”。
- `taxonRemarks` 承接 Taxon 核心表里没有专用术语的两项：模式产地（`type locality: …`）与异名原文献页码（`original page reference: …`）。
- `meta.xml` 的 `<archive metadata="eml.xml">` 用**归档内相对路径**（IPT 的写法）：validator 打开 zip 后原地就能找到 EML；写成站点绝对 URL 时它要先联网去取，站点那一版还没部署就整包判「Failed to verify archive format」，不说是哪一步。

**验证与发布**

1. 本机自检：`python _tools/build_dwca.py --check`（列数、`taxonID` 唯一性、`parentNameUsageID` / `acceptedNameUsageID` / 扩展 `coreid` 的引用完整性、`taxonRank` 取值、计数与 `metadata.json` 的 `expectedCounts` 是否一致）。
2. 规范验证：把 zip 传到 <https://www.gbif.org/tools/data-validator>，它会检查 `meta.xml` 是否合规、术语是否在 GBIF registry、`eml.xml` 是否符合 GBIF profile、ID 引用是否完整。
3. 发布：作为附加文件挂到对应 Zenodo 版本上（沿用该版本 DOI）；若要拿 GBIF 的 `10.15468` DOI，则需要一个已获 GBIF 节点背书的发布机构（publishing organization），走 IPT 或邮件 helpdesk@gbif.org 注册。

**关于发布方与联系人**

- `publishingOrganization` 写的是本项目的资源名义（`Extant Isoptera Checklist`）：这是个独立项目，没有 GBIF 节点背书的机构，就不编一个机构名。若以后有机构挂靠，把它改成机构名即可。
- `contact` 填的是项目专用邮箱 `Termite-Extant-Isoptera@protonmail.com` 与 ORCID `0009-0009-8563-8559`，两者会写进 `eml.xml` 的 `<contact>`；同一个 ORCID 也出现在 `<creator>` 和 DataCite 记录的 `nameIdentifier`。改了这几处之后重跑 `python _tools/build_dwca.py --write`（只改数据表之外的东西也要重跑，`--check` 会报不一致）。

## 已知限制与免责声明 Limitations and disclaimer

1. **不构成命名行为**：本数据集是名录汇编，不发表任何新分类单元、不提出任何命名修订（no nomenclatural act）。分类学变动请引用原始文献。
2. **中文正名是编者层**：中文名可能与其他作者的译名不同；本项目不主张其为「唯一正确」中文名。
3. **未逐条核实**：分布、模式产地、异名页码沿用来源数据，未逐条回查原文。
4. **分类框架是某一时点的快照**：白蚁分类仍在变动，引用时请注明版本。
5. **无坐标数据**：本包只有文字分布描述，不含经纬度；如需地理分析，请结合 GBIF 等来源。

## 版本与更新 Versioning

版本号采用目录发布日期（YYYY.MM.DD）。每个版本有独立的版本 DOI，概念 DOI（concept DOI）始终指向最新版。更新记录见 `CHANGELOG.md`。

## 复现 Reproducibility

需要 Python 3.9+（仅标准库，无需第三方包）：

    python .github/workflows/build_dataset.py            # 统计与自检
    python .github/workflows/build_dataset.py --write    # 重新生成全部文件
    python .github/workflows/build_dataset.py --check    # 校验仓库内文件是否最新

DwC-A 依赖上一步产出的 `data/isoptera-taxonomy.json` 与 `data/isoptera-synonyms.csv`，所以排在它之后：

    python _tools/build_dwca.py             # 统计与自检
    python _tools/build_dwca.py --write     # 重新生成 dwca/ 与 downloads/*-dwca.zip
    python _tools/build_dwca.py --check     # 校验是否最新（CI 用这个）

## English summary

This package is the citable, archived version of the "Extant Isoptera checklist: Latin scientific names with Chinese standard names" project. It covers all extant termite lineages — 13 families, 18 subfamilies, 326 genera, 3021 species and 68 subspecies (3089 taxon records) — and provides, for every record, the scientific name with authorship, the Chinese standard name, rank, full classification (clade, family, subfamily, genus; Latin and Chinese), type-species flag, type locality, distribution in Chinese and English, and synonyms with their type localities. A separate long table lists all synonyms, and 77 cited references are included with DOIs where available.

Files: one row per taxon (`isoptera-checklist.csv`), a full taxonomy tree (`isoptera-taxonomy.json`), a synonym table, family/subfamily counts, and the reference list. Formats are documented in `datapackage.json`; the DataCite 4.6 record is in `datacite-metadata.xml`. The same content is also provided as a Darwin Core Archive (`dwca/` and `downloads/*-dwca.zip`) with a Taxon core, a VernacularName extension for the Chinese names, and EML metadata, so it can be read by GBIF tools without conversion. Everything is regenerated deterministically from the project repository, so the deposit can be rebuilt and audited.

The dataset is a **compilation only and makes no nomenclatural act**. Chinese names are an editorial layer: they may differ from translations used by other authors and should be checked against the primary literature before formal use. No coordinates are included; distribution statements are textual and not individually verified.

Licensed under CC BY 4.0 — please cite the DOI of the version you used.

## 联系方式 Contact

作者：班奈特格林（bilibili）· 留言板：<https://termite-extant-isoptera.org/guestbook/> · 仓库 Issue：<https://github.com/bennetgreen-bilibili/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/issues>
