# 仓库文档索引

> 从 `SITE-INDEX.md` 拆出：只在**要查某份说明文档讲什么**时读这一页（约 3 KB）。
> 仓库内所有非页面说明文档的清单与用途；教程类长文不要通读，按标题挑。

| 文档 | 讲什么 |
| --- | --- |
| `AGENTS.md` | 硬约定：来源存档、存档格式、红线（编造 / 摘录不逐字 / 全文进仓库） |
| `CONTRIBUTING.md` | 数据流、三语同步、生成顺序、发布构建、提交前校验 |
| `README.md` | 站点功能长文：每个页面、检索、外部库、JSON-LD、数据集、部署细节 |
| `llms.txt` | 面向外部 AI 的站点说明（页面对照、数据入口、引用格式） |
| `SITE-INDEX.md` | 索引入口：页面 → 源文件、目录地图、连带关系、搜索纪律 |
| `_meta/DATA-MAP.md` | `_data/` 逐文件角色（源 / 派生 / 缓存）、分片布局与定位方法 |
| `_meta/LAYOUT.md` | 目录地图与「页面 → 源文件 / 生成脚本」对照 |
| `_meta/PIPELINE.md` | 生成链 16 步、手动脚本、校验命令、本地构建 |
| `_tools/data_shards.md` | `_data` 一阶元一档分片布局、读取方式对照、改分片数据怎么定位 |
| `_tools/数据集DOI与归档发布指南.md` | 数据集 DOI、Zenodo / GBIF / ScienceDB 路线 |
| `_tools/Zenodo发布逐步操作手册.md` | 照抄式发布操作单（字段值、命令、验收） |
| `_tools/Zenodo新版描述-2026.10.30.md` | 当前版本的 Zenodo 描述文案 |
| `_tools/分布图与瓦片使用政策.md` | 分布图流水线、1° 网格聚合、化石过滤、瓦片政策 |
| `_tools/外部权威库与一致性核对.md` | GBIF / CoL / Wikidata / BSF 外链与判定规则 |
| `_tools/文献检索器说明.md` | `/papers/` 的数据来源、查询与导出 |
| `_tools/原文归档工作流说明.md` | 合法 OA 全文下载进文库的流程 |
| `_tools/参考文献与DOI补全说明.md` | 77 条参考文献的 Crossref / 格式增强 |
| `_tools/图片授权与署名说明.md` | 图片图集的许可策略与署名规则 |
| `_tools/图片版权核查与处理清单.md` | `assets/images/` 插图的逐张核查结果 |
| `_tools/开源功能与工作流扩展建议.md` | 可加功能清单（读者收益 × 可维护性 × 工作量） |
| `_tools/物种介绍选题清单.md` | 按真实搜索需求排的选题清单 |
| `_tools/新文章模板.md` | 博客文章 front matter 模板 |
| `_tools/manual_fulltext.md` | 待人工获取全文清单（自动生成，勿手改） |
| `_reports/library-reading/SOP.md` | 文库阅读与摘录的工作流 |
| `_reports/library-reading/taxonomy-crosswalk.md` | 分类变更对照表（可读版） |
| `_reports/library-reading/book-outlines/README.md` | 各书的章节大纲 |
| `_reports/library-reading/facts/README.md` | 已抽取的事实条目 |
| `_reports/genus-morphology-gaps.md` | 属级形态描述缺口（哪些属还没有描述） |
| `_reports/genus-morphology-worklist.md` | 属级形态补写清单 |
| `_reports/genus-missing-literature.md` | 待补文献线索 |
| `_reports/genus-literature-candidates.md` | 属级文献候选汇总 |
| `_reports/species-morphology-coverage.md` | 种级形态描述覆盖率 |
| `_reports/species-morphology-worklist.md` | 物种形态补写清单（配套同名 `.csv`） |
| `_reports/species-morphology-no-source.md` | 文库中对不上号的待补种 |
| `_reports/species-morphology-bd-review.md` | B/C 类种级形态复核方法与结果 |
| `_reports/species-morphology-bd-disposition.csv` | B/C 类逐种处置表 |
| `_reports/species-morphology-dispatch.md` | 剩余 2177 种 + 46 属的补全派单（批次、渠道、工时） |
| `_reports/species-morphology-dispatch.csv` | 派单逐条明细（每种的 BSF 入口、目标文献、获取渠道） |
| `_reports/域名迁移可行性评估-2026-11-12.md` | 换域名的判断依据 |
| `_reports/域名迁移操作手册-2026-11-12.md` | 域名迁移步骤 |
| `_reports/域名迁移验收-2026-11-14.md` | 301 现状与收尾 |

新增 `_tools/*.md` 或 `_reports/**/*.md` 要登记进本表（`python _tools/build_ai_index.py --check` 按文件名核对）。
