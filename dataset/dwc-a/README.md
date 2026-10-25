# Darwin Core Archive（GBIF checklist 发布包）

本目录由 `.github/workflows/build_dataset.py` 生成（与 `dataset/data/` 同源，勿手工编辑）。用途：发布到 GBIF，取得第二个 DOI（`10.15468/…`）。

| 文件 | 内容 |
|---|---|
| `taxon.txt` | Taxon 核心表，3767 行 × 19 列：接受名 3071（种 3008 + 亚种 63）+ 次异名 696（`acceptedNameUsageID` 指回接受名） |
| `vernacularname.txt` | Vernacular Name 扩展，3071 行：`taxonID` / `vernacularName`（中文正名）/ `language`（zho） |
| `meta.xml` | Darwin Core Text 描述（核心 + 扩展映射，UTF-8 / TAB / LF） |
| `eml.xml` | EML 2.1.1（GBIF Metadata Profile 1.1，已通过 profile XSD 校验）；IPT 发布时会用元数据编辑器重新生成 |

上传用的压缩包在 `downloads/isoptera-checklist-dwca-v2026.10.17.zip`（不要传 Zenodo 的归档 zip，那个没有 `meta.xml`）。

- 重新生成：`python .github/workflows/build_dataset.py --write`
- 校验：`python .github/workflows/build_dataset.py --check`
- 完整发布流程（发布资格/背书 → IPT 上传 → 元数据 → 注册 → 回填 → 验收）：`_tools/GBIF-checklist发布逐步操作手册.md`
