---
layout: default
title: "Datos estructurados — isópteros (termitas) actuales: lista comparativa latín–chino"
description: "Datos estructurados legibles por máquina (JSON) del listado de isópteros (termitas) actuales: el punto de entrada data/index.json contiene el árbol taxonómico completo; el resto está dividido en 22 archivos por clado/familia/subfamilia."
lang: es
author: 班奈特格林 (Bennet Green)
date: 2026-10-17
version: 2026.10.30
keywords: [termitas, Isoptera, datos estructurados, JSON, listado, taxonomía, Termitidae]
permalink: /es/data/
---

# Datos estructurados

<p>Los datos legibles por máquina están divididos por taxón; el punto de entrada es <a href="{{ site.base_url }}/data/index.json"><code>data/index.json</code></a> (árbol taxonómico completo con 6 clados, 13 familias y 18 subfamilias, además del manifiesto completo de archivos). Los <strong>22 archivos JSON</strong> siguientes son accesibles y descargables de forma independiente.</p>

## Conjunto de datos archivado y DOI

<p>Todos los registros del listado están además empaquetados como un conjunto de datos archivado y citable (<strong>3068 registros</strong>: CSV con una fila por taxón, JSON de taxonomía, tabla de sinónimos, lista de referencias, más un registro DataCite 4.6 y una licencia CC BY 4.0). Descargar:
<a href="{{ site.base_url }}/{{ site.dataset.archive_file }}"><code>{{ site.dataset.archive_file }}</code></a>.</p>

<ul>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-checklist.csv"><code>dataset/data/isoptera-checklist.csv</code></a> — 3068 registros de taxones (nombre chino, localidad tipo, distribución, sinónimos)</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-taxonomy.json"><code>dataset/data/isoptera-taxonomy.json</code></a> — árbol taxonómico completo (clado–familia–subfamilia–género–especie/subespecie)</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-synonyms.csv"><code>dataset/data/isoptera-synonyms.csv</code></a> — tabla de sinónimos con localidades tipo y estado de alineación</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-counts.csv"><code>dataset/data/isoptera-counts.csv</code></a> — recuentos por familia/subfamilia</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-references.csv"><code>dataset/data/isoptera-references.csv</code></a> — 77 referencias (con DOI cuando está disponible)</li>
  <li><a href="{{ site.base_url }}/dataset/datapackage.json"><code>datapackage.json</code></a> — diccionario de campos (Frictionless Data Package)</li>
  <li><a href="{{ site.base_url }}/dataset/datacite-metadata.xml"><code>datacite-metadata.xml</code></a> — registro de metadatos DataCite</li>
  <li><a href="{{ site.base_url }}/dataset/README.md">README del conjunto de datos</a> — procedencia, métodos, campos, limitaciones, citación</li>
</ul>

{% if site.dataset.doi %}<p><strong>DOI (versión {{ site.dataset.version }})</strong>: <a href="https://doi.org/{{ site.dataset.doi }}">{{ site.dataset.doi }}</a>{% if site.dataset.concept_doi %}　<strong>DOI de concepto (siempre la última versión)</strong>: <a href="https://doi.org/{{ site.dataset.concept_doi }}">{{ site.dataset.concept_doi }}</a>{% endif %}</p>

<p><strong>Citación (APA)</strong>: Bennet Green. (2026). <i>Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names</i> (Versión {{ site.dataset.version }}) [Conjunto de datos]. {{ site.dataset.publisher }}. <a href="https://doi.org/{{ site.dataset.doi }}">https://doi.org/{{ site.dataset.doi }}</a></p>{% else %}<p><strong>Citación (APA)</strong>: Bennet Green. (2026). <i>Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names</i> (Versión {{ site.dataset.version }}) [Conjunto de datos]. <a href="{{ site.base_url }}/">{{ site.base_url }}/</a></p>

<p>El archivo está preparado para el depósito del DOI (incluye README, metadatos DataCite, licencia CC BY 4.0 y sumas de verificación SHA-256); el DOI permanente aparecerá en esta sección y en el pie del sitio una vez asignado.</p>{% endif %}

