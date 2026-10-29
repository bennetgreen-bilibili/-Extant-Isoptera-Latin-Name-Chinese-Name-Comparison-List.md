---
layout: default
title: Name discrepancies and review queue — Extant Isoptera (Termites) Latin–Chinese Name Comparison List
description: "A filterable list of name-level mismatches between this checklist and GBIF Backbone, Catalogue of Life and the Blattodea Species File: external synonyms, ambiguous matches and coverage gaps, with CSV download."
lang: en
author: 班奈特格林 (Bennet Green)
date: 2026-10-29
version: 2026.10.17
keywords: [termites, Isoptera, checklist, name discrepancies, taxonomy review, GBIF, Catalogue of Life, Blattodea Species File]
permalink: /en/list/name-issues/
pagefind: true
---
{%- assign D = site.data.name_issues -%}
{%- assign C = D.meta.counts -%}
<nav class="ni-crumbs" aria-label="Breadcrumb"><a href="{{ site.base_url }}/en/">Home</a> › <a href="{{ site.base_url }}/en/list/">List</a> › Name discrepancies</nav>
<h1 class="ni-title">Name discrepancies and review queue<span class="ni-title-alt" lang="zh-CN">命名差异与待核对</span></h1>
<p class="ni-lead">This page turns the cached name-matching results between this checklist and three external authorities — GBIF Backbone, Catalogue of Life (ChecklistBank) and the Blattodea Species File (BSF) — into a filterable list. Only entries that need human attention are shown: <b>{{ C.total }}</b> rows covering <b>{{ C.species_with_issue }}</b> species/subspecies out of {{ C.species_total }} checklist records. The synonyms behind each <em>name conflict</em> are also regrouped under the <strong>accepted name</strong> the external database uses (<a href="#synonyms">synonyms grouped by accepted name</a>): <b>{{ C.synonym_groups }}</b> accepted names, <b>{{ C.synonym_pairs }}</b> synonym→accepted pairs, and <b>{{ C.synonym_groups_in_site }}</b> of those accepted names are also listed separately in this checklist. <strong>Nothing here changes the checklist data</strong>; matching rules are documented on the <a href="{{ site.base_url }}/en/data/">data page</a>.</p>
<div class="ni-legend"><span><span class="ni-badge is-conflict">Name conflict</span>the external database treats our name as a synonym and gives its accepted name — decide whether to rename, annotate or keep ours.</span><span><span class="ni-badge is-match">Uncertain match</span>fuzzy match, or several candidate OTUs share the name, so the script cannot decide automatically.</span><span><span class="ni-badge is-gap">Coverage gap</span>only a higher taxon matched, the name is absent, or it is not found in the BSF — this affects cross-links.</span></div>
<div class="ni-summary"><span class="ni-stat"><b>{{ C.total }}</b> rows to review</span><span class="ni-stat"><b>{{ C.by_group.conflict }}</b> name conflicts → {{ C.synonym_groups }} accepted names</span><span class="ni-stat"><b>{{ C.synonym_groups_in_site }}</b> accepted names also listed here</span><span class="ni-stat"><b>{{ C.by_group.match }}</b> uncertain matches</span><span class="ni-stat"><b>{{ C.by_group.gap }}</b> coverage gaps</span><span class="ni-stat"><b>{{ C.species_with_issue }}</b> taxa involved</span><span class="ni-stat">BSF manually verified: <b>{{ C.bsf_verified }}</b></span></div>
<div class="ni-app" id="ni-root" data-page-size="50" data-text-range="Rows {a}–{b} of {t}" data-text-page="Page {p} / {pages}" data-text-empty="No matching rows — try clearing the filters.">
<div class="ni-controls">
<div class="ni-filters" role="group" aria-label="Filter by issue type">
<button type="button" class="ni-chip is-active" data-group="all" aria-pressed="true">All {{ C.total }}</button>
<button type="button" class="ni-chip" data-group="conflict" aria-pressed="false">Name conflicts {{ C.by_group.conflict }} ({{ C.synonym_groups }} accepted names)</button>
<button type="button" class="ni-chip" data-group="match" aria-pressed="false">Uncertain {{ C.by_group.match }}</button>
<button type="button" class="ni-chip" data-group="gap" aria-pressed="false">Gaps {{ C.by_group.gap }}</button>
</div>
<label class="ni-field" for="ni-source">Source <select id="ni-source"><option value="all">All</option><option value="gbif">GBIF ({{ C.by_source.gbif }})</option><option value="col">Catalogue of Life ({{ C.by_source.col }})</option><option value="bsf">Blattodea Species File ({{ C.by_source.bsf }})</option></select></label>
<label class="ni-field" for="ni-q">Search <input type="search" id="ni-q" placeholder="Scientific name / Chinese name / external name / family" autocomplete="off"></label>
<button type="button" class="ni-chip" id="ni-reset">Clear filters</button>
</div>
<p class="ni-status" id="ni-status" role="status" aria-live="polite">Rows 1–50 of {{ C.total }}</p>
<div class="ni-table-wrap">
<table class="ni-table">
<thead><tr><th scope="col">Name</th><th scope="col">Family</th><th scope="col">Source</th><th scope="col">Type</th><th scope="col">External record</th><th scope="col">Match</th><th scope="col">Notes</th></tr></thead>
<tbody id="ni-body">
{%- for it in D.issues %}
<tr class="ni-row" data-group="{{ it.group }}" data-source="{{ it.source }}" data-q="{{ it.latin | downcase }} {{ it.zh }} {{ it.theirs | downcase }} {{ it.accepted | downcase }} {{ it.family_latin | downcase }}">
<td class="ni-name"><a href="{{ site.base_url }}/species/{{ it.slug }}/">{{ it.zh }}<i>{{ it.latin }}</i></a></td>
<td class="ni-family">{{ it.family_latin }}</td>
<td class="ni-src">{%- if it.source == 'gbif' -%}GBIF{%- elsif it.source == 'col' -%}CoL{%- else -%}BSF{%- endif -%}</td>
<td class="ni-kind"><span class="ni-badge is-{{ it.group }}">{%- if it.kind == 'synonym' -%}synonym{%- elsif it.kind == 'higherrank' -%}higher rank only{%- elsif it.kind == 'missing' -%}not found{%- elsif it.kind == 'fuzzy' -%}fuzzy match{%- else -%}ambiguous{%- endif -%}</span></td>
<td class="ni-ext">{%- if it.url -%}<a href="{{ it.url }}" rel="noopener external" target="_blank"><i>{{ it.theirs }}</i></a>{%- elsif it.theirs -%}<i>{{ it.theirs }}</i>{%- else -%}—{%- endif -%}{%- if it.accepted -%}<span class="ni-accepted">accepted name {%- if it.accepted_slug %} <a href="{{ site.base_url }}/species/{{ it.accepted_slug }}/" title="also listed in this checklist"><i>{{ it.accepted }}</i></a><span class="ni-insite">also listed here</span>{%- elsif it.accepted_url %} <a href="{{ it.accepted_url }}" rel="noopener external" target="_blank"><i>{{ it.accepted }}</i></a>{%- else %} <i>{{ it.accepted }}</i>{%- endif -%}</span>{%- endif -%}</td>
<td class="ni-match">{%- if it.match -%}<span class="ni-match-type">{{ it.match }}</span>{%- if it.confidence %} · {{ it.confidence }}%{%- endif -%}{%- endif -%}{%- if it.verified %} <span class="ni-badge is-verified">verified</span>{%- elsif it.source == 'bsf' %} <span class="ni-badge">auto-matched</span>{%- endif -%}</td>
<td class="ni-note">{%- if it.note -%}<span lang="zh-CN">{{ it.note }}</span>{%- else -%}—{%- endif -%}</td>
</tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="ni-empty" id="ni-empty" hidden>No matching rows — try clearing the filters.</p>
{%- assign ni_pages = C.total | plus: 49 | divided_by: 50 -%}
<div class="ni-pager" id="ni-pager"><button type="button" id="ni-prev">‹ Previous</button><span id="ni-pageinfo" aria-current="true">Page 1 / {{ ni_pages }}</span><button type="button" id="ni-next">Next ›</button></div>
</div>
<noscript><p class="ni-noscript">Without JavaScript this page shows all {{ C.total }} rows at once, without filtering or paging.</p></noscript>
{%- assign G = D.synonym_groups -%}
<h2 id="synonyms" class="ni-syn-title">Synonyms grouped by their accepted name <span class="ni-syn-title-alt" lang="zh-CN">异名归并：按接受名（接收名）归并</span></h2>
<p class="ni-syn-lead">When an external database treats a name from this checklist as a synonym, it also reports the accepted name it uses instead. The rows below regroup those synonyms under that accepted name: <b>{{ C.synonym_groups }}</b> accepted names, <b>{{ C.synonym_pairs }}</b> synonym→accepted pairs (out of {{ C.by_group.conflict }} name-conflict rows covering {{ C.conflict_species }} names from this checklist). <b>{{ C.synonym_groups_in_site }}</b> accepted names are also listed separately here, so a merge decision is needed for those.</p>
{%- if G %}
<div class="ni-table-wrap ni-syn-wrap">
<table class="ni-table ni-syn-table">
<thead><tr><th scope="col">Accepted name</th><th scope="col">Record in this checklist</th><th scope="col">Synonyms attributed to it</th></tr></thead>
<tbody>
{%- for g in G %}
<tr>
<td class="ni-syn-acc"><i>{{ g.accepted }}</i>{%- for l in g.accepted_links %} <a class="ni-syn-ext" href="{{ l.url }}" rel="noopener external" target="_blank" title="accepted-name record in the external database">{%- if l.source == 'gbif' -%}GBIF{%- elsif l.source == 'col' -%}CoL{%- else -%}BSF{%- endif -%}</a>{%- endfor %}</td>
<td class="ni-syn-site">{%- if g.accepted_slug -%}<a href="{{ site.base_url }}/species/{{ g.accepted_slug }}/">{{ g.accepted_zh }}<i>{{ g.accepted_latin }}</i></a> <span class="ni-insite">also listed here</span>{%- else -%}<span class="ni-syn-none">not in this checklist</span>{%- endif -%}</td>
<td class="ni-syn-item"><ul class="ni-syn-list">{%- for s in g.synonyms -%}<li><a href="{{ site.base_url }}/species/{{ s.slug }}/">{{ s.zh }}<i>{{ s.latin }}</i></a> <span class="ni-syn-src">{%- for src in s.sources -%}{%- if src == 'gbif' -%}GBIF{%- elsif src == 'col' -%}CoL{%- else -%}BSF{%- endif -%}{%- unless forloop.last %} · {% endunless -%}{%- endfor -%}</span>{%- if s.match %} <span class="ni-syn-match">{{ s.match }}{% if s.confidence %} · {{ s.confidence }}%{% endif %}</span>{%- endif -%}</li>{%- endfor -%}</ul></td>
</tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="ni-syn-foot">This only records the synonym→accepted relationship reported by the external databases: every name keeps its own row here (<strong>the checklist data itself is unchanged</strong>); merging is a human decision based on the original literature and the classification used here. The species page of an accepted name that is also listed here shows the same synonyms in its “Other databases” block.</p>
{%- endif %}
<p class="ni-download"><a href="{{ site.base_url }}/downloads/isoptera-name-issues.csv" download>Download the full list as CSV ({{ C.total }} rows)</a> · <a href="{{ site.base_url }}/downloads/isoptera-synonym-groups.csv" download>synonym→accepted long table ({{ C.synonym_pairs }} rows)</a> · machine-readable copy: <code>{{ site.base_url }}/data/name-issues.json</code></p>
<p class="ni-note-foot">Cache dates: GBIF / Catalogue of Life {{ D.meta.cache_dates.authority | slice: 0, 10 }}; Blattodea Species File {{ D.meta.cache_dates.bsf | slice: 0, 10 }}. Rows marked auto-matched have not been checked by a human ({{ C.bsf_verified }} of {{ C.species_total }} verified). This page, including the table grouped by accepted name, is generated from repository caches by <code>.github/workflows/build_name_issues.py</code> and is rebuilt whenever the checklist is updated; the external records shown are whatever those databases currently report.</p>
<script src="{{ site.base_url }}/assets/name-issues.js?v={{ site.time | date: '%s' }}" defer></script>
