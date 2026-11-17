---
layout: default
title: 全文搜索：学名、中文名与拼音
description: "全站检索：名录、3089 个物种页、统计页、数据页与博客文章可一次搜完，支持中文（含繁体）、拉丁学名与拼音；本地全文索引的查询在浏览器内完成、不上传搜索词，另附联网的 AI 语义搜索（查询发往 Cloudflare）。结果按栏目归类，可直达物种页、属页与文献条目。｜白蚁名录：现生等翅下目 13 科、326 属、3021 种、68 亚种。"
lang: zh-CN
author: 班奈特格林
date: 2026-10-17
version: 2026.10.30
keywords: [白蚁, 等翅目, Isoptera, 搜索, 全文检索, Pagefind, AI 搜索, Cloudflare]
permalink: /search/
noindex: true
sitemap: false
pagefind: true
---

# 全文搜索

{% include ai-search-block.html %}

<p>只查<strong>分类群</strong>（科／亚科／属／种／亚种）时，用<a href="{{ site.base_url }}/list/">名录索引页的检索框</a>更快，可直接跳到对应的科／亚科／属／物种页面；下面的站内检索用于全站文字。</p>

<h2 id="local-fulltext">{{ site.data.i18n[page.lang].search_local_heading }}</h2>

<p>检索全站内容：名录正文、3089 个物种页、统计表、结构化数据页与博客文章。索引由开源工具 <a href="https://pagefind.app/">Pagefind</a> 在构建时生成，查询在浏览器内匹配本地索引，搜索词不会发往任何服务器（包括本站）。</p>

<div id="pagefind-search" data-pagefind-ignore data-lang="zh-CN" data-base="{{ site.base_url }}"></div>

<noscript><p>本页全文检索需要 JavaScript。未启用时可改用<a href="{{ site.base_url }}/list/">名录检索</a>。</p></noscript>
