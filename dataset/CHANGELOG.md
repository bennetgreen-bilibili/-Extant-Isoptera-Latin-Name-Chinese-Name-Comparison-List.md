# 版本记录 Changelog

版本号采用名录发布日期（YYYY.MM.DD）。同一版本重跑生成脚本应得到逐字节一致的文件；新增/修订数据请升版本号后再归档。

## 2026.10.30 — 异名补录与命名差异判定修订

- **新增文献补录（2026-10-31，同一版本，尚未归档发布）**：按近年原始文献补录 18 个新种、4 个新亚种、3 个新属，并修订 4 处分类变动——
  - 新属：*Ekueitermes*（肠棘白蚁属）、*Spiralitermes*（螺旋白蚁属）、*Scheffrahnitermes*（谢弗拉恩白蚁属），均隶尖白蚁亚科（Apicotermitinae）；
  - 新种（18）：*Ekueitermes alerosinus*、*Spiralitermes jurupari*、*Scheffrahnitermes ubuntu*、*Chasitermes tupan*、*Pseudocapritermes novus*、*Labiocapritermes microcephalus*、*L. wayanadensis*、*Proneotermes tacicuarensis*、*Acorhinotermes murui*、*Termes incognitus*、*Isognathotermes acristatus*、*I. modicus*、*I. magniplanifrons*、*I. phallicaecalis*、*I. phalloides*、*I. rectimalatus*、*I. similifinitimus*、*Amitermes californicus*；
  - 新亚种（4）：*Isognathotermes ugandensis burundii*、*I. u. kenyae*、*I. u. malawii*、*I. u. ugandensis*（方白蚁亚科）；
  - *Isognathotermes* 属整合修订（EJT 1024, 2025）：补 5 个异名（*I. gibbifrons* → *I. bulbifrons*、*I. speciosus* → *I. finitimus*、*I. gaigei* → *I. planifrons*、*I. modestior* / *I. silvestrii* → *I. severus*）；*I. congoensis* 改注 incertae sedis；
  - *Amitermes californicus* 依 Zootaxa 5128（2022）恢复为有效种，从 *A. wheeleri* 次异名中拆出（此前按外部库对照误并）；
  - *Xiaitermes tiantaiensis* 依 Insects 17: 602（2026）降为 *X. yinxianensis* 次异名，删除其物种页；
  - 计数：分类单元记录 3068 → 3089（种 3004 → 3021、亚种 64 → 68、属 323 → 326）；尖白蚁亚科 237 → 241 种 / 68 属，方白蚁亚科 142 → 149 种、亚种 6 → 10，瘤白蚁亚科 132 → 135 种，弓白蚁亚科 193 → 194 种，白蚁亚科 106 → 107 种，象白蚁亚科 607 → 606 种，木白蚁科 479 → 480 种，鼻白蚁科 61 → 62 种；
  - 三语名录、isoptera-data.json、data/ 结构化数据（含 data/index.json 计数与文件字节数）、检索索引、sitemap、统计页、dataset/ 归档包与外部库缓存（_data/authority_links.json、_data/bsf_links.json、_data/papers.json、_data/name_issues.json）均已按新名录重算；
  - 说明：新种模式产地以原文为准；*Spiralitermes jurupari*、*Chasitermes tupan*、*Scheffrahnitermes ubuntu* 的产地仅到区域级（原文摘要未给出具体地点），待补。
  - 固化：新增 `_tools/build_taxonomy_data.py`（只用标准库、确定性输出、支持 `--check`），从 `list.md` + `_species/` 统一生成 `isoptera-data.json`、`data/index.json`、`data/*.json` 与三语 `stats.md`；已接入 `validate.yml` 与 `pages.yml` 的生成顺序，此后增删类群不再需要手工改这些派生产物；
  - 修复：`data/*.json` 的 `distribution` 字段此前带一个多余的右括号（如「安哥拉）」，由历史生成逻辑残留），已统一去掉；`data/index.json` 中按支系合辑存放的科（远等翅类 4 科、新等翅类除白蚁科 6 科）的 `file` 链接改为指向实际合辑文件（此前指向不存在的单科文件）；
  - 统计页：属级明细表改为固定排序（种数降序、同种数按拉丁名升序），英文版「Overview」与亚科表表头改用英文标签；三语统计页计数与名录同步；
  - 名称微调：*Isognathotermes phalloides* 中文正名由「似阳茎等颚白蚁」定为「阳茎等颚白蚁」。

- 数据补录（初版：只补异名对应关系，不改名录主体与计数；这 3 对随后于同日正式合并，见本条末）：按 GBIF Backbone、Catalogue of Life、Blattodea Species File 的对照结果，把 3 对**可以确定**的异名写入接受名的「次异名」一节（front matter 的 `authority_synonym_*` 字段，正文生成「依外部权威库补录的异名」小节，检索可按异名命中）：
  - *Amitermes californicus* → *Amitermes wheeleri*（GBIF、CoL、BSF 一致视为异名）
  - *Coptotermes guizhouensis* → *Coptotermes formosanus*（CoL、BSF 一致；GBIF 仍标接受名）
  - *Nasutitermes dasyopsis* → *Nasutitermes nigriceps*（CoL、BSF 一致；GBIF 仍标接受名）
  - 初版 `synonym_count` / `synonyms` 仍按原始文献口径，归档数据集的次异名表（696 条）不变；随后按人工判断把这 3 对正式合并（见本条末「异名正式合并」）。
