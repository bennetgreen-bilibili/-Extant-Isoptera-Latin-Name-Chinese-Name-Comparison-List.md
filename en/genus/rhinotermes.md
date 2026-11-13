---
layout: default
title: "Genus Rhinotermes (鼻白蚁属) checklist"
description: "The genus Rhinotermes (鼻白蚁属) belongs to the family Rhinotermitidae (鼻白蚁科); the site records 4 species. Morphology and etymology are summarized above. See below."
lang: en
single_lang: true
author: 班奈特格林
family_id: rhinotermitidae
last_modified_at: 2026-10-30
permalink: /en/genus/rhinotermes/
sitemap: true
has_map: true
taxon_search: true
has_photos: true
image: "/assets/images/rhinotermitidae.jpg"
breadcrumb:
  - name: "Checklist"
    url: "/en/list/"
  - name: "Rhinotermitidae 鼻白蚁科"
    url: "/en/family/rhinotermitidae/"
  - name: "Rhinotermes 鼻白蚁属"
    url: "/en/genus/rhinotermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/rhinotermitidae/">Rhinotermitidae 鼻白蚁科</a> › <a href="{{ site.base_url }}/en/genus/rhinotermes/"><i>Rhinotermes</i> 鼻白蚁属</a> › <span>This genus</span></nav>
<header class="taxon-header">
<h1>Genus <i>Rhinotermes</i> · 鼻白蚁属</h1>
<p class="taxon-meta">Family <i>Rhinotermitidae</i> · 4 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="rhinotermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this genus (4 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this genus by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="genus" id="rhinotermes" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="genus" id="rhinotermes" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>About the genus</h2>
<p>This genus belongs to the family <a href="{{ site.base_url }}/en/family/rhinotermitidae/"><i>Rhinotermitidae</i> 鼻白蚁科</a>; the site records 4 species.</p>
<p>Type species: <i>Rhinotermes nasutus</i>.</p>
<p>This page includes a distribution map for the genus (GBIF records aggregated on a 1° grid); open a species entry to see its type locality, distribution, and references.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etymology</h2>
<p>From Greek rhis (nose) + Latin termes, for the nasute soldier.</p>
<!-- src:S0018 -->
<p class="taxon-src">The etymologies in this section are analytical breakdowns; the roots follow Brown (1956).</p>
</section>
{%- assign fza = site.data.fauna_genera["/genus/rhinotermes/"].en -%}{%- assign fz = site.data.translations_en.fauna_genera["/genus/rhinotermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz abstract=fza %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Species (4)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/species/rhinotermes-hispidus/"><i>Rhinotermes hispidus</i> Emerson, 1925 多毛鼻白蚁</a></li><li><a href="{{ site.base_url }}/en/species/rhinotermes-manni/"><i>Rhinotermes manni</i> Snyder, 1924 曼鼻白蚁</a></li><li><a href="{{ site.base_url }}/en/species/rhinotermes-marginalis/"><i>Rhinotermes marginalis</i> Linnaeus, 1758 微小鼻白蚁</a></li><li><a href="{{ site.base_url }}/en/species/rhinotermes-nasutus/"><i>Rhinotermes nasutus</i> Perty, 1833 大鼻鼻白蚁</a> <span class="taxon-type" title="Type species">★ Type species</span></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/family/rhinotermitidae/"><i>Rhinotermitidae</i> 鼻白蚁科</a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/genus/rhinotermes/#taxon",
 "name": "Rhinotermes",
 "alternateName": [
  "鼻白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/en/genus/rhinotermes/",
 "isPartOf": {
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Rhinotermitidae",
  "alternateName": [
   "鼻白蚁科"
  ],
  "taxonRank": "Family",
  "url": "{{ site.base_url }}/en/family/rhinotermitidae/"
 }
}
</script>