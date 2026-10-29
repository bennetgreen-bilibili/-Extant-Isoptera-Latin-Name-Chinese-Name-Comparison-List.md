---
layout: default
title: 结构化数据 — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: 现存等翅下目（白蚁）名录的机器可读结构化数据（JSON）：入口 data/index.json 含完整分类树，其余按支系/科/亚科拆分为 22 个文件，均可独立访问与下载。
lang: zh-CN
author: 班奈特格林
date: 2026-10-17
version: 2026.10.30
keywords: [白蚁, 等翅目, Isoptera, 结构化数据, JSON, 名录, 分类, Termitidae]
permalink: /data/
---

# 结构化数据

<p>本站的机器可读数据已按类群拆分，入口为 <a href="{{ site.base_url }}/data/index.json"><code>data/index.json</code></a>（含 6 支系、13 科、18 亚科的完整分类树与全部文件清单）。以下 <strong>22 个 JSON 文件</strong>均可独立访问与下载。</p>

## 归档数据集与 DOI <span class="fact-en">Archived dataset &amp; DOI</span>

<p>全部名录另已整理为可引用的归档数据集（<strong>3071 条记录</strong>：逐条 CSV、分类树 JSON、次异名长表、参考文献表，附 DataCite 4.6 元数据与 CC BY 4.0 许可），可直接下载：
<a href="{{ site.base_url }}/{{ site.dataset.archive_file }}"><code>{{ site.dataset.archive_file }}</code></a>。</p>

<ul>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-checklist.csv"><code>dataset/data/isoptera-checklist.csv</code></a> — 3071 行逐条分类单元表（含中文正名、模式产地、分布、次异名）</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-taxonomy.json"><code>dataset/data/isoptera-taxonomy.json</code></a> — 完整分类树（支系—科—亚科—属—种/亚种）</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-synonyms.csv"><code>dataset/data/isoptera-synonyms.csv</code></a> — 次异名长表（含模式产地与对齐状态）</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-counts.csv"><code>dataset/data/isoptera-counts.csv</code></a> — 科/亚科级计数</li>
  <li><a href="{{ site.base_url }}/dataset/data/isoptera-references.csv"><code>dataset/data/isoptera-references.csv</code></a> — 77 条参考文献（有 DOI 者随条目给出）</li>
  <li><a href="{{ site.base_url }}/dataset/datapackage.json"><code>datapackage.json</code></a> — 字段字典（Frictionless Data Package）</li>
  <li><a href="{{ site.base_url }}/dataset/datacite-metadata.xml"><code>datacite-metadata.xml</code></a> — DataCite 元数据记录</li>
  <li><a href="{{ site.base_url }}/dataset/README.md">数据集说明 README</a> — 来源、方法、字段、限制与引用</li>
</ul>

{% if site.dataset.doi %}<p><strong>DOI（版本 {{ site.dataset.version }}）</strong>：<a href="https://doi.org/{{ site.dataset.doi }}">{{ site.dataset.doi }}</a>{% if site.dataset.concept_doi %}　<strong>概念 DOI（始终指向最新版）</strong>：<a href="https://doi.org/{{ site.dataset.concept_doi }}">{{ site.dataset.concept_doi }}</a>{% endif %}</p>

<p><strong>引用格式（APA）</strong>：班奈特格林. (2026). 《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》({{ site.dataset.version }} 版) [Data set]. {{ site.dataset.publisher }}. <a href="https://doi.org/{{ site.dataset.doi }}">https://doi.org/{{ site.dataset.doi }}</a></p>{% else %}<p><strong>引用格式（APA）</strong>：班奈特格林. (2026). 《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》({{ site.dataset.version }} 版) [Data set]. <a href="{{ site.base_url }}/">{{ site.base_url }}/</a></p>

<p>该归档包已按 DOI 归档格式准备（含 README、DataCite 元数据、CC BY 4.0 许可与 SHA-256 校验）；永久 DOI 铸造后会显示在本节与全站页脚。</p>{% endif %}

{% include citation.html %}


## 按支系 / 科

