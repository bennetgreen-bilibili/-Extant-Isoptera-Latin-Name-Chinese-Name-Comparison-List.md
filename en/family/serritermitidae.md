---
layout: default
title: "Family Serritermitidae (齿白蚁科) checklist"
description: "The family Serritermitidae (齿白蚁科) is one of the extant termite families (Isoptera); the site records 2 genera and 3 species. See below. See the list below."
lang: en
single_lang: true
author: 班奈特格林
family_id: serritermitidae
last_modified_at: 2026-10-30
permalink: /en/family/serritermitidae/
sitemap: true
has_map: true
taxon_search: true
breadcrumb:
  - name: "Checklist"
    url: "/en/list/"
  - name: "Serritermitidae 齿白蚁科"
    url: "/en/family/serritermitidae/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Taxonomic position"><a href="{{ site.base_url }}/en/list/">Checklist</a> › <a href="{{ site.base_url }}/en/family/serritermitidae/">Serritermitidae 齿白蚁科</a> › <span>This family</span></nav>
<header class="taxon-header">
<h1>Family <i>Serritermitidae</i> · 齿白蚁科</h1>
<p class="taxon-meta">2 genera · 3 species</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="en" data-lang-prefix="/en" data-anchors="serritermitidae,glossotermes,serritermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/en/search/">
<label class="taxon-search-label" for="taxon-search-input">Search within this family (3 species): name, distribution, or type locality</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="e.g. termite / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filter the taxa recorded under this family by name and locality; for the whole site use the <a href="{{ site.base_url }}/en/search/">full-text search</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Distribution map</h2>
{% include distribution-map.html mode="family" id="serritermitidae" %}
</section>
<section class="taxon-section taxon-intro">
<h2>About the family</h2>
<p>The family Serritermitidae was established by Holmgren in 1910 (Serritermitidae Holmgren, 1910) (14), with the type genus Serritermes Wasmann, 1897. The family name is derived from the type genus name, formed by combining the Latin serra (saw) with termes, referring to the conspicuously saw-like, many-toothed margins of the mandibles in the soldiers and reproductives of this family. This checklist records 2 genera and 3 species.</p>
<p>This family is a small family endemic to the Neotropical realm, occurring from northern South America (the Guiana Shield) to Brazil. It lacks a true worker caste. The two genera differ markedly in their way of life: Glossotermes is a wood-dwelling termite that lives inside dry, decaying fallen logs, whereas S. serrifer is a rare obligate inquiline among termites, spending its entire life within the epigeal mound nests of the termitid Cornitermes cumulans without building a nest of its own; its soldiers have sickle-shaped mandibles with serrate inner margins. In this family the soldier head is elongate with arcuate lateral margins, and bears a small, blind-ended fontanelle at the front of the head that does not communicate with the frontal gland; the antennae have 12–15 articles (12–13 in Serritermes, 13–15 in Glossotermes). The frontal gland of the soldier is extremely well developed, extending from the head into the anterior half of the thorax and abdomen; when defending, it releases the secretion through the back of the neck by self-rupture (autothysis) (26).</p>
<p class="taxon-src">This section is the standing account the site maintains for this rank and is updated on this page as the classification is revised; the checklist index is in the <a href="{{ site.base_url }}/en/list/">Checklist</a>.</p>
</section>
{%- assign fz = site.data.translations_en.fauna_families["/family/serritermitidae/"] -%}{%- if fz %}
{% include fauna-family.html fauna=fz %}
{%- endif %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Genera (2)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/en/genus/glossotermes/"><i>Glossotermes</i> 舌白蚁属</a> <span class="taxon-count">2 species</span></li><li><a href="{{ site.base_url }}/en/genus/serritermes/"><i>Serritermes</i> 齿白蚁属</a> <span class="taxon-count">1 species</span></li></ul>
</section>
<p class="taxon-more">Parent level: <a href="{{ site.base_url }}/en/list/">Checklist index</a> · <a href="{{ site.base_url }}/en/data/">Data &amp; downloads</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/en/list/">← Back to the checklist</a> · <a href="{{ site.base_url }}/en/">Home</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/en/family/serritermitidae/#taxon",
 "name": "Serritermitidae",
 "alternateName": [
  "齿白蚁科"
 ],
 "taxonRank": "Family",
 "url": "{{ site.base_url }}/en/family/serritermitidae/",
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