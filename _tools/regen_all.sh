#!/usr/bin/env bash
# 重新生成全部派生产物（离线；不访问任何外部 API，权威库缓存已提交在仓库里）。
#
# 顺序与 .github/workflows/pages.yml（部署）、.github/workflows/validate.yml（PR 闸门）
# 保持一致：数据文件 → 索引页 → 分类数据 → 页脚正文 → 图片页 → 层级页 → sitemap
# → 检索索引 → 归档数据集 → 版本记录 → 命名差异看板。
#
# 两个调用方：
#   1. 本地提交前收尾：改了 _species / _data / dataset/CHANGELOG.md 等源文件后跑一次，
#      再把改动一起提交（否则 CI 的「生成产物过期」检查会红）。
#   2. validate.yml 的 main 自愈步骤：重跑本脚本后若有差异，自动提交并推送。
#
# 幂等：连续跑两次，第二次不应产生任何字节变化。
set -euo pipefail

cd "$(dirname "$0")/.."

python _tools/extract_taxon_data.py --check
python _tools/build_list_index.py
python _tools/build_taxonomy_data.py --write
python .github/workflows/build_genus_index.py
python .github/workflows/build_species_body.py --write
python .github/workflows/build_photo_pages.py
python .github/workflows/build_taxonomy_pages.py
python .github/workflows/build_sitemap_txt.py
python .github/workflows/build_search_index.py --write --no-enrich
python .github/workflows/build_dataset.py --write
python _tools/build_changelog.py --write
python .github/workflows/build_name_issues.py --write

# 三语分页（zh / en / es）自检：漏页、混语残留、站内链接缺语言前缀
python _tools/check_lang_pages.py --ci

echo "OK: 派生产物已全部重建"
