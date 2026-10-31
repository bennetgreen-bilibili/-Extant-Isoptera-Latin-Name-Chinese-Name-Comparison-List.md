---
layout: default
title: 文献检索 — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: 按拉丁学名、中文名或多个关键词检索白蚁相关论文；默认限定白蚁（等翅目）文献，支持多关键词、次异名、中文文献筛选、摘要展开与 GB/T 7714 / BibTeX / RIS 引用导出。
lang: zh-CN
author: 班奈特格林
date: 2026-10-30
version: 2026.10.30
keywords: [白蚁, 等翅目, Isoptera, 文献检索, 论文, OpenAlex, Crossref, 摘要]
permalink: /papers/
---

{%- assign T = site.data.i18n[page.lang] | default: site.data.i18n['zh-CN'] -%}

<h1 class="papers-title">{{ T.papers_heading }}</h1>
<p class="papers-lead">输入拉丁学名、中文名或多个关键词，检索白蚁相关论文；默认限定白蚁（等翅目）文献，多个关键词需同时匹配。自动合并次异名，支持摘要展开与引用导出。</p>

<div id="papers-app" class="papers-app" data-base="{{ site.base_url }}" data-index-url="{{ site.base_url }}/search-index.json" data-papers-url="{{ site.base_url }}/papers-index.json" data-lang="zh-CN" data-pagefind-ignore>
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
      <button type="button" data-example="分子 系统发育">分子 系统发育</button>
      <button type="button" data-example="白蚁 肠道 微生物">白蚁 肠道 微生物</button>
      <button type="button" data-example="木材 抗性">木材 抗性</button>
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
</div>

<noscript><p class="papers-noscript">本页需要 JavaScript；也可以直接去 OpenAlex、Google Scholar 或知网检索。</p></noscript>