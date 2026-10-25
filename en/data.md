---
layout: default
title: Structured Data — Extant Isoptera (Termites) Latin–Chinese Name Comparison List
description: "Machine-readable structured data (JSON) for the extant Isoptera (termite) checklist: the entry point data/index.json holds the full taxonomic tree; the rest is split into 22 files by clade/family/subfamily."
lang: en
author: 班奈特格林 (Bennet Green)
date: 2026-10-17
version: 2026.10.17
keywords: [termites, Isoptera, structured data, JSON, checklist, taxonomy, Termitidae]
permalink: /en/data/
---

# Structured Data

<p>Machine-readable data is split by taxon; the entry point is <a href="{{ site.base_url }}/data/index.json"><code>data/index.json</code></a> (full taxonomic tree with 6 clades, 13 families, 18 subfamilies, plus the complete file manifest). All <strong>22 JSON files</strong> below are independently accessible and downloadable.</p>

## Archived dataset &amp; DOI

<p>All checklist records are also packaged as a citable archived dataset (<strong>3,071 records</strong>: one-row-per-taxon CSV, taxonomy JSON, synonym table, reference list, plus a DataCite 4.6 record and a CC BY 4.0 license). Download:
<a href="{{ site.base_url }}/{{ site.dataset.archive_file }}"><code>{{ site.dataset.archive_file }}</code></a>.</p>

<ul>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-checklist.csv"><code>dataset/data/isoptera-checklist.csv</code></a> — 3,071 taxon records (Chinese name, type locality, distribution, synonyms)</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-taxonomy.json"><code>dataset/data/isoptera-taxonomy.json</code></a> — full taxonomy tree (clade–family–subfamily–genus–species/subspecies)</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-synonyms.csv"><code>dataset/data/isoptera-synonyms.csv</code></a> — synonym table with type localities and alignment status</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-counts.csv"><code>dataset/data/isoptera-counts.csv</code></a> — counts by family/subfamily</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-references.csv"><code>dataset/data/isoptera-references.csv</code></a> — 77 references (DOIs where available)</li>
  <li><a href="{{ site.base_url }}/dataset/datapackage.json"><code>datapackage.json</code></a> — field dictionary (Frictionless Data Package)</li>
  <li><a href="{{ site.base_url }}/dataset/datacite-metadata.xml"><code>datacite-metadata.xml</code></a> — DataCite metadata record</li>
  <li><a href="{{ site.base_url }}/dataset/README.md">Dataset README</a> — provenance, methods, fields, limitations, citation</li>
</ul>

{% if site.dataset.doi %}<p><strong>DOI (version {{ site.dataset.version }})</strong>: <a href="https://doi.org/{{ site.dataset.doi }}">{{ site.dataset.doi }}</a>{% if site.dataset.concept_doi %}　<strong>Concept DOI (always latest version)</strong>: <a href="https://doi.org/{{ site.dataset.concept_doi }}">{{ site.dataset.concept_doi }}</a>{% endif %}</p>

<p><strong>Citation (APA)</strong>: Bennet Green. (2026). <i>Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names</i> (Version {{ site.dataset.version }}) [Data set]. {{ site.dataset.publisher }}. <a href="https://doi.org/{{ site.dataset.doi }}">https://doi.org/{{ site.dataset.doi }}</a></p>{% else %}<p><strong>Citation (APA)</strong>: Bennet Green. (2026). <i>Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names</i> (Version {{ site.dataset.version }}) [Data set]. <a href="{{ site.base_url }}/">{{ site.base_url }}/</a></p>

<p>The archive is prepared for DOI deposition (README, DataCite metadata, CC BY 4.0 license and SHA-256 checksums included); the permanent DOI will be shown in this section and in the site footer once minted.</p>{% endif %}

## By clade / family

<ul>
  <li><a href="{{ site.base_url }}/data/mastotermitidae.json"><strong>Mastotermitidae</strong></a> — 1 genus · 1 species</li>
  <li><a href="{{ site.base_url }}/data/teletisoptera.json"><strong>Teletisoptera</strong> (Archotermopsidae / Hodotermitidae / Hodotermopsidae / Stolotermitidae)</a> — 4 families · 8 genera · 37 species</li>
  <li><a href="{{ site.base_url }}/data/kalotermitidae.json"><strong>Kalotermitidae</strong></a> — 23 genera · 479 species</li>
  <li><a href="{{ site.base_url }}/data/neoisoptera-excl-termitidae.json"><strong>Neoisoptera excl. Termitidae</strong> (Psammotermitidae / Rhinotermitidae / Serritermitidae / Stylotermitidae / Termitogetonidae / Heterotermitidae)</a> — 6 families · 14 genera · 359 species</li>
</ul>

## Termitidae (18 subfamilies, one file each)

<ul>
  <li><a href="{{ site.base_url }}/data/termitidae/amitermitinae.json">Amitermitinae</a> — 14 genera · 194 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/apicotermitinae.json">Apicotermitinae</a> — 65 genera · 237 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/crepititermitinae.json">Crepititermitinae</a> — 1 genus · 1 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/cubitermitinae.json">Cubitermitinae</a> — 28 genera · 142 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/cylindrotermitinae.json">Cylindrotermitinae</a> — 2 genera · 9 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/engelitermitinae.json">Engelitermitinae</a> — 1 genus · 1 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/foraminitermitinae.json">Foraminitermitinae</a> — 3 genera · 10 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/forficulitermitinae.json">Forficulitermitinae</a> — 1 genus · 1 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/macrotermitinae.json">Macrotermitinae</a> — 12 genera · 373 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/microcerotermitinae.json">Microcerotermitinae</a> — 2 genera · 150 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/mirocapritermitinae.json">Mirocapritermitinae</a> — 14 genera · 133 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/nasutitermitinae.json">Nasutitermitinae</a> — 81 genera · 608 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/neocapritermitinae.json">Neocapritermitinae</a> — 3 genera · 20 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/promirotermitinae.json">Promirotermitinae</a> — 2 genera · 39 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/protohamitermitinae.json">Protohamitermitinae</a> — 2 genera · 2 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/sphaerotermitinae.json">Sphaerotermitinae</a> — 1 genus · 1 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/syntermitinae.json">Syntermitinae</a> — 22 genera · 105 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/termitinae.json">Termitinae</a> — 23 genera · 106 species</li>
</ul>

## Search index

<ul>
  <li><a href="{{ site.base_url }}/search-index.json">Search index (search-index.json)</a> for the search box</li>
</ul>