- 命名差异看板改为「逐对判定关系与方向」：19 条名称差异 → 15 对；关系上 异名 4 对 / 组合差异（同种异属）11 对；方向上 外部库名为接收名 3 对 / 本站名为接收名 6 对 / 待定 6 对；可补录 3 对、已补录 3 对（正式合并 3 对后的最终数字见本条末）。物种页「其他数据库」区块与 `search-index.json` 同步。
- 修复：命名差异页的异名/接受名外链曾把 `_config.yml` 的行尾注释拼进 URL（链接失效、破坏 HTML），已修复，并在 `_tools/check_site.py` 增加坏 URL 与归并一致性校验。
- 命名差异看板新增人工核对备注（`_data/name_issue_reviews.json`）：4 条模糊匹配经查为外部库拼写变体或误配——*Cortaritermes silvestrii*（GBIF / BSF 作 *silvestri*）、*Niuginitermes variratae*（BSF / CoL / GBIF 作 *variatae*）、*Euhamitermes chhotanii*（GBIF 作 *chhotannii*）与 *Incisitermes mariae*（GBIF 未收录该新名，模糊匹配到另一有效种 *I. marianus*）——本站名与原始描述一致，不改名；看板与 CSV 标「已人工核对」并附判定依据，规则见 `_tools/外部权威库与一致性核对.md` 第 4.3 节。
- 归档文件：`downloads/isoptera-checklist-v2026.10.30.zip`（本版数据表按本条末的异名合并重新生成，元数据、版本号与 `data/isoptera-taxonomy.json` 的名称/版本随之更新）。
- DOI：本版尚未在 Zenodo 发布，版本 DOI 仍为 2026.10.17 版的 10.5281/zenodo.23646836；发布新版后回填。
- 说明：本版本为纯汇编与对照记录，不构成任何命名行为（no nomenclatural act）。
- **异名正式合并（同日修订）**：3 对「已补录」异名由「另立记录」改为正式并入接受名——
  - 删除异名物种页（`amitermes-californicus`、`coptotermes-guizhouensis`、`nasutitermes-dasyopsis`），并从三语名录、`isoptera-data.json`、`data/` 结构化数据、检索索引、sitemap 与归档数据集中移除；
  - 命名人与模式产地并入接受名的次异名列表（`synonyms` / `synonym_localities`），`synonym_count` 各加 1；`authority_synonym_*`（「依外部权威库补录的异名」）字段随之删除，物种页不再出现「另有独立记录、待合并」的提示；
  - *Amitermes californicus* → *A. wheeleri*（GBIF / CoL / BSF 一致）、*Coptotermes guizhouensis* → *C. formosanus*（CoL / BSF 一致；GBIF 仍标接受名）、*Nasutitermes dasyopsis* → *N. nigriceps*（CoL / BSF 一致；GBIF 仍标接受名）；
  - 计数调整：3071 → 3068 条记录（3008 → 3005 种，63 亚种不变）；白蚁科 2132 → 2130 种、异白蚁科 230 → 229 种、弓白蚁亚科 194 → 193 种、象白蚁亚科 608 → 607 种、弓白蚁属 113 → 112 种、乳白蚁属 59 → 58 种、象白蚁属 243 → 242 种；归档次异名表 696 → 699 条；
  - 外部库缓存同步：`_data/authority_links.json`、`_data/bsf_links.json`（含人工核对工作表）、`downloads/isoptera-authority-crossref.csv` 都按新名录重算；`_data/species_photos.json` 把 *A. californicus* 的照片并入 *A. wheeleri*，`_data/occurrence_summary.json` 与种级 GeoJSON 移除已删物种；命名差异看板减少 7 条（307 → 300 条；名称差异 19 → 12 条、逐对 15 → 12 对；已补录 3 → 0）；
  - 归档文件 `downloads/isoptera-checklist-v2026.10.30.zip` 重新生成（沿用同一版本号；本版尚未在 Zenodo 发布）。

