---
layout: default
title: References & DOIs — Extant Isoptera (Termites) Latin–Chinese Name Comparison List
description: "The 77 references of the checklist, enriched: DOI links, Crossref records, GB/T 7714-style, APA 7 and Vancouver citations, plus BibTeX, RIS and CSL-JSON — copy or download in one click."
lang: en
author: 班奈特格林 (Bennet Green)
date: 2026-10-17
version: 2026.10.17
keywords: [termites, Isoptera, references, DOI, Crossref, GB/T 7714, APA, BibTeX, RIS, CSL-JSON]
permalink: /en/references/
---

# References &amp; DOIs

{%- assign refmeta = site.data.references.meta -%}
{%- assign refcounts = refmeta.counts -%}

<p>The {{ refcounts.total }} references listed at the end of the <a href="{{ site.base_url }}/en/list/#references">checklist</a> are expanded here into one copyable entry each: a <strong>DOI link</strong>, the <strong>Crossref record</strong>, and <strong>GB/T 7714-style</strong>, <strong>APA 7</strong> and <strong>Vancouver</strong> citations, plus machine-readable <strong>BibTeX / RIS / CSL-JSON</strong>.</p>

## Coverage

<ul>
  <li>References in total: <strong>{{ refcounts.total }}</strong> (one-to-one with the numbering at the end of the checklist).</li>
  <li>With a DOI: <strong>{{ refcounts.with_doi }}</strong>, of which <strong>{{ refcounts.crossref_resolved }}</strong> were confirmed by a Crossref record.</li>
  <li>Candidate DOIs (found by Crossref search, <strong>awaiting manual review</strong>): <strong>{{ refcounts.candidates }}</strong>.</li>
  <li>BHL original-description scans: <strong>{{ refcounts.bhl }}</strong> (optional enhancement, see below).</li>
</ul>

<h2 id="sources">Sources</h2>

<ul>
  <li><strong>The source list</strong>: the 77 entries at the end of the checklist, kept with their original numbering and wording — nothing is rewritten or merged.</li>
  <li><strong>Crossref</strong> (<a href="https://www.crossref.org/" target="_blank" rel="noopener">crossref.org</a>): bibliographic records looked up per DOI (title, authors, container title, volume, issue, pages, publisher, type, ISSN, citation count). Entries without a DOI are only searched bibliographically, and matches are listed as <strong>candidates</strong> for manual review.</li>
  <li><strong>BHL</strong> (<a href="https://about.biodiversitylibrary.org/" target="_blank" rel="noopener">Biodiversity Heritage Library</a>): can add scan links to early original descriptions. Needs a free API key; optional.</li>
</ul>

<h2 id="howto">How to cite</h2>

<ul>
  <li><strong>GB/T 7714-style</strong>: authors (first three plus <em>et al.</em>), title, document-type marker ([J] journal, [M] monograph, [C] proceedings…), journal, year, volume(issue), pages, DOI.</li>
  <li><strong>APA 7</strong>: authors, year, title, journal, volume(issue), pages, then <code>https://doi.org/…</code>.</li>
  <li><strong>Vancouver</strong>: authors (first six plus <em>et al.</em>), title, journal, year;volume(issue):pages.</li>
  <li>Every field comes from the Crossref record; <strong>fields Crossref does not have are left empty — nothing is inferred or invented</strong>. The type marker follows Crossref <code>type</code> (e.g. <code>book-chapter</code> → [M]).</li>
  <li>Title and author casing follow Crossref (publisher input); a few records store author names in full capitals, which are normalised to initial capitals only — no translation, no rewriting.</li>
  <li>Entries marked “<strong>auto-matched, not yet verified</strong>” got their DOI from a title-similarity plus year match: please check before citing. Entries marked “<strong>no DOI in the source</strong>” only carry candidates, which were not adopted.</li>
</ul>

<h2 id="bhl">BHL original descriptions</h2>

<p>Original descriptions of early taxonomic works are often held by BHL. With a free API key in <code>BHL_API_KEY</code>, run <code>python .github/workflows/build_references.py --write --bhl</code>: the script searches BHL by title and adds <code>bhl.url</code> (a bibliography-level link — no scans are downloaded). Currently <strong>{{ refcounts.bhl }}</strong> entries carry such a link; without a key, or when BHL is unreachable, the field stays <code>null</code> and the rest of the page is unaffected.</p>

<h2 id="download">Download &amp; bulk use</h2>

<p>The full data (original citation, DOI status, Crossref fields, three citation styles, BibTeX, RIS, CSL-JSON, BHL) is in <a href="{{ site.base_url }}/data/references.json"><code>data/references.json</code></a>. The “Export CSL-JSON” button above the list builds a CSL-JSON array in the browser, ready for Zotero / EndNote / Mendeley (without JavaScript, use the JSON link).</p>

<p>This page is an <strong>enriched view</strong>: the authoritative entries remain the <a href="{{ site.base_url }}/en/list/#references">reference list at the end of the checklist</a>. This page only adds DOI resolution and machine-readable formats; numbering, count and wording are identical.</p>

<p>To cite the whole checklist (dataset): 班奈特格林. (2026). Checklist of extant Isoptera (termites): Latin scientific names with Chinese standard names (version {{ site.dataset.version }}) [Data set]. {{ site.dataset.publisher }}. <a href="https://doi.org/{{ site.dataset.doi }}">https://doi.org/{{ site.dataset.doi }}</a></p>

{% include references.html %}
