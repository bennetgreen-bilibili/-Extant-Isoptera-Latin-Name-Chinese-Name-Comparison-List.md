---
layout: default
title: "Familia Serritermitidae (齿白蚁科) — listado"
description: "La familia Serritermitidae (齿白蚁科) es una de las familias de termitas actuales (Isoptera); el sitio registra 2 géneros y 3 especies. Ver abajo. Ver el listado."
lang: es
single_lang: true
author: 班奈特格林
family_id: serritermitidae
last_modified_at: 2026-10-30
permalink: /es/family/serritermitidae/
sitemap: true
has_map: true
taxon_search: true
breadcrumb:
  - name: "Listado"
    url: "/es/list/"
  - name: "Serritermitidae 齿白蚁科"
    url: "/es/family/serritermitidae/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="Posición taxonómica"><a href="{{ site.base_url }}/es/list/">Listado</a> › <a href="{{ site.base_url }}/es/family/serritermitidae/">Serritermitidae 齿白蚁科</a> › <span>Esta familia</span></nav>
<header class="taxon-header">
<h1>Familia <i>Serritermitidae</i> · 齿白蚁科</h1>
<p class="taxon-meta">2 géneros · 3 especies</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="es" data-lang-prefix="/es" data-anchors="serritermitidae,glossotermes,serritermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/es/search/">
<label class="taxon-search-label" for="taxon-search-input">Buscar en esta familia (3 especies): nombre, distribución o localidad tipo</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="p. ej. termita / Amitermes / Australia" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">Filtre por nombre y localidad los taxones registrados en esta familia; para todo el sitio use la <a href="{{ site.base_url }}/es/search/">búsqueda de texto completo</a>.</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>Mapa de distribución</h2>
{% include distribution-map.html mode="family" id="serritermitidae" %}
</section>
<section class="taxon-section taxon-intro">
<h2>Acerca de la familia</h2>
<p>La familia Serritermitidae fue establecida por Holmgren en 1910 (Serritermitidae Holmgren, 1910) (14), con el género tipo Serritermes Wasmann, 1897. El nombre de la familia deriva del nombre del género tipo, formado por la combinación del latín serra (sierra) con termes, en referencia a los márgenes de las mandíbulas conspicuamente aserrados y con numerosos dientes en los soldados y reproductores de esta familia. Esta lista de verificación registra 2 géneros y 3 especies.</p>
<p>Esta familia es una familia pequeña endémica de la región neotropical, presente desde el norte de América del Sur (el escudo de las Guayanas) hasta Brasil. Carece de una casta de obreras verdadera. Los dos géneros difieren marcadamente en su modo de vida: Glossotermes es una termita que habita en la madera y vive dentro de troncos caídos secos y en descomposición, mientras que S. serrifer es un inquilino obligado raro entre las termitas, que pasa toda su vida dentro de los nidos-montículo epigeos de la termítido Cornitermes cumulans sin construir un nido propio; sus soldados tienen mandíbulas en forma de hoz con márgenes internos aserrados. En esta familia la cabeza del soldado es alargada, con márgenes laterales arqueados, y presenta una fontanela pequeña y de fondo ciego en la parte anterior de la cabeza que no se comunica con la glándula frontal; las antenas tienen 12–15 artejos (12–13 en Serritermes, 13–15 en Glossotermes). La glándula frontal del soldado está sumamente bien desarrollada, extendiéndose desde la cabeza hasta la mitad anterior del tórax y del abdomen; al defenderse, libera la secreción por la parte posterior del cuello mediante autorruptura (autotisis) (26).</p>
<p class="taxon-src">Esta sección es la explicación permanente que el sitio mantiene para este nivel y se actualiza en esta página conforme se revisa la clasificación; el índice del listado está en el <a href="{{ site.base_url }}/es/list/">Listado</a>.</p>
</section>
{%- assign fz = site.data.translations_es.fauna_families["/family/serritermitidae/"] -%}{%- if fz %}
{% include fauna-family.html fauna=fz %}
{%- endif %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>Géneros (2)</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/es/genus/glossotermes/"><i>Glossotermes</i> 舌白蚁属</a> <span class="taxon-count">2 especies</span></li><li><a href="{{ site.base_url }}/es/genus/serritermes/"><i>Serritermes</i> 齿白蚁属</a> <span class="taxon-count">1 especie</span></li></ul>
</section>
<p class="taxon-more">Nivel superior: <a href="{{ site.base_url }}/es/list/">Índice del listado</a> · <a href="{{ site.base_url }}/es/data/">Datos y descargas</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/es/list/">← Volver al listado</a> · <a href="{{ site.base_url }}/es/">Inicio</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/es/family/serritermitidae/#taxon",
 "name": "Serritermitidae",
 "alternateName": [
  "齿白蚁科"
 ],
 "taxonRank": "Family",
 "url": "{{ site.base_url }}/es/family/serritermitidae/",
 "isPartOf": {
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