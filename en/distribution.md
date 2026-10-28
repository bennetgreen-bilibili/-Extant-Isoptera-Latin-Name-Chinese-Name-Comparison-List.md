---
layout: default
title: Distribution Maps — Extant Isoptera (Termites) Latin–Chinese Name Comparison List
description: "1° grid distribution maps for the 13 termite families, aggregated from GBIF occurrence records: method, record cap, sampling bias, GeoJSON data files, and the Leaflet base-map / tile usage policy."
lang: en
author: 班奈特格林 (Bennet Green)
date: 2026-10-17
keywords: [termites, Isoptera, distribution maps, GBIF, biogeography, grid map, sampling bias, GeoJSON, Leaflet]
permalink: /en/distribution/
---

{%- assign occ = site.data.occurrence_summary -%}

# Distribution maps

<p>This page shows all <strong>13 families</strong> of this checklist side by side. Each dot is one <strong>1° × 1° grid cell</strong> (roughly 111 km across); dot size and opacity scale with the number of <strong>GBIF occurrence records</strong> in that cell, and clicking a dot shows the exact count. Maps are only created when they scroll into view, so no tile is ever requested for a map you never reach.</p>

<p>Chinese names, scientific names and the family classification come from this checklist; the coordinates come from GBIF occurrence records (specimens and observations), not from range polygons. Date accessed: <strong>{% if occ %}{{ occ.meta.access_date }}{% else %}pending{% endif %}</strong>.</p>

## Method

<ol>
  <li><strong>Resolve the GBIF taxon key</strong> with <a href="https://api.gbif.org/v1/species/match?name=TERMITIDAE&amp;rank=FAMILY"><code>species/match?name=&lt;FAMILY&gt;&amp;rank=FAMILY</code></a> and take the canonical usageKey.</li>
  <li><strong>Pull georeferenced records</strong> from <a href="https://api.gbif.org/v1/occurrence/search"><code>occurrence/search</code></a> with <code>hasCoordinate=true</code>, <code>hasGeospatialIssue=false</code>, <code>limit=300</code>, paging through <code>offset</code>. At most <strong>900 records</strong> (3 pages) per family; only <code>decimalLatitude</code> / <code>decimalLongitude</code> (plus the country code for the summary) are kept.</li>
  <li><strong>Bin to a 1° grid</strong>: cell index = <code>floor(lat)</code>, <code>floor(lon)</code>; the feature coordinate is the cell centre (<code>floor + 0.5</code>, three decimals) and the record count in that cell becomes <code>n</code>.</li>
  <li><strong>Write GeoJSON</strong>: one <code>FeatureCollection</code> per family with <code>Point</code> features whose only property is <code>n</code>; the top-level <code>properties</code> record the family, GBIF key, record and cell counts, grid size, access date and source.</li>
</ol>

<p class="distribution-note">GBIF's backbone is not identical to this checklist: <strong>Hodotermopsidae</strong>, <strong>Psammotermitidae</strong>, <strong>Termitogetonidae</strong> and <strong>Heterotermitidae</strong> are folded into Archotermopsidae / Rhinotermitidae there. To stay consistent with this checklist those four families are built by <em>aggregating their genera</em> (match each genus name, pull its records, merge under the same 900-record cap). The trade-off is explicit: their records also appear in GBIF's host family, so those four maps overlap <a href="#rhinotermitidae">Rhinotermitidae</a> and <a href="#archotermopsidae">Archotermopsidae</a>.</p>

## How to read the maps

<ul>
  <li><strong>A dot is a cell, not a collecting event</strong>: a cell with 2 records and a cell with 200 both get one dot, distinguished by size and opacity.</li>
  <li><strong>Darker means more records</strong>, i.e. more people collected there and published to GBIF — not higher termite abundance.</li>
  <li><strong>Zoom is capped at level 9</strong>: the data is 1° only, so deeper zooms add no information and would only cost tiles.</li>
  <li>Scroll-wheel zoom is off by default (long page); use the +/− control when you need it.</li>
</ul>

<div class="distribution-caveat">
<strong>Caveats</strong>
<ul>
  <li><strong>Sampling bias</strong>: GBIF records concentrate in North America and Europe; tropical regions (especially Africa, Southeast Asia, South America) are sparse. An empty cell usually means nobody sampled there, not that no termite lives there.</li>
  <li><strong>Country-level gaps</strong>: many national collections are not digitised, so border-shaped holes are not range boundaries.</li>
  <li><strong>Not a range map</strong>: no niche modelling, no range inference, no filtering of adventive or indoor records.</li>
  <li><strong>Record cap</strong>: 900 records per family, taken in GBIF's stable response order — a reproducible sample, but not a random one.</li>
  <li><strong>It changes</strong>: GBIF adds and revises records daily; regenerating (see <code>--refresh</code>) changes the numbers.</li>
</ul>
</div>

## Family maps

<p>Each card shows the family's Chinese and scientific name, with record count, grid-cell count and the number of species in this checklist; the footer links to the GeoJSON file and to the GBIF taxon page.</p>

{% include distribution-map.html mode="page" %}

## Summary

{% if occ %}
<table>
<thead>
<tr>
  <th>Family</th>
  <th>GBIF key</th>
  <th class="num">Records</th>
  <th class="num">Cells</th>
  <th class="num">Species here</th>
  <th>Resolution</th>
