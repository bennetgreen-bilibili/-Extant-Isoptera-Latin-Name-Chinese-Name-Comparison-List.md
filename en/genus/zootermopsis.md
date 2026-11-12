---
layout: default
title: "Genus Zootermopsis (动白蚁属) checklist"
description: "The genus Zootermopsis (动白蚁属) belongs to the family Archotermopsidae (古白蚁科); the site records 3 species, 2 subspecies. See below. See the checklist index."
lang: en
single_lang: true
author: 班奈特格林
family_id: archotermopsidae
last_modified_at: 2026-10-30
permalink: /en/genus/zootermopsis/
sitemap: true
has_map: true
taxon_search: true
has_photos: true
translation_pending: true
image: "/assets/images/archotermopsidae.jpg"
breadcrumb:
  - name: "Checklist"
    url: "/en/list/"
  - name: "Archotermopsidae 古白蚁科"
    url: "/en/family/archotermopsidae/"
  - name: "Zootermopsis 动白蚁属"
    url: "/en/genus/zootermopsis/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/archotermopsidae/">Archotermopsidae 古白蚁科</a> › <a href="{{ site.base_url }}/en/genus/zootermopsis/"><i>Zootermopsis</i> 动白蚁属</a> › <span>This genus</span></nav>
<header class="taxon-header">
<h1>Genus <i>Zootermopsis</i> · 动白蚁属</h1>
<p class="taxon-meta">Family <i>Archotermopsidae</i> · 3 species, 2 subspecies</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="zootermopsis" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this genus (3 species, 2 subspecies): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this genus by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="genus" id="zootermopsis" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="genus" id="zootermopsis" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>About the genus</h2>
<p>This genus belongs to the family <a href="{{ site.base_url }}/en/family/archotermopsidae/"><i>Archotermopsidae</i> 古白蚁科</a>; the site records 3 species, 2 subspecies.</p>
<p>Type species: <i>Zootermopsis angusticollis</i>.</p>
<p>This page includes a distribution map for the genus (GBIF records aggregated on a 1° grid); open a species entry to see its type locality, distribution, and references.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etymology</h2>
<p>From Greek zōon (animal) + -termopsis (term- + -opsis).</p>
<!-- src:S0018 -->
<p class="taxon-src">The etymologies in this section are analytical breakdowns; the roots follow Brown (1956).</p>
</section>
{%- assign fza = site.data.fauna_genera["/genus/zootermopsis/"].en -%}{%- assign fz = site.data.translations_en.fauna_genera["/genus/zootermopsis/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz abstract=fza %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Species (3 species, 2 subspecies)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/species/zootermopsis-angusticollis/"><i>Zootermopsis angusticollis</i> Hagen, 1858 狭颈动白蚁</a> <span class="taxon-type" title="Type species">★ Type species</span></li><li><a href="{{ site.base_url }}/en/species/zootermopsis-laticeps/"><i>Zootermopsis laticeps</i> Banks, 1906 宽头动白蚁</a></li><li><a href="{{ site.base_url }}/en/species/zootermopsis-nevadensis/"><i>Zootermopsis nevadensis</i> Hagen, 1874 内华达动白蚁</a></li><li class="taxon-sub"><a href="{{ site.base_url }}/en/species/zootermopsis-nevadensis-nevadensis/"><i>Zootermopsis nevadensis nevadensis</i> Hagen, 1874 指名亚种</a></li><li class="taxon-sub"><a href="{{ site.base_url }}/en/species/zootermopsis-nevadensis-nuttingi/"><i>Zootermopsis nevadensis nuttingi</i> Haverty & Thorne, 1989 纳丁亚种</a></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/family/archotermopsidae/"><i>Archotermopsidae</i> 古白蚁科</a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/genus/zootermopsis/#taxon",
 "name": "Zootermopsis",
 "alternateName": [
  "动白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/en/genus/zootermopsis/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Archotermopsidae",
  "alternateName": [
   "古白蚁科"
  ],
  "taxonRank": "Family",
  "url": "{{ site.base_url }}/en/family/archotermopsidae/"
 }
}
</script>