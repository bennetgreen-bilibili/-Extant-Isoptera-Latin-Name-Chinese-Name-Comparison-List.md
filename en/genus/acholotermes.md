---
layout: default
title: "Genus Acholotermes (顺白蚁属) checklist"
description: "The genus Acholotermes (顺白蚁属) belongs to the family Termitidae (白蚁科), in the subfamily Apicotermitinae (尖白蚁亚科); the site records 5 species. See below."
lang: en
single_lang: true
author: 班奈特格林
family_id: termitidae
last_modified_at: 2026-10-30
permalink: /en/genus/acholotermes/
sitemap: true
has_map: true
taxon_search: true
breadcrumb:
  - name: "Checklist"
    url: "/en/list/"
  - name: "Termitidae 白蚁科"
    url: "/en/family/termitidae/"
  - name: "Apicotermitinae 尖白蚁亚科"
    url: "/en/subfamily/apicotermitinae/"
  - name: "Acholotermes 顺白蚁属"
    url: "/en/genus/acholotermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/termitidae/">Termitidae 白蚁科</a> › <a href="{{ site.base_url }}/en/subfamily/apicotermitinae/">Apicotermitinae 尖白蚁亚科</a> › <a href="{{ site.base_url }}/en/genus/acholotermes/"><i>Acholotermes</i> 顺白蚁属</a> › <span>This genus</span></nav>
<header class="taxon-header">
<h1>Genus <i>Acholotermes</i> · 顺白蚁属</h1>
<p class="taxon-meta">Family <i>Termitidae</i> · 5 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="acholotermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this genus (5 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this genus by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="genus" id="acholotermes" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>About the genus</h2>
<p>This genus belongs to the family <a href="{{ site.base_url }}/en/family/termitidae/"><i>Termitidae</i> 白蚁科</a>, in the subfamily <a href="{{ site.base_url }}/en/subfamily/apicotermitinae/"><i>Apicotermitinae</i> 尖白蚁亚科</a>; the site records 5 species.</p>
<p>Type species: <i>Acholotermes tithasus</i>.</p>
<p>This page includes a distribution map for the genus (GBIF records aggregated on a 1° grid); open a species entry to see its type locality, distribution, and references.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etymology</h2>
<p>From Greek a- (without) + cholē (bile) + Latin termes.</p>
<!-- src:S0018 -->
<p class="taxon-src">The etymologies in this section are analytical breakdowns; the roots follow Brown (1956).</p>
</section>
{%- assign fza = site.data.fauna_genera["/genus/acholotermes/"].en -%}{%- assign fz = site.data.translations_en.fauna_genera["/genus/acholotermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz abstract=fza %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Species (5)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/species/acholotermes-chirotus/"><i>Acholotermes chirotus</i> Sands, 1972 短小顺白蚁</a></li><li><a href="{{ site.base_url }}/en/species/acholotermes-epius/"><i>Acholotermes epius</i> Sands, 1972 椭囟顺白蚁</a></li><li><a href="{{ site.base_url }}/en/species/acholotermes-imbellis/"><i>Acholotermes imbellis</i> Sands, 1972 和平顺白蚁</a></li><li><a href="{{ site.base_url }}/en/species/acholotermes-socialis/"><i>Acholotermes socialis</i> Sjöstedt, 1899 社会顺白蚁</a></li><li><a href="{{ site.base_url }}/en/species/acholotermes-tithasus/"><i>Acholotermes tithasus</i> Sands, 1972 体大顺白蚁</a> <span class="taxon-type" title="Type species">★ Type species</span></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/subfamily/apicotermitinae/"><i>Apicotermitinae</i> 尖白蚁亚科</a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/genus/acholotermes/#taxon",
 "name": "Acholotermes",
 "alternateName": [
  "顺白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/en/genus/acholotermes/",
 "isPartOf": {
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Apicotermitinae",
  "alternateName": [
   "尖白蚁亚科"
  ],
  "taxonRank": "Subfamily",
  "url": "{{ site.base_url }}/en/subfamily/apicotermitinae/"
 }
}
</script>