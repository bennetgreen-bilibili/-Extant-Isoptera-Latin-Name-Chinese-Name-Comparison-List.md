# Zenodo 发布逐步操作手册（数据集 DOI）

> 这是"照着做"的操作单：每一步都有可勾选框、可直接复制的值和"怎么判断成功"。
> 讲"为什么这样做、有哪几条路"的是同目录的《数据集DOI与归档发布指南.md》；本文件只讲"手怎么动"。
>
> **当前状态（2026.10.17 版核对）**
> - 数据集包已生成并提交：commit `2f510e0 数据包`，工作区干净、已推送 `origin/main`
> - 归档包：`downloads/isoptera-checklist-v2026.10.17.zip`，**485,517 字节**，内含 13 个文件
> - Zenodo 侧：**尚未操作**（`dataset/metadata.json` 的 `doi.version` 为空，DataCite XML 用的是占位 DOI `10.5281/zenodo.XXXXXXX`）
> - 预计耗时：账号 5 分钟 + 填表 15 分钟 + 回填 10 分钟（第一次做）；以后发新版 20 分钟

## 记录区（边做边填，填完这一版就齐了）

| 项目 | 值 |
|---|---|
| Zenodo record 网址 | https://zenodo.org/records/ |
| **版本 DOI**（version DOI） | 10.5281/zenodo. |
| **概念 DOI**（concept DOI，全部版本） | 10.5281/zenodo. |
| 实际发布日期 | |
| 发布时归档包字节数 | 485,517 |

---

## 0. 开工前自检（2 分钟）

在仓库根目录打开 PowerShell：

```powershell
cd C:\Users\32304\Documents\GitHub\-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md
[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false); $env:PYTHONIOENCODING='utf-8'
python .github/workflows/build_dataset.py --check
```

**成功的标志**是最后四行：

```text
记录 3071 条（种 3008，亚种 63）；属 323；科 13；亚科 18；支系 6
次异名 696 条；参考文献 77 条（含 DOI 46 条）
数据文件合计 3654245 字节；归档包 downloads/isoptera-checklist-v2026.10.17.zip 485517 字节；产物 13 个
ok: 全部 13 个产物与生成结果一致
```

如果报 `error: 以下产物已过期`，先运行 `--write` 再继续——**不要拿过期的 zip 去上传**。

---

## 1. 账号与 ORCID（5 分钟）

- [ ] 打开 <https://zenodo.org>，右上角 **Sign up**（或直接用 GitHub 账号登录，最省事）
- [ ] 注册 <https://orcid.org>（免费，3 分钟），记下你的 ORCID iD（形如 0000-0002-1825-0097）
- [ ] 回 Zenodo：头像 → **Settings → Linked accounts → Connect ORCID**（入口名可能略有差异，在账号设置里找 ORCID 授权即可）

**为什么要 ORCID**：Zenodo 会把这条 record 自动推进你的 ORCID 作品列表，别人在 ORCID 搜到你就能看到这个数据集；这也是 DataCite 元数据里 `nameIdentifier` 的来源。

**可选但推荐**：先去沙盒 <https://sandbox.zenodo.org> 用另一个邮箱完整练一遍（sandbox 分配的 DOI 不是真的，只是流程演练）。流程不熟时这样最不心疼。

---

## 2. 第 1 遍上传（先不发布）

- [ ] 右上角 **＋** → **New upload**
- [ ] **Upload files** → 选 `downloads/isoptera-checklist-v2026.10.17.zip`（485,517 字节）
- [ ] 等进度条走完（485 KB，很快）

**只传这一个文件就够了。** 它是"一键下载"的完整包，里面是：

