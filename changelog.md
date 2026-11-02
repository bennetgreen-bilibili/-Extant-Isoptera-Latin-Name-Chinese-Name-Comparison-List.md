---
layout: default
title: 版本记录 — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: "版本发布记录：每个版本号即其发布日期（YYYY.MM.DD），列出该版的数据变更、归档文件与 Zenodo DOI，可按 Atom 源订阅更新。｜本站《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》（2026.10.30 最终版），全站收录 13 科、18 亚科、326 属、3021 种、68 亚种的现生类群。"
lang: zh-CN
author: 班奈特格林
date: 2026-10-29
version: 2026.10.30
permalink: /changelog/
---
{%- assign CH = site.data.changelog -%}
<h1>版本记录 <span class="page-title-alt" lang="en">Changelog</span></h1>
<p class="cl-lead">版本号即名录发布日期（YYYY.MM.DD）。每次归档的变更都在这里。订阅更新：<a href="{{ site.base_url }}/changelog.atom">changelog.atom（Atom）</a> · 仓库内原文：<code>dataset/CHANGELOG.md</code> · 数据集 DOI：<a href="https://doi.org/{{ site.dataset.doi }}">{{ site.dataset.doi }}</a>。</p>
{%- for v in CH.versions %}
<section class="cl-version" id="v{{ v.version | replace: '.', '-' }}">
<h2 class="cl-title"><span class="cl-ver">{{ v.version }}</span> <span class="cl-name">{{ v.title }}</span></h2>
<ul class="cl-items">
{%- for it in v.items %}
<li class="cl-item{% if it.depth == 1 %} cl-sub{% endif %}">{{ it.html }}</li>
{%- endfor %}
</ul>
</section>
{%- endfor %}
<p class="cl-note">本页由 <code>_tools/build_changelog.py</code> 从 <code>dataset/CHANGELOG.md</code> 生成；权威来源是仓库里的 CHANGELOG 与数据集归档包。变更条目不构成任何命名行为（no nomenclatural act）。</p>