<ul>
  <li><a href="{{ site.base_url }}/data/mastotermitidae.json"><strong>澳白蚁科</strong> Mastotermitidae</a> — 1 属 · 1 种</li>
  <li><a href="{{ site.base_url }}/data/teletisoptera.json"><strong>远等翅类</strong> Teletisoptera（古白蚁科 / 草白蚁科 / 原白蚁科 / 胄白蚁科）</a> — 4 科 · 8 属 · 37 种</li>
  <li><a href="{{ site.base_url }}/data/kalotermitidae.json"><strong>木白蚁科</strong> Kalotermitidae</a> — 23 属 · 479 种</li>
  <li><a href="{{ site.base_url }}/data/neoisoptera-excl-termitidae.json"><strong>新等翅类（除白蚁科）</strong> Neoisoptera excl. Termitidae（沙白蚁科 / 鼻白蚁科 / 齿白蚁科 / 杆白蚁科 / 寡脉白蚁科 / 异白蚁科）</a> — 6 科 · 14 属 · 359 种</li>
</ul>

## 白蚁科 Termitidae（18 亚科 · 逐亚科文件）

<ul>
  <li><a href="{{ site.base_url }}/data/termitidae/amitermitinae.json">弓白蚁亚科 Amitermitinae</a> — 14 属 · 194 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/apicotermitinae.json">尖白蚁亚科 Apicotermitinae</a> — 65 属 · 237 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/crepititermitinae.json">响白蚁亚科 Crepititermitinae</a> — 1 属 · 1 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/cubitermitinae.json">方白蚁亚科 Cubitermitinae</a> — 28 属 · 142 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/cylindrotermitinae.json">圆筒白蚁亚科 Cylindrotermitinae</a> — 2 属 · 9 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/engelitermitinae.json">恩格尔白蚁亚科 Engelitermitinae</a> — 1 属 · 1 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/foraminitermitinae.json">孔白蚁亚科 Foraminitermitinae</a> — 3 属 · 10 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/forficulitermitinae.json">剪白蚁亚科 Forficulitermitinae</a> — 1 属 · 1 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/macrotermitinae.json">大白蚁亚科 Macrotermitinae</a> — 12 属 · 373 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/microcerotermitinae.json">锯白蚁亚科 Microcerotermitinae</a> — 2 属 · 150 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/mirocapritermitinae.json">瘤白蚁亚科 Mirocapritermitinae</a> — 14 属 · 133 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/nasutitermitinae.json">象白蚁亚科 Nasutitermitinae</a> — 81 属 · 608 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/neocapritermitinae.json">新扭白蚁亚科 Neocapritermitinae</a> — 3 属 · 20 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/promirotermitinae.json">前奇白蚁亚科 Promirotermitinae</a> — 2 属 · 39 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/protohamitermitinae.json">始钩白蚁亚科 Protohamitermitinae</a> — 2 属 · 2 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/sphaerotermitinae.json">圆球白蚁亚科 Sphaerotermitinae</a> — 1 属 · 1 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/syntermitinae.json">聚白蚁亚科 Syntermitinae</a> — 22 属 · 105 种</li>
  <li><a href="{{ site.base_url }}/data/termitidae/termitinae.json">白蚁亚科 Termitinae</a> — 23 属 · 106 种</li>
</ul>

## 检索索引与程序化访问 <span class="fact-en">Search index &amp; programmatic access</span>

<ul>
  <li><a href="{{ site.base_url }}/search-index.json"><code>search-index.json</code></a> — 名录检索索引（拼音 / 繁体 / 次异名，含所属科字段；由 <code>build_search_index.py</code> 生成）</li>
  <li><a href="{{ site.base_url }}/data/name-issues.json"><code>data/name-issues.json</code></a> — 命名差异与待核对清单（三类问题、外部记录链接、匹配置信度；<code>synonym_pairs</code> 逐对给出本站名与外部库接受名的关系（异名 / 组合差异）、接收名方向（外部名 / 本站名 / 待定）、各库判定与补录状态，<code>species_authority</code> 供物种页反查；同内容 <a href="{{ site.base_url }}/downloads/isoptera-name-issues.csv">CSV</a> 与 <a href="{{ site.base_url }}/downloads/isoptera-synonym-pairs.csv">逐对归并 CSV</a>）</li>
  <li><a href="{{ site.base_url }}/sitemap.txt">sitemap.txt</a> — 全站 URL 清单（每行一个绝对 URL）</li>
  <li>订阅：<a href="{{ site.base_url }}/feed.xml">feed.xml（Atom）</a> · <a href="{{ site.base_url }}/feed.json">feed.json（JSON Feed）</a> · <a href="{{ site.base_url }}/changelog.atom">changelog.atom（版本记录）</a></li>
  <li>搜索发现：<a href="{{ site.base_url }}/opensearch.xml">opensearch.xml</a>（浏览器可把本站加为搜索引擎；检索地址 <code>/search/?q=…</code>）</li>

