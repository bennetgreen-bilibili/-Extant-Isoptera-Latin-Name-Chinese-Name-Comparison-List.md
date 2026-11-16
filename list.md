---
layout: default
title: 名录索引 — 现存等翅下目（白蚁）分类层级与各级页面
description: "现存等翅下目（白蚁）分类索引：6 支系、13 科、18 亚科、326 属、3021 种。按科浏览，再进入科页、亚科页、属页看形态记述与逐条物种名录；附 77 篇参考文献。"
lang: zh-CN
author: 班奈特格林
date: 2026-10-17
version: 2026.10.30
keywords: [白蚁, 等翅目, Isoptera, 学名, 中文名, 名录索引, 分类, Termitidae]
permalink: /list/
---

# 现存等翅下目 Extant Isoptera（白蚁领科）分类索引（2026.10.30）

## 分类框架

本名录全部类群同属一个分类框架，自上而下为：

1. **域 Domain**：真核域 Eukaryota
2. **界 Kingdom**：动物界 Animalia
3. **门 Phylum**：节肢动物门 Arthropoda
4. **纲 Class**：昆虫纲 Insecta
5. **亚纲 Subclass**：有翅亚纲 Pterygota
6. **下纲 Infraclass**：新翅下纲 Neoptera
7. **总目 Superorder**：网翅总目 Dictyoptera
8. **目 Order**：蜚蠊目 Blattodea
9. **下目 Infraorder**：等翅下目 Isoptera（白蚁领科 Termitoidae）

其下依次为 **科 Family** → **亚科 Subfamily** → **属 Genus** → **种 Species**；各科、亚科、属、种详见下方名录。

科之上另有若干未定阶元的支系，彼此嵌套：真等翅类（Euisoptera）下分远等翅类（Teletisoptera）与近等翅类（Icoisoptera），近等翅类下分新等翅类（Neoisoptera），新等翅类再下分土栖等翅类（Geoisoptera）；下方各节按这一层级逐级缩进列出。

<div class="search-wrap">
  <input type="search" id="search-input" class="search-input" placeholder="搜索中文名、拉丁学名、次异名，支持拼音与繁体（如：Mastotermes、达尔文澳白蚁、baiyi、白蟻、象白蚁亚科）" autocomplete="off" aria-label="搜索名录">
  <ul id="search-results" class="search-results" style="display:none"></ul>
</div>

<p class="search-hint">可直接输入拼音（如 <code>baiyi</code>）或繁体中文检索；名录之外的内容（博客、物种页等）见 <a href="{{ site.base_url }}/search/">全站全文搜索</a>。</p>

<p class="search-hint search-hint-board">与 GBIF / Catalogue of Life / Blattodea Species File 的对照中，共有 <strong>{{ site.data.name_issues.meta.counts.total }}</strong> 条需要人工注意（名称差异 {{ site.data.name_issues.meta.counts.by_group.conflict }} 条 → {{ site.data.name_issues.meta.counts.conflict_pairs }} 对：组合差异 {{ site.data.name_issues.meta.counts.pairs_relation_combination }} · 本站名为接收名 {{ site.data.name_issues.meta.counts.pairs_direction_site }} · 已补录 {{ site.data.name_issues.meta.counts.pairs_recorded }} · 匹配存疑 {{ site.data.name_issues.meta.counts.by_group.match }} · 覆盖缺口 {{ site.data.name_issues.meta.counts.by_group.gap }}）：<a href="{{ site.base_url }}/list/name-issues/"><strong>命名差异与待核对 →</strong></a></p>

{% include distribution-notes.html %}

<h2 id="by-family">按科浏览（13 科）</h2>

<p>13 个科均可单独浏览，每页列出该科的全部亚科、属与物种链接及各级数量：</p>

<ul class="taxon-list family-browse">
<li><a href="{{ site.base_url }}/family/mastotermitidae/">澳白蚁科 <i>MASTOTERMITIDAE</i></a> <span class="taxon-count">1 属 · 1 种</span></li>
<li><a href="{{ site.base_url }}/family/archotermopsidae/">古白蚁科 <i>ARCHOTERMOPSIDAE</i></a> <span class="taxon-count">2 属 · 5 种</span></li>
<li><a href="{{ site.base_url }}/family/hodotermitidae/">草白蚁科 <i>HODOTERMITIDAE</i></a> <span class="taxon-count">3 属 · 21 种</span></li>
<li><a href="{{ site.base_url }}/family/hodotermopsidae/">原白蚁科 <i>HODOTERMOPSIDAE</i></a> <span class="taxon-count">1 属 · 1 种</span></li>
<li><a href="{{ site.base_url }}/family/stolotermitidae/">胄白蚁科 <i>STOLOTERMITIDAE</i></a> <span class="taxon-count">2 属 · 10 种</span></li>
<li><a href="{{ site.base_url }}/family/kalotermitidae/">木白蚁科 <i>KALOTERMITIDAE</i></a> <span class="taxon-count">23 属 · 480 种</span></li>
<li><a href="{{ site.base_url }}/family/psammotermitidae/">沙白蚁科 <i>PSAMMOTERMITIDAE</i></a> <span class="taxon-count">2 属 · 18 种</span></li>
<li><a href="{{ site.base_url }}/family/rhinotermitidae/">鼻白蚁科 <i>RHINOTERMITIDAE</i></a> <span class="taxon-count">5 属 · 62 种</span></li>
<li><a href="{{ site.base_url }}/family/serritermitidae/">齿白蚁科 <i>SERRITERMITIDAE</i></a> <span class="taxon-count">2 属 · 3 种</span></li>
<li><a href="{{ site.base_url }}/family/stylotermitidae/">杆白蚁科 <i>STYLOTERMITIDAE</i></a> <span class="taxon-count">1 属 · 45 种</span></li>
<li><a href="{{ site.base_url }}/family/termitogetonidae/">寡脉白蚁科 <i>TERMITOGETONIDAE</i></a> <span class="taxon-count">1 属 · 2 种</span></li>
<li><a href="{{ site.base_url }}/family/heterotermitidae/">异白蚁科 <i>HETEROTERMITIDAE</i></a> <span class="taxon-count">3 属 · 229 种</span></li>
<li><a href="{{ site.base_url }}/family/termitidae/">白蚁科 <i>TERMITIDAE</i></a> <span class="taxon-count">280 属 · 2144 种</span></li>
</ul>

<p class="list-note">本页只是分类索引：分类框架、按科浏览与参考文献在这里，每一科、亚科、属的形态、生物学与分布记述都在各自页面上，物种条目（拉丁学名、中文正名、命名人与年份、模式产地、分布）也在科页、亚科页或属页逐条列出。</p>

