---
layout: default
title: 结构化数据 — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: 现存等翅下目（白蚁）名录的机器可读结构化数据（JSON）：入口 data/index.json 含完整分类树，其余按支系/科/亚科拆分为 22 个文件，均可独立访问与下载。
lang: zh-CN
author: 班奈特格林
date: 2026-10-17
version: 2026.10.17
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

<p><strong>引用格式（APA）</strong>：班奈特格林. (2026). 《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》({{ site.dataset.version }} 版) [Data set]. {{ site.dataset.publisher }}. <a href="https://doi.org/{{ site.dataset.doi }}">https://doi.org/{{ site.dataset.doi }}</a></p>

{% if site.dataset.gbif_doi %}<p><strong>GBIF checklist（第二 DOI，10.15468）</strong>：<a href="https://doi.org/{{ site.dataset.gbif_doi }}">{{ site.dataset.gbif_doi }}</a>{% if site.dataset.gbif_dataset %}　<strong>GBIF 数据集页</strong>：<a href="{{ site.dataset.gbif_dataset }}">{{ site.dataset.gbif_dataset }}</a>{% endif %}　（Darwin Core Archive 发布，面向分类学与生物多样性检索；版本快照仍以 Zenodo DOI 为准）</p>{% endif %}{% else %}<p><strong>引用格式（APA）</strong>：班奈特格林. (2026). 《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》({{ site.dataset.version }} 版) [Data set]. <a href="{{ site.base_url }}/">{{ site.base_url }}/</a></p>

<p>该归档包已按 DOI 归档格式准备（含 README、DataCite 元数据、CC BY 4.0 许可与 SHA-256 校验）；永久 DOI 铸造后会显示在本节与全站页脚。</p>{% endif %}

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

## 检索索引

<ul>
  <li><a href="{{ site.base_url }}/search-index.json">检索索引 search-index.json</a>（供名录页搜索框使用）</li>
</ul>
