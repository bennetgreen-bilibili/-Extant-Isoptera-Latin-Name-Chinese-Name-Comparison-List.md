# GBIF checklist 发布逐步操作手册（第二 DOI：10.15468/…）

> 定位：与《Zenodo发布逐步操作手册.md》平行的第二本"照着做"操作单。讲路线取舍的是《数据集DOI与归档发布指南.md》，本文件只讲手怎么动。
>
> **当前状态（2026-10-26 核对）**
> - ✅ **DwC-A 发布包已生成并通过本地校验**：`downloads/isoptera-checklist-dwca-v2026.10.17.zip`（267,581 字节），源文件在同源目录 `dataset/dwc-a/`
> - ✅ `eml.xml` 已通过 **GBIF Metadata Profile 1.1 XSD** 校验；`meta.xml` 按 Darwin Core Text 规范映射 Taxon 核心 19 列 + VernacularName 扩展 3 列
> - ⬜ **发布资格尚未取得**：需要 IPT 账号 + 已背书（endorsed）的机构（第 2 节，唯一真正的门槛）
> - ⬜ GBIF DOI 待分配（发布并注册数据集时由 GBIF **自动**分配）
> - 预计耗时：申请账号/背书 **1–10 天（等回复）** + IPT 操作 **40 分钟** + 回填 **15 分钟**

## 记录区（发布后边做边填）

| 项目 | 值 |
|---|---|
| GBIF dataset 页 | 待填（形如 `https://www.gbif.org/dataset/<datasetKey>`） |
| **GBIF DOI（第二 DOI）** | 待填（形如 `10.15468/xxxxxxxx`） |
| datasetKey（GBIF UUID） | 待填 |
| 发布机构（publishing organization） | 待填 |
| IPT 资源网址 | 待填（形如 `https://<ipt 域名>/resource?r=extant-isoptera-checklist`） |
| 首次发布日期 | 待填 |
| DwC-A 包字节数 | 267,581（`isoptera-checklist-dwca-v2026.10.17.zip`） |

---

## 0. 先弄清"第二 DOI"到底是什么

| | **Zenodo DOI**（已有） | **GBIF DOI**（本手册的目标） |
|---|---|---|
| 前缀 | `10.5281/zenodo.…` | `10.15468/…` |
| 谁分配 | Zenodo（发布时） | **GBIF（数据集注册成功后自动分配）** |
| 层级 | **版本 DOI** 每版一个 + 概念 DOI 指向最新版 | **数据集级 DOI**，所有版本共用一个；每次"下载"另发 `10.15468/dl.…` 引用 |
| 解析到 | 归档 zip（快照，可复现） | GBIF 数据集页（活数据集，随版本更新） |
| 主要用途 | 论文/网页正式引用、长期归档 | 分类学与生物多样性社区检索入口、GBIF 物种页与文献追踪 |
| 拿它要做什么 | 上传 zip + 填元数据（已做） | **取得发布资格 → 交 DwC-A → 发布 → 注册**（DOI 自动来） |

**关键认知（省掉一次白跑）**：GBIF DOI 不是"申请"来的，是数据集在 GBIF 注册成功后由 GBIF 自动分配的。IPT 手册 *DOI Workflows* 原文：*"By default, GBIF assigns a DOI to all registered datasets. These DOIs begin 10.15468."* 所以这件任务真正的工作量只有两件：**拿到发布资格**（第 2 节）和**交一份合格的 DwC-A**（第 1 节，已完成）。

> 例外：如果你在 IPT 元数据的 "Citation identifier" 里填了现成的 Zenodo DOI，GBIF 会把那个 DOI 当作数据集的引用 DOI（相当于"沿用外部 DOI"，例如 VASCAN 用的是 `10.5886/…`），此时页面上不一定再突出 10.15468 DOI。**想要 10.15468 这个第二 DOI，第一次发布时把 Citation identifier 留空。**

---

## 1. 已就绪的发布包（不用重做）

### 1.1 产物