<nav class="taxon-toc" id="toc" aria-label="目录" data-pagefind-ignore>
<h2 class="toc-title">目录</h2>
<ul class="toc-tree">
<li data-kind="clade"><a href="#isoptera">现存等翅下目 <i>Extant Isoptera</i></a>
<ul>
<li data-kind="family"><a href="{{ site.base_url }}/family/mastotermitidae/">澳白蚁科 <i>MASTOTERMITIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/mastotermes/">澳白蚁属 <i>Mastotermes</i></a></li>
</ul>
</li>
<li data-kind="clade"><a href="#euisoptera">真等翅类 <i>Euisoptera</i></a>
<ul>
<li data-kind="clade"><a href="#teletisoptera">远等翅类 <i>Teletisoptera</i></a>
<ul>
<li data-kind="family"><a href="{{ site.base_url }}/family/archotermopsidae/">古白蚁科 <i>ARCHOTERMOPSIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/archotermopsis/">古白蚁属 <i>Archotermopsis</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/zootermopsis/">动白蚁属 <i>Zootermopsis</i></a></li>
</ul>
</li>
<li data-kind="family"><a href="{{ site.base_url }}/family/hodotermitidae/">草白蚁科 <i>HODOTERMITIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/anacanthotermes/">无刺白蚁属 <i>Anacanthotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hodotermes/">草白蚁属 <i>Hodotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/microhodotermes/">小草白蚁属 <i>Microhodotermes</i></a></li>
</ul>
</li>
<li data-kind="family"><a href="{{ site.base_url }}/family/hodotermopsidae/">原白蚁科 <i>HODOTERMOPSIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hodotermopsis/">原白蚁属 <i>Hodotermopsis</i></a></li>
</ul>
</li>
<li data-kind="family"><a href="{{ site.base_url }}/family/stolotermitidae/">胄白蚁科 <i>STOLOTERMITIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/porotermes/">洞白蚁属 <i>Porotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/stolotermes/">胄白蚁属 <i>Stolotermes</i></a></li>
</ul>
</li>
</ul>
</li>
<li data-kind="clade"><a href="#icoisoptera">近等翅类 <i>Icoisoptera</i></a>
<ul>
<li data-kind="family"><a href="{{ site.base_url }}/family/kalotermitidae/">木白蚁科 <i>KALOTERMITIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/allotermes/">奇白蚁属 <i>Allotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/bicornitermes/">双角白蚁属 <i>Bicornitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/bifiditermes/">双裂白蚁属 <i>Bifiditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/calcaritermes/">距白蚁属 <i>Calcaritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ceratokalotermes/">角木白蚁属 <i>Ceratokalotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/comatermes/">毛白蚁属 <i>Comatermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cryptotermes/">堆砂白蚁属 <i>Cryptotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/epicalotermes/">上木白蚁属 <i>Epicalotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/eucryptotermes/">真砂白蚁属 <i>Eucryptotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/glyptotermes/">树白蚁属 <i>Glyptotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/incisitermes/">楹白蚁属 <i>Incisitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/kalotermes/">木白蚁属 <i>Kalotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/longicaputermes/">头长白蚁属 <i>Longicaputermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/marginitermes/">边白蚁属 <i>Marginitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/neotermes/">新白蚁属 <i>Neotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/paraneotermes/">近新白蚁属 <i>Paraneotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/postelectrotermes/">后琥珀白蚁属 <i>Postelectrotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/procryptotermes/">前砂白蚁属 <i>Procryptotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/proneotermes/">前新白蚁属 <i>Proneotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/pterotermes/">翅白蚁属 <i>Pterotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/roisinitermes/">罗伊辛白蚁属 <i>Roisinitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rugitermes/">皱白蚁属 <i>Rugitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/tauritermes/">牛白蚁属 <i>Tauritermes</i></a></li>
</ul>
</li>
<li data-kind="clade"><a href="#neoisoptera">新等翅类 <i>Neoisoptera</i></a>
<ul>
<li data-kind="family"><a href="{{ site.base_url }}/family/psammotermitidae/">沙白蚁科 <i>PSAMMOTERMITIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/prorhinotermes/">原鼻白蚁属 <i>Prorhinotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/psammotermes/">沙白蚁属 <i>Psammotermes</i></a></li>
</ul>
</li>
<li data-kind="family"><a href="{{ site.base_url }}/family/rhinotermitidae/">鼻白蚁科 <i>RHINOTERMITIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/acorhinotermes/">尖鼻白蚁属 <i>Acorhinotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/dolichorhinotermes/">狭鼻白蚁属 <i>Dolichorhinotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/parrhinotermes/">棒鼻白蚁属 <i>Parrhinotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rhinotermes/">鼻白蚁属 <i>Rhinotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/schedorhinotermes/">长鼻白蚁属 <i>Schedorhinotermes</i></a></li>
</ul>
</li>
<li data-kind="family"><a href="{{ site.base_url }}/family/serritermitidae/">齿白蚁科 <i>SERRITERMITIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/glossotermes/">舌白蚁属 <i>Glossotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/serritermes/">齿白蚁属 <i>Serritermes</i></a></li>
</ul>
</li>
<li data-kind="family"><a href="{{ site.base_url }}/family/stylotermitidae/">杆白蚁科 <i>STYLOTERMITIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/stylotermes/">杆白蚁属 <i>Stylotermes</i></a></li>
</ul>
</li>
<li data-kind="family"><a href="{{ site.base_url }}/family/termitogetonidae/">寡脉白蚁科 <i>TERMITOGETONIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/termitogeton/">寡脉白蚁属 <i>Termitogeton</i></a></li>
</ul>
</li>
<li data-kind="clade"><a href="#geoisoptera">土栖等翅类 <i>Geoisoptera</i></a>
<ul>
<li data-kind="family"><a href="{{ site.base_url }}/family/heterotermitidae/">异白蚁科 <i>HETEROTERMITIDAE</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/coptotermes/">乳白蚁属 <i>Coptotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/heterotermes/">异白蚁属 <i>Heterotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/reticulitermes/">散白蚁属 <i>Reticulitermes</i></a></li>
</ul>
</li>
<li data-kind="family"><a href="{{ site.base_url }}/family/termitidae/">白蚁科 <i>TERMITIDAE</i></a>
<ul>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/amitermitinae/">弓白蚁亚科 <i>Amitermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ahamitermes/">无钩白蚁属 <i>Ahamitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/amitermes/">弓白蚁属 <i>Amitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/dentispicotermes/">齿尖白蚁属 <i>Dentispicotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/drepanotermes/">镰白蚁属 <i>Drepanotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/eremotermes/">漠白蚁属 <i>Eremotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/globitermes/">球白蚁属 <i>Globitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/gnathamitermes/">颚钩白蚁属 <i>Gnathamitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hoplotermes/">武白蚁属 <i>Hoplotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/incolitermes/">子民白蚁属 <i>Incolitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/invasitermes/">闯白蚁属 <i>Invasitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/orthognathotermes/">直颚白蚁属 <i>Orthognathotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/prohamitermes/">前钩白蚁属 <i>Prohamitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/pseudhamitermes/">伪钩白蚁属 <i>Pseudhamitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/synhamitermes/">同钩白蚁属 <i>Synhamitermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/apicotermitinae/">尖白蚁亚科 <i>Apicotermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/acholotermes/">顺白蚁属 <i>Acholotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/acidnotermes/">虚白蚁属 <i>Acidnotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/acutidentitermes/">尖齿白蚁属 <i>Acutidentitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/adaiphrotermes/">和白蚁属 <i>Adaiphrotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/aderitotermes/">谐白蚁属 <i>Aderitotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/adynatotermes/">弱白蚁属 <i>Adynatotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/aganotermes/">雅白蚁属 <i>Aganotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/allognathotermes/">异颚白蚁属 <i>Allognathotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/alyscotermes/">逃白蚁属 <i>Alyscotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/amalotermes/">软白蚁属 <i>Amalotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/amicotermes/">善白蚁属 <i>Amicotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/amplucrutermes/">大腿白蚁属 <i>Amplucrutermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/anaorotermes/">无戟白蚁属 <i>Anaorotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/anenteotermes/">无甲白蚁属 <i>Anenteotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/anoplotermes/">解甲白蚁属 <i>Anoplotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/apagotermes/">疲白蚁属 <i>Apagotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/aparatermes/">弯肠白蚁属 <i>Aparatermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/apicotermes/">尖白蚁属 <i>Apicotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/apolemotermes/">和平白蚁属 <i>Apolemotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/asagarotermes/">无剑白蚁属 <i>Asagarotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/astalotermes/">无利器白蚁属 <i>Astalotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/astratotermes/">无刃白蚁属 <i>Astratotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ateuchotermes/">无锐白蚁属 <i>Ateuchotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/caputitermes/">首白蚁属 <i>Caputitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/chasitermes/">蔡斯白蚁属 <i>Chasitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/compositermes/">肠刺白蚁属 <i>Compositermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/coxotermes/">基白蚁属 <i>Coxotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/disjunctitermes/">间断白蚁属 <i>Disjunctitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/dissimulitermes/">隐藏白蚁属 <i>Dissimulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/duplidentitermes/">双齿白蚁属 <i>Duplidentitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ebogotermes/">埃博戈白蚁属 <i>Ebogotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/eburnitermes/">象牙白蚁属 <i>Eburnitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/echinotermes/">多刺白蚁属 <i>Echinotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ekueitermes/">肠棘白蚁属 <i>Ekueitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/euhamitermes/">亮白蚁属 <i>Euhamitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/eurytermes/">宽白蚁属 <i>Eurytermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/firmitermes/">坚白蚁属 <i>Firmitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/gastrotermes/">胃白蚁属 <i>Gastrotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/grigiotermes/">灰白蚁属 <i>Grigiotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/heimitermes/">埃姆白蚁属 <i>Heimitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hirsutitermes/">毛糙白蚁属 <i>Hirsutitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hoplognathotermes/">锐颚白蚁属 <i>Hoplognathotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/humutermes/">腐殖白蚁属 <i>Humutermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hydrecotermes/">海德瑞克白蚁属 <i>Hydrecotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/indotermes/">印白蚁属 <i>Indotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/jugositermes/">岗白蚁属 <i>Jugositermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/koutabatermes/">库塔巴白蚁属 <i>Koutabatermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/krecekitermes/">克雷切克白蚁属 <i>Krecekitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/labidotermes/">钳白蚁属 <i>Labidotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/longustitermes/">长工白蚁属 <i>Longustitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/machadotermes/">剑白蚁属 <i>Machadotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/mangolditermes/">曼戈尔德白蚁属 <i>Mangolditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ourissotermes/">海胆白蚁属 <i>Ourissotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/patawatermes/">帕塔瓦白蚁属 <i>Patawatermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/phoxotermes/">锐白蚁属 <i>Phoxotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rostrotermes/">突吻白蚁属 <i>Rostrotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rubeotermes/">变红白蚁属 <i>Rubeotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ruptitermes/">腹爆白蚁属 <i>Ruptitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rustitermes/">拉斯特白蚁属 <i>Rustitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/scheffrahnitermes/">谢弗拉恩白蚁属 <i>Scheffrahnitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/skatitermes/">洁白蚁属 <i>Skatitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/speculitermes/">稀白蚁属 <i>Speculitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/spiralitermes/">螺旋白蚁属 <i>Spiralitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/tetimatermes/">足白蚁属 <i>Tetimatermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/tonsuritermes/">奇囟白蚁属 <i>Tonsuritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/trichotermes/">发白蚁属 <i>Trichotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/triclavitermes/">三棒白蚁属 <i>Triclavitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/tucupitermes/">黄汁白蚁属 <i>Tucupitermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/crepititermitinae/">响白蚁亚科 <i>Crepititermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/crepititermes/">响白蚁属 <i>Crepititermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/cubitermitinae/">方白蚁亚科 <i>Cubitermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/apilitermes/">无毛白蚁属 <i>Apilitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/basidentitermes/">基齿白蚁属 <i>Basidentitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/batillitermes/">铲白蚁属 <i>Batillitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/crenetermes/">刻痕白蚁属 <i>Crenetermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cubitermes/">方白蚁属 <i>Cubitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/euchilotermes/">真唇白蚁属 <i>Euchilotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/fastigitermes/">峰白蚁属 <i>Fastigitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/furculitermes/">叉白蚁属 <i>Furculitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/isognathotermes/">等颚白蚁属 <i>Isognathotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/lepidotermes/">鳞白蚁属 <i>Lepidotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/megagnathotermes/">大颚白蚁属 <i>Megagnathotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/mucrotermes/">锐尖白蚁属 <i>Mucrotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/nitiditermes/">净白蚁属 <i>Nitiditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/noditermes/">节白蚁属 <i>Noditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/okavangotermes/">奥卡万戈白蚁属 <i>Okavangotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ophiotermes/">蛇白蚁属 <i>Ophiotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/orthotermes/">直白蚁属 <i>Orthotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ovambotermes/">奥万博兰白蚁属 <i>Ovambotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/pilotermes/">棘白蚁属 <i>Pilotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/polyspathotermes/">多铲白蚁属 <i>Polyspathotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/proboscitermes/">象鼻白蚁属 <i>Proboscitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/procubitermes/">原方白蚁属 <i>Procubitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/profastigitermes/">前峰白蚁属 <i>Profastigitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ternicubitermes/">三方白蚁属 <i>Ternicubitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/thoracotermes/">胸白蚁属 <i>Thoracotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/trapellitermes/">菱角白蚁属 <i>Trapellitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/unguitermes/">爪白蚁属 <i>Unguitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/unicornitermes/">独角白蚁属 <i>Unicornitermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/cylindrotermitinae/">圆筒白蚁亚科 <i>Cylindrotermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cephalotermes/">头白蚁属 <i>Cephalotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cylindrotermes/">圆筒白蚁属 <i>Cylindrotermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/engelitermitinae/">恩格尔白蚁亚科 <i>Engelitermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/engelitermes/">恩格尔白蚁属 <i>Engelitermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/foraminitermitinae/">孔白蚁亚科 <i>Foraminitermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/foraminitermes/">孔白蚁属 <i>Foraminitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/labritermes/">唇白蚁属 <i>Labritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/pseudomicrotermes/">伪小白蚁属 <i>Pseudomicrotermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/forficulitermitinae/">剪白蚁亚科 <i>Forficulitermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/forficulitermes/">剪白蚁属 <i>Forficulitermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/macrotermitinae/">大白蚁亚科 <i>Macrotermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/acanthotermes/">刺白蚁属 <i>Acanthotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/allodontermes/">奇齿白蚁属 <i>Allodontermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ancistrotermes/">钩白蚁属 <i>Ancistrotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/euscaiotermes/">左转白蚁属 <i>Euscaiotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hypotermes/">地白蚁属 <i>Hypotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/macrotermes/">大白蚁属 <i>Macrotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/megaprotermes/">大前白蚁属 <i>Megaprotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/microtermes/">小白蚁属 <i>Microtermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/odontotermes/">土白蚁属 <i>Odontotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/protermes/">前白蚁属 <i>Protermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/pseudacanthotermes/">伪刺白蚁属 <i>Pseudacanthotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/synacanthotermes/">聚刺白蚁属 <i>Synacanthotermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/microcerotermitinae/">锯白蚁亚科 <i>Microcerotermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/microcerotermes/">锯白蚁属 <i>Microcerotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/onkotermes/">倒钩白蚁属 <i>Onkotermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/mirocapritermitinae/">瘤白蚁亚科 <i>Mirocapritermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/dicuspiditermes/">突扭白蚁属 <i>Dicuspiditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/homallotermes/">平白蚁属 <i>Homallotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/indocapritermes/">印扭白蚁属 <i>Indocapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/kemneritermes/">凯姆勒白蚁属 <i>Kemneritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/krishnacapritermes/">克里希纳扭白蚁属 <i>Krishnacapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/labiocapritermes/">唇扭白蚁属 <i>Labiocapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/mirocapritermes/">瘤白蚁属 <i>Mirocapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/oriencapritermes/">东扭白蚁属 <i>Oriencapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/pericapritermes/">近扭白蚁属 <i>Pericapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/procapritermes/">前扭白蚁属 <i>Procapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/pseudocapritermes/">伪扭白蚁属 <i>Pseudocapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rinacapritermes/">丽娜扭白蚁属 <i>Rinacapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/sinocapritermes/">华扭白蚁属 <i>Sinocapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/syncapritermes/">聚扭白蚁属 <i>Syncapritermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/nasutitermitinae/">象白蚁亚科 <i>Nasutitermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/aciculitermes/">针白蚁属 <i>Aciculitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/afrosubulitermes/">非锥白蚁属 <i>Afrosubulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/agnathotermes/">无颚白蚁属 <i>Agnathotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ahmaditermes/">钝颚白蚁属 <i>Ahmaditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ampoulitermes/">安瓿白蚁属 <i>Ampoulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/angularitermes/">棱角白蚁属 <i>Angularitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/anhangatermes/">魔白蚁属 <i>Anhangatermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/antillitermes/">安的列斯白蚁属 <i>Antillitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/araujotermes/">阿劳若白蚁属 <i>Araujotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/arcotermes/">弧白蚁属 <i>Arcotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/atlantitermes/">阿特拉斯白蚁属 <i>Atlantitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/australitermes/">澳大利亚白蚁属 <i>Australitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/baucaliotermes/">细颈白蚁属 <i>Baucaliotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/bulbitermes/">瓢白蚁属 <i>Bulbitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/caetetermes/">林白蚁属 <i>Caetetermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/caribitermes/">加勒比白蚁属 <i>Caribitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ceylonitermellus/">小锡兰白蚁属 <i>Ceylonitermellus</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ceylonitermes/">锡兰白蚁属 <i>Ceylonitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/coarctotermes/">缩狭白蚁属 <i>Coarctotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/coatitermes/">凸鼻白蚁属 <i>Coatitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/coendutermes/">箭猪白蚁属 <i>Coendutermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/constrictotermes/">缩白蚁属 <i>Constrictotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/convexitermes/">凸白蚁属 <i>Convexitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cortaritermes/">利颚白蚁属 <i>Cortaritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cucurbitermes/">葫白蚁属 <i>Cucurbitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cyranotermes/">巨鼻白蚁属 <i>Cyranotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/diversitermes/">歧白蚁属 <i>Diversitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/diwaitermes/">木象白蚁属 <i>Diwaitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/eleanoritermes/">埃莉诺白蚁属 <i>Eleanoritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/emersonitermes/">埃默森白蚁属 <i>Emersonitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/enetotermes/">针筒白蚁属 <i>Enetotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ereymatermes/">无名白蚁属 <i>Ereymatermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/eutermellus/">小真白蚁属 <i>Eutermellus</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/fulleritermes/">富勒白蚁属 <i>Fulleritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/grallatotermes/">高跷白蚁属 <i>Grallatotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hirtitermes/">多毛白蚁属 <i>Hirtitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hospitalitermes/">须白蚁属 <i>Hospitalitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hyleotermes/">森林白蚁属 <i>Hyleotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/kaudernitermes/">考登白蚁属 <i>Kaudernitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/lacessititermes/">怒白蚁属 <i>Lacessititermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/leptomyxotermes/">薄喙白蚁属 <i>Leptomyxotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/leucopitermes/">白脸白蚁属 <i>Leucopitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/longipeditermes/">长足白蚁属 <i>Longipeditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/macrosubulitermes/">大锥白蚁属 <i>Macrosubulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/malagasitermes/">马尔加什白蚁属 <i>Malagasitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/malaysiotermes/">马来白蚁属 <i>Malaysiotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/mimeutermes/">仿白蚁属 <i>Mimeutermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/muelleritermes/">米勒白蚁属 <i>Muelleritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/mycterotermes/">鸟嘴白蚁属 <i>Mycterotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/nasopilotermes/">棘象白蚁属 <i>Nasopilotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/nasutitermes/">象白蚁属 <i>Nasutitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ngauratermes/">凋落白蚁属 <i>Ngauratermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/niuginitermes/">新几内亚白蚁属 <i>Niuginitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/obtusitermes/">钝白蚁属 <i>Obtusitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/occasitermes/">西部白蚁属 <i>Occasitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/occultitermes/">隐白蚁属 <i>Occultitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/oriensubulitermes/">东锥白蚁属 <i>Oriensubulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/paraconvexitermes/">近凸白蚁属 <i>Paraconvexitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/parvitermes/">微白蚁属 <i>Parvitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/periaciculitermes/">近针白蚁属 <i>Periaciculitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/postsubulitermes/">后锥白蚁属 <i>Postsubulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rhadinotermes/">锥形白蚁属 <i>Rhadinotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/roonwalitermes/">鲁恩沃白蚁属 <i>Roonwalitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rotunditermes/">圆白蚁属 <i>Rotunditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rounditermes/">胖白蚁属 <i>Rounditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/sabahitermes/">沙巴白蚁属 <i>Sabahitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/sandsitermes/">桑兹白蚁属 <i>Sandsitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/sinonasutitermes/">华象白蚁属 <i>Sinonasutitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/sinqasapatermes/">鼻大白蚁属 <i>Sinqasapatermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/spatulitermes/">匙白蚁属 <i>Spatulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/subulioiditermes/">似锥白蚁属 <i>Subulioiditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/subulitermes/">锥白蚁属 <i>Subulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/tarditermes/">慢白蚁属 <i>Tarditermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/tenuirostritermes/">薄嘴白蚁属 <i>Tenuirostritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/tiunatermes/">暗鼻白蚁属 <i>Tiunatermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/triangularitermes/">三角白蚁属 <i>Triangularitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/trinervitermes/">三脉白蚁属 <i>Trinervitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/tumulitermes/">冢白蚁属 <i>Tumulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/velocitermes/">快白蚁属 <i>Velocitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/verrucositermes/">疣白蚁属 <i>Verrucositermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/xiaitermes/">夏氏白蚁属 <i>Xiaitermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/neocapritermitinae/">新扭白蚁亚科 <i>Neocapritermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/neocapritermes/">新扭白蚁属 <i>Neocapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/planicapritermes/">平扭白蚁属 <i>Planicapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/schievitermes/">不对称白蚁属 <i>Schievitermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/promirotermitinae/">前奇白蚁亚科 <i>Promirotermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/angulitermes/">角白蚁属 <i>Angulitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/promirotermes/">前奇白蚁属 <i>Promirotermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/protohamitermitinae/">始钩白蚁亚科 <i>Protohamitermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/orientotermes/">东方白蚁属 <i>Orientotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/protohamitermes/">始钩白蚁属 <i>Protohamitermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/sphaerotermitinae/">圆球白蚁亚科 <i>Sphaerotermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/sphaerotermes/">圆球白蚁属 <i>Sphaerotermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/syntermitinae/">聚白蚁亚科 <i>Syntermitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/acangaobitermes/">漏斗白蚁属 <i>Acangaobitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/armitermes/">戟白蚁属 <i>Armitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/bandeiratermes/">班代拉白蚁属 <i>Bandeiratermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/biratermes/">拜拉白蚁属 <i>Biratermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cahuallitermes/">弃白蚁属 <i>Cahuallitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cornitermes/">角象白蚁属 <i>Cornitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/curvitermes/">曲白蚁属 <i>Curvitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cyrilliotermes/">壶头白蚁属 <i>Cyrilliotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/embiratermes/">生白蚁属 <i>Embiratermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/genuotermes/">膝白蚁属 <i>Genuotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ibitermes/">地球白蚁属 <i>Ibitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/labiotermes/">厚唇白蚁属 <i>Labiotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/macuxitermes/">马库希白蚁属 <i>Macuxitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/mapinguaritermes/">红懒白蚁属 <i>Mapinguaritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/noirotitermes/">努瓦罗白蚁属 <i>Noirotitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/paracurvitermes/">近曲白蚁属 <i>Paracurvitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/procornitermes/">前角白蚁属 <i>Procornitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/rhynchotermes/">喙白蚁属 <i>Rhynchotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/silvestritermes/">西尔韦斯特里白蚁属 <i>Silvestritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/syntermes/">聚白蚁属 <i>Syntermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/uncitermes/">弯钩白蚁属 <i>Uncitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/vaninitermes/">瓦宁白蚁属 <i>Vaninitermes</i></a></li>
</ul>
</li>
<li data-kind="subfamily"><a href="{{ site.base_url }}/subfamily/termitinae/">白蚁亚科 <i>Termitinae</i></a>
<ul>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/apsenterotermes/">后肠白蚁属 <i>Apsenterotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/capritermes/">扭白蚁属 <i>Capritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cavitermes/">腔白蚁属 <i>Cavitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cornicapritermes/">角扭白蚁属 <i>Cornicapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/cristatitermes/">脊突白蚁属 <i>Cristatitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/dihoplotermes/">双戟白蚁属 <i>Dihoplotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/divinotermes/">迪维努白蚁属 <i>Divinotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ekphysotermes/">瘤突白蚁属 <i>Ekphysotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/ephelotermes/">棒颚白蚁属 <i>Ephelotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hapsidotermes/">络白蚁属 <i>Hapsidotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/hesperotermes/">西澳白蚁属 <i>Hesperotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/inquilinitermes/">客白蚁属 <i>Inquilinitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/lophotermes/">小脊突白蚁属 <i>Lophotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/macrognathotermes/">长颚白蚁属 <i>Macrognathotermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/palmitermes/">棕榈白蚁属 <i>Palmitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/paracapritermes/">旁扭白蚁属 <i>Paracapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/protocapritermes/">始扭白蚁属 <i>Protocapritermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/quasitermes/">相似白蚁属 <i>Quasitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/saxatilitermes/">石白蚁属 <i>Saxatilitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/spinitermes/">针刺白蚁属 <i>Spinitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/termes/">白蚁属 <i>Termes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/tuberculitermes/">小瘤白蚁属 <i>Tuberculitermes</i></a></li>
<li data-kind="genus"><a href="{{ site.base_url }}/genus/xylochomitermes/">木堆白蚁属 <i>Xylochomitermes</i></a></li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</nav>

