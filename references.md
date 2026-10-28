---
layout: default
title: 参考文献与 DOI — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: 名录 77 条参考文献的增强版：逐条给出 DOI、Crossref 书目记录、GB/T 7714 式 / APA 7 / Vancouver 引用格式，以及 BibTeX、RIS、CSL-JSON，可一键复制或下载。
lang: zh-CN
author: 班奈特格林
date: 2026-10-17
version: 2026.10.17
keywords: [白蚁, 等翅目, Isoptera, 参考文献, DOI, Crossref, GB/T 7714, APA, BibTeX, RIS, CSL-JSON]
permalink: /references/
---

# 参考文献与 DOI <span class="fact-en">References &amp; DOIs</span>

{%- assign refmeta = site.data.references.meta -%}
{%- assign refcounts = refmeta.counts -%}

<p>名录 <a href="{{ site.base_url }}/list/#references">/list/</a> 末尾的 {{ refcounts.total }} 条参考文献，在本页展开为逐条可复制的书目条目：每条给出 <strong>DOI 链接</strong>、<strong>Crossref 书目记录</strong>，以及 <strong>GB/T 7714 式</strong>、<strong>APA 7</strong>、<strong>Vancouver</strong> 三种引用格式和 <strong>BibTeX / RIS / CSL-JSON</strong> 机器可读格式。</p>

## 解析统计 <span class="fact-en">Coverage</span>

<ul>
  <li>条目总数：<strong>{{ refcounts.total }}</strong> 条（与名录末尾编号一一对应）</li>
  <li>带 DOI：<strong>{{ refcounts.with_doi }}</strong> 条，其中 <strong>{{ refcounts.crossref_resolved }}</strong> 条已由 Crossref 返回书目记录</li>
  <li>候选 DOI（Crossref 检索自动匹配、<strong>待人工核对</strong>）：<strong>{{ refcounts.candidates }}</strong> 条</li>
  <li>BHL 原始描述扫描：<strong>{{ refcounts.bhl }}</strong> 条（可选增强，见下）</li>
</ul>

<h2 id="sources">数据来源 <span class="fact-en">Sources</span></h2>

<ul>
  <li><strong>原文</strong>：名录文末的 77 条参考文献，按原编号、原措辞保留，不改写、不合并。</li>
  <li><strong>Crossref</strong>（<a href="https://www.crossref.org/" target="_blank" rel="noopener">crossref.org</a>）：逐条按 DOI 取书目记录（标题、作者、刊名、卷期、页码、出版者、类型、ISSN、被引次数）；原文没有 DOI 的条目只做书目检索，命中的结果仅作<strong>候选</strong>列出，供人工核对。</li>
  <li><strong>BHL</strong>（<a href="https://about.biodiversitylibrary.org/" target="_blank" rel="noopener">Biodiversity Heritage Library</a>）：可为早期原始描述补上扫描件链接，需要免费 API key，属可选项。</li>
</ul>

<h2 id="howto">引用说明 <span class="fact-en">How to cite</span></h2>

<ul>
  <li><strong>GB/T 7714 式</strong>：作者（超过 3 人取前 3 位加 et al）、题名、文献类型标识（[J] 期刊、[M] 专著、[C] 会议录等）、刊名、年、卷（期）、页码，末附 DOI。</li>
  <li><strong>APA 7</strong>：作者、年份、题名、刊名、卷（期）、页码，末附 <code>https://doi.org/…</code>。</li>
  <li><strong>Vancouver</strong>：作者（超过 6 人取前 6 位加 et al）、题名、刊名、年;卷（期）:页码。</li>
  <li>三种格式的全部字段都来自 Crossref 原始记录；<strong>Crossref 没有的字段一律留空，不推测、不补写</strong>。文献类型标识按 Crossref 的 <code>type</code> 映射（如 <code>book-chapter</code> → [M]）。</li>
  <li>题名、作者大小写沿用 Crossref 记录（出版方录入习惯）；个别记录的作者名整体大写，已按首字母大写归一，未做任何翻译或改写。</li>
  <li>标有「<strong>自动匹配待核对</strong>」的条目，其 DOI 由标题相似度与年份双重匹配得到，引用前请自行核对；标有「原文无 DOI」的条目，其候选 DOI 仅供参考，未被采用。</li>
</ul>

<h2 id="bhl">BHL 原始描述扫描 <span class="fact-en">BHL original descriptions</span></h2>

<p>早期分类学文献的原始描述多藏于 BHL。配置免费 API key（环境变量 <code>BHL_API_KEY</code>）后运行 <code>python .github/workflows/build_references.py --write --bhl</code>，脚本会按标题检索 BHL，为命中的条目补 <code>bhl.url</code>（书目级链接，不下载扫描件）。目前 <strong>{{ refcounts.bhl }}</strong> 条带此链接；未配置 key 或 BHL 不可达时该字段保持 <code>null</code>，页面其余内容不受影响。</p>

<h2 id="download">下载与批量使用 <span class="fact-en">Download</span></h2>

<p>整份数据（含每条的原引用、DOI 状态、Crossref 字段、三种格式、BibTeX、RIS、CSL-JSON、BHL）见 <a href="{{ site.base_url }}/data/references.json"><code>data/references.json</code></a>；页首的「导出 CSL-JSON」按钮可在浏览器内直接导出可导入 Zotero / EndNote / Mendeley 的 CSL-JSON 数组（无 JavaScript 时用上面的 JSON 链接即可）。</p>

<p>本页是名录的<strong>增强视图</strong>：权威条目仍以 <a href="{{ site.base_url }}/list/#references">名录页文末的参考文献</a>为准，本页只增加 DOI 解析与机器可读格式，两处的编号、条数、原文措辞完全一致。</p>

<p>引用整份名录（数据集）请用：班奈特格林. (2026). 《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》({{ site.dataset.version }} 版) [Data set]. {{ site.dataset.publisher }}. <a href="https://doi.org/{{ site.dataset.doi }}">https://doi.org/{{ site.dataset.doi }}</a></p>

{% include references.html %}
