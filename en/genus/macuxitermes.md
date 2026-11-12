---
layout: default
title: "Genus Macuxitermes (马库希白蚁属) checklist"
description: "The genus Macuxitermes (马库希白蚁属) belongs to the family Termitidae (白蚁科), in the subfamily Syntermitinae (聚白蚁亚科); the site records 2 species. See below."
lang: en
single_lang: true
author: 班奈特格林
family_id: termitidae
last_modified_at: 2026-10-30
permalink: /en/genus/macuxitermes/
sitemap: true
has_map: true
taxon_search: true
translation_pending: true
breadcrumb:
  - name: "Checklist"
    url: "/en/list/"
  - name: "Termitidae 白蚁科"
    url: "/en/family/termitidae/"
  - name: "Syntermitinae 聚白蚁亚科"
    url: "/en/subfamily/syntermitinae/"
  - name: "Macuxitermes 马库希白蚁属"
    url: "/en/genus/macuxitermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/termitidae/">Termitidae 白蚁科</a> › <a href="{{ site.base_url }}/en/subfamily/syntermitinae/">Syntermitinae 聚白蚁亚科</a> › <a href="{{ site.base_url }}/en/genus/macuxitermes/"><i>Macuxitermes</i> 马库希白蚁属</a> › <span>This genus</span></nav>
<header class="taxon-header">
<h1>Genus <i>Macuxitermes</i> · 马库希白蚁属</h1>
<p class="taxon-meta">Family <i>Termitidae</i> · 2 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="macuxitermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this genus (2 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this genus by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="genus" id="macuxitermes" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>About the genus</h2>
<p>This genus belongs to the family <a href="{{ site.base_url }}/en/family/termitidae/">白蚁科 <i>Termitidae</i></a>, in the subfamily <a href="{{ site.base_url }}/en/subfamily/syntermitinae/">聚白蚁亚科 <i>Syntermitinae</i></a>; the site records 2 species.</p>
<p>Type species: <i>Macuxitermes triceratops</i>.</p>
<p>This page includes a distribution map for the genus (GBIF records aggregated on a 1° grid); open a species entry to see its type locality, distribution, and references.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etymology</h2>
<p>From Macuxi (an Amazonian indigenous people) + termes.</p>
<!-- src:S0018 -->
<p class="taxon-src">The etymologies in this section are analytical breakdowns; the roots follow Brown (1956).</p>
</section>
{%- assign fz = site.data.translations_en.fauna_genera["/genus/macuxitermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Species (2 species)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/species/macuxitermes-colombicus/"><i>Macuxitermes colombicus</i> Postle & Scheffrahn, 2016 哥伦比亚马库<wbr>希白蚁</a></li><li><a href="{{ site.base_url }}/en/species/macuxitermes-triceratops/"><i>Macuxitermes triceratops</i> Cancello & Bandeira, 1992 三角马库希白<wbr>蚁</a> <span class="taxon-type" title="Type species">★ Type species</span></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/subfamily/syntermitinae/">聚白蚁亚科 <i>Syntermitinae</i></a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/genus/macuxitermes/#taxon",
 "name": "Macuxitermes",
 "alternateName": [
  "马库希白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/en/genus/macuxitermes/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Syntermitinae",
  "alternateName": [
   "聚白蚁亚科"
  ],
  "taxonRank": "Subfamily",
  "url": "{{ site.base_url }}/en/subfamily/syntermitinae/"
 }
}
</script>