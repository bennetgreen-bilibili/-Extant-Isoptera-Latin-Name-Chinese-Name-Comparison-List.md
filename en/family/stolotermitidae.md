---
layout: default
title: "Family Stolotermitidae (胄白蚁科) checklist"
description: "The family Stolotermitidae (胄白蚁科) is one of the extant termite families (Isoptera); the site records 2 genera and 10 species. See below. See the list below."
lang: en
single_lang: true
author: 班奈特格林
family_id: stolotermitidae
last_modified_at: 2026-10-30
permalink: /en/family/stolotermitidae/
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
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/stolotermitidae/">Stolotermitidae 胄白蚁科</a> › <span>This family</span></nav>
<header class="taxon-header">
<h1>Family <i>Stolotermitidae</i> · 胄白蚁科</h1>
<p class="taxon-meta">2 genera · 10 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="stolotermitidae,porotermes,stolotermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this family (10 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this family by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>

<figure class="taxa-illustration">
  <img src="{{ site.base_url }}/assets/images/stolotermitidae.jpg" alt="Stolotermes victoriensis 维多利亚胄白蚁" loading="lazy">
  <figcaption><i>Stolotermes victoriensis</i> 维多利亚胄白蚁 · Photo: <a href="https://www.inaturalist.org/photos/109922908">Nick Porch</a> · <a href="https://creativecommons.org/licenses/by-nc/4.0/deed.en">CC BY-NC 4.0</a> (iNaturalist, scaled)</figcaption>
</figure>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="family" id="stolotermitidae" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="family" id="stolotermitidae" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro">
<h2>About the family</h2>
<p>The family Stolotermitidae was established by Holmgren in 1910 (Holmgren, 1910a: 285)(14), with the type genus Stolotermes Hagen, 1858. The family name derives from the type genus Stolotermes (Greek stolos, column/expedition, popularly explained as referring to their marching activities). The soldiers of this family have a sclerotized, darkly pigmented head capsule, long, large mandibles, and 4-segmented tarsi. This checklist includes 2 genera and 10 species.</p>
<p>This family comprises the “dampwood termites” with a typical Gondwanan disjunct distribution: Porotermes is distributed in Australia, South Africa, Chile and southern South America; Stolotermes is distributed in Australia, New Zealand and South Africa. Both genera inhabit moist, decaying fallen logs and the area beneath the bark of standing dead trees; colonies nest inside the wood and live in single-piece wood nests. The historical biogeographic pattern of this family may have been influenced by both early land connections and subsequent transoceanic dispersal, and the distribution of the living genera cannot be explained solely by the breakup of Gondwana. Economically, Porotermes quadricollis occasionally damages moist wooden structures in Chile(15). According to Evans et al. (2013)(4), Porotermes adamsoni was introduced into New Zealand with wooden railway sleepers imported in 1941, and is now distributed at five sites on the North Island and one on the South Island, occurring in imported sawn timber and trees.</p>
<p class="taxon-src">This section is the standing account the site maintains for this rank and is updated on this page as the classification is revised; the checklist index is in the <a href="{{ site.base_url }}/en/list/">Checklist</a>.</p>
</section>
{%- assign fz = site.data.translations_en.fauna_families["/family/stolotermitidae/"] -%}{%- if fz %}
{% include fauna-family.html fauna=fz %}
{%- endif %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Genera (2)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/genus/porotermes/"><i>Porotermes</i> 洞白蚁属</a> <span class="taxon-count">3 species</span></li><li><a href="{{ site.base_url }}/en/genus/stolotermes/"><i>Stolotermes</i> 胄白蚁属</a> <span class="taxon-count">7 species</span></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/family/stolotermitidae/#taxon",
 "name": "Stolotermitidae",
 "alternateName": [
  "胄白蚁科"
 ],
 "taxonRank": "Family",
 "url": "{{ site.base_url }}/en/family/stolotermitidae/",
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