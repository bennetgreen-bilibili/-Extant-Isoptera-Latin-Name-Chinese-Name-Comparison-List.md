# `_data` 分片布局（一阶元一档）

`_data/*.json` 里体积大的文件已拆成「一阶元一档」的目录。**仓库里不再有这些聚合大文件**，
分片文件就是唯一真源。拆/合并由 `_tools/data_shards.py` 负责：

    python _tools/data_shards.py --status        # 每个数据集现在的状态
    python _tools/data_shards.py --verify-all    # 分片合并回去 == 拆分前的原始 JSON
    python _tools/data_shards.py --split-all     # 从 _data/<name>.json 重新生成（已删聚合时无操作）

改动分片数据时**直接改单个分片文件**，不要再去找聚合文件。

## 1. 布局

| 数据集 | 分片路径 | 文件内容 | 总数 |
| --- | --- | --- | --- |
| `morphology_species` | `_data/morphology_species/<属>/<slug>.json` | 该物种的形态描述对象 | 401 |
| `fauna_species` | `_data/fauna_species/<属>/<slug>.json` | 动物志物种条目 | 435 |
| `fauna_measurements` | `_data/fauna_measurements/<属>/<slug>.json` | 测量数据 | 255 |
| `morphology_genera` | `_data/morphology_genera/<属>.json` | 属级形态描述 | 245 |
| `genus_sources` | `_data/genus_sources/<属>.json` | 属级文献出处 | 326 |
| `taxon_literature` | `_data/taxon_literature/<rank>/<id>.json` + `meta.json`（原 `_meta` 键） | 该阶元的文献块 | 287 |
| `etymology` | `_data/etymology/meta.json`、`genera/<属>.json`、`epithets/<首字母>.json`（每字母一档 `{epithet: 值}`） | 词源 | 353 |
| `taxon_prose` | `_data/taxon_prose/<lang>/<families\|subfamilies>/<id>.json` | 科/亚科正文 | 94 |
| `translations_en` / `translations_es` | 见 §2 | 译文 | 各 1085 |
| `papers` | `_data/papers/meta.json` + `genera/<属>.json` | 论文缓存 | 327 |
| `species_photos` | `_data/species_photos/meta.json` + `species/<属>.json` | 照片缓存，文件是 `{拉丁名: …}` | 79 |
| `authority_links` | `_data/authority_links/meta.json` + `taxa/<属>.json` | 同上 | 327 |
| `bsf_links` | `_data/bsf_links/meta.json` + `name_map/<属>.json` | 同上 | 327 |

`<属>` 是 `taxonomy.json` 里的属 id（小写、无空格）；`<slug>` 是物种页 URL 的最后一段
（`/species/<slug>/` 去掉前后斜杠），可用 `_species/<slug>.md` 的 `genus_id` 定位属。

## 2. 翻译文件

`_data/translations_<lang>/` 下：

| 子块 | 形态 |
| --- | --- |
| `meta` | `meta.json` |
| `morphology_species` / `fauna_species` | `<属>/<slug>.json`，一物种一档 |
| `morphology_genera` | `<属>.json`，一属一档 |
| `fauna_genera` / `fauna_families` / `fauna_keys` | 仍是单文件（条数少，拆了没收益） |

## 3. 读取方式对照（改模板/脚本时看这里）

Liquid（`site.data.…`）：

| 旧 | 新 |
| --- | --- |
| `site.data.morphology_species[zh_url]` | `site.data.morphology_species[genus_id][slug]` |
| `site.data.fauna_species[zh_url]` | `site.data.fauna_species[genus_id][slug]` |
| `site.data.fauna_measurements[zh_url]` | `site.data.fauna_measurements[genus_id][slug]` |
| `site.data.translations_en.morphology_species[zh_url]` | `site.data.translations_en.morphology_species[genus_id][slug]` |
| `site.data.translations_en.fauna_species[zh_url]` | `site.data.translations_en.fauna_species[genus_id][slug]` |
| `site.data.morphology_genera["/genus/<id>/"]` | `site.data.morphology_genera["<id>"]` |
| `site.data.translations_en.morphology_genera["/genus/<id>/"]` | `site.data.translations_en.morphology_genera["<id>"]` |
| `site.data.taxon_literature["/family/<id>/"]` | `site.data.taxon_literature["family"]["<id>"]` |
| `site.data.taxon_literature["/genus/<id>/"]` | `site.data.taxon_literature["genus"]["<id>"]` |
| `site.data.taxon_literature["_meta"]` | `site.data.taxon_literature["_meta"]`（不变） |
| `site.data.etymology.genera["<id>"]` | 不变 |
| `site.data.etymology.epithets["<epithet>"]` | `site.data.etymology.epithets["<首字母>"]["<epithet>"]` |
| `site.data.taxon_prose[lang].families["<id>"]` | 不变（目录名顶替了 `families` 这一层） |
| `site.data.papers.genera["<属>"]` | 不变 |
| `site.data.species_photos.species["<拉丁名>"]` | `site.data.species_photos.species["<属>"]["<拉丁名>"]` |
| `site.data.authority_links.taxa["<拉丁名>"]` | `site.data.authority_links.taxa["<属>"]["<拉丁名>"]` |
| `site.data.bsf_links.name_map["<拉丁名>"]` | `site.data.bsf_links.name_map["<属>"]["<拉丁名>"]` |

`<属>` 由拉丁名首词小写得到（`page.latin | split: ' ' | first | downcase`）；
`<slug>` 由 `page.url` 取最后一段（`page.url | split: '/' | last`）。

Python（`_tools/`）：读分片用 `_tools/data_shards.py` 的 `merge(name)`，或直接
`glob` 所需子目录；**写入分片**时只写自己那一档，不要重写整棵树。

## 4. 没拆的文件（有意保留）

派生索引与列表型文件体积虽大，但拆了反而更难用，保留原样：

- `species_by_genus.json` / `species_by_family.json` / `species_by_subfamily.json`（索引表）
- `occurrence_summary.json`、`name_issues.json`、`changelog.json`、`references.json`（列表/派生）
- `taxonomy.json`、`i18n.yml`、各类 `< 200 KB` 的配置与缓存
