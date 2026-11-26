---
layout: default
title: "API v1: JSON estático del catálogo"
description: "Consulta el catálogo de Isoptera extant por nombre latino, nombre chino, sinónimo, género o familia: tabla de nombres, árbol de clasificación y 3089 registros de especies, servidos como JSON estático con CORS y sin clave."
lang: es
author: 班奈特格林
date: 2026-11-26
version: 2026.11.21
keywords: [termitas, Isoptera, API, JSON, taxonomía, nomenclatura]
permalink: /es/api/
single_lang: true
---

# API v1

Acceso JSON de solo lectura al catálogo por nombre, nivel de clasificación o slug. Los archivos se generan durante la compilación y GitHub Pages los sirve directamente; no hay servidor de aplicaciones.

- URL base: `https://termite-extant-isoptera.org/api/v1/`
- Versión: `2026.11.21`, la misma del catálogo
- Licencia: CC BY 4.0; cita más abajo
- Autenticación: ninguna. Las respuestas incluyen `Access-Control-Allow-Origin: *`, de modo que el navegador puede leerlas entre dominios
- Caché: CDN de GitHub Pages, `Cache-Control: max-age=600`

## Endpoints

| URL | Contenido |
| --- | --- |
| `/api/v1/index.json` | Versión, licencia, cita, lista de endpoints y semántica de coincidencias |
| `/api/v1/names.json` | Tabla nombre a taxón: nombres aceptados, sinónimos, nombres chinos, géneros, familias y subfamilias |
| `/api/v1/taxonomy.json` | Jerarquía de clados, familias, subfamilias y géneros con recuentos; sin detalle de especies |
| `/api/v1/species/<slug>.json` | Registro completo de una especie o subespecie; 3089 archivos |
| `/data/name-issues.json` | Comparación con GBIF, Catalogue of Life y BSF, más decisiones manuales |

El `<slug>` se deriva del nombre científico: género, epíteto específico y epíteto subespecífico unidos por guiones, en minúsculas. Por ejemplo, `Coptotermes formosanus` es `coptotermes-formosanus` y `Zootermopsis nevadensis nevadensis` es `zootermopsis-nevadensis-nevadensis`.

```bash
curl -s https://termite-extant-isoptera.org/api/v1/species/coptotermes-formosanus.json
```

## Búsqueda por nombre

`names.json` es la tabla completa. Se descarga una vez y se consulta localmente. El alojamiento estático no tiene un endpoint `?q=`; este archivo es la capa de consulta.

Normalización de claves, en orden: NFKC de Unicode, recorte de espacios, colapso de espacios internos a uno solo y minúsculas. Los nombres latinos no distinguen mayúsculas. Los nombres chinos se comparan carácter por carácter, sin conversión entre simplificado y tradicional.

```python
import re
import unicodedata

def normalize(name):
    text = unicodedata.normalize("NFKC", name)
    return re.sub(r"\s+", " ", text).strip().lower()
```

Cada valor trae un campo `match`:

| `match` | Significado | Campos clave |
| --- | --- | --- |
| `accepted` | Nombre aceptado (especie o subespecie) | `slug`, `rank`, `page` |
| `synonym` | Sinónimo | `acceptedSlug`, `accepted` |
| `zh` | Nombre chino | `slug`, `latin` |
| `genus` | Género | `slug`, `page` |
| `family` | Familia | `slug`, `page` |
| `subfamily` | Subfamilia | `slug`, `page` |
| `ambiguous` | La clave corresponde a más de un taxón | `candidates` |

Una clave ausente indica que el nombre no está en el catálogo. `ambiguous` nunca elige por su cuenta: `candidates` enumera todas las coincidencias y deja la decisión a quien llama. El nombre chino 阿马尼 corresponde a dos especies de Odontotermes; ese homónimo existe en los datos y se informa, no se oculta.

La tabla incluye dos variantes de escritura: nombre científico con autoría (por ejemplo `coptotermes formosanus shiraki, 1909`) y el nombre sin paréntesis de subgénero (así `coptotermes changtaiensis` resuelve a `Coptotermes (Polycrinitermes) changtaiensis`).

## Registros de especies

