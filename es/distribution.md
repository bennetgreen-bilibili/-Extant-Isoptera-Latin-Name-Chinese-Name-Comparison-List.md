---
layout: default
title: Mapas de distribución — Isópteros actuales (termitas) lista comparativa de nombres latinos y chinos
description: "Mapas de distribución en rejilla de 1° para las 13 familias de termitas, agregados a partir de registros de GBIF: método, límite de registros, sesgo de muestreo, archivos GeoJSON y política de uso del mapa base (Leaflet y teselas)."
lang: es
author: 班奈特格林 (Bennet Green)
date: 2026-10-17
keywords: [termitas, Isoptera, mapas de distribución, GBIF, biogeografía, rejilla, sesgo de muestreo, GeoJSON, Leaflet]
permalink: /es/distribution/
---

{%- assign occ = site.data.occurrence_summary -%}

# Mapas de distribución

<p>Esta página muestra las <strong>13 familias</strong> de la lista una al lado de otra. Cada punto es una <strong>celda de 1° × 1°</strong> (unos 111 km de lado); el tamaño y la opacidad del punto dependen del número de <strong>registros de GBIF</strong> en esa celda, y al hacer clic se ve la cifra exacta. El mapa solo se crea cuando entra en la ventana visible: nunca se piden teselas para un mapa que el lector no llega a ver.</p>

<p>Los nombres chinos, los nombres científicos y la clasificación de familias provienen de esta lista; las coordenadas provienen de registros de GBIF (ejemplares y observaciones), no de polígonos de distribución. Fecha de consulta: <strong>{% if occ %}{{ occ.meta.access_date }}{% else %}pendiente{% endif %}</strong>.</p>

## Método

<ol>
  <li><strong>Resolver la clave taxonómica de GBIF</strong> con <a href="https://api.gbif.org/v1/species/match?name=TERMITIDAE&amp;rank=FAMILY"><code>species/match?name=&lt;FAMILY&gt;&amp;rank=FAMILY</code></a> y tomar el usageKey canónico.</li>
  <li><strong>Descargar los registros georreferenciados</strong> de <a href="https://api.gbif.org/v1/occurrence/search"><code>occurrence/search</code></a> con <code>hasCoordinate=true</code>, <code>hasGeospatialIssue=false</code> y <code>limit=300</code>, recorriendo <code>offset</code>. Como máximo <strong>900 registros</strong> (3 páginas) por familia; solo se conservan <code>decimalLatitude</code> / <code>decimalLongitude</code> (y el código de país para el resumen).</li>
  <li><strong>Agrupar en una rejilla de 1°</strong>: índice de celda = <code>floor(lat)</code>, <code>floor(lon)</code>; la coordenada del elemento es el centro de la celda (<code>floor + 0.5</code>, tres decimales) y el número de registros de la celda pasa a ser <code>n</code>.</li>
  <li><strong>Escribir GeoJSON</strong>: un <code>FeatureCollection</code> por familia, con elementos <code>Point</code> cuya única propiedad es <code>n</code>; el bloque <code>properties</code> inicial guarda la familia, la clave de GBIF, el número de registros y celdas, el tamaño de la rejilla, la fecha de consulta y la fuente.</li>
</ol>

<p class="distribution-note">La taxonomía de referencia de GBIF no coincide exactamente con esta lista: <strong>Hodotermopsidae</strong>, <strong>Psammotermitidae</strong>, <strong>Termitogetonidae</strong> y <strong>Heterotermitidae</strong> aparecen allí dentro de Archotermopsidae y Rhinotermitidae. Para mantener la coherencia con esta lista, esas cuatro familias se construyen <em>agregando sus géneros</em> (se resuelve cada género y se suman sus registros, con el mismo límite de 900). La contrapartida es explícita: sus registros también cuentan en la familia anfitriona de GBIF, así que esos cuatro mapas se solapan con <a href="#rhinotermitidae">Rhinotermitidae</a> y <a href="#archotermopsidae">Archotermopsidae</a>.</p>

## Cómo leer los mapas