```text
isoptera-checklist-2026.10.17/
  README.md            10,023 B   归档说明（来源/方法/字段/限制/引用）
  LICENSE               1,913 B   CC BY 4.0
  CITATION.cff          1,726 B   机器可读引用
  CHANGELOG.md          1,174 B
  CHECKSUMS.sha256        717 B
  datapackage.json     10,890 B   字段字典（Frictionless 格式）
  datacite-metadata.xml 6,183 B   DataCite 4.6 元数据
  data/isoptera-checklist.csv     1,752,731 B  3071 行 × 22 列
  data/isoptera-taxonomy.json     1,715,138 B  完整分类树
  data/isoptera-synonyms.csv        169,975 B  次异名长表
  data/isoptera-references.csv       14,186 B  77 条文献
  data/isoptera-counts.csv            2,215 B  科/亚科/属/种计数
```

**不要**上传：整个仓库、`_tmp/`、任何临时文件。数据集 DOI 只对"数据"负责；站点是它的文档，在 Related works 里指向站点就够了。

---

## 3. 填元数据（15 分钟，照抄即可）

Zenodo 表单分 **Basic information**（带红星必填）与 **Recommended information** 两块。按下面顺序填：

### 3.1 Resource type

搜 `dataset` → 选 **Dataset**。

### 3.2 Title（主标题用英文，中文放"翻译标题"）

主标题：

```text
Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names (version 2026.10.17)
```

- [ ] 点 **Add titles** → Title type 选 **Translated title** → Language 选 **Chinese** → 填：

```text
现存等翅下目（白蚁）拉丁学名—中文正名对照名录（2026.10.17 正式版）
```

**为什么**：Zenodo 的检索与引用串都以主标题为准，英文标题能进 DataCite/OpenAIRE 的英文检索；中文标题作为翻译标题保留，中文用户搜得到。

### 3.3 Publication date

填 `2026-10-17`（与版本号 2026.10.17 同日，保持全站一致）。

若你今天才发布、想反映真实发布日，也可填当天——但注意**这个日期会成为引用年份**（APA 里显示的年），一旦发布只能改元数据、影响已发出的引用。

### 3.4 Creators

- [ ] 点 **Add creator** → 输入 `Bennet Green` 或你的 ORCID → 选中你自己
- [ ] Affiliation 填：`Independent researcher`

**说明**：绑了 ORCID 后 Zenodo 会带出 ORCID 上的英文姓名，引用串就是英文名（`Green, B.` 之类）——这对英文检索是好事，别纠结中文笔名。中文署名"班奈特格林"在 Description 与站点里都有，读者不会搞错。

### 3.5 Description（整段复制，含 HTML）

Zenodo 描述支持 HTML，下面的 `<p>` 会正常渲染。把下面代码块**整段**粘进去：

```html
<p>A checklist of all extant lineages of Isoptera (termites): Latin scientific names paired with Chinese standard names. It covers 13 families, 18 subfamilies, 323 genera, 3008 species and 63 subspecies (3071 taxon records). Each record gives the scientific name, authorship, Chinese name, rank (species/subspecies), full classification (clade-family-subfamily-genus, in Latin and Chinese), type-species flag, type locality, distribution (Chinese and English), and synonyms with their type localities. The data are provided as a structured JSON taxonomy tree, a flat one-row-per-taxon CSV, a long-format synonym table, and a reference list of 77 cited works (DOIs where available). The dataset is a taxonomic compilation for look-up, cross-checking, translation and biodiversity informatics. It makes no nomenclatural act; new taxa and nomenclatural changes must be cited from the original publications.</p>
<p>现存等翅下目（Isoptera，白蚁）全部现生类群的拉丁学名—中文正名对照名录。收录 13 科、18 亚科、323 属、3008 种、63 亚种，共 3071 条分类单元记录。每条记录含：拉丁学名、命名人与年份、中文正名、分类等级（种/亚种）、所属支系—科—亚科—属（中拉双名）、模式种标记、模式产地、分布（中/英）、次异名及其模式产地。数据同时以结构化 JSON 分类树、逐条 CSV 与次异名长表三种形式提供，并附 77 篇参考文献清单（有 DOI 者随条目给出）。本数据集为分类学名录汇编，供检索、对照、翻译与生物多样性信息学使用；不构成任何命名行为（no nomenclatural act），新分类单元与命名修订请以正式发表文献为准。</p>
<p><strong>项目网站 / Project website:</strong> <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/">https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/</a></p>
<p><strong>源码仓库 / Source repository:</strong> <a href="https://github.com/bennetgreen-bilibili/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md">https://github.com/bennetgreen-bilibili/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md</a></p>
```

