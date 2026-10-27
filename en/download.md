---
layout: default
title: Download — Extant Isoptera (Termites) Latin–Chinese Name Comparison List
title_alt: 下载 — 现存等翅下目（白蚁）拉丁学名—中文正名对照名录
description: "Download area: files provided by the site, auto-listed from the repository downloads/ folder."
lang: en
author: 班奈特格林 (Bennet Green)
permalink: /en/download/
---

# Download

<p>This page automatically lists every file in the <code>downloads/</code> folder for direct download. Whatever the site owner places into the repository's <code>downloads/</code> folder will appear here automatically — no page edits needed.</p>

{% assign downloads = site.static_files | where_exp: "f", "f.path contains '/downloads/'" %}
{% assign downloads = downloads | sort: "name" %}

{% if downloads.size > 0 %}
<p><strong>{{ downloads.size }}</strong> file(s) available:</p>
<table class="stats-table">
<thead><tr><th>File</th><th>Format</th></tr></thead>
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
<p>No files in the download area yet. The site owner can drop files into the <code>downloads/</code> folder and download links will appear here automatically.</p>
{% endif %}
