---
layout: default
title: 命名差异与待核对 — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: "把本站名录与 GBIF Backbone、Catalogue of Life、Blattodea Species File 的对照结果整理成可筛选清单：名称差异、匹配存疑、覆盖缺口，支持按类型/来源/关键词筛选、分页浏览与 CSV 下载。"
lang: zh-CN
author: 班奈特格林
date: 2026-10-29
version: 2026.10.17
keywords: [白蚁, 等翅目, 名录, 命名差异, 分类核对, GBIF, Catalogue of Life, Blattodea Species File]
permalink: /list/name-issues/
pagefind: true
---
{%- assign D = site.data.name_issues -%}
{%- assign C = D.meta.counts -%}
<nav class="ni-crumbs" aria-label="面包屑"><a href="{{ site.base_url }}/">首页</a> › <a href="{{ site.base_url }}/list/">名录</a> › 命名差异与待核对</nav>
<h1 class="ni-title">命名差异与待核对<span class="ni-title-alt" lang="en">Name discrepancies and review queue</span></h1>
<p class="ni-lead">本页把仓库里已有的「本站名 vs 外部权威库」对照结果整理成可筛选清单：GBIF Backbone、Catalogue of Life（ChecklistBank）与 Blattodea Species File（BSF）。只列出需要人工注意的条目——共 <b>{{ C.total }}</b> 条、涉及 <b>{{ C.species_with_issue }}</b> 个物种/亚种（名录共 {{ C.species_total }} 条记录）。<strong>这里只提示差异，不改动站内分类数据</strong>；匹配规则与判定口径见 <a href="{{ site.base_url }}/data/">数据页</a>，人工复核流程见 <code>_tools/外部权威库与一致性核对.md</code>。</p>
<div class="ni-legend"><span><span class="ni-badge is-conflict">名称差异</span>外部库把本站名当作异名，并给出它认为的接受名——需要判断是否改名、加注或维持现状。</span><span><span class="ni-badge is-match">匹配存疑</span>模糊匹配，或同一学名在 BSF 有多个候选 OTU，脚本无法自动判定，需要人工核对。</span><span><span class="ni-badge is-gap">覆盖缺口</span>只匹配到上级阶元、外部库未收录，或在 BSF 中检索不到——影响外链与交叉引用。</span></div>
<div class="ni-summary"><span class="ni-stat"><b>{{ C.total }}</b> 条待核对</span><span class="ni-stat"><b>{{ C.by_group.conflict }}</b> 名称差异</span><span class="ni-stat"><b>{{ C.by_group.match }}</b> 匹配存疑</span><span class="ni-stat"><b>{{ C.by_group.gap }}</b> 覆盖缺口</span><span class="ni-stat"><b>{{ C.species_with_issue }}</b> 个物种涉及</span><span class="ni-stat">BSF 已人工核对 <b>{{ C.bsf_verified }}</b> 条</span></div>
<div class="ni-app" id="ni-root" data-page-size="50" data-text-range="第 {a}–{b} 条 / 共 {t} 条" data-text-page="第 {p} / {pages} 页" data-text-empty="没有匹配的条目，试试清空筛选。">
<div class="ni-controls">
<div class="ni-filters" role="group" aria-label="按类型筛选">
<button type="button" class="ni-chip is-active" data-group="all" aria-pressed="true">全部 {{ C.total }}</button>
<button type="button" class="ni-chip" data-group="conflict" aria-pressed="false">名称差异 {{ C.by_group.conflict }}</button>
<button type="button" class="ni-chip" data-group="match" aria-pressed="false">匹配存疑 {{ C.by_group.match }}</button>
<button type="button" class="ni-chip" data-group="gap" aria-pressed="false">覆盖缺口 {{ C.by_group.gap }}</button>
</div>
<label class="ni-field" for="ni-source">来源 <select id="ni-source"><option value="all">全部</option><option value="gbif">GBIF（{{ C.by_source.gbif }}）</option><option value="col">Catalogue of Life（{{ C.by_source.col }}）</option><option value="bsf">Blattodea Species File（{{ C.by_source.bsf }}）</option></select></label>
<label class="ni-field" for="ni-q">检索 <input type="search" id="ni-q" placeholder="拉丁名 / 中文名 / 外部名 / 科名" autocomplete="off"></label>
<button type="button" class="ni-chip" id="ni-reset">清空筛选</button>
</div>
<p class="ni-status" id="ni-status" role="status" aria-live="polite">第 1–50 条 / 共 {{ C.total }} 条</p>
<div class="ni-table-wrap">
<table class="ni-table">
<thead><tr><th scope="col">名称</th><th scope="col">科</th><th scope="col">来源</th><th scope="col">类型</th><th scope="col">外部记录</th><th scope="col">匹配</th><th scope="col">备注</th></tr></thead>
<tbody id="ni-body">
{%- for it in D.issues %}
<tr class="ni-row" data-group="{{ it.group }}" data-source="{{ it.source }}" data-q="{{ it.latin | downcase }} {{ it.zh }} {{ it.theirs | downcase }} {{ it.accepted | downcase }} {{ it.family_latin | downcase }}">
<td class="ni-name"><a href="{{ site.base_url }}/species/{{ it.slug }}/">{{ it.zh }}<i>{{ it.latin }}</i></a></td>
<td class="ni-family">{{ it.family_zh }}</td>
<td class="ni-src">{%- if it.source == 'gbif' -%}GBIF{%- elsif it.source == 'col' -%}CoL{%- else -%}BSF{%- endif -%}</td>
<td class="ni-kind"><span class="ni-badge is-{{ it.group }}">{%- if it.kind == 'synonym' -%}异名{%- elsif it.kind == 'higherrank' -%}仅上级阶元{%- elsif it.kind == 'missing' -%}未收录{%- elsif it.kind == 'fuzzy' -%}模糊匹配{%- else -%}匹配不确定{%- endif -%}</span></td>
<td class="ni-ext">{%- if it.url -%}<a href="{{ it.url }}" rel="noopener external" target="_blank"><i>{{ it.theirs }}</i></a>{%- elsif it.theirs -%}<i>{{ it.theirs }}</i>{%- else -%}—{%- endif -%}{%- if it.accepted -%}<span class="ni-accepted">接受名 {%- if it.accepted_url %} <a href="{{ it.accepted_url }}" rel="noopener external" target="_blank"><i>{{ it.accepted }}</i></a>{%- else %} <i>{{ it.accepted }}</i>{%- endif -%}</span>{%- endif -%}</td>
<td class="ni-match">{%- if it.match -%}<span class="ni-match-type">{{ it.match }}</span>{%- if it.confidence %} · {{ it.confidence }}%{%- endif -%}{%- endif -%}{%- if it.verified %} <span class="ni-badge is-verified">已人工核对</span>{%- elsif it.source == 'bsf' %} <span class="ni-badge">自动匹配</span>{%- endif -%}</td>
<td class="ni-note">{%- if it.note -%}{{ it.note }}{%- else -%}—{%- endif -%}</td>
</tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="ni-empty" id="ni-empty" hidden>没有匹配的条目，试试清空筛选。</p>
<div class="ni-pager" id="ni-pager"><button type="button" id="ni-prev">‹ 上一页</button><span id="ni-pageinfo" aria-current="true">第 1 / 7 页</span><button type="button" id="ni-next">下一页 ›</button></div>
</div>
<noscript><p class="ni-noscript">未启用 JavaScript 时，本页一次展示全部 {{ C.total }} 条，不做筛选与分页。</p></noscript>
<p class="ni-download"><a href="{{ site.base_url }}/downloads/isoptera-name-issues.csv" download>下载完整清单 CSV（{{ C.total }} 条）</a> · 程序化访问：<code>{{ site.base_url }}/data/name-issues.json</code></p>
<p class="ni-note-foot">数据来源缓存：GBIF / Catalogue of Life 生成于 {{ D.meta.cache_dates.authority | slice: 0, 10 }}，Blattodea Species File 生成于 {{ D.meta.cache_dates.bsf | slice: 0, 10 }}。BSF 已人工核对 {{ C.bsf_verified }} / {{ C.species_total }} 条，标「自动匹配」的条目仅供参考；本页由 <code>.github/workflows/build_name_issues.py</code> 从仓库缓存生成，随名录更新自动重建。权威库条目以对方网站当前显示为准。</p>
<script src="{{ site.base_url }}/assets/name-issues.js?v={{ site.time | date: '%s' }}" defer></script>
