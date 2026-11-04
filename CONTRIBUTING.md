# 贡献指南（Contributing）

本仓库是「现存等翅下目（白蚁）拉丁学名—中文正名对照名录」站点的源码：Jekyll 构建、GitHub Pages 部署，三语（中文 / English / Español）。

## 数据唯一来源

请**只改源文件**，页面与派生产物全部由脚本生成：

| 内容 | 源文件 |
| --- | --- |
| 分类层级（支系—科—亚科—属） | `_data/taxonomy.json` |
| 科／亚科正文（三语） | `_data/taxon_prose.json` |
| 名录索引页的导语、按科浏览、参考文献块（三语） | `_data/list_index_blocks.json` |
| 三语名录索引页与英西译文页 | 由 `_tools/build_list_index.py` 生成，**不要手改** `list.md` / `en/list.md` / `es/list.md` / `en/list/sections.md` / `es/list/sections.md` |
| 物种页 front matter（学名、中文名、分布、模式产地、异名数…） | `_species/*.md` |
| 数据集元数据（DOI、版本、许可） | `isoptera-data.json`，许可见 `dataset/LICENSE` |
| 界面文案（三语） | `_data/i18n.yml`（`zh-CN` / `en` / `es` 三节 key 必须一致） |

`_species/*.md` 的正文写在 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 之间，由脚本按 front matter 生成；**不要手改这两个标记之间的内容**，标记之外的手写内容可以改。

## 三语同步

- 名录索引页与译文页由脚本生成，改动要落在 `_data/taxonomy.json`（层级）、`_data/list_index_blocks.json`（导语／按科浏览／参考文献）、`_data/taxon_prose.json`（科亚科正文）三处数据文件上，再重跑 `python _tools/build_list_index.py`；三语的锚点集合由 `check_site.py` 校验同构。
- 界面文案必须同时加到 `_data/i18n.yml` 的三个语言节。
- `python _tools/check_site.py` 会检查三语同构与 i18n key 一致性，不一致直接失败。

## 生成脚本与顺序

顺序已固化在 `_tools/regen_all.sh`（与 `.github/workflows/validate.yml` 一致）。改了源文件后在仓库根目录跑一句即可：

```
bash _tools/regen_all.sh
```

它依次运行：

```
python _tools/extract_taxon_data.py --check
python _tools/build_list_index.py
python _tools/build_taxonomy_data.py --write
python .github/workflows/build_genus_index.py
python .github/workflows/build_species_body.py --write
python .github/workflows/build_photo_pages.py
python .github/workflows/build_taxonomy_pages.py
python .github/workflows/build_sitemap_txt.py
python .github/workflows/build_search_index.py --write --no-enrich
python .github/workflows/build_dataset.py --write
python _tools/build_changelog.py --write
python .github/workflows/build_name_issues.py --write
```

整条链是幂等的：连跑两次，第二次不产生任何字节变化。