<h2 id="authority">外部权威库对照 <span class="fact-en">External authority cross-check</span></h2>

<p>每个物种页的「其他数据库」区块，由 <code>.github/workflows/build_authority_links.py</code> 按学名查询
<a href="https://api.gbif.org/v1/species/match">GBIF Backbone API</a>、
<a href="https://api.checklistbank.org/">Catalogue of Life ChecklistBank API</a> 与
<a href="https://query.wikidata.org/">Wikidata SPARQL</a>（P225 分类单元学名）生成，只提供外链与一致性提示，<strong>不改动本站任何分类数据</strong>。
{%- if site.data.authority_links %}{%- assign A = site.data.authority_links %}{%- assign C = A.meta.counts %}
当前缓存（抓取日期 {{ A.meta.generated | slice: 0, 10 }}）：<strong>{{ C.total }}</strong> 个学名中，GBIF 可外链 <strong>{{ C.gbif_linked }}</strong> 个（接受名 {{ C.gbif_accepted }}、异名 {{ C.gbif_synonym }}），Catalogue of Life 可外链 <strong>{{ C.col_linked }}</strong> 个，Wikidata 有条目 <strong>{{ C.wikidata }}</strong> 个；与两库接受名完全一致 <strong>{{ C.consistent }}</strong> 个，带提示 <strong>{{ C.flagged }}</strong> 个。{%- endif %}</p>

<ul>
  <li><a href="{{ site.base_url }}/downloads/isoptera-authority-crossref.csv"><code>isoptera-authority-crossref.csv</code></a> — 一致性核对表（逐条列出 GBIF / Catalogue of Life 的 ID、状态、接受名、Wikidata QID 与差异标记），可下载后自行比对或用于修订</li>
  <li>外链规则：GBIF 仅在 <code>matchType=EXACT</code>（或 FUZZY 且 confidence ≥ 95）且阶元为种/亚种时给出链接，避免把属级或低置信度结果当成本种；Catalogue of Life 链接指向 ChecklistBank 的 name usage 页。</li>
  <li>世界名录对照：Blattodea Species File（<a href="https://cockroach.speciesfile.org">cockroach.speciesfile.org</a>，已并入原 Isoptera Species File，由 TaxonWorks / TaxonPages 构建）{% if site.data.bsf_links %}{% assign B = site.data.bsf_links.meta.counts %}——已自动匹配 <strong>{{ B.valid }}</strong> 个有效名、<strong>{{ B.synonym }}</strong> 个异名，待人工核对或未收录 <strong>{{ B.ambiguous }}</strong> / <strong>{{ B.missing }}</strong> 个；物种页上自动匹配的条目标注「自动匹配」，人工核对后才标「已人工核对」，核对流程见仓库 <code>_tools/bsf对照/操作说明.md</code>{% endif %}</li>
  <li>结构化数据：物种页另有 schema.org <code>Taxon</code> + <code>BreadcrumbList</code> JSON-LD，<code>sameAs</code> 指向上述外部库条目，并通过 <code>isPartOf</code> 关联本站 Dataset 实体。</li>
  <li><a href="{{ site.base_url }}/data/references.json"><code>data/references.json</code></a> — 77 条参考文献的 Crossref 增强数据（DOI、Crossref 书目字段、GB/T 7714 式 / APA / Vancouver 引用、BibTeX / RIS / CSL-JSON）。</li>
</ul>

</ul>