**为什么这么写**：第一段是数据集内容与字段清单（检索命中靠它），第二段是中文（中文库检索与中文读者），第三、四段把站点与仓库挂上（形成"数据集 ↔ 站点"双向关联）。

### 3.6 License

- [ ] 选 **Creative Commons Attribution 4.0 International**（`CC BY 4.0`）

必填。与你仓库里 `dataset/LICENSE`、`_config.yml` 的 `license_name` 一致；不一致会被 DataCite 收录成另一种许可，别人引用时会困惑。

### 3.7 Keywords（逐个回车，不要一行逗号粘贴）

英文：

- termites
- Isoptera
- Blattodea
- checklist
- taxonomy
- species list
- Chinese names
- scientific names
- synonyms
- biodiversity informatics

中文：

- 白蚁
- 等翅目
- 等翅下目
- 拉丁学名
- 中文正名
- 物种名录
- 分类学
- 生物多样性
- 次异名
- 模式种

### 3.8 Version / Language

- [ ] **Version**：`2026.10.17`
- [ ] **Language**：Chinese（有 Chinese (Simplified) 就选它）

### 3.9 Related works（两个链接，很关键）

- [ ] **Add related work** → Relation 选语义最近的（"is documented by" / "is supplemented by"；若下拉里没有就选 "is referenced by"），Identifier 填：

```text
https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/
```

- [ ] 再加一条，Identifier 填：

```text
https://github.com/bennetgreen-bilibili/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md
```

**为什么重要**：这是"站点 ↔ 数据集"的机器可读双向链接。聚合器和搜索引擎据此知道"这个 DOI 对应的内容在这个网站上"，你站内 `<link rel="cite-as">` 是反方向。漏了不影响发布，但会损失一部分可发现性。

### 3.10 不用填的字段

Contributors、Funding、Publisher（自动 Zenodo）、Notes（除非你想加"不是命名行为"的补充说明，已经在 Description 里了）。

### 3.11 保存

- [ ] 点 **Save draft**

存草稿后可以关掉页面，之后在 **My uploads** 里找回来继续。⚠️ **不要点 Delete 删草稿**——删了预留的 DOI 就没了（见第 4 步）。

---

## 4. 预留 DOI（关键，顺序别搞反）

- [ ] 在 **Basic information** 顶部找到 DOI 那一栏，问题大概是 *"Do you already have a DOI for this upload?"*
- [ ] 选 **No / I don't have a DOI**
- [ ] 点 **Get a DOI now!** → 立即出现一个 `10.5281/zenodo.XXXXXXXX`

**这是"预留"，不是"注册"**：此刻 doi.org 还解析不了，这是正常的，不要以为失败。它只在你点 Publish 后才真正生效。

- [ ] 把预留 DOI 抄进本文件顶部的"记录区"

⚠️ 三个必须记住的点：
1. **删草稿 = 预留 DOI 作废**，要重新预留一个新号；
2. 预留 DOI 一旦写进文件、而你后来又换了新号，文件里的 DOI 就是错的——所以第 5 步要在**预留之后**做；
3. 概念 DOI（全部版本的那个号）要**发布之后**才出现在右侧 **Versions** 面板，现在只有版本 DOI。

---

## 5. 把 DOI 写回仓库、重新打包、重传文件（最容易漏的一步）

**为什么必须做**：归档包里 `README.md`、`CITATION.cff`、`datacite-metadata.xml` 三处都要写 DOI。现在包里是占位符 `10.5281/zenodo.XXXXXXX`。别人下载压缩包、离线打开 README 时看到的应该是真 DOI —— 这正是"先预留 DOI 再上传文件"这个顺序存在的意义。写完要重新生成 zip，所以**必须重传一次文件**。