| 文件 | 内容 | 规模 |
|---|---|---|
| `downloads/isoptera-checklist-dwca-v2026.10.17.zip` | **上传 IPT 用**的 Darwin Core Archive（压平 zip） | 267,581 字节 |
| `dataset/dwc-a/taxon.txt` | Taxon 核心表：接受名 3071 + 次异名 696 | 3,767 行 × 19 列 |
| `dataset/dwc-a/vernacularname.txt` | VernacularName 扩展：中文正名（`language=zho`） | 3,071 行 × 3 列 |
| `dataset/dwc-a/meta.xml` | Darwin Core Text 描述文件（核心 + 扩展映射） | 2.1 KB |
| `dataset/dwc-a/eml.xml` | EML 2.1.1 元数据（GBIF Metadata Profile 1.1） | 3.9 KB |

包内 `taxon.txt` 的列：`taxonID / scientificName / scientificNameAuthorship / taxonRank / taxonomicStatus / acceptedNameUsageID / parentNameUsageID / nameAccordingTo / nameAccordingToID / nomenclaturalCode / kingdom / phylum / class / order / family / genus / specificEpithet / infraspecificEpithet / taxonRemarks`。

设计要点（改数据时会用到）：

- `taxonID` = 站点物种页 URL（稳定、可解析）；异名记录 = 同一 URL + `#synonym-n`，用 `acceptedNameUsageID` 指回接受名；
- 亚种的 `parentNameUsageID` 指向母种**同一数据集内**的记录（GBIF 要求引用必须存在）；
- 分类采用 GBIF 支持的 **denormalized** 方式（kingdom/phylum/class/order/family/genus 每行写全）；亚科/支系不是 Darwin Core Taxon 核心术语，写进 `taxonRemarks` 保留；
- 中文名走 **VernacularName 扩展**（GBIF 推荐做法），不塞进 `scientificName`；
- 异名 `taxonRank` 由名称本身推断（双名 = species，三名 = subspecies）。

### 1.2 本地复核（2 分钟）

```powershell
cd C:\Users\32304\Documents\GitHub\-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md
$env:PYTHONIOENCODING='utf-8'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false)

# 1) 生成/校验全部产物（DwC-A 与 Zenodo 包一次生成）
python .github/workflows/build_dataset.py --check

# 2) 看 DwC-A 里有什么
python -c "import zipfile; [print(i.filename, i.file_size) for i in zipfile.ZipFile(r'downloads/isoptera-checklist-dwca-v2026.10.17.zip').infolist()]"
```

`--check` 成功的标志（最后两行）：

```text
DwC-A：taxon 3767 行（接受名 3071，异名 696）；vernacularname 3071 行；包 downloads/isoptera-checklist-dwca-v2026.10.17.zip 267581 字节
ok: 全部 18 个产物与生成结果一致
```

### 1.3 改数据后怎么重新生成

```powershell
python .github/workflows/build_dataset.py --write   # 重写 dataset/、Downloads 两个包、CITATION.cff 等
python .github/workflows/build_dataset.py --check   # 确认产物与生成结果一致
```

数据来源是 `_species/*.md` + `data/index.json` + `dataset/metadata.json`；DwC-A 与 Zenodo 包**同源**，不要手工各改一份。

### 1.4 为什么 DwC-A 不放进 Zenodo 归档包

- Zenodo 包是"引用快照"（CSV/JSON/README/DataCite XML），已经发布；**再改内容会改变归档字节数**，就得再发一个 Zenodo 版本。
- DwC-A 是"GBIF 发布源"，GBIF 侧会随版本更新，且 IPT 发布时会用自己的 EML 重新打包；两者用途不同。
- 若以后希望 DwC-A 也进归档：在下一版 Zenodo 里一起打包，并在 `dataset/README.md` 的 AUTO 区块加一行（那会变字节数，属正常的新版本）。

---

## 2. 取得发布资格（唯一真正的门槛）

GBIF 的发布资格是**三层**，缺一不可：

