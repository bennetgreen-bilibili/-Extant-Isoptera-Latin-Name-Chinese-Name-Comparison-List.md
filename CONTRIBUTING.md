# 贡献指南（Contributing）

本仓库是「现存等翅下目（白蚁）拉丁学名—中文正名对照名录」站点的源码：Jekyll 构建、GitHub Pages 部署，三语（中文 / English / Español）。

## 数据唯一来源

请**只改源文件**，页面与派生产物全部由脚本生成：

| 内容 | 源文件 |
| --- | --- |
| 名录（中文 / English / Español） | `list.md` / `en/list.md` / `es/list.md` |
| 物种页 front matter（学名、中文名、分布、模式产地、异名数…） | `_species/*.md` |
| 数据集元数据（DOI、版本、许可） | `isoptera-data.json`，许可见 `dataset/LICENSE` |
| 界面文案（三语） | `_data/i18n.yml`（`zh-CN` / `en` / `es` 三节 key 必须一致） |

`_species/*.md` 的正文写在 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 之间，由脚本按 front matter 生成；**不要手改这两个标记之间的内容**，标记之外的手写内容可以改。

## 三语同步

- 名录改动必须同时落到 `list.md`、`en/list.md`、`es/list.md`（行数、锚点、属/种顺序保持一致）。
- 界面文案必须同时加到 `_data/i18n.yml` 的三个语言节。
- `python _tools/check_site.py` 会检查三语同构与 i18n key 一致性，不一致直接失败。

## 生成脚本与顺序

顺序以 `.github/workflows/pages.yml`（部署）与 `.github/workflows/validate.yml`（PR 闸门）为准：

```
python .github/workflows/build_genus_index.py
python .github/workflows/build_species_body.py --write
python .github/workflows/build_sitemap_txt.py
python .github/workflows/build_search_index.py --write --no-enrich
python .github/workflows/build_dataset.py --write
python .github/workflows/build_name_issues.py --write
python _tools/build_changelog.py --write
```

- `--no-enrich` 是仓库内的基础版检索索引；部署时 CI 会装 pypinyin / OpenCC 再生成增强版，两者互不冲突。
- 外部 API 缓存类脚本（`build_authority_links.py`、`build_bsf_links.py`、`build_species_photos.py`、`build_references.py`、`build_occurrence_geojson.py`）**只在需要刷新缓存时**手动运行，不要无意义重跑。

## 提交前校验

```
python _tools/check_site.py        # 结构 / 三语同构 / 计数 / sitemap / i18n / 命名差异产物自洽
python _tools/check_site.py --ci   # 与 CI 相同的严格模式
```

生成的产物必须一并提交：CI 会重新生成并断言 `git status --porcelain` 为空（见 `.github/workflows/validate.yml`），忘记重跑脚本会直接红。

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