### 5.1 改元数据

编辑 `dataset/metadata.json`，把

```json
  "version": "",
```

改成（版本 DOI；`concept` 先留空）：

```json
  "version": "10.5281/zenodo.XXXXXXXX",
```

### 5.2 重新生成全部产物

```powershell
python .github/workflows/build_dataset.py --write
```

### 5.3 确认 DOI 真的进了文件（三处）

```powershell
Select-String -Path dataset/datacite-metadata.xml -Pattern "10.5281"
Select-String -Path dataset/CITATION.cff -Pattern "^doi:"
Select-String -Path dataset/README.md -Pattern "10.5281"
```

期望：
- `datacite-metadata.xml` 第 3 行变成 `<identifier identifierType="DOI">10.5281/zenodo.XXXXXXXX</identifier>`
- `CITATION.cff` 多出一行 `doi: "10.5281/zenodo.XXXXXXXX"`（根目录 `CITATION.cff` 同步）
- `dataset/README.md` 的 DOI 区块从"待铸造"变成 DOI 链接 + APA 引用 + BibTeX

### 5.4 再校验一次

```powershell
python .github/workflows/build_dataset.py --check
Get-Item downloads/isoptera-checklist-v2026.10.17.zip | Select-Object Length,LastWriteTime
```

`--check` 必须通过；zip 字节数会变（可能仍是 485,517，也可能差几十字节，取决于 DOI 长度），**以 `LastWriteTime` 是刚才为准**。

### 5.5 在 Zenodo 草稿里替换文件

- [ ] 文件区删掉旧 zip（垃圾桶图标）
- [ ] **Upload files** → 传新生成的同一个 zip
- [ ] 确认字节数与 `Get-Item` 报的一致

### 5.6 这一步的 git 改动先别急着提交

留着和第 7 步一起提交（一次 commit 说清"数据集 DOI 回填"）。想现在提交也没问题。

---

## 6. 发布（Publish）

- [ ] 点 **Preview** 看一眼：标题、作者、描述渲染是否正常，DOI 是否已显示
- [ ] 确认 Visibility = **Public**（文件公开，元数据本来就公开）
- [ ] 点 **Publish** → 弹窗确认

### 发布后立刻做三件事

1. **记下两个 DOI**
   - 版本 DOI：页面 DOI 徽章上的号 = 你预留的那个
   - 概念 DOI：右侧 **Versions** 面板 → *"Cite all versions?"* 那段里的号。它代表"全部版本"，永远指向最新版
2. **验证解析**
   - 浏览器打开 `https://doi.org/10.5281/zenodo.XXXXXXXX` → 应跳回 record 页
   - 跑一句 API（返回 JSON 就说明 DataCite 已收到元数据）：
     ```powershell
     Invoke-RestMethod "https://api.datacite.org/dois/10.5281/zenodo.XXXXXXXX" | ConvertTo-Json -Depth 4 | Select-String "relatedIdentifiers|license|titles|types"
     ```
   - 打开 <https://commons.datacite.org> 用 DOI 搜，能看到 record 即被收录
3. **补记录区**：把版本 DOI、概念 DOI、发布日期、字节数填进本文件顶部的表

---

## 7. 回填站点、提交推送、验收

### 7.1 两处配置

[_config.yml](../_config.yml) 的 `dataset:` 块：

```yaml
dataset:
  doi: "10.5281/zenodo.XXXXXXXX"        # 版本 DOI
  concept_doi: "10.5281/zenodo.YYYYYYY"  # 概念 DOI
```

`dataset/metadata.json` 的 `concept`（顺手补齐，DataCite XML 会生成 `IsVersionOf` 关系）：

```json
  "concept": "10.5281/zenodo.YYYYYYY",
```

### 7.2 重新生成并校验

```powershell
python .github/workflows/build_dataset.py --write
python .github/workflows/build_dataset.py --check
```

### 7.3 手工补 llms.txt（脚本不改它）

