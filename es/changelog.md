---
layout: default
title: Historial de versiones — isópteros actuales, lista comparativa latín–chino
description: "Historial de publicaciones de la lista: cada versión es su fecha de publicación (AAAA.MM.DD), con cambios, archivos de archivo y DOI; suscripción por Atom."
lang: es
author: 班奈特格林 (Bennet Green)
date: 2026-10-29
version: 2026.10.30
permalink: /es/changelog/
---
{%- assign CH = site.data.changelog -%}
<h1>Historial de versiones <span class="page-title-alt" lang="zh-CN">版本记录</span></h1>
<p class="cl-lead">Cada número de versión es la fecha de publicación de la lista (AAAA.MM.DD). Aquí se recogen todos los cambios archivados. Suscripción: <a href="{{ site.base_url }}/changelog.atom">changelog.atom (Atom)</a> · archivo fuente: <code>dataset/CHANGELOG.md</code> · DOI del conjunto de datos: <a href="https://doi.org/{{ site.dataset.doi }}">{{ site.dataset.doi }}</a>. Los textos de las entradas se mantienen en su idioma original.</p>
{%- for v in CH.versions %}
<section class="cl-version" id="v{{ v.version | replace: '.', '-' }}">
<h2 class="cl-title"><span class="cl-ver">{{ v.version }}</span> <span class="cl-name" lang="zh-CN">{{ v.title }}</span></h2>
<ul class="cl-items">
{%- for it in v.items %}
<li class="cl-item{% if it.depth == 1 %} cl-sub{% endif %}" lang="zh-CN">{{ it.html }}</li>
{%- endfor %}
</ul>
</section>
{%- endfor %}
<p class="cl-note">Generado por <code>_tools/build_changelog.py</code> a partir de <code>dataset/CHANGELOG.md</code>; el CHANGELOG del repositorio y el paquete archivado siguen siendo la fuente autorizada. Ninguna entrada constituye un acto nomenclatural.</p>
