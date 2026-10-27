---
layout: default
title: Blog — isópteros (termitas) actuales: artículos y notas
description: "Artículos y notas de actualización del autor, ordenados del más reciente al más antiguo."
lang: es
author: 班奈特格林 (Bennet Green)
permalink: /es/blog/
---

# Blog

<p>Artículos y notas de actualización del autor, ordenados del más reciente al más antiguo.</p>

{% if site.posts.size > 0 %}
<p><strong>{{ site.posts.size }}</strong> entrada(s):</p>
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
<p>Aún no hay entradas. Aparecerán automáticamente cuando se publiquen.</p>
{% endif %}