[llms.txt](../llms.txt) 的「归档数据集（带 DOI）」一节第 3 条现在写的是"版本 DOI、概念 DOI 与 APA 引用格式见上述数据页"。改成把号直接写出来，AI 摘要引擎才好抓：

```text
- 版本 DOI：10.5281/zenodo.XXXXXXXX（该版本）；概念 DOI：10.5281/zenodo.YYYYYYY（全部版本）
```

### 7.4 提交推送

```powershell
git add -A
git commit -m "数据集 DOI 回填：Zenodo 10.5281/zenodo.XXXXXXXX"
git push
```

推送后 GitHub Pages 会自动重建（`.github/workflows/pages.yml` 里已有 `build_dataset.py --write` 步骤，产物与提交内容一致，不会打架）。

### 7.5 部署后验收（5 项，缺一不可）

推送后 Pages 要重建，等 1–3 分钟再跑。下面的脚本逐项打印 True/False：

```powershell
$u    = "https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/"
$data = (Invoke-WebRequest "${u}data/" -UseBasicParsing).Content
$home = (Invoke-WebRequest "$u" -UseBasicParsing).Content
$sp   = (Invoke-WebRequest "${u}species/acangaobitermes-krishnai/" -UseBasicParsing).Content
"data 页有 DOI        : " + ($data -match '10\.5281/zenodo')
"data 页有 cite-as    : " + ($data -match 'rel="cite-as"')
"data 页有 APA 引用   : " + ($data -match 'doi\.org/10\.5281')
"首页 JSON-LD 有 DOI  : " + ($home -match '"identifier"')
"物种页页脚有 DOI     : " + ($sp -match '10\.5281/zenodo')
```

- [ ] `/data/` 页出现"归档数据集与 DOI"区块，里面有 DOI 链接与 APA 引用
- [ ] 任意物种页页脚出现 DOI 链接（全站 3086 页共用 `_layouts/default.html`）
- [ ] 首页源码里有 JSON-LD `"identifier"` 且含 DOI
- [ ] `/data/` 的 `<head>` 里有 `<link rel="cite-as" href="https://doi.org/10.5281/zenodo.XXXXXXXX">`
- [ ] 归档包链接能下载，且下载后 `README.md` 里是真 DOI

> 物种页路径规则是 `/species/<文件名>/`（`_config.yml` 里 `permalink: /species/:name/`），例如上面的 `/species/acangaobitermes-krishnai/`；随便换一个物种页看页脚也一样，不必逐个试。

---

## 8. 发布之后：真正带来曝光的 6 件事

DOI 只是准入证。以下按"性价比"排序：

1. **ORCID 自动同步**（0 成本）：Zenodo 元数据更新后通常 24 小时内出现在你的 ORCID Works；没出现就在 ORCID 里 *Add works → Search & link → Zenodo* 手动链。
2. **Google Dataset Search**（0 成本，被动）：无需提交，靠抓取。前提是 record 公开 + `/data/` 页有 schema.org `Dataset` 结构化数据（已有）。收录通常要几周到几个月，去 <https://datasetsearch.research.google.com> 搜 `Isoptera checklist` / `termites` 观察是否出现。
3. **把 DOI 放出去**：B 站视频简介、GitHub 仓库 About 里的 Website、你写的中文文章/图鉴、相关微信群与论坛。**没有链接的 DOI 等于没有。**
4. **让别人能一行引用**：record 页 *Cite as* 里有 APA / BibTeX / DataCite JSON，直接复制；站点页脚与 /data/ 页已指向 DOI，形成闭环。
5. **GBIF checklist（第二 DOI，10.15468）**：分类学与生物多样性社区真正的入口，GBIF 的文献追踪会把引用该 DOI 的论文自动挂回数据集页。工作量大（要 DwC-A + IPT 或走 GBIF 节点），**建议 Zenodo 这套跑顺之后再单独做一轮**，不要一次摊两摊。
6. **发新版而不是发新 record**：每年更新名录时在 record 页点 **New version**，概念 DOI 不变，引用与引用计数都累积在同一条目上。这条对长期曝光比任何单次推广都重要。

