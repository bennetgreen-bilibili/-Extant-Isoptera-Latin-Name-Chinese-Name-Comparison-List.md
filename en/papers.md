---
layout: default
title: Literature search — Extant Isoptera (Termites) Latin–Chinese Name Comparison List
description: Search termite literature by Latin name, Chinese name or multiple keywords; termite-only scope by default, multi-keyword matching, synonyms, Chinese-only filtering, abstracts and GB/T 7714 / BibTeX / RIS export.
lang: en
author: 班奈特格林
date: 2026-10-30
version: 2026.10.30
keywords: [termites, Isoptera, literature search, papers, OpenAlex, Crossref, abstracts]
permalink: /en/papers/
---

{%- assign T = site.data.i18n[page.lang] | default: site.data.i18n['zh-CN'] -%}

<h1 class="papers-title">{{ T.papers_heading }}</h1>
<p class="papers-lead">Search termite literature by Latin name, Chinese name or multiple keywords. Results are limited to termites (Isoptera) by default; separate keywords with spaces and all must match. Synonyms are merged automatically; abstracts and citations are included.</p>

<div id="papers-app" class="papers-app" data-base="{{ site.base_url }}" data-index-url="{{ site.base_url }}/search-index.json" data-papers-url="{{ site.base_url }}/papers-index.json" data-lang="en" data-pagefind-ignore>
  <form id="papers-form" class="papers-form" role="search" novalidate>
    <div class="papers-search-row">
      <div class="papers-search-wrap">
        <label class="visually-hidden" for="papers-q">{{ T.papers_placeholder }}</label>
        <input id="papers-q" class="papers-input" type="search" name="q" placeholder="{{ T.papers_placeholder }}" autocomplete="off" spellcheck="false" aria-describedby="papers-hint" aria-autocomplete="list" aria-controls="papers-suggestions" aria-expanded="false">
        <ul id="papers-suggestions" class="papers-suggestions" role="listbox" hidden></ul>
      </div>
      <button id="papers-submit" class="papers-submit" type="submit">{{ T.papers_search }}</button>
    </div>
    <p id="papers-selected" class="papers-selected" hidden></p>
    <p id="papers-hint" class="papers-hint">{{ T.papers_hint }}</p>
    <div class="papers-options">
      <label class="papers-check"><input id="papers-scope" type="checkbox" checked> {{ T.papers_scope }}</label>
      <label class="papers-check"><input id="papers-syn" type="checkbox" checked> {{ T.papers_synonyms }}</label>
      <label class="papers-check"><input id="papers-zh" type="checkbox"> {{ T.papers_chinese_only }}</label>
      <label class="papers-check"><input id="papers-has-abstract" type="checkbox"> {{ T.papers_has_abstract }}</label>
      <label class="papers-check"><input id="papers-fulltext" type="checkbox"> {{ T.papers_fulltext }}</label>
      <label class="papers-sort-label">{{ T.papers_sort }}
        <select id="papers-sort" class="papers-sort">
          <option value="relevance">{{ T.papers_sort_relevance }}</option>
          <option value="newest">{{ T.papers_sort_newest }}</option>
          <option value="cited">{{ T.papers_sort_cited }}</option>
        </select>
      </label>
      <button id="papers-clear" class="papers-clear" type="button">{{ T.papers_clear }}</button>
    </div>
    <div class="papers-examples">
      <span>{{ T.papers_examples }}：</span>
      <button type="button" data-example="molecular phylogeny">molecular phylogeny</button>
      <button type="button" data-example="gut microbiota">gut microbiota</button>
      <button type="button" data-example="wood resistance">wood resistance</button>
      <button type="button" data-example="Coptotermes formosanus">Coptotermes formosanus</button>
    </div>
  </form>

  <div id="papers-status" class="papers-status" role="status" aria-live="polite"></div>
  <div id="papers-results" class="papers-results"></div>
  <button id="papers-more" class="papers-more" type="button" hidden>{{ T.papers_more }}</button>
  <p class="papers-abstract-note">{{ T.papers_abstract_note }}</p>
  <p class="papers-cache-link"><a href="{{ site.base_url }}/papers-index.json" download>{{ T.papers_cache_download }}</a></p>

  <section class="papers-external" aria-labelledby="papers-external-title">
    <h2 id="papers-external-title">{{ T.papers_external }}</h2>
    <ul class="papers-external-list">
      <li><a data-external="openalex" href="https://openalex.org/" target="_blank" rel="noopener">OpenAlex</a></li>
      <li><a data-external="crossref" href="https://search.crossref.org/" target="_blank" rel="noopener">Crossref</a></li>
      <li><a data-external="scholar" href="https://scholar.google.com/" target="_blank" rel="noopener">Google Scholar</a></li>
      <li><a data-external="cnki" href="https://kns.cnki.net/" target="_blank" rel="noopener">CNKI 知网</a></li>
      <li><a data-external="wanfang" href="https://s.wanfangdata.com.cn/" target="_blank" rel="noopener">万方</a></li>
      <li><a data-external="baidu" href="https://xueshu.baidu.com/" target="_blank" rel="noopener">百度学术</a></li>
      <li><a data-external="bhl" href="https://www.biodiversitylibrary.org/" target="_blank" rel="noopener">BHL</a></li>
    </ul>
  </section>

  {% include papers-i18n.html %}
  {% include papers-glossary.html %}
</div>

<noscript><p class="papers-noscript">This page needs JavaScript. You can also search OpenAlex, Google Scholar or CNKI directly.</p></noscript>