1. **机构（organization）已在 GBIF 注册并被背书（endorsed）** —— 由 GBIF 节点经理（node manager）或 GBIF 秘书处审批；
2. 该机构被 IPT 管理员加进某个 **IPT** 的 Organization 列表；
3. 你有一个 **IPT 账号**（Manager 角色）。

对个人研究者，最省事的顺序是：**先问中国节点（中科院）→ 不行再问 GBIF 帮助台 → 再考虑 data hosting centre → 最后才是自建 IPT**。

### 2.1 路线 A：走 GBIF 中国节点（推荐先问）

节点信息（2026-10-26 取自 GBIF Registry API `/v1/node`，以官网当前记录为准）：

| 项目 | 值 |
|---|---|
| 节点 | Chinese Academy of Sciences（中国科学院，GBIF 中国节点） |
| 节点 key | `e760dc6f-dd68-474d-ab41-bd3588571793` |
| 节点经理 Node manager | Zheping Xu — `xuzp@mail.las.ac.cn` |
| 节点工作人员 Node staff | Maofang Luo — `maofang@ibcas.ac.cn` |
| 代表团团长 Head of delegation | Keping Ma — `kpma@ibcas.ac.cn` |
| 其他联系人 | Congtian Lin `linct@ioz.ac.cn`；Meiling Piao `piaoml@ibcas.ac.cn` |

> 注意：注册表里该节点的门户仍写着 `www.gbifchina.org`，但该域名现在打开是"域名出售"页面（2026-10-26 实测）。**别等门户，直接发邮件给节点经理/工作人员**。

邮件模板（中文，可直接改）：

```text
主题：咨询通过 GBIF 中国节点发布一份白蚁名录 checklist（申请 IPT 发布账号）

许老师、罗老师：

您好！我是独立研究者班奈特格林，编制了一份《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》：
- 项目网站：https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/
- 已归档版本（Zenodo）：10.5281/zenodo.23646836
- 规模：13 科 18 亚科 323 属 3008 种 63 亚种，共 3071 条记录，含次异名 696 条、中文正名 3071 条

希望以 checklist 形式发布到 GBIF，取得 GBIF 数据集 DOI（10.15468）。Darwin Core Archive 已准备好并通过本地校验
（taxon.txt 3767 行 + vernacularname.txt 3071 行 + meta.xml + eml.xml），可直接上传 IPT。

想请教三件事：
1. 是否可以通过中国节点的 IPT 发布？如可以，如何申请账号？
2. 我的机构背书（endorsement）应该走哪条流程——需要我填 https://www.gbif.org/become-a-publisher 吗？
3. 发布为 checklist 时，资源类型/子类型建议选哪个（GLOBAL_SPECIES_DATASET 是否合适）？

附件/链接：DwC-A 包可随时提供；元数据、字段说明、许可（CC BY 4.0）均已就绪。

顺颂
班奈特格林
<你的邮箱>
```

英文版要点（发给国际联系人时用）：*independent researcher; checklist of extant Isoptera (3071 taxa, 696 synonyms, Chinese vernacular names); DwC-A ready (Taxon core + VernacularName extension, EML valid against GBIF profile); asking for an IPT account / endorsement route; Zenodo DOI 10.5281/zenodo.23646836.*

### 2.2 路线 B：GBIF 秘书处 / 帮助台

- 邮箱：`helpdesk@gbif.org`
- IPT 手册明确写了：**没有 data hosting centre、也没有技术条件自建 IPT 的发布者，可以联系帮助台协助**；没隶属机构的发布者也可以直接问帮助台。
- 说明：GBIF 秘书处运营的 **hosted IPT** 官方口径是"仅对正式 GBIF Participant 开放"（见 <https://www.gbif.org/ipt> 的 Regional cloud-hosted IPTs 一段），所以个人申请时把自己的情况（无机构、有完整 DwC-A、愿用 CC BY 4.0）写清楚，让帮助台给方案（常见结果是转给节点或 data hosting centre）。
- 另有一个**公开测试 IPT** <https://ipt.gbif.org/>，可向帮助台申请账号练手（数据不用于正式发布）——**强烈建议正式发布前先在测试实例上走一遍**。

