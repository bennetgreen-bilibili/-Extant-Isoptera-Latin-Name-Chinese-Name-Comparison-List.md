---
layout: default
title: "API v1: static JSON for the checklist"
description: "Read the extant Isoptera checklist by Latin name, Chinese name, synonym, genus or family: a name lookup table, the classification tree and 3089 species records, served as static JSON with CORS and no key."
lang: en
author: 班奈特格林
date: 2026-11-26
version: 2026.11.21
keywords: [termites, Isoptera, API, JSON, taxonomy, nomenclature]
permalink: /en/api/
single_lang: true
---

# API v1

Read-only JSON access to the checklist by name, classification level or slug. The files are generated at build time and served directly by GitHub Pages; no application server is involved.

- Base URL: `https://termite-extant-isoptera.org/api/v1/`
- Version: `2026.11.21`, the same as the checklist data
- License: CC BY 4.0; citation below
- Authentication: none. Responses carry `Access-Control-Allow-Origin: *`, so browsers can read them cross-origin
- Caching: GitHub Pages CDN, `Cache-Control: max-age=600`

## Endpoints

| URL | Content |
| --- | --- |
| `/api/v1/index.json` | Version, license, citation, endpoint list and matching semantics |
| `/api/v1/names.json` | Name-to-taxon lookup: accepted names, synonyms, Chinese names, genera, families, subfamilies |
| `/api/v1/taxonomy.json` | Clade, family, subfamily and genus hierarchy with counts; no species detail |
| `/api/v1/species/<slug>.json` | One species or subspecies record; 3089 files |
| `/data/name-issues.json` | Name comparisons against GBIF, Catalogue of Life and BSF, plus manual decisions |

`<slug>` is derived from the scientific name: genus, species epithet and subspecies epithet joined by hyphens, all lowercase. For example `Coptotermes formosanus` is `coptotermes-formosanus`, and `Zootermopsis nevadensis nevadensis` is `zootermopsis-nevadensis-nevadensis`.

```bash
curl -s https://termite-extant-isoptera.org/api/v1/species/coptotermes-formosanus.json
```

## Name lookup

`names.json` is the complete lookup table. Fetch it once and query it locally. Static hosting has no server-side `?q=` endpoint; this file is the query layer.

Key normalization, in order: Unicode NFKC, trim, collapse internal whitespace to one space, lowercase. Latin names are case-insensitive. Chinese names match by exact characters, with no simplified/traditional conversion.

```python
import re
import unicodedata

def normalize(name):
    text = unicodedata.normalize("NFKC", name)
    return re.sub(r"\s+", " ", text).strip().lower()
```

Every value has a `match` field:

| `match` | Meaning | Key fields |
| --- | --- | --- |
| `accepted` | Accepted name (species or subspecies) | `slug`, `rank`, `page` |
| `synonym` | Synonym | `acceptedSlug`, `accepted` |
| `zh` | Chinese name | `slug`, `latin` |
| `genus` | Genus | `slug`, `page` |
| `family` | Family | `slug`, `page` |
| `subfamily` | Subfamily | `slug`, `page` |
| `ambiguous` | The key resolves to more than one taxon | `candidates` |

A missing key means the name is not in the checklist. `ambiguous` never picks a winner: `candidates` lists every match and leaves the choice to the caller. The Chinese name 阿马尼 maps to two Odontotermes species; that homonym exists in the site data and is reported, not hidden.

The table also carries two spelling variants: scientific name plus authorship (for example `coptotermes formosanus shiraki, 1909`), and the name with subgenus parentheses removed (so `coptotermes changtaiensis` resolves to `Coptotermes (Polycrinitermes) changtaiensis`).

## Species records

`/api/v1/species/<slug>.json` contains every field for one species or subspecies:

| Field | Description |
| --- | --- |
| `apiVersion`, `version` | API version and data version |
| `latin`, `zh`, `rank` | Scientific name, Chinese name, rank (`species` or `subspecies`) |
| `authorship` | Author and year |
| `isTypeSpecies` | Whether it is the type species of its genus |
| `typeLocality` | Type locality |
| `classification` | `clade`, `family`, `subfamily`, `genus`, each with `id`, `latin` and `zh`; `subfamily` is `null` when absent |
| `distribution` | Distribution in `zh` and `en`; species only |
| `synonyms` | Array with `asPublished`, `name`, `authorship`, `reference`, `note`, `typeLocality`, `localityAlignment` |
| `subspecies` | Array of subspecies; species only |
| `parent` | `latin`, `zh`, `slug` of the parent species; subspecies only |
| `authorityChecks` | Comparison entries against GBIF, CoL and BSF; present only when differences exist |
| `authorityReview` | Manual review record; present only when one exists |
| `pageUrl`, `apiUrl` | Human-readable page and API address |

`reference` is the page in the original publication; `asPublished` preserves the original spelling in the checklist. `localityAlignment` states whether the synonym type locality agrees with the accepted name.

## Classification index

`/api/v1/taxonomy.json` lists clades, families, subfamilies and genera with counts. It suits dropdowns, filters and summary tables. Species detail stays in the individual records and is not duplicated here.

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

## Nomenclature differences

`/data/name-issues.json` is the existing public copy of the comparison between this checklist and GBIF, Catalogue of Life and Blattodea Species File. Each entry has `source`, `group`, `kind`, `theirs`, `accepted`, `match` and `note`; `synonym_pairs` lists cross-database synonym pairs, and `species_authority` groups incoming synonyms by accepted name.

## Examples

### Python

```python
import json
import urllib.request

base = "https://termite-extant-isoptera.org/api/v1"
names = json.load(urllib.request.urlopen(base + "/names.json"))
hit = names.get("coptotermes formosanus")

if hit and hit["match"] == "accepted":
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

Fetch one record by slug:

```text
let
    Source = Json.Document(Web.Contents("https://termite-extant-isoptera.org/api/v1/species/coptotermes-formosanus.json")),
    Synonyms = Source[synonyms]
in
    Synonyms
```

Look up a name: fetch `names.json`, then read the key with `Record.Field`.

```text
let
    Names = Json.Document(Web.Contents("https://termite-extant-isoptera.org/api/v1/names.json")),
    Hit = Record.Field(Names, "coptotermes formosanus")
in
    Hit
```

For batch cleaning, download `names.json` once, turn it into a table and join your own name column to it. Do not request it per row.

### curl and jq

```bash
curl -s https://termite-extant-isoptera.org/api/v1/names.json \
  | jq '.["termes errabundus"]'
```

## Versioning and citation

`apiVersion` is `1`. Added fields keep the version; removed fields or changed semantics move to `/api/v2/` and v1 stays available. The data version follows checklist releases; `dateModified` in `index.json` records the last change.

Cite the API or the data with the dataset version DOI:

> Bennet Green. Extant Isoptera (termites): Latin scientific names and Chinese standard names, version 2026.11.21. Zenodo. https://doi.org/10.5281/zenodo.23646836

The license is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): copy, redistribute and adapt freely, with attribution.

## Errors and limits

- An unknown slug returns the GitHub Pages 404 page (HTML), not JSON. Check the HTTP status.
- There is no fuzzy matching, pinyin search or full-text search here; the site search page covers those.
- Name matching covers spellings recorded in the checklist. It does not correct typos or pull in synonyms absent from the data.
- `names.json` is about 2.9 MB uncompressed; HTTP transfer is gzip-compressed. Fetch it once for batch work.
