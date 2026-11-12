---
layout: default
title: "Genus Proneotermes (前新白蚁属) checklist"
description: "The genus Proneotermes (前新白蚁属) belongs to the family Kalotermitidae (木白蚁科); the site records 4 species. Morphology and etymology are summarized above."
lang: en
single_lang: true
author: 班奈特格林
family_id: kalotermitidae
last_modified_at: 2026-10-30
permalink: /en/genus/proneotermes/
sitemap: true
has_map: true
taxon_search: true
translation_pending: true
image: "/assets/images/kalotermitidae.jpg"
breadcrumb:
  - name: "Checklist"
    url: "/en/list/"
  - name: "Kalotermitidae 木白蚁科"
    url: "/en/family/kalotermitidae/"
  - name: "Proneotermes 前新白蚁属"
    url: "/en/genus/proneotermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/kalotermitidae/">Kalotermitidae 木白蚁科</a> › <a href="{{ site.base_url }}/en/genus/proneotermes/"><i>Proneotermes</i> 前新白蚁属</a> › <span>This genus</span></nav>
<header class="taxon-header">
<h1>Genus <i>Proneotermes</i> · 前新白蚁属</h1>
<p class="taxon-meta">Family <i>Kalotermitidae</i> · 4 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="proneotermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this genus (4 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this genus by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="genus" id="proneotermes" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>About the genus</h2>
<p>This genus belongs to the family <a href="{{ site.base_url }}/en/family/kalotermitidae/">木白蚁科 <i>Kalotermitidae</i></a>; the site records 4 species.</p>
<p>Type species: <i>Proneotermes perezi</i>.</p>
<p>This page includes a distribution map for the genus (GBIF records aggregated on a 1° grid); open a species entry to see its type locality, distribution, and references.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etymology</h2>
<p>From Greek pro- (before) + neos (new) + Latin termes.</p>
<!-- src:S0018 -->
<p class="taxon-src">The etymologies in this section are analytical breakdowns; the roots follow Brown (1956).</p>
</section>
{%- assign fz = site.data.translations_en.fauna_genera["/genus/proneotermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Species (4 species)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/species/proneotermes-latifrons/"><i>Proneotermes latifrons</i> Silvestri, 1901 宽额前新白蚁<wbr></a></li><li><a href="{{ site.base_url }}/en/species/proneotermes-macondianus/"><i>Proneotermes macondianus</i> Casalla, Scheffrahn & Korb, 2016 马康多前新白<wbr>蚁</a></li><li><a href="{{ site.base_url }}/en/species/proneotermes-perezi/"><i>Proneotermes perezi</i> Holmgren, 1911 佩雷斯前新白<wbr>蚁</a> <span class="taxon-type" title="Type species">★ Type species</span></li><li><a href="{{ site.base_url }}/en/species/proneotermes-tacicuarensis/"><i>Proneotermes tacicuarensis</i> Jurado-Vargas, Méndez-Montiel, García-Díaz & Cruz-de León, 2025 塔西夸罗前新<wbr>白蚁</a></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/family/kalotermitidae/">木白蚁科 <i>Kalotermitidae</i></a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/genus/proneotermes/#taxon",
 "name": "Proneotermes",
 "alternateName": [
  "前新白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/en/genus/proneotermes/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Kalotermitidae",
  "alternateName": [
   "木白蚁科"
  ],
  "taxonRank": "Family",
  "url": "{{ site.base_url }}/en/family/kalotermitidae/"
 }
}
</script>