<h2 id="isoptera" class="clade-h clade-lvl-1">现存等翅下目 Extant Isoptera</h2>

<p class="clade-count clade-lvl-1">共 13 科 · 18 亚科 · 326 属 · 3021 种 · 68 亚种（含下分支系）</p>
<p class="clade-sub clade-lvl-1">下分 <a href="#euisoptera">真等翅类 Euisoptera</a>（见下文）。直接归入本支系的科如下：</p>

<ul class="taxon-list clade-lvl-1">
<li><a href="{{ site.base_url }}/family/mastotermitidae/">澳白蚁科 <i>MASTOTERMITIDAE</i></a> <span class="taxon-count">1 属 · 1 种</span></li>
</ul>

<h3 id="euisoptera" class="clade-h clade-lvl-2">真等翅类 Euisoptera</h3>

<p class="clade-count clade-lvl-2">共 12 科 · 18 亚科 · 325 属 · 3020 种 · 68 亚种（含下分支系）</p>
<p class="clade-sub clade-lvl-2">本支系不含直接归属的科，下分 <a href="#teletisoptera">远等翅类 Teletisoptera</a>、<a href="#icoisoptera">近等翅类 Icoisoptera</a>（见下文）。</p>

<h4 id="teletisoptera" class="clade-h clade-lvl-3">远等翅类 Teletisoptera</h4>

