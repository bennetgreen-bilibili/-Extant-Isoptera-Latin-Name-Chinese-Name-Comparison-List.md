---
layout: default
title: Búsqueda en todo el sitio
description: "Búsqueda de texto completo en el listado, las 3089 páginas de especies, estadísticas, datos y blog: chino (también tradicional), nombres latinos y pinyin. Las consultas locales no salen del navegador; la búsqueda semántica con IA, opcional, las envía a Cloudflare."
lang: es
author: 班奈特格林
date: 2026-10-17
version: 2026.10.30
keywords: [termitas, Isoptera, búsqueda, texto completo, Pagefind, búsqueda IA, Cloudflare]
permalink: /es/search/
noindex: true
sitemap: false
pagefind: true
---

# Búsqueda en todo el sitio

{% include ai-search-block.html %}

<p>Para buscar un <strong>taxón</strong> (familia / subfamilia / género / especie / subespecie), el <a href="{{ site.base_url }}/es/list/">buscador del índice</a> es más rápido y lleva directamente a la página correspondiente; la búsqueda de abajo cubre el texto de todo el sitio.</p>

<h2 id="local-fulltext">{{ site.data.i18n[page.lang].search_local_heading }}</h2>

<p>Busca en todo el sitio: el texto del listado, las 3089 páginas de especies, las tablas estadísticas, las páginas de datos y el blog. El índice se genera al compilar el sitio con la herramienta libre <a href="https://pagefind.app/">Pagefind</a>; las consultas se resuelven contra ese índice local en su navegador y los términos no se envían a ningún servidor, tampoco al de este sitio.</p>

<div id="pagefind-search" data-pagefind-ignore data-lang="es" data-base="{{ site.base_url }}"></div>

<noscript><p>La búsqueda de texto completo requiere JavaScript. Puede usar el <a href="{{ site.base_url }}/es/list/">buscador del listado</a>.</p></noscript>