</tr>
</thead>
<tbody>
{%- for f in occ.families %}
<tr>
  <td><a href="#{{ f.id }}">{{ f.zh }} <i class="latin">{{ f.latin }}</i></a></td>
  <td>{% if f.gbif_key %}<a href="{{ f.gbif_url }}" rel="noopener">{{ f.gbif_key }}</a>{% else %}genus aggregate{% endif %}</td>
  <td class="num">{{ f.records }}</td>
  <td class="num">{{ f.cells }}</td>
  <td class="num">{{ f.species }}</td>
  <td>{% if f.resolution == 'genus_aggregate' %}genus aggregate{% else %}family key{% endif %}</td>
</tr>
{%- endfor %}
<tr>
  <td><strong>Total</strong></td>
  <td>—</td>
  <td class="num"><strong>{{ occ.meta.records_families }}</strong></td>
  <td class="num"><strong>{{ occ.meta.cells_families }}</strong></td>
  <td class="num"><strong>3071</strong></td>
  <td>13 families</td>
</tr>
</tbody>
</table>
{% else %}
<p>Summary data has not been generated yet (<code>_data/occurrence_summary.json</code> is missing).</p>
{% endif %}

## Data files

<p>Every map is plain GeoJSON, ready for QGIS or any GeoJSON library; coordinates are <code>[longitude, latitude]</code> cell centres. File names follow the family id, which is also the anchor on this page.</p>

<ul>
{%- if occ -%}
{%- for f in occ.families %}
  <li><a href="{{ site.base_url }}/{{ f.file }}" download><code>{{ f.file }}</code></a> — {{ f.latin }}, {{ f.records }} records in {{ f.cells }} cells</li>
{%- endfor -%}
  <li><code>_data/occurrence_summary.json</code> — summary (records, cells, records by country, access date); every number on this page comes from it (a Jekyll data file, shipped with the repository, not published separately)</li>
  <li><a href="{{ site.base_url }}/en/data/">Structured data</a> — taxonomy tree and per-taxon JSON that goes with these maps</li>
{%- else %}
  <li>Data files pending.</li>
{%- endif %}
</ul>

<h3 id="genus-files">Genus-level files</h3>

{% if occ and occ.genera and occ.genera.size > 0 %}
<p>Genera with 12 or more species get their own map: <strong>{{ occ.genera.size }}</strong> files, each under 60 KB.</p>
<ul>
{%- for g in occ.genera %}
  <li><a href="{{ site.base_url }}/{{ g.file }}" download><code>{{ g.file }}</code></a> — <i class="latin">{{ g.latin }}</i> ({{ g.family_zh }}), {{ g.records }} records in {{ g.cells }} cells</li>
{%- endfor %}
</ul>
{% else %}
<p>This run did not produce genus-level files (genus level is optional; family level is always generated).</p>
{% endif %}

## Sources &amp; licence

<ul>
  <li><strong>Occurrence records</strong>: GBIF.org (Global Biodiversity Information Facility) via the <a href="https://api.gbif.org/v1/occurrence/search">GBIF Occurrence API</a>, accessed {% if occ %}{{ occ.meta.access_date }}{% endif %}. Per-record licences are shown on GBIF; cite per the <a href="https://www.gbif.org/citation-guidelines">GBIF citation guidelines</a> (dataset DOIs).</li>
  <li><strong>Backbone</strong>: GBIF Backbone Taxonomy (<a href="https://api.gbif.org/v1/species/match">species/match</a>); the family classification used here (Engel 2021 and later) is in the <a href="{{ site.base_url }}/en/list/">checklist</a>.</li>
  <li><strong>Base map</strong>: GBIF's public raster tiles (<a href="https://tile.gbif.org/">tile.gbif.org</a>, built from OpenMapTiles / OpenStreetMap data), with OpenStreetMap's own tiles as fallback; map data © OpenStreetMap contributors, see the <a href="https://www.openstreetmap.org/copyright">OSM copyright page</a>.</li>
  <li><strong>Renderer</strong>: Leaflet 1.9.4, BSD-2-Clause, self-hosted in <code>assets/vendor/leaflet/</code> — never loaded from a CDN at runtime.</li>
  <li><strong>Derived data</strong>: the GeoJSON and summary JSON on this page are produced by this site and released with it under CC BY 4.0.</li>
</ul>

<h3 id="tiles">Base map and tile usage policy</h3>

<p>Maps are lazy by design: a Leaflet instance and its tiles are created only when the map container enters the viewport. There is no prefetching, no server-side tile fetching, and zoom is capped at level 9 to bound the number of tiles. GBIF's public tile service is preferred (GBIF publishes these tiles for GBIF.org and API users), with OpenStreetMap's tile server as a fallback that respects the <a href="https://operations.osmfoundation.org/policies/tiles/">OSM tile usage policy</a> (attribution plus <code>referrerpolicy="no-referrer-when-downgrade"</code>). The full policy checklist is in <code>_tools/分布图与瓦片使用政策.md</code>.</p>

<p>Why family/genus rather than species level? A per-species map would mean <strong>3,071</strong> pages each pulling its own data and tile set — far beyond a reasonable load on public tile services, and pointless for 1° aggregates that are dominated by sampling effort anyway. Family/genus aggregation is the deliberate compromise.</p>

<h3 id="regenerate">Regenerating</h3>

<pre class="cite-text">python .github/workflows/build_occurrence_geojson.py --write --refresh</pre>

<p>Drop <code>--refresh</code> to reuse the cache in <code>_tmp/gbif_cache/</code> (a rerun never refetches); use <code>--check</code> to verify that the committed artefacts still match the script.</p>
