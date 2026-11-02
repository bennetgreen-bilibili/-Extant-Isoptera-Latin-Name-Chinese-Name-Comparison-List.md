---
layout: default
title: 博客（推文） — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: "作者班奈特格林的博客：名录版本更新说明、各科与亚科的收录范围讨论、参考文献导读，按发布时间倒序排列，可按 Atom 源订阅，可当作使用名录的入门读物。｜本站《现存等翅下目（白蚁）拉丁学名—中文正名对照名录》（2026.10.30 最终版），全站收录 13 科、18 亚科、326 属、3021 种、68 亚种的现生类群。"
lang: zh-CN
author: 班奈特格林
permalink: /blog/
---

# 博客（推文）

<p>这里列出作者的文章与更新说明，按日期倒序排列。</p>

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
