---
layout: default
title: Name discrepancies and review queue — Extant Isoptera (Termites) Latin–Chinese Name Comparison List
description: "A filterable list of name-level mismatches between this checklist and GBIF Backbone, Catalogue of Life and the Blattodea Species File: external synonyms, ambiguous matches and coverage gaps, with CSV download."
lang: en
author: 班奈特格林 (Bennet Green)
date: 2026-10-29
version: 2026.10.30
keywords: [termites, Isoptera, checklist, name discrepancies, taxonomy review, GBIF, Catalogue of Life, Blattodea Species File]
permalink: /en/list/name-issues/
pagefind: true
---
{%- assign D = site.data.name_issues -%}
{%- assign C = D.meta.counts -%}
<nav class="ni-crumbs" aria-label="Breadcrumb"><a href="{{ site.base_url }}/en/">Home</a> › <a href="{{ site.base_url }}/en/list/">List</a> › Name discrepancies</nav>
<h1 class="ni-title">Name discrepancies and review queue<span class="ni-title-alt" lang="zh-CN">命名差异与待核对</span></h1>
<p class="ni-lead">This page turns the cached name-matching results between this checklist and three external authorities — GBIF Backbone, Catalogue of Life (ChecklistBank) and the Blattodea Species File (BSF) — into a filterable list. Only entries that need human attention are shown: <b>{{ C.total }}</b> rows covering <b>{{ C.species_with_issue }}</b> species/subspecies out of {{ C.species_total }} checklist records. Each <em>name conflict</em> is also resolved into one pair with a <strong>relation</strong> and a <strong>direction</strong> (<a href="#synonyms">pairs with relation and direction</a>): {{ C.pairs_relation_synonym }} synonym pairs vs {{ C.pairs_relation_combination }} combination differences; the receiving name is the external one in {{ C.pairs_direction_external }} pairs, ours in {{ C.pairs_direction_site }}, and undecided in {{ C.pairs_direction_disputed }}. {{ C.pairs_recorded }} pair(s) have already been written into the <a href="#synonyms">junior-synonym section</a> of the accepted name's species page. <strong>Nothing here changes the checklist data</strong>; matching rules are documented on the <a href="{{ site.base_url }}/en/data/">data page</a>.</p>
<div class="ni-legend"><span><span class="ni-badge is-conflict">Name conflict</span>the external database treats our name as a synonym and gives its accepted name — decide whether to rename, annotate or keep ours.</span><span><span class="ni-badge is-match">Uncertain match</span>fuzzy match, or several candidate OTUs share the name, so the script cannot decide automatically.</span><span><span class="ni-badge is-gap">Coverage gap</span>only a higher taxon matched, the name is absent, or it is not found in the BSF — this affects cross-links.</span></div>
<div class="ni-summary"><span class="ni-stat"><b>{{ C.total }}</b> rows to review</span><span class="ni-stat"><b>{{ C.by_group.conflict }}</b> name conflicts → {{ C.conflict_pairs }} pairs</span><span class="ni-stat"><b>{{ C.pairs_relation_combination }}</b> are combination differences</span><span class="ni-stat"><b>{{ C.pairs_direction_disputed }}</b> pairs with undecided direction</span><span class="ni-stat"><b>{{ C.pairs_recorded }}</b> pairs recorded</span><span class="ni-stat"><b>{{ C.by_group.match }}</b> uncertain matches</span><span class="ni-stat"><b>{{ C.by_group.gap }}</b> coverage gaps</span><span class="ni-stat"><b>{{ C.species_with_issue }}</b> taxa involved</span><span class="ni-stat">Manually verified: <b>{{ C.manually_reviewed }}</b> (BSF {{ C.bsf_verified }})</span></div>
<div class="ni-app" id="ni-root" data-page-size="50" data-text-range="Rows {a}–{b} of {t}" data-text-page="Page {p} / {pages}" data-text-empty="No matching rows — try clearing the filters.">
<div class="ni-controls">
<div class="ni-filters" role="group" aria-label="Filter by issue type">
<button type="button" class="ni-chip is-active" data-group="all" aria-pressed="true">All {{ C.total }}</button>
<button type="button" class="ni-chip" data-group="conflict" aria-pressed="false">Name conflicts {{ C.by_group.conflict }} ({{ C.conflict_pairs }} pairs)</button>
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
<td class="ni-kind">{%- if it.group == 'conflict' -%}{%- if it.relation == 'combination' -%}<span class="ni-badge is-comb">combination</span>{%- else -%}<span class="ni-badge is-conflict">synonym</span>{%- endif -%}{%- if it.direction == 'site' -%} <span class="ni-badge is-verified">our name is the receiving name</span>{%- elsif it.direction == 'disputed' -%} <span class="ni-badge">direction undecided</span>{%- elsif it.disputed -%} <span class="ni-badge">databases disagree</span>{%- endif -%}{%- if it.recorded %} <span class="ni-badge is-verified">recorded</span>{%- endif -%}{%- else -%}<span class="ni-badge is-{{ it.group }}">{%- if it.kind == 'higherrank' -%}higher rank only{%- elsif it.kind == 'missing' -%}not found{%- elsif it.kind == 'fuzzy' -%}fuzzy match{%- else -%}ambiguous{%- endif -%}</span>{%- endif -%}</td>
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
{%- assign P = D.synonym_pairs -%}
<h2 id="synonyms" class="ni-syn-title">Each discrepancy as one pair: relation and direction <span class="ni-syn-title-alt" lang="zh-CN">名称差异逐对归并：关系与方向</span></h2>
<p class="ni-syn-lead">The {{ C.by_group.conflict }} name-conflict rows become <b>{{ C.conflict_pairs }}</b> pairs of “our name ↔ the accepted name the external database claims” (the same pair reported by several databases counts once). Two things are decided per pair: the <strong>relation</strong> — a different epithet is a <em>synonym</em> (<b>{{ C.pairs_relation_synonym }}</b> pairs), while the same species under a different genus is a <em>combination difference</em> (<b>{{ C.pairs_relation_combination }}</b> pairs) — and the <strong>direction</strong> — the receiving name is the external name in <b>{{ C.pairs_direction_external }}</b> pairs, our name in <b>{{ C.pairs_direction_site }}</b> pairs, and undecided in <b>{{ C.pairs_direction_disputed }}</b> pairs. The “database verdicts” column shows each database's species-level verdict on our name (higher-rank-only, fuzzy and not-found results do not vote).</p>
{%- if P %}
<div class="ni-table-wrap ni-syn-wrap">
<table class="ni-table ni-syn-table">
<thead><tr><th scope="col">Our name</th><th scope="col">Accepted name claimed externally</th><th scope="col">Relation</th><th scope="col">Direction (receiving name)</th><th scope="col">Database verdicts</th><th scope="col">Recorded</th></tr></thead>
<tbody>
{%- for p in P %}
<tr>
<td class="ni-syn-our"><a href="{{ site.base_url }}/species/{{ p.our.slug }}/">{{ p.our.zh }}<i>{{ p.our.latin }}</i></a></td>
<td class="ni-syn-extname"><i>{{ p.external.name }}</i>{%- for l in p.external_links %} <a class="ni-syn-ext" href="{{ l.url }}" rel="noopener external" target="_blank" title="this record in the external database">{%- if l.source == 'gbif' -%}GBIF{%- elsif l.source == 'col' -%}CoL{%- else -%}BSF{%- endif -%}</a>{%- endfor %}{%- if p.receiving.in_site and p.receiving.slug and p.receiving.latin != p.our.latin %} <a class="ni-insite" href="{{ site.base_url }}/species/{{ p.receiving.slug }}/">also listed here</a>{%- endif -%}</td>
<td class="ni-syn-rel">{%- if p.relation == 'combination' -%}<span class="ni-badge is-comb">combination</span>{%- else -%}<span class="ni-badge is-conflict">synonym</span>{%- endif -%}{%- if p.disputed %} <span class="ni-badge">databases disagree</span>{%- endif -%}</td>
<td class="ni-syn-dir">{%- if p.direction == 'external' -%}external name is the receiving name{%- elsif p.direction == 'site' -%}our name is the receiving name{%- else -%}undecided{%- endif -%}</td>
<td class="ni-syn-votes">{%- if p.votes.synonym contains 'gbif' -%}<span class="ni-vote is-syn">GBIF synonym</span>{%- elsif p.votes.accepted contains 'gbif' -%}<span class="ni-vote is-acc">GBIF accepted</span>{%- endif -%}{%- if p.votes.synonym contains 'col' -%}<span class="ni-vote is-syn">CoL synonym</span>{%- elsif p.votes.accepted contains 'col' -%}<span class="ni-vote is-acc">CoL accepted</span>{%- endif -%}{%- if p.votes.synonym contains 'bsf' -%}<span class="ni-vote is-syn">BSF synonym</span>{%- elsif p.votes.accepted contains 'bsf' -%}<span class="ni-vote is-acc">BSF valid</span>{%- endif -%}{%- if p.votes.synonym.size == 0 and p.votes.accepted.size == 0 -%}—{%- endif -%}</td>
<td class="ni-syn-rec">{%- if p.recorded -%}<span class="ni-badge is-verified">recorded</span>{%- elsif p.recordable -%}<span class="ni-badge">recordable</span>{%- else -%}—{%- endif -%}</td>
</tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="ni-syn-foot">Rules: only <strong>species-level</strong> verdicts vote (genus/family-only matches, fuzzy matches and “not found” do not). A <strong>synonym</strong> means a different epithet — a genuinely different name; a <strong>combination difference</strong> means the same species under a different genus, which is not a synonym. In the latter case GBIF often sinks the genus used here into an older one and reports our name as its “accepted name”, so the direction is easily reversed — hence the direction is decided by the database votes. Only pairs that are “true synonym + externally receiving name + at least two taxonomic databases agreeing” are recordable (a contrary GBIF verdict is shown as “databases disagree” and does not veto): <b>{{ C.pairs_recorded }}</b> pair(s) have been written into the accepted name's species page under “Synonyms recorded from external authorities” in its junior-synonym section (front-matter fields <code>authority_synonym_*</code>, also searchable). Everything else — including combination differences and undecided directions — remains a review note; no name is deleted here, and a formal merge still follows the original literature and the classification used here.</p>
{%- endif %}

<p class="ni-download"><a href="{{ site.base_url }}/downloads/isoptera-name-issues.csv" download>Download the full list as CSV ({{ C.total }} rows)</a> · <a href="{{ site.base_url }}/downloads/isoptera-synonym-pairs.csv" download>per-pair relation/direction table ({{ C.conflict_pairs }} rows)</a> · machine-readable copy: <code>{{ site.base_url }}/data/name-issues.json</code></p>
<p class="ni-note-foot">Cache dates: GBIF / Catalogue of Life {{ D.meta.cache_dates.authority | slice: 0, 10 }}; Blattodea Species File {{ D.meta.cache_dates.bsf | slice: 0, 10 }}. Rows marked auto-matched have not been checked by a human ({{ C.bsf_verified }} of {{ C.species_total }} verified). This page, including the relation/direction table and the recording status, is generated from repository caches by <code>.github/workflows/build_name_issues.py</code> and is rebuilt whenever the checklist is updated; the external records shown are whatever those databases currently report.</p>
<script src="{{ site.base_url }}/assets/name-issues.js?v={{ site.time | date: '%s' }}" defer></script>