- **名称修订（同日第二次修订）**：对人工复核确认的 4 对名称差异，按外部权威库的接受名改正本站记录（改后这些名字不再出现在命名差异看板）——
  - *Velocitermes aporeticus* → *Diversitermes aporeticus*（并入歧白蚁属，中文名改「怀疑歧白蚁」；GBIF 接受组合）
  - *Parvitermes mexicanus* → *Nasutitermes mexicanus*（并入象白蚁属，中文名改「墨西哥象白蚁」；GBIF 接受组合）
  - *Parvitermes bacchanalis* → *Obtusitermes bacchanalis*（并入钝白蚁属，中文名改「酒神钝白蚁」；Catalogue of Life 接受组合）
  - *Pericapritermes metatus* → 亚种 *Pericapritermes appellans metata* Silvestri, 1914（Catalogue of Life；原种级记录改为 *P. appellans* 下的亚种，中文名「丈量亚种」，模式产地 Guinea: Camayenne; Kakoulima; Kindia 保留）
  - 计数：种 3005 → 3004、亚种 63 → 64（分类单元记录仍 3068 条）；白蚁科 2130 → 2129 种、49 → 50 亚种；瘤白蚁亚科 133 → 132 种、2 → 3 亚种；属级：*Velocitermes* 10 → 9、*Diversitermes* 3 → 4、*Parvitermes* 13 → 11、*Nasutitermes* 242 → 243、*Obtusitermes* 3 → 4、*Pericapritermes* 41 → 40 种（亚种 2 → 3）；旧组合不写入次异名（次异名表仍 699 条）。
  - 外部数据与派生产物同步：`_data/authority_links.json` / `_data/bsf_links.json`（BSF 抽查 20/20）、`downloads/isoptera-authority-crossref.csv`、`_tools/bsf对照/工作表.csv`、`_data/species_photos.json`、`_data/occurrence_summary.json` 与种级 GeoJSON（改名并更新属性）、三语名录、`isoptera-data.json`、`data/` 结构化数据、检索索引、sitemap 与归档数据集。
  - 归档文件 `downloads/isoptera-checklist-v2026.10.30.zip` 重新生成（沿用同一版本号；本版尚未在 Zenodo 发布）。

- **名称修订（同日第三次修订）**：对人工复核确认的 1 项组合差异按外部权威库的接受名改正本站记录（改后该名字不再出现在命名差异看板）——
  - *Megagnathotermes katangensis* → *Polyspathotermes katangensis*（并入多铲白蚁属，中文名改「加丹加多铲白蚁」；Catalogue of Life 与 BSF 均接受该组合，GBIF Backbone 尚未收录、只匹配到多铲白蚁属）；旧组合不写入次异名（次异名表仍 699 条）。
  - 计数：种 3004、亚种 64、分类单元记录 3068 均不变；属级 *Megagnathotermes* 2 → 1 种、*Polyspathotermes* 7 → 8 种；方白蚁亚科 142 种、白蚁科 2129 种不变。
  - 人工核对备注：*Ruptitermes franciscoi* 与 *Anoplotermes franciscoi* 经查是同一物种的两套组合（Acioli & Constantino, 2015, Zootaxa 4032: 451–492 的新组合；Constantino 的 Termite Database 2025-05 版同此），GBIF 的「(Snyder, 1946)」为 Plazi / Zootaxa 题名元数据笔误（正文与图注均作 1959）；本站名不改，结论写入 `_data/name_issue_reviews.json`（看板标「已人工核对」，人工核对条目 4 → 5）。
  - 外部数据与派生产物同步：`_data/authority_links.json` / `_data/bsf_links.json`（BSF 抽查 20/20）、`downloads/isoptera-authority-crossref.csv`、`_tools/bsf对照/工作表.csv`、`_data/species_photos.json`、`_data/occurrence_summary.json` 与分布图（改名后 GBIF Backbone 无对应种，该种级地图移除；同时补上 *Obtusitermes bacchanalis* 的种级地图，种级地图仍 1,180 个、记录仍 87,075 条）、三语名录、`isoptera-data.json`、`data/` 结构化数据、检索索引、sitemap 与归档数据集。
  - 归档文件 `downloads/isoptera-checklist-v2026.10.30.zip` 重新生成（沿用同一版本号；本版尚未在 Zenodo 发布）。

## 2026.10.17 — 首个 DOI 归档版本 First archived release

- 数据内容与项目网站 2026.10.17 正式版一致：13 科、18 亚科、323 属、3008 种、63 亚种（3071 条记录）。
- 归档文件：
  - `data/isoptera-checklist.csv`：逐条分类单元表，22 列（含中文正名、模式产地、分布中英、次异名、页面链接）。
  - `data/isoptera-taxonomy.json`：完整分类树，含各级计数与页面链接。
  - `data/isoptera-synonyms.csv`：次异名长表（含与模式产地的对应状态 localityAlignment）。
  - `data/isoptera-counts.csv`：科/亚科级计数。
  - `data/isoptera-references.csv`：77 条参考文献（带 DOI 者随条目给出）。
  - `datapackage.json`：Frictionless Data Package 描述（含字段字典）。
  - `datacite-metadata.xml`：DataCite Metadata Schema 4.6 记录。
- 许可：CC BY 4.0。
- 归档 DOI（2026-10-25 于 Zenodo 发布）：版本 DOI [10.5281/zenodo.23646836](https://doi.org/10.5281/zenodo.23646836)；概念 DOI（全部版本，始终指向最新版）[10.5281/zenodo.23646835](https://doi.org/10.5281/zenodo.23646835)。
- 说明：本版本为纯汇编，不构成任何命名行为（no nomenclatural act）。