- `_tools/build_list_index.py`：从上面三个数据文件 + `_species/` 生成三语 `/list/` 索引页与 `/en/list/sections/`、`/es/list/sections/` 译文页；`_tools/extract_taxon_data.py --check` 校验三个数据文件自身自洽（不读 `list.md`）。
- `_tools/build_taxonomy_data.py`：从 `_data/taxonomy.json` + `_species/` 生成 `isoptera-data.json`、`data/index.json`、`data/*.json` 与三语 `stats.md`；改分类层级、学名或分布后必须重跑，`--check` 可校验。
- `--no-enrich` 是仓库内的基础版检索索引；部署时 CI 会装 pypinyin / OpenCC 再生成增强版，两者互不冲突。
- 科／亚科／属页面由 `.github/workflows/build_taxonomy_pages.py` 从 `_data/taxonomy.json` + `_data/taxon_prose.json` + `_species/` 生成，标题与锚点都取自 taxonomy.json 的 id；`_tools/checklist_headings.py` 的 `NON_TAXON_IDS` 记录索引页与各处的非分类学标题 id（`by-family`、`toc`、`references` 等），新增此类标题必须同步登记。
- 模板（`_layouts/`、`_includes/` 与所有带 front matter 的页面）的 Liquid 语法由 `_tools/check_liquid.py` 检查，CI 在 Jekyll 之前就跑一遍。**Liquid 4 会连 comment 块内部一起解析**：注释里不要直接写标签示例（曾经一个缺变量名的 capture 示例写在注释里，让整站构建在解析期就失败，只留下一条 Ruby 堆栈）。要举例就写成自然语言，或保证参数完整。
- 改动 `_species` front matter 的 `authority_synonym_*`（「依外部权威库补录的异名」）后，必须按上面的顺序重跑 `build_species_body.py`、`build_search_index.py`、`build_name_issues.py`（看板的「已补录」标记与检索命中都依赖这三步），`check_site.py` 会校验三者一致。
- 外部 API 缓存类脚本（`build_authority_links.py`、`build_bsf_links.py`、`build_species_photos.py`、`build_references.py`、`build_occurrence_geojson.py`）**只在需要刷新缓存时**手动运行，不要无意义重跑。
- **刷新缓存后必须重跑 `build_name_issues.py --write` 并与之一起提交**：命名差异看板会把 `_data/authority_links.json` / `_data/bsf_links.json` 的 `meta.generated` 写进 `_data/name_issues.json` 的 `cache_dates`，只提交缓存、不重跑看板，CI 的「生成产物过期」检查会变红（`data/name-issues.json` 是同一内容的公开副本，要一起提交）。

## 提交前校验

```
python _tools/check_site.py        # 结构 / 三语索引页同构 / 层级页面齐备 / 计数 / sitemap / i18n 自洽
python _tools/check_site.py --ci   # 与 CI 相同的严格模式
python _tools/check_liquid.py      # Liquid 语法（成对标签 / 参数个数 / 定界符；含 comment 内部）
```

生成的产物必须一并提交：CI 会重新生成并断言 `git status --porcelain` 为空（见 `.github/workflows/validate.yml`）。

不过「忘了重跑」不再需要人工救火：main 分支上的推送会先跑一遍 `_tools/regen_all.sh`，产物有差异就由 `github-actions[bot]` 自动提交推回（提交信息 `chore(data): 自动重建过期产物 [skip ci]`），然后再做检查。PR 与手动 dispatch 保持严格闸门，不会改写分支——所以在 PR 里仍然要自己跑一次。

归档包 `downloads/*.zip` 只比内容不比字节：`build_dataset.py --check` 逐成员比对（成员名 + 字节），因为 deflate 的输出依赖平台 zlib；`--write` 在成员清单一致时会保留仓库里原有的字节，不会因为换平台就来回改。需要注意的是 **`dataset/CHANGELOG.md` 与 `dataset/LICENSE` 也被打进归档包**，改这两个文件同样会让归档包过期（这正是 2026-11-04 那次 main 变红的原因）。

## Issue 与 PR

- 命名 / 分布 / 次异名 / 拼写 / 分类位置有疑问 → 用 Issue 模板「命名与分布纠错」，**请附证据链接**（原始文献 DOI、GBIF、Catalogue of Life、Blattodea Species File 等）。
- 数据引用、字段含义、许可、使用范围等提问 → 用模板「数据使用提问」。
- PR 请按其模板勾选自检项；数据改动请说明依据文献。

## 许可

- **数据**：CC BY 4.0（注明作者可自由复制、分发、改编、商用，含机器学习训练），全文见 `dataset/LICENSE`。
- **站内插图**：各自遵循原始版权与许可，**含 NC（非商业）等限制**；引用前请逐图核对图片下方的署名与许可链接（另见 `_tools/图片授权与署名说明.md`）。
- **代码与模板**：随仓库发布，未单独声明许可；引用站点样式/脚本前请先开 Issue 说明用途。

## 其他约定

- 不要提交 `_tmp/`（已在 `.gitignore` 中忽略）与本地缓存。
- 不要手改渲染后的页面或派生产物；改源文件 + 重跑脚本。
- 描述性文案保持三语齐备（中文为主，English / Español 跟随）。