<p class="clade-count clade-lvl-3">共 4 科 · 8 属 · 37 种 · 2 亚种</p>

<ul class="taxon-list clade-lvl-3">
<li><a href="{{ site.base_url }}/family/archotermopsidae/">古白蚁科 <i>ARCHOTERMOPSIDAE</i></a> <span class="taxon-count">2 属 · 5 种 · 2 亚种</span></li>
<li><a href="{{ site.base_url }}/family/hodotermitidae/">草白蚁科 <i>HODOTERMITIDAE</i></a> <span class="taxon-count">3 属 · 21 种</span></li>
<li><a href="{{ site.base_url }}/family/hodotermopsidae/">原白蚁科 <i>HODOTERMOPSIDAE</i></a> <span class="taxon-count">1 属 · 1 种</span></li>
<li><a href="{{ site.base_url }}/family/stolotermitidae/">胄白蚁科 <i>STOLOTERMITIDAE</i></a> <span class="taxon-count">2 属 · 10 种</span></li>
</ul>

<h4 id="icoisoptera" class="clade-h clade-lvl-3">近等翅类 Icoisoptera</h4>

<p class="clade-count clade-lvl-3">共 8 科 · 18 亚科 · 317 属 · 2983 种 · 66 亚种（含下分支系）</p>
<p class="clade-sub clade-lvl-3">下分 <a href="#neoisoptera">新等翅类 Neoisoptera</a>（见下文）。直接归入本支系的科如下：</p>