<ul>
  <li><strong>Un punto es una celda, no un registro</strong>: una celda con 2 registros y otra con 200 se dibujan igual, diferenciadas por tamaño y opacidad.</li>
  <li><strong>Más oscuro significa más registros</strong>, es decir, más personas recolectaron allí y publicaron en GBIF; no significa mayor abundancia de termitas.</li>
  <li><strong>El zoom está limitado al nivel 9</strong>: los datos son de 1°, así que ampliar más no aporta información y solo gastaría teselas.</li>
  <li>El zoom con rueda está desactivado por defecto (la página es larga); use el control +/− cuando lo necesite.</li>
</ul>

<div class="distribution-caveat">
<strong>Advertencias</strong>
<ul>
  <li><strong>Sesgo de muestreo</strong>: los registros de GBIF se concentran en Norteamérica y Europa; las regiones tropicales (sobre todo África, el sudeste asiático y Sudamérica) están poco representadas. Una celda vacía suele significar que nadie muestreó allí, no que no haya termitas.</li>
  <li><strong>Vacíos por país</strong>: muchas colecciones nacionales no están digitalizadas, de modo que los huecos con forma de frontera no son límites de distribución.</li>
  <li><strong>No es un mapa de área de distribución</strong>: no hay modelado de nicho, ni inferencia de áreas, ni filtrado de registros adventicios o de interior.</li>
  <li><strong>Límite de registros</strong>: 900 por familia, tomados en el orden estable de respuesta de GBIF: una muestra reproducible, pero no aleatoria.</li>
  <li><strong>Cambia</strong>: GBIF añade y revisa registros a diario; al regenerar los datos (véase <code>--refresh</code>) cambian las cifras.</li>
</ul>
</div>

## Mapas por familia

<p>Cada tarjeta muestra el nombre chino y el nombre científico de la familia, con el número de registros, el de celdas y el de especies en esta lista; al pie hay enlaces al archivo GeoJSON y a la ficha de GBIF.</p>

{% include distribution-map.html mode="page" %}

## Resumen

{% if occ %}
<table>
<thead>
<tr>
  <th>Familia</th>
  <th>Clave GBIF</th>
  <th class="num">Registros</th>
  <th class="num">Celdas</th>
  <th class="num">Especies aquí</th>
  <th>Resolución</th>
</tr>
</thead>
<tbody>
{%- for f in occ.families %}
<tr>
  <td><a href="#{{ f.id }}">{{ f.zh }} <i class="latin">{{ f.latin }}</i></a></td>
  <td>{% if f.gbif_key %}<a href="{{ f.gbif_url }}" rel="noopener">{{ f.gbif_key }}</a>{% else %}agregado por género{% endif %}</td>
  <td class="num">{{ f.records }}</td>
  <td class="num">{{ f.cells }}</td>
  <td class="num">{{ f.species }}</td>
  <td>{% if f.resolution == 'genus_aggregate' %}agregado por género{% else %}clave de familia{% endif %}</td>
</tr>
{%- endfor %}
<tr>
  <td><strong>Total</strong></td>
  <td>—</td>
  <td class="num"><strong>{{ occ.meta.records_families }}</strong></td>
  <td class="num"><strong>{{ occ.meta.cells_families }}</strong></td>
  <td class="num"><strong>3071</strong></td>
  <td>13 familias</td>
</tr>
</tbody>
</table>
{% else %}
<p>Aún no se han generado los datos de resumen (falta <code>_data/occurrence_summary.json</code>).</p>
{% endif %}

## Archivos de datos

<p>Todos los mapas se ofrecen en GeoJSON puro, listos para QGIS o cualquier biblioteca GeoJSON; las coordenadas son centros de celda <code>[longitud, latitud]</code>. El nombre del archivo coincide con el id de la familia, que es también el ancla en esta página.</p>

<ul>
{%- if occ -%}
{%- for f in occ.families %}
  <li><a href="{{ site.base_url }}/{{ f.file }}" download><code>{{ f.file }}</code></a> — {{ f.latin }}, {{ f.records }} registros en {{ f.cells }} celdas</li>
{%- endfor -%}
  <li><code>_data/occurrence_summary.json</code> — resumen (registros, celdas, registros por país, fecha de consulta); todas las cifras de esta página salen de él (archivo de datos de Jekyll, se distribuye con el repositorio, no se publica aparte)</li>
  <li><a href="{{ site.base_url }}/es/data/">Datos estructurados</a> — árbol taxonómico y JSON por taxón, compañeros de estos mapas</li>
{%- else %}
  <li>Archivos pendientes.</li>
{%- endif %}
</ul>

