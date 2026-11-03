---
layout: default
title: "孔白蚁属 Foraminitermes 物种名录"
description: "孔白蚁属（Foraminitermes）是白蚁科（TERMITIDAE）下的一个属，隶属孔白蚁亚科（Foraminitermitinae），本站收录 6 种。本页列出该属的全部物种与亚种，并标注模式种，物种页含模式产地、分布地图与同属物种。属的分类位置见名录索引与上级科、亚科页面。详见名录索引。按分类系统逐级排列。"
lang: zh-CN
lang_only: true
author: 班奈特格林
family_id: termitidae
last_modified_at: 2026-10-30
permalink: /genus/foraminitermes/
sitemap: true
has_map: true
taxon_search: true
breadcrumb:
  - name: "名录"
    url: "/list/"
  - name: "白蚁科 TERMITIDAE"
    url: "/family/termitidae/"
  - name: "孔白蚁亚科 Foraminitermitinae"
    url: "/subfamily/foraminitermitinae/"
  - name: "孔白蚁属 Foraminitermes"
    url: "/genus/foraminitermes/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="分类位置"><a href="{{ site.base_url }}/list/">名录</a> › <a href="{{ site.base_url }}/family/termitidae/">白蚁科</a> › <a href="{{ site.base_url }}/subfamily/foraminitermitinae/">孔白蚁亚科</a> › <a href="{{ site.base_url }}/genus/foraminitermes/">孔白蚁属 <i>Foraminitermes</i></a> › <span>本属</span></nav>
<header class="taxon-header">
<h1>孔白蚁属 <i>Foraminitermes</i></h1>
<p class="taxon-meta">白蚁科 TERMITIDAE · 6 种</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-anchors="foraminitermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/search/">
<label class="taxon-search-label" for="taxon-search-input">在本属范围内检索（6 个种与亚种）：中文名或拉丁学名</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="如 白蚁 / Amitermes / abruptus" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">只检索本属登记的分类单元；全站网页请用<a href="{{ site.base_url }}/search/">全文搜索</a>。</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>分布图</h2>
{% include distribution-map.html mode="genus" id="foraminitermes" %}
</section>
<section class="taxon-section taxon-intro" data-pagefind-ignore>
<h2>属级介绍</h2>
<p>本属隶属<a href="{{ site.base_url }}/family/termitidae/">白蚁科 <i>Termitidae</i></a>下的<a href="{{ site.base_url }}/subfamily/foraminitermitinae/">孔白蚁亚科 <i>Foraminitermitinae</i></a>，本站收录 6 种。</p>
<p>模式种：<i>Foraminitermes tubifrons</i>。</p>
<p>本页附有本属的分布图（GBIF 记录按 1° 网格汇总）；点开物种条目可查看各自模式产地、分布与参考文献。</p>
</section>
{%- assign fz = site.data.fauna_genera["/genus/foraminitermes/"] -%}{%- if fz %}
{% include fauna-genus.html fauna=fz %}
{%- endif %}
{%- assign fk = site.data.fauna_keys["/genus/foraminitermes/"] -%}{%- if fk %}
{% include fauna-keys.html fk=fk %}
{%- endif %}
<section class="taxon-section">
<h2>物种（6 种）</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/species/foraminitermes-coatoni/"><i>Foraminitermes coatoni</i> Krishna, 1963 科顿孔白蚁</a></li><li><a href="{{ site.base_url }}/species/foraminitermes-corniferus/"><i>Foraminitermes corniferus</i> Sjöstedt, 1905 具角孔白蚁</a></li><li><a href="{{ site.base_url }}/species/foraminitermes-harrisi/"><i>Foraminitermes harrisi</i> Krishna, 1963 哈里斯孔白蚁</a></li><li><a href="{{ site.base_url }}/species/foraminitermes-rhinoceros/"><i>Foraminitermes rhinoceros</i> Sjöstedt, 1905 犀牛孔白蚁</a></li><li><a href="{{ site.base_url }}/species/foraminitermes-tubifrons/"><i>Foraminitermes tubifrons</i> Holmgren, 1912 瘤额孔白蚁</a> <span class="taxon-type" title="模式种">★ 模式种</span></li><li><a href="{{ site.base_url }}/species/foraminitermes-valens/"><i>Foraminitermes valens</i> Silvestri, 1914 强健孔白蚁</a></li></ul>
</section>
<p class="taxon-more">上一级：<a href="{{ site.base_url }}/list/">名录索引</a> · <a href="{{ site.base_url }}/subfamily/foraminitermitinae/">孔白蚁亚科 <i>Foraminitermitinae</i></a> · <a href="{{ site.base_url }}/data/">数据与下载</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/list/">← 返回名录索引</a> · <a href="{{ site.base_url }}/">首页</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/genus/foraminitermes/#taxon",
 "name": "Foraminitermes",
 "alternateName": [
  "孔白蚁属"
 ],
 "taxonRank": "Genus",
 "url": "{{ site.base_url }}/genus/foraminitermes/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Foraminitermitinae",
  "alternateName": [
   "孔白蚁亚科"
  ],
  "taxonRank": "Subfamily",
  "url": "{{ site.base_url }}/subfamily/foraminitermitinae/"
 }
}
</script>