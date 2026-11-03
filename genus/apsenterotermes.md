---
layout: default
title: "后肠白蚁属 Apsenterotermes 物种名录"
description: "后肠白蚁属（Apsenterotermes）是白蚁科（TERMITIDAE）下的一个属，隶属白蚁亚科（Termitinae），本站收录 5 种。本页列出该属的全部物种与亚种，并标注模式种，物种页含模式产地、分布地图与同属物种。每一条目均可跳转到对应的物种页面，查看拉丁学名、命名人年份、中文正名、参考文献与引用格式。"
lang: zh-CN
lang_only: true
author: 班奈特格林
family_id: termitidae
last_modified_at: 2026-10-30
permalink: /genus/apsenterotermes/
sitemap: true
has_map: true
taxon_search: true
breadcrumb:
  - name: "名录"
    url: "/list/"
  - name: "白蚁科 TERMITIDAE"
    url: "/family/termitidae/"
  - name: "白蚁亚科 Termitinae"
    url: "/subfamily/termitinae/"
  - name: "后肠白蚁属 Apsenterotermes"
    url: "/genus/apsenterotermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="分类位置"><a href="{{ site.base_url }}/list/">名录</a> › <a href="{{ site.base_url }}/family/termitidae/">白蚁科</a> › <a href="{{ site.base_url }}/subfamily/termitinae/">白蚁亚科</a> › <a href="{{ site.base_url }}/genus/apsenterotermes/">后肠白蚁属 <i>Apsenterotermes</i></a> › <span>本属</span></nav>
<header class="taxon-header">
<h1>后肠白蚁属 <i>Apsenterotermes</i></h1>
<p class="taxon-meta">白蚁科 TERMITIDAE · 5 种</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-anchors="apsenterotermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/search/">
<label class="taxon-search-label" for="taxon-search-input">在本属范围内检索（5 个种与亚种）：中文名或拉丁学名</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="如 白蚁 / Amitermes / abruptus" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">只检索本属登记的分类单元；全站网页请用<a href="{{ site.base_url }}/search/">全文搜索</a>。</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>分布图</h2>
{% include distribution-map.html mode="genus" id="apsenterotermes" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>属级介绍</h2>
<p>本属隶属<a href="{{ site.base_url }}/family/termitidae/">白蚁科 <i>Termitidae</i></a>下的<a href="{{ site.base_url }}/subfamily/termitinae/">白蚁亚科 <i>Termitinae</i></a>，本站收录 5 种。</p>
<p>模式种：<i>Apsenterotermes iridipennis</i>。</p>
<p>本页附有本属的分布图（GBIF 记录按 1° 网格汇总）；点开物种条目可查看各自模式产地、分布与参考文献。</p>
</section>
{%- assign fz = site.data.fauna_genera["/genus/apsenterotermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{%- assign fk = site.data.fauna_keys["/genus/apsenterotermes/"] -%}{%- if fk %}
{% include fauna-keys.html fk=fk %}
{%- endif %}
<section class="taxon-section">
<h2>物种（5 种）</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/species/apsenterotermes-aspersus/"><i>Apsenterotermes aspersus</i> Miller, 1991 散乱后肠白蚁</a></li><li><a href="{{ site.base_url }}/species/apsenterotermes-declinatus/"><i>Apsenterotermes declinatus</i> Miller, 1991 长弯后肠白蚁</a></li><li><a href="{{ site.base_url }}/species/apsenterotermes-improcerus/"><i>Apsenterotermes improcerus</i> Miller, 1991 粗短后肠白蚁</a></li><li><a href="{{ site.base_url }}/species/apsenterotermes-iridipennis/"><i>Apsenterotermes iridipennis</i> Gay, 1956 虹翅后肠白蚁</a> <span class="taxon-type" title="模式种">★ 模式种</span></li><li><a href="{{ site.base_url }}/species/apsenterotermes-stenopronos/"><i>Apsenterotermes stenopronos</i> Miller, 1991 细管后肠白蚁</a></li></ul>
</section>
<p class="taxon-more">上一级：<a href="{{ site.base_url }}/list/">名录索引</a> · <a href="{{ site.base_url }}/subfamily/termitinae/">白蚁亚科 <i>Termitinae</i></a> · <a href="{{ site.base_url }}/data/">数据与下载</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/list/">← 返回名录索引</a> · <a href="{{ site.base_url }}/">首页</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/genus/apsenterotermes/#taxon",
 "name": "Apsenterotermes",
 "alternateName": [
  "后肠白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/genus/apsenterotermes/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Termitinae",
  "alternateName": [
   "白蚁亚科"
  ],
  "taxonRank": "Subfamily",
  "url": "{{ site.base_url }}/subfamily/termitinae/"
 }
}
</script>