### 2.3 路线 C：Data hosting centre

- 目录：<https://www.gbif.org/data-hosting-centres>
- 一些博物馆/大学/节点愿意为外部发布者托管 IPT（有的收少量费用）。找与你研究方向接近（昆虫/分类学）的机构发邮件，模板同 2.1，把"发布内容 + 数据量 + 许可 + 已有 DwC-A"写清楚。

### 2.4 路线 D：自建 IPT（不推荐第一次就做）

- IPT 是开源软件（<https://github.com/gbif/ipt>），需要 Java + Tomcat + 域名 + HTTPS + 长期在线，安装文档见 <https://ipt.gbif.org/manual/en/ipt/latest/getting-started>。
- **自建也不能绕过背书**：注册数据集时仍要选一个已背书的机构。
- 适合"已经发布过、需要长期自动化"的场景；第一次发布走托管 IPT 更省事。

### 2.5 机构背书（endorsement）本身

- 入口：<https://www.gbif.org/become-a-publisher>（IPT 手册里叫 "online questionnaire"）
- 流程：填机构信息 + 拟发布的数据类型/范围 → 由对应国家的 GBIF 节点经理（中国即 2.1 的中科院节点）或 GBIF 秘书处审批 → 通过后机构出现在 GBIF Registry，才能被加进 IPT。
- 时间：官方说法"可能要几天"；实际取决于节点回复速度，**可以边等边在测试 IPT 上练手**。
- 无机构个人：不要自己在表单里虚构机构；直接按 2.1 / 2.2 发邮件说明情况，请对方给出"以什么机构身份发布"的方案（常见是挂在节点或合作机构名下，你作为资源管理者/联系人）。

**本节完成标志**：你拿到 ① IPT 网址 + 账号（Manager）② 该 IPT 的 Organization 列表里有你将要选择的已背书机构。

---

## 3. 在 IPT 里发布（有账号后约 40 分钟）

> 以下按 IPT 3.x 界面写；不同版本菜单名可能略有差异。第一次强烈建议先在 <https://ipt.gbif.org/> 测试实例上完整走一遍。

### 3.1 建资源

1. 登录 IPT → **Manage Resources** → 页面下方 **Create a New Resource**。
2. **Shortname** 填 `extant-isoptera-checklist`（会进 URL，三字符以上、只用字母数字和 `-`/`_`）。
3. Resource type 选 **Checklist**（上传 DwC-A 后会自动识别并覆盖，选错也不怕）。
4. **Choose File** → 选 `downloads/isoptera-checklist-dwca-v2026.10.17.zip` → **Create**。
5. 导入成功的标志：页面顶部出现导入结果提示，**Manage Resources** 里能看到资源，Records 数约为 3,767（核心记录数）。

### 3.2 检查映射（Source Data / Mapping）

- Core：`taxon.txt` → **Taxon**，应自动映射 19 个字段（`taxonID` 作为 ID）；
- Extension：`vernacularname.txt` → **Vernacular Name**，3 个字段（`taxonID` 作 coreid，`vernacularName`、`dc:language`）；
- 若某个字段没自动认出来（常见于 `taxonRemarks` 或 `language`），在 Mapping 页面手动选术语即可，**不要改源文件**。

### 3.3 元数据（Metadata，照抄 `dataset/metadata.json`）