{% include citation.html %}


## Por clado / familia

<ul>
  <li><a href="{{ site.base_url }}/data/mastotermitidae.json"><strong>Mastotermitidae</strong></a> — 1 género · 1 especie</li>
  <li><a href="{{ site.base_url }}/data/teletisoptera.json"><strong>Teletisoptera</strong> (Archotermopsidae / Hodotermitidae / Hodotermopsidae / Stolotermitidae)</a> — 4 familias · 8 géneros · 37 especies</li>
  <li><a href="{{ site.base_url }}/data/kalotermitidae.json"><strong>Kalotermitidae</strong></a> — 23 géneros · 479 especies</li>
  <li><a href="{{ site.base_url }}/data/neoisoptera-excl-termitidae.json"><strong>Neoisoptera excl. Termitidae</strong> (Psammotermitidae / Rhinotermitidae / Serritermitidae / Stylotermitidae / Termitogetonidae / Heterotermitidae)</a> — 6 familias · 14 géneros · 358 especies</li>
</ul>

## Termitidae (18 subfamilias, un archivo por subfamilia)

<ul>
  <li><a href="{{ site.base_url }}/data/termitidae/amitermitinae.json">Amitermitinae</a> — 14 géneros · 193 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/apicotermitinae.json">Apicotermitinae</a> — 65 géneros · 237 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/crepititermitinae.json">Crepititermitinae</a> — 1 género · 1 especie</li>
  <li><a href="{{ site.base_url }}/data/termitidae/cubitermitinae.json">Cubitermitinae</a> — 28 géneros · 142 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/cylindrotermitinae.json">Cylindrotermitinae</a> — 2 géneros · 9 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/engelitermitinae.json">Engelitermitinae</a> — 1 género · 1 especie</li>
  <li><a href="{{ site.base_url }}/data/termitidae/foraminitermitinae.json">Foraminitermitinae</a> — 3 géneros · 10 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/forficulitermitinae.json">Forficulitermitinae</a> — 1 género · 1 especie</li>
  <li><a href="{{ site.base_url }}/data/termitidae/macrotermitinae.json">Macrotermitinae</a> — 12 géneros · 373 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/microcerotermitinae.json">Microcerotermitinae</a> — 2 géneros · 150 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/mirocapritermitinae.json">Mirocapritermitinae</a> — 14 géneros · 132 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/nasutitermitinae.json">Nasutitermitinae</a> — 81 géneros · 607 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/neocapritermitinae.json">Neocapritermitinae</a> — 3 géneros · 20 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/promirotermitinae.json">Promirotermitinae</a> — 2 géneros · 39 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/protohamitermitinae.json">Protohamitermitinae</a> — 2 géneros · 2 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/sphaerotermitinae.json">Sphaerotermitinae</a> — 1 género · 1 especie</li>
  <li><a href="{{ site.base_url }}/data/termitidae/syntermitinae.json">Syntermitinae</a> — 22 géneros · 105 especies</li>
  <li><a href="{{ site.base_url }}/data/termitidae/termitinae.json">Termitinae</a> — 23 géneros · 106 especies</li>
</ul>

## Índice de búsqueda y acceso programático

