# 版本记录 Changelog

版本号采用名录发布日期（YYYY.MM.DD）。同一版本重跑生成脚本应得到逐字节一致的文件；新增/修订数据请升版本号后再归档。

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
- 说明：本版本为纯汇编，不构成任何命名行为（no nomenclatural act）。
