---
layout: default
title: 分布图 — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: "按 GBIF 出现记录聚合的 13 科白蚁 1° 网格分布图：方法、记录上限、采样偏差、GeoJSON 数据文件，以及 Leaflet 底图与瓦片使用政策。"
lang: zh-CN
author: 班奈特格林
date: 2026-10-17
keywords: [白蚁, 等翅目, Isoptera, 分布图, GBIF, 生物地理, 网格地图, 采样偏差, GeoJSON, Leaflet]
permalink: /distribution/
---

{%- assign occ = site.data.occurrence_summary -%}

# 分布图

<p>本页把本站 <strong>13 个科</strong>的分布图并列展示。每个圆点是一个 <strong>1°×1° 网格</strong>（约 111 km 见方），圆点大小与深浅按该网格内的 <strong>GBIF 出现记录条数</strong>缩放；点击圆点可以看到具体条数。地图只在滚动到视口内时才创建，不会为看不见的地图预取任何瓦片。</p>

<p>中文名、学名与科级分类取自本站名录；坐标来自 GBIF 的出现记录（occurrence，即标本与观察记录），不是分布区边界。访问日期：<strong>{% if occ %}{{ occ.meta.access_date }}{% else %}待生成{% endif %}</strong>。</p>

## 方法 <span class="fact-en" lang="en">Method</span> <span class="fact-es" lang="es">Método</span>

<ol>
  <li><strong>取科名对应的 GBIF 分类键</strong>：用 <a href="https://api.gbif.org/v1/species/match?name=TERMITIDAE&amp;rank=FAMILY"><code>species/match?name=&lt;FAMILY&gt;&amp;rank=FAMILY</code></a> 取得该科的 canonical usageKey。若 GBIF 分类骨架中没有同名科，则改为按其属逐一匹配后汇总（见下）。</li>
  <li><strong>拉取带坐标的记录</strong>：<a href="https://api.gbif.org/v1/occurrence/search"><code>occurrence/search</code></a>，参数固定为 <code>hasCoordinate=true</code>、<code>hasGeospatialIssue=false</code>、<code>limit=300</code>，按 <code>offset</code> 翻页；每科最多取 <strong>900 条</strong>记录（3 页），到上限或记录耗尽即停。只保留 <code>decimalLatitude</code> / <code>decimalLongitude</code>（以及用于统计的国家代码）。</li>
  <li><strong>归入 1° 网格</strong>：格号 = <code>floor(lat)</code>、<code>floor(lon)</code>，坐标取格心（<code>floor + 0.5</code>，保留三位小数），同一格内的记录数记为 <code>n</code>。</li>
  <li><strong>输出 GeoJSON</strong>：每个科一个 <code>FeatureCollection</code>，<code>Point</code> 要素的属性只有 <code>n</code>，文件头部的 <code>properties</code> 记录科名、GBIF 键、记录数、网格数、网格大小、访问日期与来源。</li>
</ol>

<p class="distribution-note">GBIF 分类骨架与本名录并非完全一致：<strong>原白蚁科 Hodotermopsidae</strong>、<strong>沙白蚁科 Psammotermitidae</strong>、<strong>寡脉白蚁科 Termitogetonidae</strong>、<strong>异白蚁科 Heterotermitidae</strong> 在 GBIF 中被并入古白蚁科 / 鼻白蚁科。为保持与本名录的分类一致，这 4 科改为「按属汇总」：逐个匹配属名取 taxonKey，再把各属记录合并、仍以 900 条为限。代价是它们的记录同时也会出现在 GBIF 的宿主科里，因此这 4 科与 <a href="#rhinotermitidae">鼻白蚁科</a>、<a href="#archotermopsidae">古白蚁科</a> 的地图存在重叠——这不是错误，而是两套分类系统的差异被如实保留。</p>

## 怎么读这些图 <span class="fact-en" lang="en">How to read the maps</span> <span class="fact-es" lang="es">Cómo leer los mapas</span>

<ul>
  <li><strong>点 = 网格，不是采集点</strong>：同一格里无论 2 条还是 200 条记录，都只画一个点，靠大小与深浅区分。</li>
  <li><strong>颜色深浅 ≈ 记录密度</strong>，反映的是「有多少人在这里采过、把数据传给了 GBIF」，不等于白蚁的真实多度。</li>
  <li><strong>缩放上限为 9 级</strong>：数据本身只有 1° 精度，再放大没有新信息，还会浪费瓦片请求。</li>
  <li>地图默认关闭滚轮缩放，避免在长页面上误触；需要缩放时用左上角的 +/− 按钮。</li>