| IPT 字段 | 填什么 |
|---|---|
| Title | `Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names`（可加版本号） |
| Type / Subtype | Checklist / **Global species dataset**（全球性名录；若只覆盖某区域则选 regional） |
| Description | `metadata.json` 的 `description.en`（英文摘要）；可另加一段中文摘要（Abstract 支持多段/多语言） |
| Language | Chinese (zho)；可再加 English |
| Creators | 班奈特格林（Bennet Green）；有 ORCID 就填 |
| Contacts | 加一个 **Point of contact**（填你能公开的邮箱）+ 一个 **Administrative point of contact**；Metadata author 可同 creator |
| Publication date | `2026-10-17`（与版本一致） |
| License | **CC BY 4.0** |
| Keywords | `termites; Isoptera; Blattodea; checklist; taxonomy; Chinese names; scientific names; synonyms; biodiversity informatics` |
| Citation identifier | **留空**（见第 0 节的例外说明：填了就不产生 10.15468 DOI） |
| Citation | 让 IPT 自动生成（会带版本号与 DOI） |
| Geographic coverage | Global |
| Taxonomic coverage | Isoptera / Blattodea；13 科 18 亚科 323 属 3008 种 63 亚种 |
| Additional information | 写一句：Versioned snapshot archived at Zenodo, doi:10.5281/zenodo.23646836；项目网站 URL |

### 3.4 组织与可见性

- **Organization**：选第 2 节拿到的那家已背书机构（下拉里没有 → 说明 IPT 管理员还没加，回第 2 节）。
- **Visibility / Publishing**：设为 **Public**；如 IPT 有 "auto-publish" 选项，可开（数据更新后自动重新发布）。

### 3.5 发布 + 注册

1. 点 **Publish**（发布到 IPT 的公有 URL）。
2. 点 **Register with GBIF**（或 IPT 自动注册，视版本）——这一步才会在 GBIF Registry 建条目。
3. 等索引：GBIF 抓取 + 解析通常 **几分钟到几小时**。dataset 页出现时，页面上就会显示 **DOI（10.15468/…）** 与自动生成的 Citation。

**成功标志**：`https://www.gbif.org/dataset/<datasetKey>` 能打开，DOI 一栏是 `10.15468/…`，Records 约 3,767，Taxa 约 3,000+。

---

## 4. 拿到 DOI 后的回填（15 分钟）

### 4.1 先把记录区填了

把 datasetKey、GBIF DOI、IPT 资源 URL、发布日期填进本文件顶部的"记录区"。

### 4.2 站内回填

`_config.yml` 的 `dataset:` 块里已预留注释行，**取消注释并填值**：

```yaml
  gbif_doi: "10.15468/xxxxxxxx"                                  # GBIF 数据集 DOI（第二 DOI）
  gbif_dataset: "https://www.gbif.org/dataset/<datasetKey>"      # GBIF 数据集页
```

`data.md` 已有对应条件块：填了才会显示，不填不影响页面。改完 push，等 GitHub Pages 重建（1–3 分钟），打开 `/data/` 确认出现 "GBIF checklist（第二 DOI）" 一行。

### 4.3 Zenodo 记录补关联

打开 <https://zenodo.org/records/23646836> → **Edit** → Related works 加一条：

| 字段 | 值 |
|---|---|
| Identifier | `10.15468/xxxxxxxx` |
| Scheme | DOI |
| Relation | **Is identical to**（同一数据集在 GBIF 的发布载体；想保守可选 *Is supplemented by*） |
| Resource type | Dataset |

同时建议在 Zenodo 的 Description 末尾补一句：`Also published as a GBIF checklist dataset: https://doi.org/10.15468/xxxxxxxx`（元数据可改，不影响已发布文件）。

### 4.4 反向补一条（推荐但非必须）

回到 IPT 的元数据 → Additional information 里写上 Zenodo DOI（如 3.3 已写则不用改）；这样 GBIF 数据集页也会出现归档快照的入口。

### 4.5 两个 DOI 的引用写法

- 论文里追求**可复现**：引 Zenodo **版本 DOI**（`10.5281/zenodo.23646836`）+ 版本号；
- 需要"永远指向最新版/活数据集"或强调分类学数据库入口：引 GBIF DOI（`10.15468/…`）；
- 两者都给最稳：*"…(Zenodo: 10.5281/zenodo.23646836; GBIF: 10.15468/xxxxxxxx)"*。

---

## 5. 发布后 72 小时验收（逐项打勾）

