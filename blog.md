---
layout: default
title: 博客（推文） — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: "作者的文章与更新说明。Word 文档（docx）自动转换为网页文章，放入 _posts 文件夹即自动按日期倒序列出（与下载区 downloads 同理）。"
lang: zh-CN
author: 班奈特格林
permalink: /blog/
---

<link rel="stylesheet" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/assets/custom.css">
<a class="lang-switch" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/en/blog/">English</a>
<link rel="alternate" hreflang="zh-CN" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/blog/">
<link rel="alternate" hreflang="en" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/en/blog/">
<link rel="alternate" hreflang="x-default" href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/blog/">

<nav class="site-nav" aria-label="主导航">
  <span class="brand">现存等翅下目（白蚁）拉丁学名—中文正名对照名录</span>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/">首页</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/list/">名录</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/about/">简介</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/stats/">统计</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/download/">下载</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/blog/" aria-current="page">博客</a>
  <a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/guestbook/">留言</a>
</nav>

# 博客（推文）

<p>这里列出作者的文章与更新说明。把 Word 文档（<code>.docx</code>）或纯文本（<code>.txt</code> / <code>.md</code>）放进仓库的 <code>_inbox/</code> 文件夹，推送后由 GitHub Actions 自动转成网页文章并发布，本页按日期倒序自动列出——和下载区自动列出 <code>downloads/</code> 文件夹里的文件是同一个道理。</p>

{% if site.posts.size > 0 %}
<p>当前共 <strong>{{ site.posts.size }}</strong> 篇：</p>
<ul class="post-list">
{% for post in site.posts %}
  <li>
    <h2><a href="https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md{{ post.url }}">{{ post.title }}</a></h2>
    <p class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</p>
    {% if post.excerpt != empty %}<p class="post-excerpt">{{ post.excerpt }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
{% else %}
<p>还没有文章。放进 <code>_posts/</code> 后会自动出现。</p>
{% endif %}
