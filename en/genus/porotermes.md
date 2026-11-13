---
layout: default
title: "Genus Porotermes (洞白蚁属) checklist"
description: "The genus Porotermes (洞白蚁属) belongs to the family Stolotermitidae (胄白蚁科); the site records 3 species. Every species and subspecies of the genus is listed below."
lang: en
single_lang: true
author: 班奈特格林
family_id: stolotermitidae
last_modified_at: 2026-10-30
permalink: /en/genus/porotermes/
sitemap: true
has_map: true
taxon_search: true
has_photos: true
image: "/assets/images/stolotermitidae.jpg"
breadcrumb:
  - name: "Checklist"
    url: "/en/list/"
  - name: "Stolotermitidae 胄白蚁科"
    url: "/en/family/stolotermitidae/"
  - name: "Porotermes 洞白蚁属"
    url: "/en/genus/porotermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/stolotermitidae/">Stolotermitidae 胄白蚁科</a> › <a href="{{ site.base_url }}/en/genus/porotermes/"><i>Porotermes</i> 洞白蚁属</a> › <span>This genus</span></nav>
<header class="taxon-header">
<h1>Genus <i>Porotermes</i> · 洞白蚁属</h1>
<p class="taxon-meta">Family <i>Stolotermitidae</i> · 3 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="porotermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this genus (3 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this genus by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="genus" id="porotermes" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="genus" id="porotermes" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>About the genus</h2>
<p>This genus belongs to the family <a href="{{ site.base_url }}/en/family/stolotermitidae/"><i>Stolotermitidae</i> 胄白蚁科</a>; the site records 3 species.</p>
<p>Type species: <i>Porotermes quadricollis</i>.</p>
<p>This page includes a distribution map for the genus (GBIF records aggregated on a 1° grid); open a species entry to see its type locality, distribution, and references.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etymology</h2>
<p>From Greek poros (pore, passage) + Latin termes.</p>
<!-- src:S0018 -->
<p class="taxon-src">The etymologies in this section are analytical breakdowns; the roots follow Brown (1956).</p>
</section>
{%- assign fza = site.data.fauna_genera["/genus/porotermes/"].en -%}{%- assign fz = site.data.translations_en.fauna_genera["/genus/porotermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz abstract=fza %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Species (3)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/species/porotermes-adamsoni/"><i>Porotermes adamsoni</i> Froggatt, 1897 亚当森洞白蚁</a></li><li><a href="{{ site.base_url }}/en/species/porotermes-planiceps/"><i>Porotermes planiceps</i> Sjöstedt, 1904 扁头洞白蚁</a></li><li><a href="{{ site.base_url }}/en/species/porotermes-quadricollis/"><i>Porotermes quadricollis</i> Rambur, 1842 方颈洞白蚁</a> <span class="taxon-type" title="Type species">★ Type species</span></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/family/stolotermitidae/"><i>Stolotermitidae</i> 胄白蚁科</a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/genus/porotermes/#taxon",
 "name": "Porotermes",
 "alternateName": [
  "洞白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/en/genus/porotermes/",
 "isPartOf": {
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Stolotermitidae",
  "alternateName": [
   "胄白蚁科"
  ],
  "taxonRank": "Family",
  "url": "{{ site.base_url }}/en/family/stolotermitidae/"
 }
}
</script>