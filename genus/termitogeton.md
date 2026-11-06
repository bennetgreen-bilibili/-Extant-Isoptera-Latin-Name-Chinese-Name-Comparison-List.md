---
layout: default
title: "寡脉白蚁属 Termitogeton 物种名录"
description: "寡脉白蚁属（Termitogeton）是寡脉白蚁科（TERMITOGETONIDAE）下的一个属，本站收录 2 种。本页列出该属的全部物种与亚种，并标注模式种，物种页含模式产地、分布地图与同属物种。每一条目均可跳转到对应的物种页面，查看拉丁学名、命名人年份、中文正名、参考文献与引用格式。详见名录索引。"
lang: zh-CN
lang_only: true
author: 班奈特格林
family_id: termitogetonidae
last_modified_at: 2026-10-30
permalink: /genus/termitogeton/
sitemap: true
has_map: true
taxon_search: true
has_photos: true
image: "/assets/images/termitogetonidae.jpg"
breadcrumb:
  - name: "名录"
    url: "/list/"
  - name: "寡脉白蚁科 TERMITOGETONIDAE"
    url: "/family/termitogetonidae/"
  - name: "寡脉白蚁属 Termitogeton"
    url: "/genus/termitogeton/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="分类位置"><a href="{{ site.base_url }}/list/">名录</a> › <a href="{{ site.base_url }}/family/termitogetonidae/">寡脉白蚁科</a> › <a href="{{ site.base_url }}/genus/termitogeton/">寡脉白蚁属 <i>Termitogeton</i></a> › <span>本属</span></nav>
<header class="taxon-header">
<h1>寡脉白蚁属 <i>Termitogeton</i></h1>
<p class="taxon-meta">寡脉白蚁科 TERMITOGETONIDAE · 2 种</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-anchors="termitogeton" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/search/">
<label class="taxon-search-label" for="taxon-search-input">在本属范围内检索（2 个种与亚种）：名字、分布或模式产地</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="如 白蚁 / Amitermes / 澳大利亚" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">按名字与产地筛选本属登记的分类单元；全站网页请用<a href="{{ site.base_url }}/search/">全文搜索</a>。</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>分布图</h2>
{% include distribution-map.html mode="genus" id="termitogeton" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="genus" id="termitogeton" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>属级介绍</h2>
<p>本属隶属<a href="{{ site.base_url }}/family/termitogetonidae/">寡脉白蚁科 <i>Termitogetonidae</i></a>，本站收录 2 种。</p>
<p>模式种：<i>Termitogeton planus</i>。</p>
<p>本页附有本属的分布图（GBIF 记录按 1° 网格汇总）；点开物种条目可查看各自模式产地、分布与参考文献。</p>
</section>
{%- assign fz = site.data.fauna_genera["/genus/termitogeton/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{% include genus-morphology.html %}
<section class="taxon-section">
<h2>物种（2 种）</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/species/termitogeton-planus/"><i>Termitogeton planus</i> Haviland, 1898 平坦寡脉白蚁</a> <span class="taxon-type" title="模式种">★ 模式种</span></li><li><a href="{{ site.base_url }}/species/termitogeton-umbilicatus/"><i>Termitogeton umbilicatus</i> Hagen, 1858 中凹寡脉白蚁</a></li></ul>
</section>
<p class="taxon-more">上一级：<a href="{{ site.base_url }}/list/">名录索引</a> · <a href="{{ site.base_url }}/family/termitogetonidae/">寡脉白蚁科 <i>Termitogetonidae</i></a> · <a href="{{ site.base_url }}/data/">数据与下载</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/list/">← 返回名录索引</a> · <a href="{{ site.base_url }}/">首页</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/genus/termitogeton/#taxon",
 "name": "Termitogeton",
 "alternateName": [
  "寡脉白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/genus/termitogeton/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Termitogetonidae",
  "alternateName": [
   "寡脉白蚁科"
  ],
  "taxonRank": "Family",
  "url": "{{ site.base_url }}/family/termitogetonidae/"
 }
}
</script>