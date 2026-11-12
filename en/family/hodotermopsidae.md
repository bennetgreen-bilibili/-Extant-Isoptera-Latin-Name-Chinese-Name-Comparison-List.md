---
layout: default
title: "Family Hodotermopsidae (原白蚁科) checklist"
description: "The family Hodotermopsidae (原白蚁科) is one of the extant termite families (Isoptera); the site records 1 genus and 1 species. See below. See the list below."
lang: en
single_lang: true
author: 班奈特格林
family_id: hodotermopsidae
last_modified_at: 2026-10-30
permalink: /en/family/hodotermopsidae/
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
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/hodotermopsidae/">Hodotermopsidae 原白蚁科</a> › <span>This family</span></nav>
<header class="taxon-header">
<h1>Family <i>Hodotermopsidae</i> · 原白蚁科</h1>
<p class="taxon-meta">1 genus · 1 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="hodotermopsidae,hodotermopsis" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this family (1 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this family by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>

<figure class="taxa-illustration">
  <img src="{{ site.base_url }}/assets/images/hodotermopsidae.jpg" alt="Hodotermopsis sjostedti 山林原白蚁" loading="lazy">
  <figcaption>Hodotermopsis sjostedti 山林原白蚁</figcaption>
</figure>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="family" id="hodotermopsidae" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="family" id="hodotermopsidae" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro">
<h2>About the family</h2>
<p>The family Hodotermopsidae was proposed by Engel in 2021(11). The type genus is Hodotermopsis Holmgren, 1911. The family name derives from the type genus: Hodotermopsis means “resembling Hodotermes”, formed from Hodotermes plus the Greek opsis (appearance). This checklist includes 1 genera and 1 species.</p>
<p>The living species Hodotermopsis sjostedti is distributed in Japan, Taiwan (China), southern China and Vietnam(12). Consistent with its close relatives, Hodotermopsis inhabits moist, decaying wood; the colony nests inside fallen logs and lives in a single-piece wood nest, with labor within the nest performed by pseudergates. The soldiers have a subquadrate-oval, flattened head with the anterior half darker; the vertex bears a central depression; the ocelli are distinct and kidney-shaped; the mandibles are robust and symmetrical, the left mandible bearing four and the right mandible two large marginal teeth; the antennae have 22–24 segments; the pronotum is crescent-shaped and slightly narrower than the head. The winged adults are 12–13.5 mm long, with 21–26 antennal segments and the forewing scale slightly larger than the hindwing scale. Economically, Hodotermopsis sjostedti damages living and felled trees in southern China and is a wood-boring pest(13)</p>
<p class="taxon-src">This section is the standing account the site maintains for this rank and is updated on this page as the classification is revised; the checklist index is in the <a href="{{ site.base_url }}/en/list/">Checklist</a>.</p>
</section>
{%- assign fz = site.data.translations_en.fauna_families["/family/hodotermopsidae/"] -%}{%- if fz %}
{% include fauna-family.html fauna=fz %}
{%- endif %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Genus (1)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/genus/hodotermopsis/"><i>Hodotermopsis</i> 原白蚁属</a> <span class="taxon-count">1 species</span></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/family/hodotermopsidae/#taxon",
 "name": "Hodotermopsidae",
 "alternateName": [
  "原白蚁科"
 ],
 "taxonRank": "Family",
 "url": "{{ site.base_url }}/en/family/hodotermopsidae/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Isoptera",
  "alternateName": [
   "现存等翅下目"
  ],
  "taxonRank": "Infraorder"
 }
}
</script>