<ul class="taxon-list clade-lvl-3">
<li><a href="{{ site.base_url }}/family/kalotermitidae/">木白蚁科 <i>KALOTERMITIDAE</i></a> <span class="taxon-count">23 属 · 480 种 · 4 亚种</span></li>
</ul>

<h5 id="neoisoptera" class="clade-h clade-lvl-4">新等翅类 Neoisoptera</h5>

<p class="clade-count clade-lvl-4">共 7 科 · 18 亚科 · 294 属 · 2503 种 · 62 亚种（含下分支系）</p>
<p class="clade-sub clade-lvl-4">下分 <a href="#geoisoptera">土栖等翅类 Geoisoptera</a>（见下文）。直接归入本支系的科如下：</p>

<ul class="taxon-list clade-lvl-4">
<li><a href="{{ site.base_url }}/family/psammotermitidae/">沙白蚁科 <i>PSAMMOTERMITIDAE</i></a> <span class="taxon-count">2 属 · 18 种</span></li>
<li><a href="{{ site.base_url }}/family/rhinotermitidae/">鼻白蚁科 <i>RHINOTERMITIDAE</i></a> <span class="taxon-count">5 属 · 62 种</span></li>
<li><a href="{{ site.base_url }}/family/serritermitidae/">齿白蚁科 <i>SERRITERMITIDAE</i></a> <span class="taxon-count">2 属 · 3 种</span></li>
<li><a href="{{ site.base_url }}/family/stylotermitidae/">杆白蚁科 <i>STYLOTERMITIDAE</i></a> <span class="taxon-count">1 属 · 45 种</span></li>
<li><a href="{{ site.base_url }}/family/termitogetonidae/">寡脉白蚁科 <i>TERMITOGETONIDAE</i></a> <span class="taxon-count">1 属 · 2 种</span></li>
</ul>

