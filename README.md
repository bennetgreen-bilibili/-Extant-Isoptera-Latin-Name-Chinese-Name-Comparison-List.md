# 现存等翅下目（白蚁）拉丁学名—中文正名对照名录（站点）

多页结构化的 GitHub Pages 站点。将本目录内全部文件放入仓库根目录即可。

## 页面
| 文件 | 页面 |
|---|---|
| `index.md` | 首页：搜索框（中文/拉丁名检索）+ 三页导航 + JSON-LD |
| `list.md` | 名录：完整对照表（支系—科—亚科—属—种），属级嵌套目录，可靠锚点 |
| `about.md` | 简介：作者、版本、收录范围、引用格式 |
| `stats.md` | 统计：科/亚科/属级物种数统计表 |

## 结构化数据（按类群拆分）
- 入口：`data/index.json`（分类树 + 全部文件清单）
- `data/mastotermitidae.json`、`data/teletisoptera.json`、`data/kalotermitidae.json`、`data/neoisoptera-excl-termitidae.json`
- `data/termitidae/*.json`（白蚁科 18 亚科，逐亚科文件）
- `search-index.json`（检索索引，供首页搜索框）

## 其它
- `_config.yml`：启用 jekyll-seo-tag 与 jekyll-sitemap
- `robots.txt`：允许主流搜索引擎与 AI 爬虫抓取
- `sitemap.xml`：站点地图（jekyll-sitemap 构建时会自动覆盖为含全部页面）
- `llms.txt`：llmstxt.org 规范的站点说明
- `assets/search.js`、`assets/custom.css`：搜索框脚本与样式
