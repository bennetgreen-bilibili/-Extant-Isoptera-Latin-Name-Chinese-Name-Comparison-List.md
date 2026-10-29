---
layout: default
title: 命名差异与待核对 — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: "把本站名录与 GBIF Backbone、Catalogue of Life、Blattodea Species File 的对照结果整理成可筛选清单：名称差异、匹配存疑、覆盖缺口，支持按类型/来源/关键词筛选、分页浏览与 CSV 下载。"
lang: zh-CN
author: 班奈特格林
date: 2026-10-29
version: 2026.10.30
keywords: [白蚁, 等翅目, 名录, 命名差异, 分类核对, GBIF, Catalogue of Life, Blattodea Species File]
permalink: /list/name-issues/
pagefind: true
---
{%- assign D = site.data.name_issues -%}
{%- assign C = D.meta.counts -%}
<nav class="ni-crumbs" aria-label="面包屑"><a href="{{ site.base_url }}/">首页</a> › <a href="{{ site.base_url }}/list/">名录</a> › 命名差异与待核对</nav>
<h1 class="ni-title">命名差异与待核对<span class="ni-title-alt" lang="en">Name discrepancies and review queue</span></h1>
<p class="ni-lead">本页把仓库里已有的「本站名 vs 外部权威库」对照结果整理成可筛选清单：GBIF Backbone、Catalogue of Life（ChecklistBank）与 Blattodea Species File（BSF）。只列出需要人工注意的条目——共 <b>{{ C.total }}</b> 条、涉及 <b>{{ C.species_with_issue }}</b> 个物种/亚种（名录共 {{ C.species_total }} 条记录）。「名称差异」已逐对判定<b>关系</b>与<b>接收名方向</b>（异名 {{ C.pairs_relation_synonym }} 对 · 组合差异 {{ C.pairs_relation_combination }} 对；接收名在外部库名一侧 {{ C.pairs_direction_external }} 对 · 在站名一侧 {{ C.pairs_direction_site }} 对 · 待定 {{ C.pairs_direction_disputed }} 对），见页末<a href="#synonyms">名称差异逐对归并</a>；其中 {{ C.pairs_recorded }} 对已补录进接受名物种页的「次异名」一节。<strong>这里只提示差异，不改动站内分类数据</strong>；匹配规则与判定口径见 <a href="{{ site.base_url }}/data/">数据页</a>，人工复核流程见 <code>_tools/外部权威库与一致性核对.md</code>。</p>
<div class="ni-legend"><span><span class="ni-badge is-conflict">名称差异</span>外部库把本站名当作异名，并给出它认为的接受名——需要判断是否改名、加注或维持现状。</span><span><span class="ni-badge is-match">匹配存疑</span>模糊匹配，或同一学名在 BSF 有多个候选 OTU，脚本无法自动判定，需要人工核对。</span><span><span class="ni-badge is-gap">覆盖缺口</span>只匹配到上级阶元、外部库未收录，或在 BSF 中检索不到——影响外链与交叉引用。</span></div>
<div class="ni-summary"><span class="ni-stat"><b>{{ C.total }}</b> 条待核对</span><span class="ni-stat"><b>{{ C.by_group.conflict }}</b> 名称差异 → {{ C.conflict_pairs }} 对</span><span class="ni-stat"><b>{{ C.pairs_relation_combination }}</b> 对为组合差异</span><span class="ni-stat"><b>{{ C.pairs_direction_disputed }}</b> 对方向待定</span><span class="ni-stat"><b>{{ C.pairs_recorded }}</b> 对已补录</span><span class="ni-stat"><b>{{ C.by_group.match }}</b> 匹配存疑</span><span class="ni-stat"><b>{{ C.by_group.gap }}</b> 覆盖缺口</span><span class="ni-stat"><b>{{ C.species_with_issue }}</b> 个物种涉及</span><span class="ni-stat">已人工核对 <b>{{ C.manually_reviewed }}</b> 条（BSF {{ C.bsf_verified }}）</span></div>
<div class="ni-app" id="ni-root" data-page-size="50" data-text-range="第 {a}–{b} 条 / 共 {t} 条" data-text-page="第 {p} / {pages} 页" data-text-empty="没有匹配的条目，试试清空筛选。">
<div class="ni-controls">
<div class="ni-filters" role="group" aria-label="按类型筛选">
<button type="button" class="ni-chip is-active" data-group="all" aria-pressed="true">全部 {{ C.total }}</button>
<button type="button" class="ni-chip" data-group="conflict" aria-pressed="false">名称差异 {{ C.by_group.conflict }}（{{ C.conflict_pairs }} 对）</button>
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
<td class="ni-kind">{%- if it.group == 'conflict' -%}{%- if it.relation == 'combination' -%}<span class="ni-badge is-comb">组合差异</span>{%- else -%}<span class="ni-badge is-conflict">异名</span>{%- endif -%}{%- if it.direction == 'site' -%} <span class="ni-badge is-verified">本站名为接收名</span>{%- elsif it.direction == 'disputed' -%} <span class="ni-badge">方向待定</span>{%- elsif it.disputed -%} <span class="ni-badge">方向有分歧</span>{%- endif -%}{%- if it.recorded %} <span class="ni-badge is-verified">已补录</span>{%- endif -%}{%- else -%}<span class="ni-badge is-{{ it.group }}">{%- if it.kind == 'higherrank' -%}仅上级阶元{%- elsif it.kind == 'missing' -%}未收录{%- elsif it.kind == 'fuzzy' -%}模糊匹配{%- else -%}匹配不确定{%- endif -%}</span>{%- endif -%}</td>
<td class="ni-ext">{%- if it.url -%}<a href="{{ it.url }}" rel="noopener external" target="_blank"><i>{{ it.theirs }}</i></a>{%- elsif it.theirs -%}<i>{{ it.theirs }}</i>{%- else -%}—{%- endif -%}{%- if it.accepted -%}<span class="ni-accepted">接受名 {%- if it.accepted_slug %} <a href="{{ site.base_url }}/species/{{ it.accepted_slug }}/" title="本名录也收录该名"><i>{{ it.accepted }}</i></a><span class="ni-insite">本站另有收录</span>{%- elsif it.accepted_url %} <a href="{{ it.accepted_url }}" rel="noopener external" target="_blank"><i>{{ it.accepted }}</i></a>{%- else %} <i>{{ it.accepted }}</i>{%- endif -%}</span>{%- endif -%}</td>
<td class="ni-match">{%- if it.match -%}<span class="ni-match-type">{{ it.match }}</span>{%- if it.confidence %} · {{ it.confidence }}%{%- endif -%}{%- endif -%}{%- if it.verified %} <span class="ni-badge is-verified">已人工核对</span>{%- elsif it.source == 'bsf' %} <span class="ni-badge">自动匹配</span>{%- endif -%}</td>
<td class="ni-note">{%- if it.note -%}{{ it.note }}{%- else -%}—{%- endif -%}</td>
</tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="ni-empty" id="ni-empty" hidden>没有匹配的条目，试试清空筛选。</p>
{%- assign ni_pages = C.total | plus: 49 | divided_by: 50 -%}
<div class="ni-pager" id="ni-pager"><button type="button" id="ni-prev">‹ 上一页</button><span id="ni-pageinfo" aria-current="true">第 1 / {{ ni_pages }} 页</span><button type="button" id="ni-next">下一页 ›</button></div>
</div>
<noscript><p class="ni-noscript">未启用 JavaScript 时，本页一次展示全部 {{ C.total }} 条，不做筛选与分页。</p></noscript>
{%- assign P = D.synonym_pairs -%}
<h2 id="synonyms" class="ni-syn-title">名称差异逐对归并：关系与方向 <span class="ni-syn-title-alt" lang="en">Each discrepancy as one pair, with relation and direction</span></h2>
<p class="ni-syn-lead">下表把 {{ C.by_group.conflict }} 条「名称差异」整理成 <b>{{ C.conflict_pairs }}</b> 对「本站名 ↔ 外部库主张的接受名」（同一对出现在多个库只算一次），并判定两件事：<strong>关系</strong>——加词不同记为「异名」<b>{{ C.pairs_relation_synonym }}</b> 对，同种异属（只是换了属）记为「组合差异」<b>{{ C.pairs_relation_combination }}</b> 对；<strong>方向</strong>——接收名在外部库名一侧 <b>{{ C.pairs_direction_external }}</b> 对、在本站名一侧 <b>{{ C.pairs_direction_site }}</b> 对、方向待定 <b>{{ C.pairs_direction_disputed }}</b> 对。「各库判定」列是各外部库对本站名的物种级结论（上位阶元、模糊匹配、未收录不计票）。</p>
{%- if P %}
<div class="ni-table-wrap ni-syn-wrap">
<table class="ni-table ni-syn-table">
<thead><tr><th scope="col">本站名</th><th scope="col">外部库主张的接受名</th><th scope="col">关系</th><th scope="col">方向（接收名）</th><th scope="col">各库判定</th><th scope="col">补录</th></tr></thead>
<tbody>
{%- for p in P %}
<tr>
<td class="ni-syn-our"><a href="{{ site.base_url }}/species/{{ p.our.slug }}/">{{ p.our.zh }}<i>{{ p.our.latin }}</i></a></td>
<td class="ni-syn-extname"><i>{{ p.external.name }}</i>{%- for l in p.external_links %} <a class="ni-syn-ext" href="{{ l.url }}" rel="noopener external" target="_blank" title="外部库中的该条记录">{%- if l.source == 'gbif' -%}GBIF{%- elsif l.source == 'col' -%}CoL{%- else -%}BSF{%- endif -%}</a>{%- endfor %}{%- if p.receiving.in_site and p.receiving.slug and p.receiving.latin != p.our.latin %} <a class="ni-insite" href="{{ site.base_url }}/species/{{ p.receiving.slug }}/">本站另有收录</a>{%- endif -%}</td>
<td class="ni-syn-rel">{%- if p.relation == 'combination' -%}<span class="ni-badge is-comb">组合差异</span>{%- else -%}<span class="ni-badge is-conflict">异名</span>{%- endif -%}{%- if p.disputed %} <span class="ni-badge">方向有分歧</span>{%- endif -%}</td>
<td class="ni-syn-dir">{%- if p.direction == 'external' -%}外部库名为接收名{%- elsif p.direction == 'site' -%}本站名为接收名{%- else -%}方向待定{%- endif -%}</td>
<td class="ni-syn-votes">{%- if p.votes.synonym contains 'gbif' -%}<span class="ni-vote is-syn">GBIF 异名</span>{%- elsif p.votes.accepted contains 'gbif' -%}<span class="ni-vote is-acc">GBIF 接受</span>{%- endif -%}{%- if p.votes.synonym contains 'col' -%}<span class="ni-vote is-syn">CoL 异名</span>{%- elsif p.votes.accepted contains 'col' -%}<span class="ni-vote is-acc">CoL 接受</span>{%- endif -%}{%- if p.votes.synonym contains 'bsf' -%}<span class="ni-vote is-syn">BSF 异名</span>{%- elsif p.votes.accepted contains 'bsf' -%}<span class="ni-vote is-acc">BSF 有效</span>{%- endif -%}{%- if p.votes.synonym.size == 0 and p.votes.accepted.size == 0 -%}—{%- endif -%}</td>
<td class="ni-syn-rec">{%- if p.recorded -%}<span class="ni-badge is-verified">已补录</span>{%- elsif p.recordable -%}<span class="ni-badge">可补录</span>{%- else -%}—{%- endif -%}</td>
</tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="ni-syn-foot">判定规则：任一外部库只按<strong>物种级</strong>结论计票（仅匹配到属/科、模糊匹配、未收录都不算）。<strong>异名</strong>指加词不同、确为不同名；<strong>组合差异</strong>是同一种只是换了属，不算异名——这类里 GBIF 常把本名录的属并入旧属、把本站名写成它认为的「接受名」，方向容易写反，所以按各库票数判定接收名。只有「真异名 + 外部库名为接收名 + 至少两个分类数据库一致认定」的对才可补录（GBIF 仍标接受名时只标「方向有分歧」，不否决）：目前 <b>{{ C.pairs_recorded }}</b> 对已写进接受名物种页「次异名」的<strong>「依外部权威库补录的异名」</strong>小节（front matter 的 <code>authority_synonym_*</code>，检索也能按异名命中）。其余（含组合差异与方向待定）只作核对提示；本名录不删除任何名字，正式合并与否以原始文献与本站分类系统为准。</p>
{%- endif %}

<p class="ni-download"><a href="{{ site.base_url }}/downloads/isoptera-name-issues.csv" download>下载完整清单 CSV（{{ C.total }} 条）</a> · <a href="{{ site.base_url }}/downloads/isoptera-synonym-pairs.csv" download>名称差异逐对归并 CSV（{{ C.conflict_pairs }} 行）</a> · 程序化访问：<code>{{ site.base_url }}/data/name-issues.json</code></p>
<p class="ni-note-foot">数据来源缓存：GBIF / Catalogue of Life 生成于 {{ D.meta.cache_dates.authority | slice: 0, 10 }}，Blattodea Species File 生成于 {{ D.meta.cache_dates.bsf | slice: 0, 10 }}。BSF 已人工核对 {{ C.bsf_verified }} / {{ C.species_total }} 条，标「自动匹配」的条目仅供参考；本页由 <code>.github/workflows/build_name_issues.py</code> 从仓库缓存生成（含关系/方向判定与补录状态），随名录更新自动重建。权威库条目以对方网站当前显示为准。</p>
<script src="{{ site.base_url }}/assets/name-issues.js?v={{ site.time | date: '%s' }}" defer></script>
