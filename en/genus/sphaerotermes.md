---
layout: default
title: "Genus Sphaerotermes (圆球白蚁属) checklist"
description: "The genus Sphaerotermes (圆球白蚁属) belongs to the family Termitidae (白蚁科), in the subfamily Sphaerotermitinae (圆球白蚁亚科); the site records 1 species. See below."
lang: en
single_lang: true
author: 班奈特格林
family_id: termitidae
last_modified_at: 2026-10-30
permalink: /en/genus/sphaerotermes/
sitemap: true
has_map: true
taxon_search: true
translation_pending: true
breadcrumb:
  - name: "Checklist"
    url: "/en/list/"
  - name: "Termitidae 白蚁科"
    url: "/en/family/termitidae/"
  - name: "Sphaerotermitinae 圆球白蚁亚科"
    url: "/en/subfamily/sphaerotermitinae/"
  - name: "Sphaerotermes 圆球白蚁属"
    url: "/en/genus/sphaerotermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/termitidae/">Termitidae 白蚁科</a> › <a href="{{ site.base_url }}/en/subfamily/sphaerotermitinae/">Sphaerotermitinae 圆球白蚁亚科</a> › <a href="{{ site.base_url }}/en/genus/sphaerotermes/"><i>Sphaerotermes</i> 圆球白蚁属</a> › <span>This genus</span></nav>
<header class="taxon-header">
<h1>Genus <i>Sphaerotermes</i> · 圆球白蚁属</h1>
<p class="taxon-meta">Family <i>Termitidae</i> · 1 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="sphaerotermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this genus (1 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this genus by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="genus" id="sphaerotermes" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>About the genus</h2>
<p>This genus belongs to the family <a href="{{ site.base_url }}/en/family/termitidae/"><i>Termitidae</i> 白蚁科</a>, in the subfamily <a href="{{ site.base_url }}/en/subfamily/sphaerotermitinae/"><i>Sphaerotermitinae</i> 圆球白蚁亚科</a>; the site records 1 species.</p>
<p>Type species: <i>Sphaerotermes sphaerothorax</i>.</p>
<p>This page includes a distribution map for the genus (GBIF records aggregated on a 1° grid); open a species entry to see its type locality, distribution, and references.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etymology</h2>
<p>From Greek sphaira (sphere) + Latin termes.</p>
<!-- src:S0018 -->
<p class="taxon-src">The etymologies in this section are analytical breakdowns; the roots follow Brown (1956).</p>
</section>
{%- assign fza = site.data.fauna_genera["/genus/sphaerotermes/"].en -%}{%- assign fz = site.data.translations_en.fauna_genera["/genus/sphaerotermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz abstract=fza %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Species (1)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/species/sphaerotermes-sphaerothorax/"><i>Sphaerotermes sphaerothorax</i> Sjöstedt, 1911 圆胸圆球白蚁</a> <span class="taxon-type" title="Type species">★ Type species</span></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/subfamily/sphaerotermitinae/"><i>Sphaerotermitinae</i> 圆球白蚁亚科</a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/genus/sphaerotermes/#taxon",
 "name": "Sphaerotermes",
 "alternateName": [
  "圆球白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/en/genus/sphaerotermes/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Sphaerotermitinae",
  "alternateName": [
   "圆球白蚁亚科"
  ],
  "taxonRank": "Subfamily",
  "url": "{{ site.base_url }}/en/subfamily/sphaerotermitinae/"
 }
}
</script>