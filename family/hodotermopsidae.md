---
layout: default
title: "原白蚁科 HODOTERMOPSIDAE 分类名录"
description: "原白蚁科（HODOTERMOPSIDAE）是现存等翅下目（Isoptera）下的一个科，本站收录 1 个属、1 个种。本页按分类系统列出该科的全部属，并汇总各级物种数量。点击任一属可查看其全部物种与亚种，点击物种可查看模式产地、分布地图、同属物种与 GB/T 7714、BibTeX、RIS 引用格式。"
lang: zh-CN
single_lang: true
author: 班奈特格林
family_id: hodotermopsidae
last_modified_at: 2026-10-30
permalink: /family/hodotermopsidae/
sitemap: true
has_map: true
taxon_search: true
has_photos: true
image: "/assets/images/hodotermopsidae.jpg"
breadcrumb:
  - name: "名录"
    url: "/list/"
  - name: "原白蚁科"
    url: "/family/hodotermopsidae/"
---
<article class="taxon-page">
<nav class="taxon-crumbs" aria-label="分类位置"><a href="{{ site.base_url }}/list/">名录</a> › <a href="{{ site.base_url }}/family/hodotermopsidae/">原白蚁科</a> › <span>本科</span></nav>
<header class="taxon-header">
<h1>原白蚁科 <i>Hodotermopsidae</i></h1>
<p class="taxon-meta">1 属 · 1 种</p>
</header>
<div class="taxon-search" data-pagefind-ignore data-lang="zh-CN" data-lang-prefix="" data-anchors="hodotermopsidae,hodotermopsis" data-index="{{ site.base_url }}/search-index.json" data-search-page="{{ site.base_url }}/search/">
<label class="taxon-search-label" for="taxon-search-input">在本科范围内检索（1 个种与亚种）：名字、分布或模式产地</label>
<input type="search" id="taxon-search-input" class="taxon-search-input" placeholder="如 白蚁 / Amitermes / 澳大利亚" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="taxon-search-results" aria-autocomplete="list">
<p class="taxon-search-status" hidden></p>
<ul class="taxon-search-results" hidden></ul>
<p class="taxon-search-hint">按名字与产地筛选本科登记的分类单元；全站网页请用<a href="{{ site.base_url }}/search/">全文搜索</a>。</p>
</div>

<figure class="taxa-illustration">
  <img src="{{ site.base_url }}/assets/images/hodotermopsidae.jpg" alt="Hodotermopsis sjostedti 山林原白蚁" loading="lazy">
  <figcaption>Hodotermopsis sjostedti 山林原白蚁</figcaption>
</figure>
<section class="taxon-section taxon-distribution" data-pagefind-ignore>
<h2>分布图</h2>
{% include distribution-map.html mode="family" id="hodotermopsidae" %}
</section>
<section class="taxon-section taxon-photos-section" data-pagefind-ignore>
{% include taxon-photos.html kind="family" id="hodotermopsidae" limit=6 more="1" %}
</section>
<section class="taxon-section taxon-intro">
<h2>科级介绍</h2>
<p>原白蚁科由 Engel 于 2021 年提出(11)。模式属为原白蚁属 Hodotermopsis Holmgren, 1911。科名词出模式属：Hodotermopsis 意为“似草白蚁的”，由 Hodotermes 加希腊文 opsis（外观）构成。本名录收录 1 属 1 种。</p>
<p>现生种山林原白蚁分布于日本、中国台湾、中国南部及越南(12)。与近缘类群一致，原白蚁栖息于湿润腐木之中，巢群筑于倒木内部，营单块木巢生活，由拟工蚁执行巢内劳动。兵蚁头近方卵形、扁平，头前半部色深，头顶中央具一凹坑，单眼明显、呈肾形，上颚粗壮对称，左上颚具4枚、右上颚具2枚大型缘齿，触角22—24节，前胸背板半月形、略狭于头；有翅成虫体长12—13.5 mm，触角21—26节，前翅鳞略大于后翅鳞。经济上，山林原白蚁 Hodotermopsis sjostedti 在中国南方危害活树与伐倒木，是蛀干害虫(13)</p>
<p class="taxon-src">本节是本站为这一级分类维护的常设说明，随分类修订在本页更新；名录索引见<a href="{{ site.base_url }}/list/">名录</a>。</p>
</section>
{%- assign fz = site.data.fauna_families["/family/hodotermopsidae/"] -%}{%- if fz %}
{% include fauna-family.html fauna=fz %}
{%- endif %}
{% include taxon-literature.html %}
<section class="taxon-section">
<h2>属（1）</h2><ul class="taxon-list"><li><a href="{{ site.base_url }}/genus/hodotermopsis/"><i>Hodotermopsis</i> 原白蚁属</a> <span class="taxon-count">1 种</span></li></ul>
</section>
<p class="taxon-more">上一级：<a href="{{ site.base_url }}/list/">名录索引</a> · <a href="{{ site.base_url }}/data/">数据与下载</a></p>
<p class="taxon-back"><a href="{{ site.base_url }}/list/">← 返回名录索引</a> · <a href="{{ site.base_url }}/">首页</a></p>
</article>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Taxon",
 "@id": "{{ site.base_url }}/family/hodotermopsidae/#taxon",
 "name": "Hodotermopsidae",
 "alternateName": [
  "原白蚁科"
 ],
 "taxonRank": "Family",
 "url": "{{ site.base_url }}/family/hodotermopsidae/",
 "isPartOf": {
  "@type": "Dataset",
  "@id": "{{ site.base_url }}/#dataset"
 },
 "version": "{{ site.dataset.version }}",
 "dateModified": "{{ site.dataset.version | replace: '.', '-' }}",
 "parentTaxon": {
  "@type": "Taxon",
  "name": "Isoptera",
  "alternateName": [
   "现存等翅下目"
  ],
  "taxonRank": "Infraorder"
 }
}
</script>