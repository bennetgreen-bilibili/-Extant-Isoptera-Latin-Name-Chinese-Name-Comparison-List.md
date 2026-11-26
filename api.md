---
layout: default
title: "API v1：名录的静态 JSON 接口"
description: "按拉丁学名、中文正名、异名、属名或科名读取现存等翅下目名录的 JSON 接口：名称查找表、分类层级与 3089 条物种记录；静态托管、可跨域、无需密钥。"
lang: zh-CN
author: 班奈特格林
date: 2026-11-26
version: 2026.11.21
keywords: [白蚁, 等翅目, Isoptera, API, JSON, 学名, 中文名, 分类]
permalink: /api/
single_lang: true
---

# API v1

名录的只读 JSON 接口，按名称、分类层级或 slug 读取数据。文件在构建时生成，由 GitHub Pages 直接返回，不经过应用服务器。

- 基址：`https://termite-extant-isoptera.org/api/v1/`
- 版本：`2026.11.21`，与名录数据版本一致
- 许可：CC BY 4.0，引用方式见下文
- 认证：无；响应带 `Access-Control-Allow-Origin: *`，浏览器可直接跨域读取
- 缓存：由 GitHub Pages CDN 提供，`Cache-Control: max-age=600`

## 端点

| URL | 内容 |
| --- | --- |
| `/api/v1/index.json` | 版本、许可、引用格式、端点清单与匹配语义 |
| `/api/v1/names.json` | 名称 → 分类单元的查找表，含接受名、异名、中文名、属、科、亚科 |
| `/api/v1/taxonomy.json` | 支系 → 科 → 亚科 / 属的层级与计数，不含种级明细 |
| `/api/v1/species/<slug>.json` | 单个种或亚种的完整记录，共 3089 个 |
| `/data/name-issues.json` | 与 GBIF、Catalogue of Life、BSF 的名称对照及人工裁定 |

`<slug>` 由学名生成：属名、种加词、亚种加词依次用连字符连接，全部小写。例如 `Coptotermes formosanus` 对应 `coptotermes-formosanus`，`Zootermopsis nevadensis nevadensis` 对应 `zootermopsis-nevadensis-nevadensis`。

```bash
curl -s https://termite-extant-isoptera.org/api/v1/species/coptotermes-formosanus.json
```

## 名称查找

`names.json` 是完整的名称查找表：取一次，在本地按规范化后的键查。静态托管没有 `?q=` 形式的服务端查询，这个文件就是查询层。

键的规范化顺序：Unicode NFKC → 去首尾空白 → 连续空白折叠为一个空格 → 转小写。学名不区分大小写。中文名按原字匹配，不做繁简转换。

```python
import re
import unicodedata

def normalize(name):
    text = unicodedata.normalize("NFKC", name)
    return re.sub(r"\s+", " ", text).strip().lower()
```

每个值带 `match` 字段，取值如下：

| `match` | 含义 | 关键字段 |
| --- | --- | --- |
| `accepted` | 接受名（种或亚种） | `slug`、`rank`、`page` |
| `synonym` | 异名 | `acceptedSlug`、`accepted` |
| `zh` | 中文正名 | `slug`、`latin` |
| `genus` | 属 | `slug`、`page` |
| `family` | 科 | `slug`、`page` |
| `subfamily` | 亚科 | `slug`、`page` |
| `ambiguous` | 同一键命中多个分类单元 | `candidates` |

键不存在表示名录未收录该名称。`ambiguous` 不会擅自选一个：`candidates` 列出全部候选，由调用方决定。中文名「阿马尼」同时对应两种锯白蚁，是站内真实存在的重名。

查找表还收录了两类变体：学名加命名人（如 `coptotermes formosanus shiraki, 1909`），以及去掉亚属括号的写法（如 `coptotermes changtaiensis` 可命中 `Coptotermes (Polycrinitermes) changtaiensis`）。

## 物种记录

`/api/v1/species/<slug>.json` 是一个种或亚种的全部字段：

| 字段 | 说明 |
| --- | --- |
| `apiVersion`、`version` | 接口版本与数据版本 |
| `latin`、`zh`、`rank` | 学名、中文正名、阶元（`species` 或 `subspecies`） |
| `authorship` | 命名人与年份 |
| `isTypeSpecies` | 是否为模式种 |
| `typeLocality` | 模式产地 |
| `classification` | `clade`、`family`、`subfamily`、`genus` 四级，每级含 `id`、`latin`、`zh`；无亚科时 `subfamily` 为 `null` |
| `distribution` | `zh` 与 `en` 两种文字的分布；仅种级有 |
| `synonyms` | 异名数组，含 `asPublished`、`name`、`authorship`、`reference`、`note`、`typeLocality`、`localityAlignment` |
| `subspecies` | 亚种数组，仅种级有 |
| `parent` | 所属种的 `latin`、`zh`、`slug`；仅亚种有 |
| `authorityChecks` | 该名称与 GBIF / CoL / BSF 的差异条目；仅在存在差异时出现 |
| `authorityReview` | 人工裁定记录；仅在存在记录时出现 |
| `pageUrl`、`apiUrl` | 对应的人类可读页面与 API 地址 |