</ul>

<div class="distribution-caveat">
<strong>局限与免责</strong> <span class="fact-en" lang="en">Caveats</span> <span class="fact-es" lang="es">Advertencias</span>
<ul>
  <li><strong>采样偏差</strong>：GBIF 记录高度集中在北美与欧洲，热带（尤其是非洲、东南亚、南美）记录稀疏。空白格往往代表「没人采样」，而不是「没有白蚁」。</li>
  <li><strong>国家/地区空白</strong>：部分国家的馆藏数据几乎未数字化，地图上的国界式空缺不能当作分布界线。</li>
  <li><strong>不是分布区图</strong>：这里没有做生态位模型、没有做分布区推演，也没有剔除逸散记录与室内记录。</li>
  <li><strong>记录上限</strong>：每科最多 900 条，按 GBIF 返回顺序（记录键序）截取，是可复现的样本，但不是随机样本。</li>
  <li><strong>会变</strong>：GBIF 每天新增与修订记录，重新生成（见 <code>--refresh</code>）后数字会变。</li>
</ul>
</div>

## 13 科分布图 <span class="fact-en" lang="en">Family maps</span> <span class="fact-es" lang="es">Mapas por familia</span>

<p>卡片标题为科的中文名与学名，副行是该科的记录数、网格数与名录中的物种数；每张卡片下方可以下载该科的 GeoJSON，或跳到 GBIF 分类页。</p>

{% include distribution-map.html mode="page" %}

## 汇总表 <span class="fact-en" lang="en">Summary</span> <span class="fact-es" lang="es">Resumen</span>

{% if occ %}
<table>
<thead>
<tr>
  <th>科 <span class="fact-en" lang="en">Family</span></th>
  <th>GBIF 键</th>
  <th class="num">记录</th>
  <th class="num">网格</th>
  <th class="num">名录物种</th>
  <th>取数方式</th>
</tr>
</thead>
<tbody>
{%- for f in occ.families %}
<tr>
  <td><a href="#{{ f.id }}">{{ f.zh }} <i class="latin">{{ f.latin }}</i></a></td>
  <td>{% if f.gbif_key %}<a href="{{ f.gbif_url }}" rel="noopener">{{ f.gbif_key }}</a>{% else %}按属汇总{% endif %}</td>
  <td class="num">{{ f.records }}</td>
  <td class="num">{{ f.cells }}</td>
  <td class="num">{{ f.species }}</td>
  <td>{% if f.resolution == 'genus_aggregate' %}属级汇总 <span class="fact-en" lang="en">genus aggregate</span>{% else %}科级键 <span class="fact-en" lang="en">family key</span>{% endif %}</td>
</tr>
{%- endfor %}
<tr>
  <td><strong>合计</strong> <span class="fact-en" lang="en">Total</span></td>
  <td>—</td>
  <td class="num"><strong>{{ occ.meta.records_families }}</strong></td>
  <td class="num"><strong>{{ occ.meta.cells_families }}</strong></td>
  <td class="num"><strong>3071</strong></td>
  <td>13 科</td>
</tr>
</tbody>
</table>
{% else %}
<p>汇总数据尚未生成（<code>_data/occurrence_summary.json</code> 缺失）。</p>
{% endif %}

## 数据文件 <span class="fact-en" lang="en">Data files</span> <span class="fact-es" lang="es">Archivos de datos</span>

<p>所有地图都以纯 GeoJSON 提供，可直接下载、写进 QGIS 或用任何 GeoJSON 库读取；坐标是 <code>[经度, 纬度]</code> 的格心。文件名与科 id 一致，也与名录锚点一致。</p>

<ul>
{%- if occ -%}
{%- for f in occ.families %}
  <li><a href="{{ site.base_url }}/{{ f.file }}" download><code>{{ f.file }}</code></a> — {{ f.zh }} <i class="latin">{{ f.latin }}</i>，{{ f.records }} 条记录 / {{ f.cells }} 个网格</li>
{%- endfor -%}
  <li><code>_data/occurrence_summary.json</code> — 汇总（记录数、网格数、各国记录数、访问日期），本页所有数字都来自它；该文件是站点数据文件（Jekyll 的 <code>_data</code> 不单独发布），随仓库提供</li>
  <li><a href="{{ site.base_url }}/data/">结构化数据页</a> — 分类树与逐类群 JSON（与本页地图配套的清单数据）</li>
{%- else %}
  <li>数据文件待生成。</li>
{%- endif %}
</ul>

