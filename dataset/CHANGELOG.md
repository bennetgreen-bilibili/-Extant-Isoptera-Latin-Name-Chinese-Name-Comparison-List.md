# 版本记录 Changelog

版本号采用名录发布日期（YYYY.MM.DD）。同一版本重跑生成脚本应得到逐字节一致的文件；新增/修订数据请升版本号后再归档。

## 2026.10.30 — 异名补录与命名差异判定修订

- 数据补录（只补异名对应关系，不改名录主体与计数）：按 GBIF Backbone、Catalogue of Life、Blattodea Species File 的对照结果，把 3 对**可以确定**的异名写入接受名的「次异名」一节（front matter 的 `authority_synonym_*` 字段，正文生成「依外部权威库补录的异名」小节，检索可按异名命中）：
  - *Amitermes californicus* → *Amitermes wheeleri*（GBIF、CoL、BSF 一致视为异名）
  - *Coptotermes guizhouensis* → *Coptotermes formosanus*（CoL、BSF 一致；GBIF 仍标接受名）
  - *Nasutitermes dasyopsis* → *Nasutitermes nigriceps*（CoL、BSF 一致；GBIF 仍标接受名）
  - `synonym_count` / `synonyms` 仍按原始文献口径，归档数据集的次异名表（696 条）不变。
- 命名差异看板改为「逐对判定关系与方向」：19 条名称差异 → 15 对；关系上 异名 4 对 / 组合差异（同种异属）11 对；方向上 外部库名为接收名 3 对 / 本站名为接收名 6 对 / 待定 6 对；可补录 3 对、已补录 3 对。物种页「其他数据库」区块与 `search-index.json` 同步。
- 修复：命名差异页的异名/接受名外链曾把 `_config.yml` 的行尾注释拼进 URL（链接失效、破坏 HTML），已修复，并在 `_tools/check_site.py` 增加坏 URL 与归并一致性校验。
- 命名差异看板新增人工核对备注（`_data/name_issue_reviews.json`）：4 条模糊匹配经查为外部库拼写变体或误配——*Cortaritermes silvestrii*（GBIF / BSF 作 *silvestri*）、*Niuginitermes variratae*（BSF / CoL / GBIF 作 *variatae*）、*Euhamitermes chhotanii*（GBIF 作 *chhotannii*）与 *Incisitermes mariae*（GBIF 未收录该新名，模糊匹配到另一有效种 *I. marianus*）——本站名与原始描述一致，不改名；看板与 CSV 标「已人工核对」并附判定依据，规则见 `_tools/外部权威库与一致性核对.md` 第 4.3 节。
- 归档文件：`downloads/isoptera-checklist-v2026.10.30.zip`（数据表与上一版一致，元数据、版本号与 `data/isoptera-taxonomy.json` 的名称/版本随之更新）。
- DOI：本版尚未在 Zenodo 发布，版本 DOI 仍为 2026.10.17 版的 10.5281/zenodo.23646836；发布新版后回填。
- 说明：本版本为纯汇编与对照记录，不构成任何命名行为（no nomenclatural act）。

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
