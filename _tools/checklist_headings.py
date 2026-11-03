#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""名录页里「非分类学标题」的锚点名单。

历史：`/list/` 曾是全量名录，标题按 `<hN id="anchor">中文名 LATIN</hN>` 表达分类阶元
（h2 支系 / h3 科 / h4 亚科 / h5 属），页内另有导航栏、目录、参考文献这类只有中文的
标题；凡按「中文名 LATIN」解析标题的脚本都必须先跳过它们。

名录改版为索引页之后，层级与顺序一律取 `_data/taxonomy.json`，
`build_taxonomy_data.py` 与 `build_search_index.py` 都已不再解析标题；只剩迁移脚本
`_tools/extract_taxon_data.py` 还在用这份名单（抽取旧名录时跳过导航类锚点，
免得把「目录」「参考文献」当成科/亚科正文）。

新建索引页类标题时把 id 加进 NON_TAXON_IDS 即可；不要在脚本里另抄一份名单。
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