---

## 9. 命令速查

```powershell
$env:PYTHONIOENCODING='utf-8'

# 只统计与自检（不写文件）
python .github/workflows/build_dataset.py

# 生成/覆盖全部产物
python .github/workflows/build_dataset.py --write

# 校验仓库内产物是否与生成结果一致（CI 用这个）
python .github/workflows/build_dataset.py --check

# 计数与 metadata.json 的 expectedCounts 不符就失败
python .github/workflows/build_dataset.py --strict

# 看归档包里有什么
python -c "import zipfile;[print(i.filename, i.file_size) for i in zipfile.ZipFile(r'downloads/isoptera-checklist-v2026.10.17.zip').infolist()]"

# 站点里所有 DOI 出现位置
Select-String -Path _config.yml,dataset/metadata.json,llms.txt -Pattern "10.5281"

# 查 DataCite 已收录的元数据
Invoke-RestMethod "https://api.datacite.org/dois/10.5281/zenodo.XXXXXXXX" | ConvertTo-Json -Depth 4
```

---

## 10. 下一版（例如 2027 版）怎么发

1. 更新数据源（物种页 / 长文件名录）→ `build_dataset.py --write`
2. 改版本号：`dataset/metadata.json` 的 `version` 与 `dates`；`_config.yml` 的 `dataset.version` 与 `dataset.archive_file`
3. Zenodo 打开上一版 record → **New version** → **Import files**（可先导入再替换）→ 上传新 zip
4. 新版本有**自己的版本 DOI**；概念 DOI 不变
5. 回填：`_config.yml` 的 `dataset.doi` 改成新版 DOI，`concept_doi` 保持不变；`dataset/metadata.json` 的 `doi.version` 改新版、`doi.concept` 不变
6. 重跑 `--write --check` → commit → push → 验收

> 站点 `dataset.doi` 指向"最新版本 DOI"、`concept_doi` 指向"全部版本"，页面上两者都会显示（`render_doi_block` 会写"（概念 DOI / 全部版本：…）"）。这样引用具体版本和引用整个数据集都有落点。

---

## 11. 常见坑（按踩中概率排序）

| # | 坑 | 后果 | 避免方法 |
|---|---|---|---|
| 1 | 删掉草稿（想重来） | 预留 DOI 作废，文件里写的 DOI 失效 | 重来就**改草稿**，别删；非要删就重新预留并重跑第 5 步 |
| 2 | 预留 DOI 后没重传文件 | 归档包里是 `zenodo.XXXXXXX` 占位符 | 第 5 步必须做，`Select-String` 验三处 |
| 3 | 拿过期 zip 上传 | 数据与站点/CHANGELOG 不一致 | 上传前 `--check` 通过 + 看 `LastWriteTime` |
| 4 | 发布后改文件超过 45 天 | 只能改元数据，文件锁死 | 小错改元数据；大改走 **New version** |
| 5 | 描述里写"正式命名"之类的话 | 与"不构成命名行为"声明冲突，学术上不严谨 | 已按"taxonomic compilation / no nomenclatural act"写好，别改 |
| 6 | License 与仓库不一致 | DataCite 元数据自相矛盾 | 统一 CC BY 4.0 |
| 7 | 每次更新都新建 record | 引用分散，曝光被摊薄 | 用 **New version**，概念 DOI 累积引用 |
| 8 | 只发 DOI 不宣传 | 零曝光 | 第 8 节 1–4 项至少做掉 |

---

## 12. 我（AI）能替你做的部分

已做：数据集包、元数据、生成脚本、站内 DOI 位、CI、本手册。
需要你本人做：注册账号、点上传/发布（涉及你的身份与授权，必须你点）。
**拿到预留 DOI 后把号发我**，我可以帮你改 `dataset/metadata.json`、重跑 `--write --check`、把改动 commit 好，你只需要在 Zenodo 重传一次文件并点 Publish。
