---
layout: default
title: 下载：名录 CSV、JSON 与文献清单
description: "下载区：名录 CSV、JSON 结构化数据、参考文献清单与 Darwin Core 归档等文件，由仓库 downloads/ 目录自动列出，可见文件大小与更新时间，便于离线检索、教学演示与二次分析；文件随名录版本同步更新。｜白蚁名录：现生等翅下目 13 科、326 属、3021 种、68 亚种。"
lang: zh-CN
author: 班奈特格林
permalink: /download/
---

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
    <td><a href="https://termite-extant-isoptera.org{{ f.path }}" download>{{ f.name }}</a></td>
    <td class="num">{{ f.extname | remove_first: '.' | upcase }}</td>
  </tr>
{% endfor %}
</tbody>
</table>
{% else %}
<p>下载区暂时还没有文件。站长向 <code>downloads/</code> 文件夹放入文件后，这里会自动出现下载链接。</p>
{% endif %}