<h3 id="genus-files">属级数据文件 <span class="fact-en" lang="en">Genus files</span></h3>

{% if occ and occ.genera and occ.genera.size > 0 %}
<p>物种数 ≥ 12 的大属另外出图，共 <strong>{{ occ.genera.size }}</strong> 个文件（每个文件小于 60 KB）：</p>
<ul>
{%- for g in occ.genera %}
  <li><a href="{{ site.base_url }}/{{ g.file }}" download><code>{{ g.file }}</code></a> — <i class="latin">{{ g.latin }}</i> {{ g.zh }}（{{ g.family_zh }}），{{ g.records }} 条记录 / {{ g.cells }} 个网格</li>
{%- endfor %}
</ul>
{% else %}
<p>本次生成未包含属级文件（属级为可选增强，科级始终生成）。</p>
{% endif %}

## 来源与许可 <span class="fact-en" lang="en">Sources &amp; licence</span> <span class="fact-es" lang="es">Fuentes y licencia</span>

<ul>
  <li><strong>出现记录</strong>：GBIF.org（Global Biodiversity Information Facility），通过 <a href="https://api.gbif.org/v1/occurrence/search">GBIF Occurrence API</a> 获取，访问日期 {% if occ %}{{ occ.meta.access_date }}{% endif %}。各条记录的具体许可见 GBIF 条目；引用方式见 <a href="https://www.gbif.org/citation-guidelines">GBIF 引用指南</a>（按数据集 DOI 引用）。</li>
  <li><strong>分类骨架</strong>：GBIF Backbone Taxonomy（<a href="https://api.gbif.org/v1/species/match">species/match</a>）；本站采用的科级分类（Engel 2021 等）见<a href="{{ site.base_url }}/list/">名录</a>。</li>
  <li><strong>底图</strong>：GBIF 公共栅格瓦片（<a href="https://tile.gbif.org/">tile.gbif.org</a>，基于 OpenMapTiles / OpenStreetMap 数据），回退方案为 OpenStreetMap 官方瓦片；版权归 © OpenStreetMap contributors，见 <a href="https://www.openstreetmap.org/copyright">OSM 版权页</a>。</li>
  <li><strong>渲染库</strong>：Leaflet 1.9.4，BSD-2-Clause，本地自托管（<code>assets/vendor/leaflet/</code>），不从 CDN 运行时加载。</li>
  <li><strong>衍生数据</strong>：本页的 GeoJSON 与汇总 JSON 由本站生成，随本站以 CC BY 4.0 提供。</li>
</ul>

<h3 id="tiles">底图与瓦片使用政策 <span class="fact-en" lang="en">Tile usage policy</span></h3>

<p>地图采用「按需加载 + 本地库 + 可回退底图」的策略：只有滚动到视口内的地图才会创建 Leaflet 实例并请求瓦片；不发任何预取请求，不在服务端抓取瓦片，缩放上限 9 级以限制瓦片数量。优先使用 GBIF 提供的公共瓦片服务（GBIF 明确将其瓦片开放给公众与 API 使用者），失败时回退到 OpenStreetMap 官方瓦片，并按 <a href="https://operations.osmfoundation.org/policies/tiles/">OSM 瓦片使用政策</a> 带上署名与 <code>referrerpolicy="no-referrer-when-downgrade"</code>。完整说明与合规清单见仓库内 <code>_tools/分布图与瓦片使用政策.md</code>。</p>

<p>为什么只做到科/属级、不做种级？种级地图意味着 <strong>3071 个</strong>页面各自请求一组瓦片与一份数据，既超过 OSM/GBIF 公共瓦片的合理使用量，也没有必要——1° 网格的聚合结果在科级已经能看出采样格局。这也是本站接受的折中：<strong>科级/属级聚合，而不是种级分布</strong>。</p>

<h3 id="regenerate">如何更新 <span class="fact-en" lang="en">Regenerating</span></h3>

<p>数据由 <code>.github/workflows/build_occurrence_geojson.py</code> 生成，产物已提交到仓库；重新生成只需：</p>

<pre class="cite-text">python .github/workflows/build_occurrence_geojson.py --write --refresh</pre>

<p>去掉 <code>--refresh</code> 会复用 <code>_tmp/gbif_cache/</code> 里的缓存（重跑不重复请求 GBIF），<code>--check</code> 则只校验已提交的产物是否与脚本一致。</p>