```powershell
$k = "<datasetKey>"    # 换成第 4 节记录的 UUID
Invoke-RestMethod "https://api.gbif.org/v1/dataset/$k" | Select-Object key, doi, title, version, publicationDate
Invoke-RestMethod "https://api.gbif.org/v1/species/search?datasetKey=$k&q=Mastotermes&limit=3" | Select-Object -ExpandProperty results | Select-Object scientificName, taxonRank, vernacularName
```

| 检查项 | 怎么查 | 通过标准 |
|---|---|---|
| 数据集已注册 | `api.gbif.org/v1/dataset/<key>` | 返回 JSON，`doi` 以 `10.15468/` 开头 |
| DOI 可解析 | 浏览器打开 `https://doi.org/<doi>` | 跳到 GBIF 数据集页 |
| DataCite 已登记 | `https://api.datacite.org/dois/<doi>` | 200，creators/publisher 正确 |
| 记录数与分类单元 | dataset 页 Statistics | Records ≈ 3,767；Taxa ≈ 3,000+ |
| 中文名可检索 | GBIF 搜索框搜"白蚁"或物种页 | 物种页出现 vernacular name（中文正名） |
| 名字匹配问题 | dataset 页 **Issues / Metrics** | 关注 `TAXON_MATCH_*` 一类 issue；科名全大写若被大量标记，见第 7 节第 4 条 |
| 站点已显示 | `/data/` 页面 | 出现 GBIF DOI 行 |
| Zenodo 已关联 | Zenodo 记录页 Related works | 有 GBIF DOI 条目 |

---

## 6. 以后的版本更新

1. 更新数据 → `python .github/workflows/build_dataset.py --write`（会同时更新 DwC-A 与 Zenodo 包）；
2. 改版本号：`dataset/metadata.json` 的 `version`/`dates`；`_config.yml` 的 `dataset.version` 与 `archive_file`；
3. Zenodo：上一版 record → **New version** → 上传新 zip（版本 DOI 变、概念 DOI 不变）；
4. GBIF：IPT 里 **Source Data** 上传新 DwC-A → **Publish** 新版本（major/minor 由 IPT 版本策略决定）；
5. **GBIF DOI 不变**（数据集级），下载时另发的 `10.15468/dl.…` 才是"某次下载"的引用 DOI；
6. 站内回填 Zenodo 新版本 DOI（GBIF DOI 不用动）。

---

## 7. 常见坑（都是会实际卡住的）

1. **以为 GBIF DOI 要单独申请**：不，注册数据集时自动分配；申请不到 DOI 的根因永远是"没注册成功"。
2. **在 IPT 的 Citation identifier 里填了 Zenodo DOI**：GBIF 会把它当作数据集 DOI，页面上就不再突出 10.15468。想两个都要 → 留空。
3. **把 Zenodo 归档 zip 传进 IPT**：那不是 DwC-A（没有 `meta.xml`），IPT 不会识别。要传 `downloads/isoptera-checklist-dwca-v2026.10.17.zip`。
4. **科名全大写（MASTOTERMITIDAE）**：GBIF 名称解析大小写不敏感，通常能匹配；若 Issues 里大量 `TAXON_MATCH_HIGHERRANK`/`TAXON_MATCH_NONE`，把 `build_dataset.py` 里输出 family 的地方改成首字母大写（`MASTOTERMITIDAE` → `Mastotermitidae`）重新生成——但这样与站点/CSV 的显示就不完全一致，改前先看 Issues 数量是否真的值得。
5. **Organization 下拉里没有你的机构**：不是你的错，是 IPT 管理员没加；回第 2 节。
6. **发布后马上改数据**：已注册的数据集要等 GBIF 重新抓取（几小时）；要立刻生效就走新版本，别反复 Publish。
7. **把"分布"当坐标发**：本数据集只有文字分布，DwC-A 里放在 `taxonRemarks`，**不要**为了"看起来更完整"编造经纬度或 occurrence。
8. **中文名塞进 scientificName**：绝对不行（会污染名称解析）；已在 VernacularName 扩展里。
9. **eml.xml 与 IPT 元数据不一致**：以 IPT 为准。包里的 `eml.xml` 是给非 IPT 渠道和人工核对用的模板（已通过 GBIF Profile 1.1 XSD 校验），IPT 发布会用编辑器内容重新生成。
10. **taxonID 被改**：`taxonID` 用的是站点物种页 URL，是 GBIF 里所有引用（异名指向、扩展关联）的锚点。**改站点 URL 规则 = 换 ID = 制造重复分类单元**；确需改时整套重新生成并作为新版本发布。
11. **无机构硬闯**：不要虚构 affiliation；按 2.1/2.2 找节点或帮助台，他们会给可行方案。
12. **只在 IPT 点了 Publish 没点 Register**：数据集只在那个 IPT 上可见，GBIF 上没有条目、自然没有 DOI。发布后一定确认 **Registered** 状态。

