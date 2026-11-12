---
layout: default
title: "Género Hodotermopsis (原白蚁属) — listado"
description: "El género Hodotermopsis (原白蚁属) pertenece a la familia Hodotermopsidae (原白蚁科); el sitio registra 1 especie. La morfología y la etimología se resumen arriba."
lang: es
single_lang: true
author: 班奈特格林
family_id: hodotermopsidae
last_modified_at: 2026-10-30
permalink: /es/genus/hodotermopsis/
sitemap: true
has_map: true
taxon_search: true
has_photos: true
image: "/assets/images/hodotermopsidae.jpg"
breadcrumb:
  - name: "Listado"
    url: "/es/list/"
  - name: "Hodotermopsidae 原白蚁科"
    url: "/es/family/hodotermopsidae/"
  - name: "Hodotermopsis 原白蚁属"
    url: "/es/genus/hodotermopsis/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Posición taxonómica"><a href="{{ site.base_url }}/es/list/">Listado</a> › <a href="{{ site.base_url }}/es/family/hodotermopsidae/">Hodotermopsidae 原白蚁科</a> › <a href="{{ site.base_url }}/es/genus/hodotermopsis/"><i>Hodotermopsis</i> 原白蚁属</a> › <span>Este género</span></nav>
<header class="taxon-header">
<h1>Género <i>Hodotermopsis</i> · 原白蚁属</h1>
<p class="taxon-meta">Familia <i>Hodotermopsidae</i> · 1 especie</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="es" data-lang-prefix="/es" data-anchors="hodotermopsis" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/es/search/">
<label class="taxon-search-label" for="taxon-search-input">Buscar en este género (1 especie): nombre, distribución o localidad tipo</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="p. ej. termita / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filtre por nombre y localidad los taxones registrados en este género; para todo el sitio use la <a href="{{ site.base_url }}/es/search/">búsqueda de texto completo</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Mapa de distribución</h2>
{% include distribution-map.html mode="genus" id="hodotermopsis" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="genus" id="hodotermopsis" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>Acerca del género</h2>
<p>Este género pertenece a la familia <a href="{{ site.base_url }}/es/family/hodotermopsidae/">原白蚁科 <i>Hodotermopsidae</i></a>; el sitio registra 1 especie.</p>
<p>Especie tipo: <i>Hodotermopsis sjostedti</i>.</p>
<p>Esta página incluye un mapa de distribución del género (registros de GBIF agregados en una cuadrícula de 1°); abra una entrada de especie para ver su localidad tipo, distribución y referencias.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etimología</h2>
<p>Del griego hodos (sendero) + -termopsis.</p>
<!-- src:S0018 -->
<p class="taxon-src">Las etimologías de esta sección son descomposiciones analíticas; las raíces siguen a Brown (1956).</p>
</section>
{%- assign fz = site.data.translations_es.fauna_genera["/genus/hodotermopsis/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Especies (1 especie)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/es/species/hodotermopsis-sjostedti/"><i>Hodotermopsis sjostedti</i> Holmgren, 1911 山林原白蚁</a> <span class="taxon-type" title="Especie tipo">★ Especie tipo</span></li></ul>
</section>
<p class="taxon-more">Nivel superior: <a href="{{ site.base_url }}/es/list/">Índice del listado</a> · <a href="{{ site.base_url }}/es/family/hodotermopsidae/">原白蚁科 <i>Hodotermopsidae</i></a> · <a href="{{ site.base_url }}/es/data/">Datos y descargas</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/es/list/">← Volver al listado</a> · <a href="{{ site.base_url }}/es/">Inicio</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/es/genus/hodotermopsis/#taxon",
 "name": "Hodotermopsis",
 "alternateName": [
  "原白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/es/genus/hodotermopsis/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Hodotermopsidae",
  "alternateName": [
   "原白蚁科"
  ],
  "taxonRank": "Family",
  "url": "{{ site.base_url }}/es/family/hodotermopsidae/"
 }
}
</script>