---
layout: default
title: "齿白蚁科 SERRITERMITIDAE 分类名录"
description: "齿白蚁科（SERRITERMITIDAE）是新等翅类（Neoisoptera）下的一个科，本站收录 2 个属、3 个种。本页按分类系统列出该科的全部属，并汇总各级物种数量。点击任一属可查看其全部物种与亚种，点击物种可查看模式产地、分布地图、同属物种与 GB/T 7714、BibTeX、RIS 引用格式。"
lang: zh-CN
lang_only: true
author: 班奈特格林
family_id: serritermitidae
last_modified_at: 2026-10-30
permalink: /family/serritermitidae/
sitemap: true
has_map: true
taxon_search: true
breadcrumb:
  - name: "名录"
    url: "/list/"
  - name: "齿白蚁科 SERRITERMITIDAE"
    url: "/family/serritermitidae/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="分类位置"><a href="{{ site.base_url }}/list/">名录</a> › <a href="{{ site.base_url }}/family/serritermitidae/">齿白蚁科</a> › <span>本科</span></nav>
<header class="taxon-header">
<h1>齿白蚁科 <i>Serritermitidae</i></h1>
<p class="taxon-meta">新等翅类 Neoisoptera · 2 属 · 3 种</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-anchors="serritermitidae,glossotermes,serritermes" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/search/">
<label class="taxon-search-label" for="taxon-search-input">在本科范围内检索（3 个种与亚种）：中文名或拉丁学名</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="如 白蚁 / Amitermes / abruptus" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">只检索本科登记的分类单元；全站网页请用<a href="{{ site.base_url }}/search/">全文搜索</a>。</p>
</div>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>分布图</h2>
{% include distribution-map.html mode="family" id="serritermitidae" %}
</section>
<section class="taxon-section taxon-intro">
<h2>科级介绍</h2>
<p>齿白蚁科由 Holmgren 于 1910 年建立（Serritermitidae Holmgren, 1910）(14)，模式属为 Serritermes Wasmann, 1897。科名词自模式属名，由拉丁语 serra（锯）与 termes 拼合，指本科兵蚁与繁殖蚁上颚具明显的锯状多齿缘。本名录收录 2 属 3 种。</p>
<p>本科为新热带界特有小科，产南美北部（圭亚那地盾）至巴西。本科无真工蚁品级。两属生活方式迥异：Glossotermes 为木栖白蚁，栖于干腐倒木内；S. serrifer 则是白蚁中罕见的专性寄居者，终生寄居于白蚁科 Cornitermes cumulans 的地表垅巢内，不自筑巢，兵蚁上颚镰刀状、内缘具锯齿。本科兵蚁头长、侧缘呈弧形，头前具一小而呈盲端的囟门，不与额腺相通，触角12–15节（Serritermes 属12–13节，Glossotermes 属13–15节）；本科兵蚁额腺极为发达，自头部延伸至胸腹前半部，御敌时以自体爆裂方式经颈背释放分泌物(26)。</p>
<p class="taxon-src">本节是本站为这一级分类维护的常设说明，随分类修订在本页更新；名录索引见<a href="{{ site.base_url }}/list/">名录</a>。</p>
</section>
{%- assign fz = site.data.fauna_families["/family/serritermitidae/"] -%}{%- if fz %}
{% include fauna-family.html fauna=fz %}
{%- endif %}
{%- assign fk = site.data.fauna_keys["/family/serritermitidae/"] -%}{%- if fk %}
{% include fauna-keys.html fk=fk %}
{%- endif %}
<section class="taxon-section">
<h2>属（2）</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/genus/glossotermes/"><i>Glossotermes</i> 舌白蚁属</a> <span class="taxon-count">2 种</span></li><li><a href="{{ site.base_url }}/genus/serritermes/"><i>Serritermes</i> 齿白蚁属</a> <span class="taxon-count">1 种</span></li></ul>
</section>
<p class="taxon-more">上一级：<a href="{{ site.base_url }}/list/">名录索引</a> · <a href="{{ site.base_url }}/data/">数据与下载</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/list/">← 返回名录索引</a> · <a href="{{ site.base_url }}/">首页</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/family/serritermitidae/#taxon",
 "name": "Serritermitidae",
 "alternateName": [
  "齿白蚁科"
 ],
 "taxonRank": "Family",
 "url": "{{ site.base_url }}/family/serritermitidae/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "新等翅类",
  "alternateName": [
   "Neoisoptera"
  ],
  "taxonRank": "Clade"
 }
}
</script>