<h6 id="geoisoptera" class="clade-h clade-lvl-5">土栖等翅类 Geoisoptera</h6>

<p class="clade-count clade-lvl-5">共 2 科 · 18 亚科 · 283 属 · 2373 种 · 62 亚种</p>

<ul class="taxon-list clade-lvl-5">
<li><a href="{{ site.base_url }}/family/heterotermitidae/">异白蚁科 <i>HETEROTERMITIDAE</i></a> <span class="taxon-count">3 属 · 229 种 · 8 亚种</span></li>
<li><a href="{{ site.base_url }}/family/termitidae/">白蚁科 <i>TERMITIDAE</i></a> <span class="taxon-count">280 属 · 2144 种 · 54 亚种</span></li>
</ul>

{%- assign fk = site.data.fauna_keys["/list/"] -%}{%- if fk %}{% include fauna-keys.html fk=fk %}{%- endif %}

<h2 id="references">参考文献</h2>

1. Desneux J. À propos de la phylogénie des
    Termitides. Ann Soc Entomol Belg. 1904;
    48(8):278-286.

2. Bourguignon T, Lo N, Cameron SL, Šobotník
    J, Hayashi Y, Shigenobu S, et al. The
    evolutionary history of termites as inferred
    from 66 mitochondrial genomes. Mol Biol Evol.
    2015;
    32(2):406-421. [doi: 10.1093/molbev/msu308](https://doi.org/10.1093/molbev/msu308)

3. Krishna K, Grimaldi DA, Krishna V, Engel
    MS. Treatise on the Isoptera of the world.
    Bull Am Mus Nat Hist. 2013;
    377:1-2704. [doi: 10.1206/377.1](https://doi.org/10.1206/377.1)

4. Evans TA, Forschler BT, Grace JK. Biology
    of invasive termites: a worldwide review.
    Annu Rev Entomol. 2013;
    58:455-474. [doi: 10.1146/annurev-ento-120811-153554](https://doi.org/10.1146/annurev-ento-120811-153554)

5. Engel MS, Grimaldi DA, Krishna K. Termites
    (Isoptera): their phylogeny, classification,
    and rise to ecological dominance. Am Mus
    Novit. 2009;
    3650:1-27. [doi: 10.1206/651.1](https://doi.org/10.1206/651.1)

6. Oregon State University Extension.
    Controlling dampwood termites [Internet].
    [cited 2026 Oct 16].

7. Harris WV. Termites of the genus
    Anacanthotermes in North Africa and the Near
    East (Isoptera: Hodotermitidae). Proc R
    Entomol Soc Lond B. 1967;
    36(5-6):79-86. [doi: 10.1111/j.1365-3113.1967.tb00540.x](https://doi.org/10.1111/j.1365-3113.1967.tb00540.x)

8. Rouland-Lefèvre C. Termites as pests of
    agriculture. In: Bignell DE, Roisin Y, Lo N,
    editors. Biology of termites: a modern
    synthesis. Dordrecht: Springer;
     2011. p. 499-517. [doi: 10.1007/978-90-481-3977-4_18](https://doi.org/10.1007/978-90-481-3977-4_18)

9. Khamraev AS, Lebedeva NI, Zuginisov TI,
    Abdullaev II, Rakhmatullaev A, Raina AK. Food
    preferences of the Turkestan termite
    Anacanthotermes turkestanicus (Isoptera:
    Hodotermitidae). Sociobiology. 2007;
    50(2):469-478.

10. Mitchell JD. Termites as pests of crops,
    forestry, rangeland and structures in
    southern Africa and their control.
    Sociobiology. 2002;
    40(1):47-69.

11. Blattodea Species File. Hodotermopsidae
    Engel, 2021 [Internet]. [cited 2026 Oct 13].

12. GBIF. Hodotermopsis sjostedti Holmgren,
    1911 [Internet]. [cited 2026 Oct 13].

13. 智汇三农. 山林原白蚁 Hodotermopsis sjostedti
    [Internet]. [cited 2026 Oct 16].

14. Holmgren N. Das System der Termiten. Zool
    Anz. 1910;
    35(9-10):284-286.

15. Artigas JN, Villan L. Resistencia
    termitica de la madera a Porotermes
    quadricollis (Rambur), termita de la madera
    humeda (Isoptera, Termopsidae). Gayana
    (Concepc). 2009;
    73(1):1-11. [doi: 10.4067/S0717-65382009000100001](https://doi.org/10.4067/S0717-65382009000100001)

16. Engel MS. Family-group names for termites
    (Isoptera), redux. ZooKeys. 2011;
    148:171-184. [doi: 10.3897/zookeys.148.1682](https://doi.org/10.3897/zookeys.148.1682)

17. Chouvenc T, Šobotník J, Engel MS,
    Bourguignon T. Termite evolution: mutualistic
    associations, key innovations, and the rise
    of Termitidae. Cell Mol Life Sci. 2021;
    78(6):2749-2769. [doi: 10.1007/s00018-020-03728-z](https://doi.org/10.1007/s00018-020-03728-z)

18. University of Florida IFAS Extension.
    Western drywood termite, Incisitermes minor
    (Hagen) (Insecta: Blattodea: Kalotermitidae)
    [Internet]. [cited 2026 Oct 13].

19. Thirugnanasuntharan K, Jayachandran ICR.
    Distinctive morphological characters of
    termites in high and mid grown tea in Sri
    Lanka. Sri Lanka J Tea Sci. 1989;
    58(2):104-110.

20. Laffont ER. Daños de Rugitermes sp.
    (Isoptera: Kalotermitidae) en Ilex
    paraguariensis. AgriScientia. 2005;
    22(1):33-35. [doi: 10.31047/1668.298x.v22.n1.2677](https://doi.org/10.31047/1668.298x.v22.n1.2677)

21. Hellemans S, Rocha MM, Wang M, Romero
    Arias J, Aanen DK, Bagnères AG, et al.
    Genomic data provide insights into the
    classification of extant termites. Nat
    Commun. 2024;
    15:6724. [doi: 10.1038/s41467-024-51028-y](https://doi.org/10.1038/s41467-024-51028-y)

22. Termite Web. Termite pictures –
    Prorhinotermes flavus [Internet]. [cited 2026
    Oct 13].

23. Hebrew University of Jerusalem, Robert H.
    Smith Faculty of Agriculture. Psammotermes
    hypostoma [Internet]. [cited 2026 Oct 16].

24. University of Florida IFAS Extension.
    Cuban subterranean termite, Prorhinotermes
    simplex [Internet]. [cited 2026 Oct 16].

25. ABIS. Schedorhinotermes species
    [Internet]. [cited 2026 Oct 13].

26. Šobotník J, Bourguignon T, Hanus R,
    Sillam-Dussès D, Pflegerová J, Weyda F, et
    al. Not only soldiers have weapons: evolution
    of the frontal gland in imagoes of the
    termite families Rhinotermitidae and
    Serritermitidae. PLoS One. 2010;
    5(12):e15761. [doi: 10.1371/journal.pone.0015761](https://doi.org/10.1371/journal.pone.0015761)

27. Liang WR, Wu CC, Li HF. Discovery of a
    cryptic termite genus, Stylotermes (Isoptera:
    Stylotermitidae), in Taiwan, with the
    description of a new species. Ann Entomol Soc
    Am. 2017;
    110(4):360-373. [doi: 10.1093/aesa/sax034](https://doi.org/10.1093/aesa/sax034)

28. Wu LW, Bourguignon T, Šobotník J, Wen P,
    Liang WR, Li HF. Phylogenetic position of the
    enigmatic termite family Stylotermitidae
    (Insecta: Blattodea). Invertebr Syst. 2018;
    32(5):1111-1117. [doi: 10.1071/IS17093](https://doi.org/10.1071/IS17093)

29. Dolejšová K, Krasulová J, Kutalová K,
    Hanus R. Chemical alarm in the termite
    Termitogeton planus (Rhinotermitidae). J Chem
    Ecol. 2014;
    40(11-12):1269-1276. [doi: 10.1007/s10886-014-0515-0](https://doi.org/10.1007/s10886-014-0515-0)

30. Parmentier D, Roisin Y. Caste morphology
    and development in Termitogeton nr. planus
    (Insecta, Isoptera, Rhinotermitidae). J
    Morphol. 2003;
    255(1):69-79. [doi: 10.1002/jmor.10047](https://doi.org/10.1002/jmor.10047)

31. University of Florida IFAS Extension.
    Formosan subterranean termite, Coptotermes
    formosanus Shiraki [Internet]. [cited 2026
    Oct 13].

32. ISSG;
     IUCN. Global Invasive Species Database —
    Species profile: Coptotermes formosanus
    (Formosan subterranean termite) [Internet].
    2006 [cited 2026 Oct 16].

33. 中华人民共和国国家质量监督检验检疫总局. SN/T 1105-2014
    大家白蚁检疫鉴定方法（Detection and identification of
    Coptotermes curvignathus Holmgren）[Internet].
    2014 [cited 2026 Oct 16].

34. Constantino R. The pest termites of South
    America: taxonomy, distribution and status. J
    Appl Entomol. 2002;
    126(7-8):355-365. [doi: 10.1046/j.1439-0418.2002.00670.x](https://doi.org/10.1046/j.1439-0418.2002.00670.x)

35. Bordereau C, Robert A, Van Tuyen V,
    Peppuy A. Suicidal defensive behaviour by
    frontal gland dehiscence in Globitermes
    sulphureus Haviland soldiers (Isoptera).
    Insectes Soc. 1997;
    44(3):289-297. [doi: 10.1007/s000400050049](https://doi.org/10.1007/s000400050049)

36. Bodine MC, Ueckert DN. Effect of desert
    termites on herbage and litter in a
    shortgrass ecosystem in west Texas. J Range
    Manage. 1975;
    28(5):353-358. [doi: 10.2307/3897490](https://doi.org/10.2307/3897490)

37. Watson JAL, Perry DH. The Australian
    harvester termites of the genus Drepanotermes
    (Isoptera, Termitinae). Aust J Zool Suppl
    Ser. 1981;
    29(78):1-153.

38. Kumar R. Termite, a new pest of potato in
    India. Indian Potato J. 1965;
    7(1):1-49.

39. Abdul Hafiz AM, Abu Hassan A. Foraging
    population, territory and control of
    Globitermes sulphureus (Isoptera: Termitidae)
    with fipronil in Penang, Malaysia. Malays
    Appl Biol. 2012;
    40(2).

40. Malaka SLO. Economic importance of
    termites: six case studies in Nigeria and
    Ghana. Nigerian Field. 1983;
    47(4):222-230.

41. Grassé PP, Noirot C. Apicotermes arquieri
    (Isoptère): ses constructions, sa biologie.
    Considérations générales sur la sous-famille
    des Apicotermitinae nov. Ann Sci Nat Zool.
    1955;
    16(3-4):345-388.

42. Czepak C, Ferreira E, Nogueira SB.
    Identificação e quantificação de cupins
    rizófagos na cultura do arroz de sequeiro.
    Pesqui Agropecu Bras. 1993;
    28(8):871-875.

43. Amaral-Castro NR, Zanetti R, Moraes JC,
    Zanuncio JC. Species of soil inhabiting
    termites (Insecta: Isoptera) collected in
    Eucalyptus plantations in the State of Minas
    Gerais, Brazil. Sociobiology. 2004;
    44(3):717-727.

44. Ministério da Agricultura e Pecuária
    (MAPA/AGROFIT). Cupim (Aparatermes
    abbreviatus) — Controles Registrados
    [Internet]. [cited 2026 Oct 16].

45. Rocha MM, Cuezzo C. Redescription of the
    monotypic Neotropical genus Crepititermes
    Emerson (Termitidae: Termitinae). Neotrop
    Entomol. 2015;
    44(5):457-465. [doi: 10.1007/s13744-015-0307-4](https://doi.org/10.1007/s13744-015-0307-4)

46. Roonwal ML, Verma SC. Evolution and
    systematic significance of wing
    micro-sculpturing in termites. IX. Subfamily
    Termitinae of family Termitidae. Proc Indian
    Natl Sci Acad B. 1980;
    46(4):455-469.

47. Mikaelyan A, Dietrich C, Köhler T,
    Poulsen M, Sillam-Dussès D, Brune A. Diet is
    the primary determinant of bacterial
    community structure in the guts of higher
    termites. Mol Ecol. 2015;
    24(20):5284-5295. [doi: 10.1111/mec.13376](https://doi.org/10.1111/mec.13376)

48. Okwakol MJN. Effects of Cubitermes
    testaceus (Williams) on some physical and
    chemical properties of soil in a grassland
    area of Uganda. Afr J Ecol. 1987;
    25(3):147-153. [doi: 10.1111/j.1365-2028.1987.tb01101.x](https://doi.org/10.1111/j.1365-2028.1987.tb01101.x)

49. Friedrich MW, Schmitt-Wagner D, Lueders
    T, Brune A. Axial differences in community
    structure of Crenarchaeota and Euryarchaeota
    in the highly compartmentalized gut of the
    soil-feeding termite Cubitermes orthognathus.
    Appl Environ Microbiol. 2001;
    67(10):4880-4890. [doi: 10.1128/AEM.67.10.4880-4890.2001](https://doi.org/10.1128/AEM.67.10.4880-4890.2001)

50. Kooyman C, Onck RFM. The interactions
    between termite activity, agricultural
    practices and soil characteristics in Kisii
    District, Kenya. Agricultural University
    Wageningen Papers 87-3. Wageningen:
    Wageningen Agricultural University;
     1987.

51. Miranda CS, Vasconcellos A, Bandeira AG.
    Termites in sugar cane in Northeast Brazil:
    ecological aspects and pest status. Neotrop
    Entomol. 2004;
    33(2):237-241. [doi: 10.1590/S1519-566X2004000200015](https://doi.org/10.1590/S1519-566X2004000200015)

52. Romero Arias J, Hellemans S, Kaymak E,
    Akama PD, Bourguignon T, Roisin Y, et al.
    Mitochondrial phylogenetics position a new
    Afrotropical termite species into its own
    subfamily, the Engelitermitinae (Blattodea:
    Termitidae). Syst Entomol. 2024;
    49(1):72-83. [doi: 10.1111/syen.12607](https://doi.org/10.1111/syen.12607)

53. ICZN. Opinion 2038 (Case 3155):
    Macrotermitinae Kemner, 1934 (Insecta,
    Isoptera): precedence over Acanthotermitinae
    Sjöstedt, 1926. Bull Zool Nomencl. 2003;
    60(2):162.

54. Aanen DK, Eggleton P, Rouland-Lefèvre C,
    Guldberg-Frøslev T, Rosendahl S, Boomsma JJ.
    The evolution of fungus-growing termites and
    their mutualistic fungal symbionts. Proc Natl
    Acad Sci U S A. 2002;
    99(23):14887-14892. [doi: 10.1073/pnas.222313099](https://doi.org/10.1073/pnas.222313099)

55. Huang QY, Lei CL, Xue D. Field evaluation
    of a fipronil bait against subterranean
    termite Odontotermes formosanus (Isoptera:
    Termitidae). J Econ Entomol. 2006;
    99(2):455-461. [doi: 10.1603/0022-0493-99.2.455](https://doi.org/10.1603/0022-0493-99.2.455)

56. 李茅苗. 白蚁对甘蔗的为害及防治措施. 植物医生. 2013;(2).

57. Rana A, Chandel RS, Verma KS, Joshi MJ.
    Termites in important crops and their
    management. Indian J Entomol. 2021;
    83(3):486-504. [doi: 10.5958/0974-8172.2021.00001.8](https://doi.org/10.5958/0974-8172.2021.00001.8)

58. Deka B, Babu A, Peter AJ, Kumhar KC,
    Sarkar S, Rajbongshi H, et al. Potential of
    the entomopathogenic fungus, Metarhizium
    anisopliae s.l. in controlling live-wood
    eating termite, Microtermes obesi (Holmgren)
    (Blattodea: Termitidae) infesting tea crop.
    Egypt J Biol Pest Control. 2021;
    31:132. [doi: 10.1186/s41938-021-00477-4](https://doi.org/10.1186/s41938-021-00477-4)

59. Habibpour B. Laboratory evaluation of
    Flurox, a chitin synthesis inhibitor, on the
    termite, Microcerotermes diversus. J Insect
    Sci. 2010;
    10:2. [doi: 10.1673/031.010.0201](https://doi.org/10.1673/031.010.0201)

60. Sales MJD, Matos WC, Reis YT, Ribeiro GT.
    Frequência e riqueza de cupins em áreas de
    plantio de eucalipto no litoral norte da
    Bahia. Pesqui Agropecu Bras. 2010;
    45(12):1351-1356. [doi: 10.1590/S0100-204X2010001200003](https://doi.org/10.1590/S0100-204X2010001200003)

61. Kuan KC, Chiu CI, Shih MC, Chi KJ, Li HF.
    Termite's twisted mandible presents fast,
    powerful, and precise strikes. Sci Rep. 2020;
    10:9462. [doi: 10.1038/s41598-020-66294-1](https://doi.org/10.1038/s41598-020-66294-1)

62. Pinnamaneni R, Potineni K. Integrated
    pest management (IPM) in oil palm, Elaeis
    guineensis Jacq. In: Palm oil – current
    status and updates. London: IntechOpen;
     2023. [doi: 10.5772/intechopen.108580](https://doi.org/10.5772/intechopen.108580)

63. Hare L. Termite phylogeny as evidenced by
    soldier mandible development. Ann Entomol Soc
    Am. 1937;
    30(3):459-486. [doi: 10.1093/aesa/30.3.459](https://doi.org/10.1093/aesa/30.3.459)

64. Nutting WL, Blum MS, Fales HM. Behavior
    of the North American termite
    Tenuirostritermes tenuirostris, with special
    reference to the soldier frontal gland
    secretion, its chemical composition, and use
    in defense. Psyche (Camb Mass). 1974;
    81:167-177. [doi: 10.1155/1974/13854](https://doi.org/10.1155/1974/13854)

65. Coconut Research Institute (Sri Lanka).
    Termites and their control [Internet]. [cited
    2026 Oct 13].

66. University of Florida IFAS Extension.
    Conehead termite, Nasutitermes corniger
    (Motschulsky) (Insecta: Blattodea:
    Termitidae: Nasutitermitinae) [Internet].
    [cited 2026 Oct 13].

67. Ye F, Ke YL, Li ZQ. Revisiting a Chinese
    Endemic Termite Genus of Building Timber
    Pests: Mitochondrial Genomic and
    Morphological Dissection and Phylogenetic
    Positioning of Xiaitermes Gao & He, 1994
    (Termitidae: Nasutitermitinae). Insects. 2026;
    17(6):602. [doi: 10.3390/insects17060602](https://doi.org/10.3390/insects17060602)

68. Roonwal ML, Rathore NS. New termite pests
    of eucalyptus in India and their control. Z
    Angew Entomol. 1984;
    98(1-5):225-230. [doi: 10.1111/j.1439-0418.1984.tb02705.x](https://doi.org/10.1111/j.1439-0418.1984.tb02705.x)

69. Lovleen, Prerna. Control measures for
    Hospitalitermes monoceros, a major pest of
    sugarcane by using medicinal plants. J Punjab
    Acad Forensic Med Toxicol. 2019;
    19(1):35-38. [doi: 10.5958/0974-083X.2019.00007.4](https://doi.org/10.5958/0974-083X.2019.00007.4)

70. Šobotník J, Bourguignon T, Hanus R,
    Demianová Z, Pytelková J, Mareš M, et al.
    Explosive backpacks in old termite workers.
    Science. 2012;
    337(6093):436. [doi: 10.1126/science.1219129](https://doi.org/10.1126/science.1219129)

71. Junqueira LK, Gonçalves ER, Teixeira LMC.
    Termite communities in sugarcane plantations
    in southeastern Brazil: an ecological
    approach. EntomoBrasilis. 2015;
    8(2):105-116. [doi: 10.12741/ebrasilis.v8i2.502](https://doi.org/10.12741/ebrasilis.v8i2.502)

72. Lind BM, Hanan NP, Gigliotti LC, Allen
    RL, McHenry A, Gardiner A. Termite diversity
    along a catena in southern Kruger National
    Park, South Africa. Afr J Ecol. 2019;
    57(1):160-165. [doi: 10.1111/aje.12569](https://doi.org/10.1111/aje.12569)

73. Engel MS, Krishna K. Family-group names
    for termites (Isoptera). Am Mus Novit. 2004;
    3432:1-9. [doi: 10.1206/0003-0082(2004)432<0001:FNFTI>2.0.CO;2](https://doi.org/10.1206/0003-0082%282004%29432%3C0001:FNFTI%3E2.0.CO%3B2)

74. Andres-Bray TC, Smith J, Nichols I, Abwe
    EE, Gonder MK. Ecological correlates of
    chimpanzee termite fishing behavior in Mbam &
    Djerem National Park, Cameroon. Ecol Evol.
    2024;
    14(7):e70080. [doi: 10.1002/ece3.70080](https://doi.org/10.1002/ece3.70080)

75. Silva GH, Godoi-Junior MA, Martins JVS,
    Ribeiro LS, Ribeiro JPO, Araújo FF, et al.
    First report the Syntermes molestus Burm.
    (1839)
    (Isoptera: Termitidae) causing severe
    mechanical damage to Solanum tuberosum roots.
    Braz J Biol. 2023;
    83:e269325. [doi: 10.1590/1519-6984.269325](https://doi.org/10.1590/1519-6984.269325)

76. Silva KL, Ladeia S, Nunes W, Santos ICL,
    Santos A. Occurrence of Tectona grandis stem
    injury caused by Cornitermes cumulans
    termite. Floresta Ambient. 2019;
    26(3):e20180356. [doi: 10.1590/2179-8087.035618](https://doi.org/10.1590/2179-8087.035618)

77. Cabaña Acosta ME, Alonzo Griffith LA,
    Gaona Mena E, Chamorro Díaz SM, Sarubbi-Orue
    H, Ruiz Samudio FP, et al. Incidencia y
    distribución de termiteros sobre pastizal:
    requisito previo para su manejo y control en
    condiciones de campo. Rev Investig Estud UNA.
    2024;
    15(1):62-70. [doi: 10.57201/ieuna2413372](https://doi.org/10.57201/ieuna2413372)
