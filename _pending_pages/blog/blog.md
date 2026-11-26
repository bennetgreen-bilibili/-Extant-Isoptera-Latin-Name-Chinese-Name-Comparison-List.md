---
layout: default
title: 博客：版本更新与文献导读
description: "作者班奈特格林的博客：名录版本更新说明、各科与亚科的收录范围讨论、参考文献导读，按发布时间倒序排列，可按 Atom 源订阅，也可当作使用名录与核对学名的入门读物，从最早一篇读起能了解分类口径的来龙去脉。｜白蚁名录：现生等翅下目 13 科、326 属、3021 种、68 亚种。"
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
    <h2><a href="https://termite-extant-isoptera.org{{ post.url }}">{{ post.title }}</a></h2>
    <p class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</p>
    {% if post.excerpt != empty %}<p class="post-excerpt">{{ post.excerpt }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
{% else %}
<p>还没有文章。放进 <code>_posts/</code> 后会自动出现。</p>
{% endif %}
