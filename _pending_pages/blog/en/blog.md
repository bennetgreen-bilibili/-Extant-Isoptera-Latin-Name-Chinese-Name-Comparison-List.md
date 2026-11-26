---
layout: default
title: Blog
description: "Author's blog: the checklist's release notes, notes on taxonomic coverage by family and subfamily, and literature guides, newest first, with an Atom feed."
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
    <h2><a href="https://termite-extant-isoptera.org{{ post.url }}">{{ post.title }}</a></h2>
    <p class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</p>
    {% if post.excerpt != empty %}<p class="post-excerpt">{{ post.excerpt }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
{% else %}
<p>No posts yet. They appear automatically once placed in <code>_posts/</code>.</p>
{% endif %}
