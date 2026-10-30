---
layout: default
title: Structured Data — Extant Isoptera (Termites) Latin–Chinese Name Comparison List
description: "Machine-readable structured data (JSON) for the extant Isoptera (termite) checklist: the entry point data/index.json holds the full taxonomic tree; the rest is split into 22 files by clade/family/subfamily."
lang: en
author: 班奈特格林 (Bennet Green)
date: 2026-10-17
version: 2026.10.30
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

{% include citation.html %}


## By clade / family

<ul>
  <li><a href="{{ site.base_url }}/data/mastotermitidae.json"><strong>Mastotermitidae</strong></a> — 1 genus · 1 species</li>
  <li><a href="{{ site.base_url }}/data/teletisoptera.json"><strong>Teletisoptera</strong> (Archotermopsidae / Hodotermitidae / Hodotermopsidae / Stolotermitidae)</a> — 4 families · 8 genera · 37 species</li>
  <li><a href="{{ site.base_url }}/data/kalotermitidae.json"><strong>Kalotermitidae</strong></a> — 23 genera · 479 species</li>
  <li><a href="{{ site.base_url }}/data/neoisoptera-excl-termitidae.json"><strong>Neoisoptera excl. Termitidae</strong> (Psammotermitidae / Rhinotermitidae / Serritermitidae / Stylotermitidae / Termitogetonidae / Heterotermitidae)</a> — 6 families · 14 genera · 358 species</li>
</ul>

## Termitidae (18 subfamilies, one file each)

<ul>
  <li><a href="{{ site.base_url }}/data/termitidae/amitermitinae.json">Amitermitinae</a> — 14 genera · 193 species</li>
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
  <li><a href="{{ site.base_url }}/data/termitidae/nasutitermitinae.json">Nasutitermitinae</a> — 81 genera · 607 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/neocapritermitinae.json">Neocapritermitinae</a> — 3 genera · 20 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/promirotermitinae.json">Promirotermitinae</a> — 2 genera · 39 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/protohamitermitinae.json">Protohamitermitinae</a> — 2 genera · 2 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/sphaerotermitinae.json">Sphaerotermitinae</a> — 1 genus · 1 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/syntermitinae.json">Syntermitinae</a> — 22 genera · 105 species</li>
  <li><a href="{{ site.base_url }}/data/termitidae/termitinae.json">Termitinae</a> — 23 genera · 106 species</li>
</ul>

## Search index &amp; programmatic access

<ul>
  <li><a href="{{ site.base_url }}/search-index.json"><code>search-index.json</code></a> — checklist search index (pinyin / traditional Chinese / synonyms, with the family field; generated by <code>build_search_index.py</code>)</li>
  <li><a href="{{ site.base_url }}/data/name-issues.json"><code>data/name-issues.json</code></a> — name discrepancies and review queue (issue type, external record links, match confidence; <code>synonym_pairs</code> gives, pair by pair, the relation between our name and the accepted name an external database claims (synonym / combination difference), the receiving-name direction (external / our name / undecided), each database's verdict and the recording status; <code>species_authority</code> powers the species-page lookup; also as <a href="{{ site.base_url }}/downloads/isoptera-name-issues.csv">CSV</a> and a <a href="{{ site.base_url }}/downloads/isoptera-synonym-pairs.csv">per-pair table</a>)</li>
  <li><a href="{{ site.base_url }}/sitemap.txt">sitemap.txt</a> — every URL on the site, one per line</li>
  <li>Subscribe: <a href="{{ site.base_url }}/feed.xml">feed.xml (Atom)</a> · <a href="{{ site.base_url }}/feed.json">feed.json (JSON Feed)</a> · <a href="{{ site.base_url }}/changelog.atom">changelog.atom (release changelog)</a></li>
  <li>Search discovery: <a href="{{ site.base_url }}/opensearch.xml">opensearch.xml</a> (add this site as a browser search engine; query URL <code>/search/?q=…</code>)</li>

<h2 id="authority">External authority cross-check</h2>

<p>The "Other databases" block on every species page is generated by <code>.github/workflows/build_authority_links.py</code>, which queries the
<a href="https://api.gbif.org/v1/species/match">GBIF Backbone API</a>,
<a href="https://api.checklistbank.org/">Catalogue of Life ChecklistBank API</a> and
<a href="https://query.wikidata.org/">Wikidata SPARQL</a> (P225 taxon name) by scientific name. It only adds links and consistency hints &mdash; <strong>the checklist data itself is never modified</strong>.
{%- if site.data.authority_links %}{%- assign A = site.data.authority_links %}{%- assign C = A.meta.counts %}
Current cache (fetched {{ A.meta.generated | slice: 0, 10 }}): of <strong>{{ C.total }}</strong> names, <strong>{{ C.gbif_linked }}</strong> link to GBIF ({{ C.gbif_accepted }} accepted, {{ C.gbif_synonym }} synonyms), <strong>{{ C.col_linked }}</strong> link to Catalogue of Life, <strong>{{ C.wikidata }}</strong> have a Wikidata item; <strong>{{ C.consistent }}</strong> agree with both accepted names, <strong>{{ C.flagged }}</strong> carry a hint.{%- endif %}</p>

<ul>
  <li><a href="{{ site.base_url }}/downloads/isoptera-authority-crossref.csv"><code>isoptera-authority-crossref.csv</code></a> &mdash; the cross-check table (GBIF / Catalogue of Life IDs, statuses, accepted names, Wikidata QIDs and flags) for download and manual review.</li>
  <li>Linking rule: GBIF links are emitted only when <code>matchType=EXACT</code> (or FUZZY with confidence &ge; 95) and the rank is species/subspecies, so higher-rank or low-confidence matches are never passed off as this taxon.</li>
  <li>World catalogue: Blattodea Species File (<a href="https://cockroach.speciesfile.org">cockroach.speciesfile.org</a>, now including the former Isoptera Species File, built with TaxonWorks / TaxonPages){% if site.data.bsf_links %}{% assign B = site.data.bsf_links.meta.counts %} &mdash; auto-matched <strong>{{ B.valid }}</strong> valid names and <strong>{{ B.synonym }}</strong> synonyms; <strong>{{ B.ambiguous }}</strong> ambiguous and <strong>{{ B.missing }}</strong> not found still need review. Entries on species pages say "auto-matched" until a human confirms them.{% endif %}</li>
  <li>Structured data: species pages also emit schema.org <code>Taxon</code> + <code>BreadcrumbList</code> JSON-LD whose <code>sameAs</code> points at these external records and whose <code>isPartOf</code> links to the site Dataset entity.</li>
  <li><a href="{{ site.base_url }}/data/references.json"><code>data/references.json</code></a> &mdash; Crossref-enriched data for the 77 references (DOIs, Crossref fields, GB/T 7714-style / APA / Vancouver citations, BibTeX / RIS / CSL-JSON).</li>
</ul>

</ul>
