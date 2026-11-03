---
layout: default
title: "古白蚁属 Archotermopsis 物种名录"
description: "古白蚁属（Archotermopsis）是古白蚁科（ARCHOTERMOPSIDAE）下的一个属，本站收录 2 种。本页列出该属的全部物种与亚种，并标注模式种，物种页含模式产地、分布地图与同属物种。每一条目均可跳转到对应的物种页面，查看拉丁学名、命名人年份、中文正名、参考文献与引用格式。详见完整名录。"
lang: zh-CN
lang_only: true
author: 班奈特格林
family_id: archotermopsidae
last_modified_at: 2026-10-30
permalink: /genus/archotermopsis/
sitemap: true
has_map: true
taxon_search: true
image: "/assets/images/archotermopsidae.jpg"
breadcrumb:
  - name: "名录"
    url: "/list/"
  - name: "古白蚁科 ARCHOTERMOPSIDAE"
    url: "/family/archotermopsidae/"
  - name: "古白蚁属 Archotermopsis"
    url: "/genus/archotermopsis/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="分类位置"><a href="{{ site.base_url }}/list/">名录</a> › <a href="{{ site.base_url }}/list/#archotermopsidae">古白蚁科</a> › <a href="{{ site.base_url }}/list/#archotermopsis">古白蚁属 <i>Archotermopsis</i></a> › <span>本属</span></nav>
<header class="taxon-header">
<h1>古白蚁属 <i>Archotermopsis</i></h1>
<p class="taxon-meta">古白蚁科 ARCHOTERMOPSIDAE · 2 种</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-anchors="archotermopsis" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/search/">
<label class="taxon-search-label" for="taxon-search-input">在本属范围内检索（2 个种与亚种）：中文名或拉丁学名</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="如 白蚁 / Amitermes / abruptus" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">只检索本属登记的分类单元；全站网页请用<a href="{{ site.base_url }}/search/">全文搜索</a>。</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>分布图</h2>
{% include distribution-map.html mode="genus" id="archotermopsis" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>属级介绍</h2>
<p>本属隶属<a href="{{ site.base_url }}/family/archotermopsidae/">古白蚁科 <i>Archotermopsidae</i></a>，本站收录 2 种。</p>
<p>模式种：<i>Archotermopsis wroughtoni</i>。</p>
<p>本页附有本属的分布图（GBIF 记录按 1° 网格汇总）；点开物种条目可查看各自模式产地、分布与参考文献。</p>
</section>
{%- assign fz = site.data.fauna_genera["/genus/archotermopsis/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
<section class="taxon-section">
<h2>物种（2 种）</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/species/archotermopsis-kuznetsovi/"><i>Archotermopsis kuznetsovi</i> Belyaeva, 2004 库兹涅佐夫古白蚁</a></li><li><a href="{{ site.base_url }}/species/archotermopsis-wroughtoni/"><i>Archotermopsis wroughtoni</i> Desneux, 1904 罗夫顿古白蚁</a> <span class="taxon-type" title="模式种">★ 模式种</span></li></ul>
</section>
<p class="taxon-more">该属的形态、分布与经济意义：<a href="{{ site.base_url }}/list/#archotermopsis">完整名录对应章节</a>；结构化数据：<a href="{{ site.base_url }}/data/">数据与下载</a>。</p>
<p class="taxon-back"><a href="{{ site.base_url }}/list/">← 返回完整名录</a> · <a href="{{ site.base_url }}/">首页</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/genus/archotermopsis/#taxon",
 "name": "Archotermopsis",
 "alternateName": [
  "古白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/genus/archotermopsis/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Archotermopsidae",
  "alternateName": [
   "古白蚁科"
  ],
  "taxonRank": "Family",
  "url": "{{ site.base_url }}/family/archotermopsidae/"
 }
}
</script>