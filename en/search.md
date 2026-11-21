---
layout: default
title: Full-site search
description: "Full-text search across the checklist, 3089 species pages, statistics, data and blog: Chinese (traditional too), Latin names and pinyin. Local queries stay in the browser; the optional AI chat sends questions to Cloudflare."
lang: en
author: 班奈特格林
date: 2026-10-17
version: 2026.11.21
keywords: [termites, Isoptera, search, full-text, Pagefind, AI chat, Cloudflare]
permalink: /en/search/
noindex: true
sitemap: false
pagefind: true
---

# Full-site search

{% include ai-chat-block.html %}

<p>To look up a <strong>taxon</strong> (family / subfamily / genus / species / subspecies), the <a href="{{ site.base_url }}/en/list/">index search box</a> is faster and jumps straight to the matching family / subfamily / genus / species page; the search below covers the whole site's text.</p>

<h2 id="local-fulltext">{{ site.data.i18n[page.lang].search_local_heading }}</h2>

<p>Search everything on the site: the checklist text, all 3089 species pages, the statistics and data pages, and blog posts. The index is generated at build time by the open-source <a href="https://pagefind.app/">Pagefind</a> tool; queries are matched against that local index in your browser and the search terms are not sent to any server, this site's included.</p>

<div id="pagefind-search" data-pagefind-ignore data-lang="en" data-base="{{ site.base_url }}"></div>

<noscript><p>Full-text search requires JavaScript. You can still use the <a href="{{ site.base_url }}/en/list/">checklist search</a>.</p></noscript>
