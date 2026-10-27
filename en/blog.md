---
layout: default
title: Blog — Extant Isoptera (Termites) Latin–Chinese Name Comparison List
description: "Author's articles and update notes: checklist updates, classification notes and reference guides, newest first."
lang: en
author: 班奈特格林 (Bennet Green)
permalink: /en/blog/
---

# Blog

<p>Author's articles and update notes, newest first.</p>

{% if site.posts.size > 0 %}
<p><strong>{{ site.posts.size }}</strong> post(s):</p>
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
<p>No posts yet. They appear automatically once placed in <code>_posts/</code>.</p>
{% endif %}
