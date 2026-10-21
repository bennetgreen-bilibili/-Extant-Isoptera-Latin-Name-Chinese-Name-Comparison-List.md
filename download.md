---
layout: default
title: 下载 — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: "下载区：本站提供的资料文件，随仓库 downloads/ 文件夹自动更新。"
lang: zh-CN
author: 班奈特格林
permalink: /download/
---

<link rel="stylesheet" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/assets/custom.css">
<a class="lang-switch" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/en/download/">English</a>
<link rel="alternate" hreflang="zh-CN" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/download/">
<link rel="alternate" hreflang="en" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/en/download/">
<link rel="alternate" hreflang="x-default" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/download/">

<nav class="site-nav" aria-label="主导航">
  <span class="brand">现存等翅下目（白蚁）拉丁学名—中文正名对照名录</span>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/">首页</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/list/">名录</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/about/">简介</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/stats/">统计</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/download/">下载</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/guestbook/">留言</a>
</nav>

# 下载

<p>本页自动列出 <code>downloads/</code> 文件夹里的全部文件，供直接下载。站长在 GitHub 仓库的 <code>downloads/</code> 文件夹里放入什么文件，这里就会自动显示并更新，无需改动本页。</p>

{% assign downloads = site.static_files | where_exp: "f", "f.path contains '/downloads/'" %}
{% assign downloads = downloads | sort: "name" %}

{% if downloads.size > 0 %}
<p>当前共 <strong>{{ downloads.size }}</strong> 个文件：</p>
<table class="stats-table">
<thead><tr><th>文件</th><th>格式</th></tr></thead>
<tbody>
{% for f in downloads %}
  <tr>
    <td><a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md{{ f.path }}" download>{{ f.name }}</a></td>
    <td class="num">{{ f.extname | remove_first: '.' | upcase }}</td>
  </tr>
{% endfor %}
</tbody>
</table>
{% else %}
<p>下载区暂时还没有文件。站长向 <code>downloads/</code> 文件夹放入文件后，这里会自动出现下载链接。</p>
{% endif %}
