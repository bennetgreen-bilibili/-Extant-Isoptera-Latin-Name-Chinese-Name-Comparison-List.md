---
layout: default
title: "缩狭白蚁属 Coarctotermes 物种名录"
description: "缩狭白蚁属（Coarctotermes）是白蚁科（TERMITIDAE）下的一个属，隶属象白蚁亚科（Nasutitermitinae），本站收录 4 种。本页列出该属的全部物种与亚种，并标注模式种，物种页含模式产地、分布地图与同属物种。属的分类位置见名录索引与上级科、亚科页面。详见名录索引。按分类系统逐级排列。"
lang: zh-CN
single_lang: true
author: 班奈特格林
family_id: termitidae
last_modified_at: 2026-10-30
permalink: /genus/coarctotermes/
sitemap: true
has_map: true
taxon_search: true
breadcrumb:
  - name: "名录"
    url: "/list/"
  - name: "白蚁科"
    url: "/family/termitidae/"
  - name: "象白蚁亚科"
    url: "/subfamily/nasutitermitinae/"
  - name: "缩狭白蚁属 Coarctotermes"
    url: "/genus/coarctotermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="分类位置"><a href="{{ site.base_url }}/list/">名录</a> › <a href="{{ site.base_url }}/family/termitidae/">白蚁科</a> › <a href="{{ site.base_url }}/subfamily/nasutitermitinae/">象白蚁亚科</a> › <a href="{{ site.base_url }}/genus/coarctotermes/">缩狭白蚁属 <i>Coarctotermes</i></a> › <span>本属</span></nav>
<header class="taxon-header">
<h1>缩狭白蚁属 <i>Coarctotermes</i></h1>
<p class="taxon-meta">白蚁科 TERMITIDAE · 4 种</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="zh-CN" data-lang-prefix="" data-anchors="coarctotermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/search/">
<label class="taxon-search-label" for="taxon-search-input">在本属范围内检索（4 个种与亚种）：名字、分布或模式产地</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="如 白蚁 / Amitermes / 澳大利亚" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">按名字与产地筛选本属登记的分类单元；全站网页请用<a href="{{ site.base_url }}/search/">全文搜索</a>。</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>分布图</h2>
{% include distribution-map.html mode="genus" id="coarctotermes" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>属级介绍</h2>
<p>本属隶属<a href="{{ site.base_url }}/family/termitidae/">白蚁科 <i>Termitidae</i></a>下的<a href="{{ site.base_url }}/subfamily/nasutitermitinae/">象白蚁亚科 <i>Nasutitermitinae</i></a>，本站收录 4 种。</p>
<p>模式种：<i>Coarctotermes clepsydra</i>。</p>
<p>本页附有本属的分布图（GBIF 记录按 1° 网格汇总）；点开物种条目可查看各自模式产地、分布与参考文献。</p>
</section>
{%- assign fz = site.data.fauna_genera["/genus/coarctotermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>物种（4 种）</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/species/coarctotermes-beharaensis/"><i>Coarctotermes beharaensis</i> Cachan, 1949 贝哈拉缩狭白蚁</a></li><li><a href="{{ site.base_url }}/species/coarctotermes-clepsydra/"><i>Coarctotermes clepsydra</i> Sjöstedt, 1904 漏壶缩狭白蚁</a> <span class="taxon-type" title="模式种">★ 模式种</span></li><li><a href="{{ site.base_url }}/species/coarctotermes-nasonovi/"><i>Coarctotermes nasonovi</i> Czerwinski, 1901 纳索诺夫缩狭白蚁</a></li><li><a href="{{ site.base_url }}/species/coarctotermes-pauliani/"><i>Coarctotermes pauliani</i> Cachan, 1949 波利昂缩狭白蚁</a></li></ul>
</section>
<p class="taxon-more">上一级：<a href="{{ site.base_url }}/list/">名录索引</a> · <a href="{{ site.base_url }}/subfamily/nasutitermitinae/">象白蚁亚科 <i>Nasutitermitinae</i></a> · <a href="{{ site.base_url }}/data/">数据与下载</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/list/">← 返回名录索引</a> · <a href="{{ site.base_url }}/">首页</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/genus/coarctotermes/#taxon",
 "name": "Coarctotermes",
 "alternateName": [
  "缩狭白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/genus/coarctotermes/",
 "isPartOf": {
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Nasutitermitinae",
  "alternateName": [
   "象白蚁亚科"
  ],
  "taxonRank": "Subfamily",
  "url": "{{ site.base_url }}/subfamily/nasutitermitinae/"
 }
}
</script>