`reference` 是原始文献页码，`asPublished` 是名录里的原始写法。`localityAlignment` 表示异名模式产地与接受名是否一致。

## 分类索引

`/api/v1/taxonomy.json` 给出支系、科、亚科、属及其计数，适合构建下拉框、筛选器或统计表。种级明细只在各自的物种记录里，不重复塞进分类索引。

```json
{
  "apiVersion": "1",
  "version": "2026.11.21",
  "counts": {"clades": 6, "families": 13, "subfamilies": 18, "genera": 326, "species": 3021, "subspecies": 68},
  "clades": [{"id": "isoptera", "latin": "Extant Isoptera", "zh": "现存等翅下目", "parentId": ""}],
  "families": [
    {
      "id": "mastotermitidae",
      "latin": "Mastotermitidae",
      "zh": "澳白蚁科",
      "cladeId": "isoptera",
      "subfamilies": [],
      "genera": [
        {
          "id": "mastotermes",
          "latin": "Mastotermes",
          "zh": "澳白蚁属",
          "subfamilyId": "",
          "typeSpecies": "Mastotermes darwiniensis",
          "counts": {"species": 1, "subspecies": 0}
        }
      ]
    }
  ]
}
```

## 命名差异

`/data/name-issues.json` 是站点既有的公开副本，记录本站名与 GBIF、Catalogue of Life、Blattodea Species File 的对照结果：每条含 `source`、`group`、`kind`、`theirs`、`accepted`、`match`、`note` 等字段；`synonym_pairs` 记录跨库异名对，`species_authority` 按接受名汇总外来异名。

## 代码示例

### Python

```python
import json
import urllib.request

base = "https://termite-extant-isoptera.org/api/v1"
names = json.load(urllib.request.urlopen(base + "/names.json"))
hit = names.get("台湾乳白蚁")

if hit and hit["match"] == "zh":
    record = json.load(urllib.request.urlopen(base + "/species/" + hit["slug"] + ".json"))
    print(record["latin"], record["classification"]["family"]["latin"])
```

### R

```r
library(jsonlite)
x <- fromJSON("https://termite-extant-isoptera.org/api/v1/species/coptotermes-formosanus.json")
x$classification$family$latin
x$synonyms$name
```

### Excel Power Query

按 slug 直接取一条记录：

```text
let
    Source = Json.Document(Web.Contents("https://termite-extant-isoptera.org/api/v1/species/coptotermes-formosanus.json")),
    Synonyms = Source[synonyms]
in
    Synonyms
```

按名称查：先取 `names.json`，再用 `Record.Field` 取键。

```text
let
    Names = Json.Document(Web.Contents("https://termite-extant-isoptera.org/api/v1/names.json")),
    Hit = Record.Field(Names, "coptotermes formosanus")
in
    Hit
```

批量清洗时只需下载一次 `names.json`，在本地转成表后与自己的名称列做连接，不要逐条请求。

### curl 与 jq

```bash
curl -s https://termite-extant-isoptera.org/api/v1/names.json \
  | jq '.["termes errabundus"]'
```

## 版本与引用

`apiVersion` 为 `1`。新增字段不改变版本；删除字段或改变语义时启用 `/api/v2/`，v1 保留。数据版本随名录发布更新，`index.json` 的 `dateModified` 给出最后修改日期。

引用本接口或数据时使用数据集版本 DOI：

> 班奈特格林. 现存等翅下目（白蚁）拉丁学名—中文正名对照名录（2026.11.21 版）. Zenodo. https://doi.org/10.5281/zenodo.23646836

许可为 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)：复制、分发、改编均可，需注明作者与来源。

## 错误与限制

- 不存在的 slug 返回 GitHub Pages 的 404 页面（HTML），不是 JSON；调用方应按 HTTP 状态码判断。
- 接口不提供模糊搜索、拼音检索或全文检索；这些在站内搜索页完成。
- 名称匹配只覆盖名录收录的拼写，不做拼写纠错、不做异名数据库的自动扩展。
- `names.json` 未压缩约 2.9 MB；HTTP 传输会 gzip 压缩。批量场景只取一次。
