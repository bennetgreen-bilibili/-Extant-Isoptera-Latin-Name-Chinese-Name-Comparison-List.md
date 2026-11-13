---
layout: default
title: "前角白蚁属 Procornitermes 物种名录"
description: "前角白蚁属（Procornitermes）是白蚁科（TERMITIDAE）下的一个属，隶属聚白蚁亚科（Syntermitinae），本站收录 5 种。本页列出该属的全部物种与亚种，并标注模式种，物种页含模式产地、分布地图与同属物种。属的分类位置见名录索引与上级科、亚科页面。详见名录索引。按分类系统逐级排列。"
lang: zh-CN
single_lang: true
author: 班奈特格林
family_id: termitidae
last_modified_at: 2026-10-30
permalink: /genus/procornitermes/
sitemap: true
has_map: true
taxon_search: true
has_photos: true
breadcrumb:
  - name: "名录"
    url: "/list/"
  - name: "白蚁科"
    url: "/family/termitidae/"
  - name: "聚白蚁亚科"
    url: "/subfamily/syntermitinae/"
  - name: "前角白蚁属 Procornitermes"
    url: "/genus/procornitermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="分类位置"><a href="{{ site.base_url }}/list/">名录</a> › <a href="{{ site.base_url }}/family/termitidae/">白蚁科</a> › <a href="{{ site.base_url }}/subfamily/syntermitinae/">聚白蚁亚科</a> › <a href="{{ site.base_url }}/genus/procornitermes/">前角白蚁属 <i>Procornitermes</i></a> › <span>本属</span></nav>
<header class="taxon-header">
<h1>前角白蚁属 <i>Procornitermes</i></h1>
<p class="taxon-meta">白蚁科 TERMITIDAE · 5 种</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="zh-CN" data-lang-prefix="" data-anchors="procornitermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/search/">
<label class="taxon-search-label" for="taxon-search-input">在本属范围内检索（5 个种与亚种）：名字、分布或模式产地</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="如 白蚁 / Amitermes / 澳大利亚" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">按名字与产地筛选本属登记的分类单元；全站网页请用<a href="{{ site.base_url }}/search/">全文搜索</a>。</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>分布图</h2>
{% include distribution-map.html mode="genus" id="procornitermes" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="genus" id="procornitermes" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>属级介绍</h2>
<p>本属隶属<a href="{{ site.base_url }}/family/termitidae/">白蚁科 <i>Termitidae</i></a>下的<a href="{{ site.base_url }}/subfamily/syntermitinae/">聚白蚁亚科 <i>Syntermitinae</i></a>，本站收录 5 种。</p>
<p>模式种：<i>Procornitermes triacifer</i>。</p>
<p>本页附有本属的分布图（GBIF 记录按 1° 网格汇总）；点开物种条目可查看各自模式产地、分布与参考文献。</p>
</section>
{%- assign fz = site.data.fauna_genera["/genus/procornitermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{% include genus-morphology.html %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>物种（5 种）</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/species/procornitermes-araujoi/"><i>Procornitermes araujoi</i> Emerson, 1952 阿劳若前角白蚁</a></li><li><a href="{{ site.base_url }}/species/procornitermes-lespesii/"><i>Procornitermes lespesii</i> Müller, 1873 莱佩斯前角白蚁</a></li><li><a href="{{ site.base_url }}/species/procornitermes-romani/"><i>Procornitermes romani</i> Emerson, 1952 罗曼前角白蚁</a></li><li><a href="{{ site.base_url }}/species/procornitermes-striatus/"><i>Procornitermes striatus</i> Hagen, 1858 具沟前角白蚁</a></li><li><a href="{{ site.base_url }}/species/procornitermes-triacifer/"><i>Procornitermes triacifer</i> Silvestri, 1901 三尖唇前角白蚁</a> <span class="taxon-type" title="模式种">★ 模式种</span></li></ul>
</section>
<p class="taxon-more">上一级：<a href="{{ site.base_url }}/list/">名录索引</a> · <a href="{{ site.base_url }}/subfamily/syntermitinae/">聚白蚁亚科 <i>Syntermitinae</i></a> · <a href="{{ site.base_url }}/data/">数据与下载</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/list/">← 返回名录索引</a> · <a href="{{ site.base_url }}/">首页</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/genus/procornitermes/#taxon",
 "name": "Procornitermes",
 "alternateName": [
  "前角白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/genus/procornitermes/",
 "isPartOf": {
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Syntermitinae",
  "alternateName": [
   "聚白蚁亚科"
  ],
  "taxonRank": "Subfamily",
  "url": "{{ site.base_url }}/subfamily/syntermitinae/"
 }
}
</script>