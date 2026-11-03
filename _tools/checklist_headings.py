#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""list.md 标题的解析约定（多个脚本共用，改这一份即可全员同步）。

名录用 <hN id="anchor">中文名 LATIN</hN> 表达分类阶元：
  h2 支系 / h3 科 / h4 亚科 / h5 属 —— 标题必须是「中文名 + 拉丁名」。
页面里还有若干**非分类学**标题（导航栏、目录、参考文献），它们只有中文、
没有拉丁名，任何按「中文名 LATIN」解析的地方都必须先把这些锚点跳过，
否则会以「无法拆分标题 / 无法拆分名录标题」直接失败。

新增这类标题（例如再加一个「按亚科浏览」）时，只需把它的 id 加进
NON_TAXON_IDS；本仓库里所有解析 list.md 标题的脚本都从这里取名单：

  _tools/build_taxonomy_data.py            （分类树 / data/*.json / 三语 stats.md）
  .github/workflows/build_search_index.py  （search-index.json）

不要在各脚本里另抄一份名单。
"""

from __future__ import annotations

# 名录正文中的非分类学标题锚点（按页面出现顺序，便于阅读）
NON_TAXON_IDS = frozenset({
    "by-family",      # 「按科浏览（13 科）」导航段
    "toc",            # 「目录」
    "references",     # 「参考文献」
    "references-doi", # 「参考文献（DOI 索引）」等既有别名
})

# 旧名兼容：脚本里的常量一直叫 SKIP_IDS，含义即「解析标题时要跳过的锚点」
SKIP_IDS = NON_TAXON_IDS


def is_non_taxon(anchor: str) -> bool:
    """该标题锚点是否属于非分类学标题（导航 / 目录 / 参考文献）。"""
    return anchor in NON_TAXON_IDS