---

## 8. 速查链接与命令

**GBIF 相关**

| 用途 | 链接 |
|---|---|
| 成为发布者（机构注册/背书） | <https://www.gbif.org/become-a-publisher> |
| Data hosting centres | <https://www.gbif.org/data-hosting-centres> |
| 各国节点目录 | <https://www.gbif.org/nodes> |
| IPT 介绍 | <https://www.gbif.org/ipt> |
| 公开测试 IPT | <https://ipt.gbif.org/>（账号找 helpdesk@gbif.org） |
| IPT 手册 | <https://ipt.gbif.org/manual/en/ipt/latest/> |
| Checklist 发布指引 | <https://ipt.gbif.org/manual/en/ipt/latest/checklist-data> |
| Checklist 最佳实践 | <https://ipt.gbif.org/manual/en/ipt/latest/best-practices-checklists> |
| DOI 工作流 | <https://ipt.gbif.org/manual/en/ipt/latest/doi-workflow> |
| 数据集引用格式 | <https://ipt.gbif.org/manual/en/ipt/latest/citation> |
| EML ↔ DataCite 映射 | <https://ipt.gbif.org/manual/en/ipt/latest/datacite-mappings> |
| 帮助台 | <mailto:helpdesk@gbif.org> |

**本仓库命令**

```powershell
$env:PYTHONIOENCODING='utf-8'

python .github/workflows/build_dataset.py            # 统计与自检（不写文件）
python .github/workflows/build_dataset.py --write    # 重写全部产物（含 DwC-A 与两个 zip）
python .github/workflows/build_dataset.py --check    # 校验产物与生成结果一致
python .github/workflows/build_dataset.py --strict   # 计数与 metadata.json 不符即失败

# DwC-A 内容
python -c "import zipfile; [print(i.filename, i.file_size) for i in zipfile.ZipFile(r'downloads/isoptera-checklist-dwca-v2026.10.17.zip').infolist()]"

# 取 GBIF 数据集 JSON（发布后）
Invoke-RestMethod "https://api.gbif.org/v1/dataset/<datasetKey>" | ConvertTo-Json -Depth 3
```

---

## 9. 验收清单（发布完成后整体过一遍）

- [ ] IPT 里资源类型 = Checklist，Records ≈ 3,767，扩展 = Vernacular Name
- [ ] 元数据：License = CC BY 4.0、Language 含 zho、Citation identifier 留空、Organization = 已背书机构
- [ ] 已 Publish 且状态为 **Registered**
- [ ] GBIF dataset 页可打开，DOI = `10.15468/…`，`https://doi.org/<doi>` 可解析
- [ ] `api.gbif.org/v1/dataset/<key>` 的 `doi` 字段正确
- [ ] 中文正名能在 GBIF 物种页显示（抽 3 个物种检查）
- [ ] `_config.yml` 已回填 `gbif_doi` / `gbif_dataset`，`/data/` 页面显示 GBIF DOI
- [ ] Zenodo 记录 Related works 已加 GBIF DOI，Description 已补一句
- [ ] 本文件"记录区"填完
