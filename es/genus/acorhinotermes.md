---
layout: default
title: "Género Acorhinotermes (尖鼻白蚁属) — listado"
description: "El género Acorhinotermes (尖鼻白蚁属) pertenece a la familia Rhinotermitidae (鼻白蚁科); el sitio registra 3 especies. La morfología y la etimología se resumen arriba."
lang: es
single_lang: true
author: 班奈特格林
family_id: rhinotermitidae
last_modified_at: 2026-10-30
permalink: /es/genus/acorhinotermes/
sitemap: true
has_map: true
taxon_search: true
has_photos: true
image: "/assets/images/rhinotermitidae.jpg"
breadcrumb:
  - name: "Listado"
    url: "/es/list/"
  - name: "Rhinotermitidae 鼻白蚁科"
    url: "/es/family/rhinotermitidae/"
  - name: "Acorhinotermes 尖鼻白蚁属"
    url: "/es/genus/acorhinotermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Posición taxonómica"><a href="{{ site.base_url }}/es/list/">Listado</a> › <a href="{{ site.base_url }}/es/family/rhinotermitidae/">Rhinotermitidae 鼻白蚁科</a> › <a href="{{ site.base_url }}/es/genus/acorhinotermes/"><i>Acorhinotermes</i> 尖鼻白蚁属</a> › <span>Este género</span></nav>
<header class="taxon-header">
<h1>Género <i>Acorhinotermes</i> · 尖鼻白蚁属</h1>
<p class="taxon-meta">Familia <i>Rhinotermitidae</i> · 3 especies</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="es" data-lang-prefix="/es" data-anchors="acorhinotermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/es/search/">
<label class="taxon-search-label" for="taxon-search-input">Buscar en este género (3 especies): nombre, distribución o localidad tipo</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="p. ej. termita / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filtre por nombre y localidad los taxones registrados en este género; para todo el sitio use la <a href="{{ site.base_url }}/es/search/">búsqueda de texto completo</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Mapa de distribución</h2>
{% include distribution-map.html mode="genus" id="acorhinotermes" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="genus" id="acorhinotermes" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>Acerca del género</h2>
<p>Este género pertenece a la familia <a href="{{ site.base_url }}/es/family/rhinotermitidae/">鼻白蚁科 <i>Rhinotermitidae</i></a>; el sitio registra 3 especies.</p>
<p>Especie tipo: <i>Acorhinotermes subfusciceps</i>.</p>
<p>Esta página incluye un mapa de distribución del género (registros de GBIF agregados en una cuadrícula de 1°); abra una entrada de especie para ver su localidad tipo, distribución y referencias.</p>
</section>
<section class="taxon-section taxon-etymology" data-pagefind-ignore>
<h2>Etimología</h2>
<p>Contiene el griego rhis (nariz) + latín termes; la derivación del prefijo es incierta.</p>
<!-- src:S0018 -->
<p class="taxon-src">Las etimologías de esta sección son descomposiciones analíticas; las raíces siguen a Brown (1956).</p>
</section>
{%- assign fz = site.data.translations_es.fauna_genera["/genus/acorhinotermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Especies (3 especies)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/es/species/acorhinotermes-claritae/"><i>Acorhinotermes claritae</i> Castro & Scheffrahn, 2019 克拉丽塔尖鼻<wbr>白蚁</a></li><li><a href="{{ site.base_url }}/es/species/acorhinotermes-murui/"><i>Acorhinotermes murui</i> Castro, 2023 穆鲁伊尖鼻白<wbr>蚁</a></li><li><a href="{{ site.base_url }}/es/species/acorhinotermes-subfusciceps/"><i>Acorhinotermes subfusciceps</i> Emerson, 1925 棕头尖鼻白蚁<wbr></a> <span class="taxon-type" title="Especie tipo">★ Especie tipo</span></li></ul>
</section>
<p class="taxon-more">Nivel superior: <a href="{{ site.base_url }}/es/list/">Índice del listado</a> · <a href="{{ site.base_url }}/es/family/rhinotermitidae/">鼻白蚁科 <i>Rhinotermitidae</i></a> · <a href="{{ site.base_url }}/es/data/">Datos y descargas</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/es/list/">← Volver al listado</a> · <a href="{{ site.base_url }}/es/">Inicio</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/es/genus/acorhinotermes/#taxon",
 "name": "Acorhinotermes",
 "alternateName": [
  "尖鼻白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/es/genus/acorhinotermes/",
 "isPartOf": {
  "@type": "Dataset",
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
  "url": "{{ site.base_url }}/es/family/rhinotermitidae/"
 }
}
</script>