`/api/v1/species/<slug>.json` contiene todos los campos de una especie o subespecie:

| Campo | Descripción |
| --- | --- |
| `apiVersion`, `version` | Versión de la API y versión de los datos |
| `latin`, `zh`, `rank` | Nombre científico, nombre chino y rango (`species` o `subspecies`) |
| `authorship` | Autor y año |
| `isTypeSpecies` | Si es la especie tipo de su género |
| `typeLocality` | Localidad tipo |
| `classification` | `clade`, `family`, `subfamily`, `genus`, cada uno con `id`, `latin` y `zh`; `subfamily` es `null` si falta |
| `distribution` | Distribución en `zh` y `en`; solo especies |
| `synonyms` | Matriz con `asPublished`, `name`, `authorship`, `reference`, `note`, `typeLocality`, `localityAlignment` |
| `subspecies` | Matriz de subespecies; solo especies |
| `parent` | `latin`, `zh`, `slug` de la especie parental; solo subespecies |
| `authorityChecks` | Entradas de comparación con GBIF, CoL y BSF; solo si hay diferencias |
| `authorityReview` | Registro de revisión manual; solo si existe |
| `pageUrl`, `apiUrl` | Página legible y dirección de la API |

`reference` es la página de la publicación original; `asPublished` conserva la escritura original del catálogo. `localityAlignment` indica si la localidad tipo del sinónimo coincide con la del nombre aceptado.

## Índice de clasificación

`/api/v1/taxonomy.json` enumera clados, familias, subfamilias y géneros con sus recuentos. Sirve para menús, filtros y tablas resumen. El detalle de especies queda en cada registro y no se duplica aquí.

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

## Diferencias de nomenclatura

`/data/name-issues.json` es la copia pública existente de la comparación entre este catálogo y GBIF, Catalogue of Life y Blattodea Species File. Cada entrada tiene `source`, `group`, `kind`, `theirs`, `accepted`, `match` y `note`; `synonym_pairs` reúne pares de sinónimos entre bases y `species_authority` agrupa los sinónimos entrantes por nombre aceptado.

## Ejemplos

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

Obtener un registro por slug:

```text
let
    Source = Json.Document(Web.Contents("https://termite-extant-isoptera.org/api/v1/species/coptotermes-formosanus.json")),
    Synonyms = Source[synonyms]
in
    Synonyms
```

Buscar un nombre: descargar `names.json` y leer la clave con `Record.Field`.

```text
let
    Names = Json.Document(Web.Contents("https://termite-extant-isoptera.org/api/v1/names.json")),
    Hit = Record.Field(Names, "coptotermes formosanus")
in
    Hit
```

Para limpieza por lotes, descargue `names.json` una vez, conviértalo en tabla y únalo a su columna de nombres. No lo solicite fila por fila.

### curl y jq

```bash
curl -s https://termite-extant-isoptera.org/api/v1/names.json \
  | jq '.["termes errabundus"]'
```

## Versión y cita

`apiVersion` es `1`. Agregar campos no cambia la versión; quitar campos o cambiar su semántica pasa a `/api/v2/` y v1 sigue disponible. La versión de los datos acompaña a cada publicación del catálogo; `dateModified` en `index.json` registra el último cambio.

Cite la API o los datos con el DOI de la versión del conjunto de datos:

> Bennet Green. Extant Isoptera (termites): Latin scientific names and Chinese standard names, version 2026.11.21. Zenodo. https://doi.org/10.5281/zenodo.23646836

La licencia es [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): copiar, redistribuir y adaptar es libre con atribución.

## Errores y límites

- Un slug inexistente devuelve la página 404 de GitHub Pages (HTML), no JSON. Compruebe el estado HTTP.
- Aquí no hay búsqueda difusa, búsqueda por pinyin ni búsqueda de texto completo; la página de búsqueda del sitio cubre esos casos.
- La coincidencia de nombres cubre las grafías registradas en el catálogo. No corrige errores de escritura ni añade sinónimos ausentes de los datos.
- `names.json` ocupa unos 2.9 MB sin comprimir; la transferencia HTTP usa gzip. Descárguelo una sola vez para trabajo por lotes.