<h3 id="genus-files">Archivos por género</h3>

{% if occ and occ.genera and occ.genera.size > 0 %}
<p>Los géneros con 12 especies o más tienen su propio mapa: <strong>{{ occ.genera.size }}</strong> archivos, cada uno por debajo de 60 KB.</p>
<ul>
{%- for g in occ.genera %}
  <li><a href="{{ site.base_url }}/{{ g.file }}" download><code>{{ g.file }}</code></a> — <i class="latin">{{ g.latin }}</i> ({{ g.family_zh }}), {{ g.records }} registros en {{ g.cells }} celdas</li>
{%- endfor %}
</ul>
{% else %}
<p>Esta ejecución no generó archivos por género (el nivel de género es opcional; el de familia siempre se genera).</p>
{% endif %}

## Fuentes y licencia

<ul>
  <li><strong>Registros</strong>: GBIF.org (Global Biodiversity Information Facility) mediante la <a href="https://api.gbif.org/v1/occurrence/search">API de ocurrencias de GBIF</a>, consultada el {% if occ %}{{ occ.meta.access_date }}{% endif %}. La licencia de cada registro figura en GBIF; cite según las <a href="https://www.gbif.org/citation-guidelines">pautas de citación de GBIF</a> (DOI del conjunto de datos).</li>
  <li><strong>Taxonomía de referencia</strong>: GBIF Backbone Taxonomy (<a href="https://api.gbif.org/v1/species/match">species/match</a>); la clasificación de familias usada aquí (Engel 2021 y posteriores) está en la <a href="{{ site.base_url }}/es/list/">lista</a>.</li>
  <li><strong>Mapa base</strong>: teselas ráster públicas de GBIF (<a href="https://tile.gbif.org/">tile.gbif.org</a>, generadas a partir de datos de OpenMapTiles / OpenStreetMap), con las teselas de OpenStreetMap como alternativa; datos del mapa © colaboradores de OpenStreetMap, véase la <a href="https://www.openstreetmap.org/copyright">página de copyright de OSM</a>.</li>
  <li><strong>Motor de mapas</strong>: Leaflet 1.9.4, BSD-2-Clause, alojado en el propio sitio (<code>assets/vendor/leaflet/</code>); nunca se carga desde una CDN en tiempo de ejecución.</li>
  <li><strong>Datos derivados</strong>: los GeoJSON y el JSON de resumen de esta página los produce este sitio y se publican con él bajo CC BY 4.0.</li>
</ul>

<h3 id="tiles">Mapa base y política de uso de teselas</h3>

<p>Los mapas se cargan de forma diferida: la instancia de Leaflet y sus teselas se crean solo cuando el contenedor entra en la ventana visible. No hay precarga, no se descargan teselas en el servidor y el zoom está limitado al nivel 9 para acotar el número de teselas. Se prefiere el servicio público de teselas de GBIF (GBIF publica estas teselas para GBIF.org y para usuarios de su API), con las teselas de OpenStreetMap como alternativa que respeta la <a href="https://operations.osmfoundation.org/policies/tiles/">política de uso de teselas de OSM</a> (atribución y <code>referrerpolicy="no-referrer-when-downgrade"</code>). La lista de comprobación completa está en <code>_tools/分布图与瓦片使用政策.md</code>.</p>

<p>¿Por qué nivel de familia/género y no de especie? Un mapa por especie supondría <strong>3.071</strong> páginas, cada una con sus datos y su conjunto de teselas: mucho más de lo razonable para servicios públicos de teselas, y sin sentido para agregados de 1° que están dominados por el esfuerzo de muestreo. La agregación por familia/género es el compromiso deliberado.</p>

<h3 id="regenerate">Regenerar</h3>

<pre class="cite-text">python .github/workflows/build_occurrence_geojson.py --write --refresh</pre>

<p>Sin <code>--refresh</code> se reutiliza la caché de <code>_tmp/gbif_cache/</code> (una nueva ejecución no vuelve a descargar); con <code>--check</code> solo se verifica que los archivos ya incluidos coincidan con el script.</p>
