---
layout: default
title: Descargas — isópteros (termitas) actuales: lista comparativa latín–chino
description: "Zona de descargas: archivos del sitio, listados automáticamente desde la carpeta downloads/ del repositorio."
lang: es
author: 班奈特格林 (Bennet Green)
permalink: /es/download/
---

# Descargas

<p>Esta página lista automáticamente todos los archivos de la carpeta <code>downloads/</code> para descargarlos directamente. Lo que el autor coloque en la carpeta <code>downloads/</code> del repositorio aparecerá aquí automáticamente, sin necesidad de editar la página.</p>

{% assign downloads = site.static_files | where_exp: "f", "f.path contains '/downloads/'" %}
{% assign downloads = downloads | sort: "name" %}

{% if downloads.size > 0 %}
<p><strong>{{ downloads.size }}</strong> archivo(s) disponible(s):</p>
<table class="stats-table">
<thead><tr><th>Archivo</th><th>Formato</th></tr></thead>
<tbody>
{% for f in downloads %}
  <tr>
    <td><a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md{{ f.path }}" download>{{ f.name }}</a></td>
    <td class="num">{{ f.extname | remove_first: '.' | upcase }}</td>
  </tr>
{% endfor %}
</tbody>
</table>
{% else %}
<p>Todavía no hay archivos en la zona de descargas. El autor puede añadir archivos a la carpeta <code>downloads/</code> y los enlaces de descarga aparecerán aquí automáticamente.</p>
{% endif %}
