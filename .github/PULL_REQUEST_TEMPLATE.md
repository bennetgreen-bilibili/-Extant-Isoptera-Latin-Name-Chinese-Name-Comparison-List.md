<!-- 感谢贡献！请填好下面的内容，并勾选已完成的自检项。 -->

## 改动内容

<!-- 一句话说明改了什么、为什么改；数据改动请附证据链接（DOI / GBIF / COL / BSF）。 -->

- 

## 自检清单（数据 / 生成产物改动必勾）

- [ ] 改了 `list.md` 后已同步 `en/list.md` 与 `es/list.md`（三语名录行数、锚点、属/种顺序一致）
- [ ] 未手改 `<!-- AUTO:BEGIN -->` / `<!-- AUTO:END -->` 之间的自动区块（正文由 `.github/workflows/build_species_body.py` 生成，手写内容放在标记之外）
- [ ] 已按 CI 顺序重跑全部生成脚本：
  - `python .github/workflows/build_genus_index.py`
  - `python .github/workflows/build_species_body.py --write`
  - `python .github/workflows/build_sitemap_txt.py`
  - `python .github/workflows/build_search_index.py --write --no-enrich`
  - `python .github/workflows/build_dataset.py --write`
  - `python .github/workflows/build_name_issues.py --write`
  - `python _tools/build_changelog.py --write`
- [ ] 已运行 `python _tools/check_site.py`（CI 用 `python _tools/check_site.py --ci`）并通过
- [ ] `git status --porcelain` 只包含本次预期文件，`_tmp/` 等临时目录未提交
- [ ] 未把外部 API 缓存类产物（`build_authority_links.py` 等）无意义地重跑并混入本 PR

## 备注

<!-- 其他需要维护者知道的信息（可选）。 -->
