---
layout: default
title: "Genus Hodotermopsis (原白蚁属) checklist"
description: "The genus Hodotermopsis (原白蚁属) belongs to the family Hodotermopsidae (原白蚁科); the site records 1 species. Morphology and etymology are summarized above."
lang: en
single_lang: true
author: 班奈特格林
family_id: hodotermopsidae
last_modified_at: 2026-10-30
permalink: /en/genus/hodotermopsis/
sitemap: true
has_map: true
taxon_search: true
has_photos: true
image: "/assets/images/hodotermopsidae.jpg"
breadcrumb:
  - name: "Checklist"
    url: "/en/list/"
  - name: "Hodotermopsidae 原白蚁科"
    url: "/en/family/hodotermopsidae/"
  - name: "Hodotermopsis 原白蚁属"
    url: "/en/genus/hodotermopsis/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/hodotermopsidae/">Hodotermopsidae 原白蚁科</a> › <a href="{{ site.base_url }}/en/genus/hodotermopsis/"><i>Hodotermopsis</i> 原白蚁属</a> › <span>This genus</span></nav>
<header class="taxon-header">
<h1>Genus <i>Hodotermopsis</i> · 原白蚁属</h1>
<p class="taxon-meta">Family <i>Hodotermopsidae</i> · 1 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="hodotermopsis" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this genus (1 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this genus by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="genus" id="hodotermopsis" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="genus" id="hodotermopsis" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>About the genus</h2>
<p>This genus belongs to the family <a href="{{ site.base_url }}/en/family/hodotermopsidae/">原白蚁科 <i>Hodotermopsidae</i></a>; the site records 1 species.</p>
<p>Type species: <i>Hodotermopsis sjostedti</i>.</p>
<p>This page includes a distribution map for the genus (GBIF records aggregated on a 1° grid); open a species entry to see its type locality, distribution, and references.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etymology</h2>
<p>From Greek hodos (path) + -termopsis.</p>
<!-- src:S0018 -->
<p class="taxon-src">The etymologies in this section are analytical breakdowns; the roots follow Brown (1956).</p>
</section>
{%- assign fz = site.data.translations_en.fauna_genera["/genus/hodotermopsis/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Species (1 species)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/species/hodotermopsis-sjostedti/"><i>Hodotermopsis sjostedti</i> Holmgren, 1911 山林原白蚁</a> <span class="taxon-type" title="Type species">★ Type species</span></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/family/hodotermopsidae/">原白蚁科 <i>Hodotermopsidae</i></a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/genus/hodotermopsis/#taxon",
 "name": "Hodotermopsis",
 "alternateName": [
  "原白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/en/genus/hodotermopsis/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Hodotermopsidae",
  "alternateName": [
   "原白蚁科"
  ],
  "taxonRank": "Family",
  "url": "{{ site.base_url }}/en/family/hodotermopsidae/"
 }
}
</script>