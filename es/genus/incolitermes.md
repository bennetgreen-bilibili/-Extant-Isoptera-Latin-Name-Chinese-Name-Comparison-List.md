---
layout: default
title: "Género Incolitermes (子民白蚁属) — listado"
description: "El género Incolitermes (子民白蚁属) pertenece a la familia Termitidae (白蚁科), en la subfamilia Amitermitinae (弓白蚁亚科); el sitio registra 1 especie. Ver abajo."
lang: es
single_lang: true
author: 班奈特格林
family_id: termitidae
last_modified_at: 2026-10-30
permalink: /es/genus/incolitermes/
sitemap: true
has_map: true
taxon_search: true
breadcrumb:
  - name: "Listado"
    url: "/es/list/"
  - name: "Termitidae 白蚁科"
    url: "/es/family/termitidae/"
  - name: "Amitermitinae 弓白蚁亚科"
    url: "/es/subfamily/amitermitinae/"
  - name: "Incolitermes 子民白蚁属"
    url: "/es/genus/incolitermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Posición taxonómica"><a href="{{ site.base_url }}/es/list/">Listado</a> › <a href="{{ site.base_url }}/es/family/termitidae/">Termitidae 白蚁科</a> › <a href="{{ site.base_url }}/es/subfamily/amitermitinae/">Amitermitinae 弓白蚁亚科</a> › <a href="{{ site.base_url }}/es/genus/incolitermes/"><i>Incolitermes</i> 子民白蚁属</a> › <span>Este género</span></nav>
<header class="taxon-header">
<h1>Género <i>Incolitermes</i> · 子民白蚁属</h1>
<p class="taxon-meta">Familia <i>Termitidae</i> · 1 especie</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="es" data-lang-prefix="/es" data-anchors="incolitermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/es/search/">
<label class="taxon-search-label" for="taxon-search-input">Buscar en este género (1 especie): nombre, distribución o localidad tipo</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="p. ej. termita / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filtre por nombre y localidad los taxones registrados en este género; para todo el sitio use la <a href="{{ site.base_url }}/es/search/">búsqueda de texto completo</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Mapa de distribución</h2>
{% include distribution-map.html mode="genus" id="incolitermes" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>Acerca del género</h2>
<p>Este género pertenece a la familia <a href="{{ site.base_url }}/es/family/termitidae/">白蚁科 <i>Termitidae</i></a>, en la subfamilia <a href="{{ site.base_url }}/es/subfamily/amitermitinae/">弓白蚁亚科 <i>Amitermitinae</i></a>; el sitio registra 1 especie.</p>
<p>Especie tipo: <i>Incolitermes pumilus</i>.</p>
<p>Esta página incluye un mapa de distribución del género (registros de GBIF agregados en una cuadrícula de 1°); abra una entrada de especie para ver su localidad tipo, distribución y referencias.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etimología</h2>
<p>Del latín incola (habitante) + termes.</p>
<!-- src:S0018 -->
<p class="taxon-src">Las etimologías de esta sección son descomposiciones analíticas; las raíces siguen a Brown (1956).</p>
</section>
{%- assign fz = site.data.translations_es.fauna_genera["/genus/incolitermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Especies (1 especie)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/es/species/incolitermes-pumilus/"><i>Incolitermes pumilus</i> Hill, 1942 侏儒子民白蚁<wbr></a> <span class="taxon-type" title="Especie tipo">★ Especie tipo</span></li></ul>
</section>
<p class="taxon-more">Nivel superior: <a href="{{ site.base_url }}/es/list/">Índice del listado</a> · <a href="{{ site.base_url }}/es/subfamily/amitermitinae/">弓白蚁亚科 <i>Amitermitinae</i></a> · <a href="{{ site.base_url }}/es/data/">Datos y descargas</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/es/list/">← Volver al listado</a> · <a href="{{ site.base_url }}/es/">Inicio</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/es/genus/incolitermes/#taxon",
 "name": "Incolitermes",
 "alternateName": [
  "子民白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/es/genus/incolitermes/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Amitermitinae",
  "alternateName": [
   "弓白蚁亚科"
  ],
  "taxonRank": "Subfamily",
  "url": "{{ site.base_url }}/es/subfamily/amitermitinae/"
 }
}
</script>