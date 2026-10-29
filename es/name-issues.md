---
layout: default
title: Discrepancias de nombres y cola de revisión — Isópteros actuales (termitas), lista comparativa latín–chino
description: "Lista filtrable de discrepancias entre esta lista y GBIF Backbone, Catalogue of Life y Blattodea Species File: sinónimos externos, coincidencias ambiguas y vacíos de cobertura, con descarga CSV."
lang: es
author: 班奈特格林 (Bennet Green)
date: 2026-10-29
version: 2026.10.17
keywords: [termitas, Isoptera, lista, discrepancias de nombres, revisión taxonómica, GBIF, Catalogue of Life, Blattodea Species File]
permalink: /es/list/name-issues/
pagefind: true
---
{%- assign D = site.data.name_issues -%}
{%- assign C = D.meta.counts -%}
<nav class="ni-crumbs" aria-label="Migas de pan"><a href="{{ site.base_url }}/es/">Inicio</a> › <a href="{{ site.base_url }}/es/list/">Listado</a> › Discrepancias</nav>
<h1 class="ni-title">Discrepancias de nombres y cola de revisión<span class="ni-title-alt" lang="zh-CN">命名差异与待核对</span></h1>
<p class="ni-lead">Esta página convierte los resultados de cotejo ya almacenados en caché entre esta lista y tres autoridades externas — GBIF Backbone, Catalogue of Life (ChecklistBank) y Blattodea Species File (BSF) — en una lista filtrable. Solo se muestran las entradas que requieren atención humana: <b>{{ C.total }}</b> filas que afectan a <b>{{ C.species_with_issue }}</b> especies/subespecies de {{ C.species_total }} registros. <strong>Aquí no se modifica ningún dato de la lista</strong>; las reglas de cotejo están en la <a href="{{ site.base_url }}/es/data/">página de datos</a>.</p>
<div class="ni-legend"><span><span class="ni-badge is-conflict">Conflicto de nombre</span>la base externa trata nuestro nombre como sinónimo y da su nombre aceptado: hay que decidir si renombrar, anotar o mantener.</span><span><span class="ni-badge is-match">Coincidencia incierta</span>coincidencia difusa o varias OTU candidatas con el mismo nombre, de modo que el script no puede decidir.</span><span><span class="ni-badge is-gap">Vacíos de cobertura</span>solo coincidió un rango superior, el nombre no figura o no se encuentra en BSF: afecta a los enlaces cruzados.</span></div>
<div class="ni-summary"><span class="ni-stat"><b>{{ C.total }}</b> filas por revisar</span><span class="ni-stat"><b>{{ C.by_group.conflict }}</b> conflictos</span><span class="ni-stat"><b>{{ C.by_group.match }}</b> inciertas</span><span class="ni-stat"><b>{{ C.by_group.gap }}</b> vacíos</span><span class="ni-stat"><b>{{ C.species_with_issue }}</b> taxones implicados</span><span class="ni-stat">BSF verificadas a mano: <b>{{ C.bsf_verified }}</b></span></div>
<div class="ni-app" id="ni-root" data-page-size="50" data-text-range="Filas {a}–{b} de {t}" data-text-page="Página {p} / {pages}" data-text-empty="No hay filas que coincidan; pruebe a limpiar los filtros.">
<div class="ni-controls">
<div class="ni-filters" role="group" aria-label="Filtrar por tipo">
<button type="button" class="ni-chip is-active" data-group="all" aria-pressed="true">Todas {{ C.total }}</button>
<button type="button" class="ni-chip" data-group="conflict" aria-pressed="false">Conflictos {{ C.by_group.conflict }}</button>
<button type="button" class="ni-chip" data-group="match" aria-pressed="false">Inciertas {{ C.by_group.match }}</button>
<button type="button" class="ni-chip" data-group="gap" aria-pressed="false">Vacíos {{ C.by_group.gap }}</button>
</div>
<label class="ni-field" for="ni-source">Fuente <select id="ni-source"><option value="all">Todas</option><option value="gbif">GBIF ({{ C.by_source.gbif }})</option><option value="col">Catalogue of Life ({{ C.by_source.col }})</option><option value="bsf">Blattodea Species File ({{ C.by_source.bsf }})</option></select></label>
<label class="ni-field" for="ni-q">Buscar <input type="search" id="ni-q" placeholder="Nombre científico / chino / externo / familia" autocomplete="off"></label>
<button type="button" class="ni-chip" id="ni-reset">Limpiar filtros</button>
</div>
<p class="ni-status" id="ni-status" role="status" aria-live="polite">Filas 1–50 de {{ C.total }}</p>
<div class="ni-table-wrap">
<table class="ni-table">
<thead><tr><th scope="col">Nombre</th><th scope="col">Familia</th><th scope="col">Fuente</th><th scope="col">Tipo</th><th scope="col">Registro externo</th><th scope="col">Coincidencia</th><th scope="col">Notas</th></tr></thead>
<tbody id="ni-body">
{%- for it in D.issues %}
<tr class="ni-row" data-group="{{ it.group }}" data-source="{{ it.source }}" data-q="{{ it.latin | downcase }} {{ it.zh }} {{ it.theirs | downcase }} {{ it.accepted | downcase }} {{ it.family_latin | downcase }}">
<td class="ni-name"><a href="{{ site.base_url }}/species/{{ it.slug }}/">{{ it.zh }}<i>{{ it.latin }}</i></a></td>
<td class="ni-family">{{ it.family_latin }}</td>
<td class="ni-src">{%- if it.source == 'gbif' -%}GBIF{%- elsif it.source == 'col' -%}CoL{%- else -%}BSF{%- endif -%}</td>
<td class="ni-kind"><span class="ni-badge is-{{ it.group }}">{%- if it.kind == 'synonym' -%}sinónimo{%- elsif it.kind == 'higherrank' -%}solo rango superior{%- elsif it.kind == 'missing' -%}no figura{%- elsif it.kind == 'fuzzy' -%}coincidencia difusa{%- else -%}coincidencia ambigua{%- endif -%}</span></td>
<td class="ni-ext">{%- if it.url -%}<a href="{{ it.url }}" rel="noopener external" target="_blank"><i>{{ it.theirs }}</i></a>{%- elsif it.theirs -%}<i>{{ it.theirs }}</i>{%- else -%}—{%- endif -%}{%- if it.accepted -%}<span class="ni-accepted">nombre aceptado {%- if it.accepted_url %} <a href="{{ it.accepted_url }}" rel="noopener external" target="_blank"><i>{{ it.accepted }}</i></a>{%- else %} <i>{{ it.accepted }}</i>{%- endif -%}</span>{%- endif -%}</td>
<td class="ni-match">{%- if it.match -%}<span class="ni-match-type">{{ it.match }}</span>{%- if it.confidence %} · {{ it.confidence }}%{%- endif -%}{%- endif -%}{%- if it.verified %} <span class="ni-badge is-verified">verificada</span>{%- elsif it.source == 'bsf' %} <span class="ni-badge">automática</span>{%- endif -%}</td>
<td class="ni-note">{%- if it.note -%}<span lang="zh-CN">{{ it.note }}</span>{%- else -%}—{%- endif -%}</td>
</tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="ni-empty" id="ni-empty" hidden>No hay filas que coincidan; pruebe a limpiar los filtros.</p>
<div class="ni-pager" id="ni-pager"><button type="button" id="ni-prev">‹ Anterior</button><span id="ni-pageinfo" aria-current="true">Página 1 / 7</span><button type="button" id="ni-next">Siguiente ›</button></div>
</div>
<noscript><p class="ni-noscript">Sin JavaScript esta página muestra las {{ C.total }} filas de una vez, sin filtros ni paginación.</p></noscript>
<p class="ni-download"><a href="{{ site.base_url }}/downloads/isoptera-name-issues.csv" download>Descargar la lista completa en CSV ({{ C.total }} filas)</a> · copia legible por máquina: <code>{{ site.base_url }}/data/name-issues.json</code></p>
<p class="ni-note-foot">Fechas de caché: GBIF / Catalogue of Life {{ D.meta.cache_dates.authority | slice: 0, 10 }}; Blattodea Species File {{ D.meta.cache_dates.bsf | slice: 0, 10 }}. Las filas «automática» no han sido revisadas a mano ({{ C.bsf_verified }} de {{ C.species_total }} verificadas). Esta página se genera desde las cachés del repositorio con <code>.github/workflows/build_name_issues.py</code> y se reconstruye cada vez que se actualiza la lista; los registros externos son los que muestran esas bases en cada momento.</p>
<script src="{{ site.base_url }}/assets/name-issues.js?v={{ site.time | date: '%s' }}" defer></script>