<ul>
  <li><a href="{{ site.base_url }}/search-index.json"><code>search-index.json</code></a> — índice de búsqueda del listado (pinyin / chino tradicional / sinónimos, con el campo de familia; generado por <code>build_search_index.py</code>)</li>
  <li><a href="{{ site.base_url }}/data/name-issues.json"><code>data/name-issues.json</code></a> — discrepancias de nombres y cola de revisión (tipo de incidencia, enlaces a registros externos, confianza del cotejo; <code>synonym_pairs</code> da, par a par, la relación entre nuestro nombre y el nombre aceptado que indica la base externa (sinónimo / diferencia de combinación), la dirección del nombre receptor (externo / nuestro / indeterminada), el veredicto de cada base y el estado de registro; <code>species_authority</code> alimenta la consulta en las páginas de especie; también en <a href="{{ site.base_url }}/downloads/isoptera-name-issues.csv">CSV</a> y en una <a href="{{ site.base_url }}/downloads/isoptera-synonym-pairs.csv">tabla por pares</a>)</li>
  <li><a href="{{ site.base_url }}/sitemap.txt">sitemap.txt</a> — todas las URL del sitio, una por línea</li>
  <li>Suscripción: <a href="{{ site.base_url }}/feed.xml">feed.xml (Atom)</a> · <a href="{{ site.base_url }}/feed.json">feed.json (JSON Feed)</a> · <a href="{{ site.base_url }}/changelog.atom">changelog.atom (historial de versiones)</a></li>
  <li>Descubrimiento de búsqueda: <a href="{{ site.base_url }}/opensearch.xml">opensearch.xml</a> (añadir el sitio como buscador del navegador; URL de consulta <code>/search/?q=…</code>)</li>

<h2 id="authority">Cotejo con bases de datos externas</h2>

<p>El bloque «Otras bases de datos» de cada página de especie lo genera <code>.github/workflows/build_authority_links.py</code> consultando la
<a href="https://api.gbif.org/v1/species/match">API de GBIF Backbone</a>,
<a href="https://api.checklistbank.org/">API de Catalogue of Life (ChecklistBank)</a> y
<a href="https://query.wikidata.org/">Wikidata SPARQL</a> (P225) por nombre científico. Solo añade enlaces y avisos de consistencia: <strong>los datos de la lista no se modifican</strong>.
{%- if site.data.authority_links %}{%- assign A = site.data.authority_links %}{%- assign C = A.meta.counts %}
Caché actual (consultada el {{ A.meta.generated | slice: 0, 10 }}): de <strong>{{ C.total }}</strong> nombres, <strong>{{ C.gbif_linked }}</strong> enlazan con GBIF ({{ C.gbif_accepted }} aceptados, {{ C.gbif_synonym }} sinónimos), <strong>{{ C.col_linked }}</strong> con Catalogue of Life y <strong>{{ C.wikidata }}</strong> tienen elemento en Wikidata; <strong>{{ C.consistent }}</strong> coinciden con ambos nombres aceptados y <strong>{{ C.flagged }}</strong> llevan un aviso.{%- endif %}</p>

<ul>
  <li><a href="{{ site.base_url }}/downloads/isoptera-authority-crossref.csv"><code>isoptera-authority-crossref.csv</code></a> &mdash; tabla de cotejo (ID de GBIF / Catalogue of Life, estados, nombres aceptados, QID de Wikidata y marcas) para descargar y revisar.</li>
  <li>Regla de enlace: GBIF solo se enlaza cuando <code>matchType=EXACT</code> (o FUZZY con confianza &ge; 95) y el rango es especie/subespecie.</li>
  <li>Catálogo mundial: Blattodea Species File (<a href="https://cockroach.speciesfile.org">cockroach.speciesfile.org</a>, que absorbió el antiguo Isoptera Species File){% if site.data.bsf_links %}{% assign B = site.data.bsf_links.meta.counts %} &mdash; <strong>{{ B.valid }}</strong> nombres válidos y <strong>{{ B.synonym }}</strong> sinónimos emparejados automáticamente; <strong>{{ B.ambiguous }}</strong> dudosos y <strong>{{ B.missing }}</strong> no encontrados.{% endif %}</li>
  <li>Datos estructurados: las páginas de especie emiten JSON-LD schema.org <code>Taxon</code> + <code>BreadcrumbList</code> con <code>sameAs</code> a estos registros y <code>isPartOf</code> al Dataset del sitio.</li>
  <li><a href="{{ site.base_url }}/data/references.json"><code>data/references.json</code></a> &mdash; datos enriquecidos con Crossref de las 77 referencias (DOI, campos de Crossref, citas GB/T 7714 / APA / Vancouver, BibTeX / RIS / CSL-JSON).</li>
</ul>

</ul>
