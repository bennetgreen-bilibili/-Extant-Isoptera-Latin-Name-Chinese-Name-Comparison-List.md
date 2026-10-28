---
layout: default
title: "Referencias y DOI — isópteros (termitas) actuales: lista comparativa latín–chino"
description: "Las 77 referencias de la lista, enriquecidas: enlaces DOI, registros de Crossref, citas en estilo GB/T 7714, APA 7 y Vancouver, más BibTeX, RIS y CSL-JSON, para copiar o descargar."
lang: es
author: 班奈特格林 (Bennet Green)
date: 2026-10-17
version: 2026.10.17
keywords: [termitas, Isoptera, referencias, DOI, Crossref, GB/T 7714, APA, BibTeX, RIS, CSL-JSON]
permalink: /es/references/
---

# Referencias y DOI

{%- assign refmeta = site.data.references.meta -%}
{%- assign refcounts = refmeta.counts -%}

<p>Las {{ refcounts.total }} referencias del final del <a href="{{ site.base_url }}/es/list/#references">listado</a> se amplían aquí una por una: <strong>enlace DOI</strong>, <strong>registro de Crossref</strong> y citas en estilo <strong>GB/T 7714</strong>, <strong>APA 7</strong> y <strong>Vancouver</strong>, además de formatos legibles por máquina <strong>BibTeX / RIS / CSL-JSON</strong>.</p>

## Cobertura

<ul>
  <li>Referencias en total: <strong>{{ refcounts.total }}</strong> (una por cada número del listado original).</li>
  <li>Con DOI: <strong>{{ refcounts.with_doi }}</strong>, de las cuales <strong>{{ refcounts.crossref_resolved }}</strong> fueron confirmadas por un registro de Crossref.</li>
  <li>DOI candidatos (búsqueda en Crossref, <strong>pendientes de revisión manual</strong>): <strong>{{ refcounts.candidates }}</strong>.</li>
  <li>Escaneos de descripciones originales en BHL: <strong>{{ refcounts.bhl }}</strong> (mejora opcional, véase abajo).</li>
</ul>

<h2 id="sources">Fuentes</h2>

<ul>
  <li><strong>La lista de origen</strong>: las 77 entradas del final del listado, con su numeración y redacción originales; no se reescribe ni se fusiona nada.</li>
  <li><strong>Crossref</strong> (<a href="https://www.crossref.org/" target="_blank" rel="noopener">crossref.org</a>): registros bibliográficos consultados por DOI (título, autores, revista, volumen, número, páginas, editor, tipo, ISSN, número de citas). Las entradas sin DOI solo se buscan bibliográficamente y las coincidencias se listan como <strong>candidatos</strong> para revisión manual.</li>
  <li><strong>BHL</strong> (<a href="https://about.biodiversitylibrary.org/" target="_blank" rel="noopener">Biodiversity Heritage Library</a>): puede añadir enlaces a escaneos de descripciones originales antiguas. Requiere una clave de API gratuita; es opcional.</li>
</ul>

<h2 id="howto">Cómo citar</h2>

<ul>
  <li><strong>Estilo GB/T 7714</strong>: autores (los tres primeros más <em>et al.</em>), título, marca de tipo documental ([J] artículo, [M] monografía, [C] congreso…), revista, año, volumen(número), páginas, DOI.</li>
  <li><strong>APA 7</strong>: autores, año, título, revista, volumen(número), páginas y <code>https://doi.org/…</code>.</li>
  <li><strong>Vancouver</strong>: autores (los seis primeros más <em>et al.</em>), título, revista, año;volumen(número):páginas.</li>
  <li>Todos los campos provienen del registro de Crossref; <strong>los campos que Crossref no tiene se dejan vacíos: no se deducen ni se inventan</strong>. La marca de tipo sigue el <code>type</code> de Crossref (p. ej. <code>book-chapter</code> → [M]).</li>
  <li>Las mayúsculas de títulos y autores siguen a Crossref; algunos registros guardan los nombres en mayúsculas y solo se normalizan a mayúscula inicial, sin traducción ni reescritura.</li>
  <li>Las entradas marcadas «<strong>coincidencia automática sin verificar</strong>» obtuvieron su DOI por similitud de título más coincidencia de año: verifíquelo antes de citar. Las marcadas «<strong>sin DOI en el original</strong>» solo muestran candidatos, que no se adoptaron.</li>
</ul>

<h2 id="bhl">Descripciones originales en BHL</h2>

<p>Las descripciones originales de trabajos taxonómicos antiguos suelen estar en BHL. Con una clave gratuita en <code>BHL_API_KEY</code>, ejecute <code>python .github/workflows/build_references.py --write --bhl</code>: el script busca por título en BHL y añade <code>bhl.url</code> (enlace a nivel de bibliografía, sin descargar escaneos). Actualmente <strong>{{ refcounts.bhl }}</strong> entradas tienen ese enlace; sin clave, o si BHL no responde, el campo queda en <code>null</code> y el resto de la página no se ve afectado.</p>

<h2 id="download">Descarga y uso masivo</h2>

<p>Los datos completos (cita original, estado del DOI, campos de Crossref, tres estilos, BibTeX, RIS, CSL-JSON, BHL) están en <a href="{{ site.base_url }}/data/references.json"><code>data/references.json</code></a>. El botón «Exportar CSL-JSON» sobre la lista genera en el navegador un arreglo CSL-JSON listo para Zotero / EndNote / Mendeley (sin JavaScript, use el enlace JSON).</p>

<p>Esta página es una <strong>vista enriquecida</strong>: las entradas canónicas siguen siendo las de la <a href="{{ site.base_url }}/es/list/#references">lista de referencias al final del listado</a>. Aquí solo se añaden la resolución de DOI y los formatos legibles por máquina; la numeración, el número de entradas y la redacción son idénticos.</p>

<p>Para citar el listado completo (conjunto de datos): 班奈特格林. (2026). Lista comparativa de nombres latinos y chinos de los isópteros actuales (versión {{ site.dataset.version }}) [Conjunto de datos]. {{ site.dataset.publisher }}. <a href="https://doi.org/{{ site.dataset.doi }}">https://doi.org/{{ site.dataset.doi }}</a></p>

{% include references.html %}
