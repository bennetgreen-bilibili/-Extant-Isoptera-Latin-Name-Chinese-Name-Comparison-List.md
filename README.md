# 现存等翅下目（白蚁）拉丁学名—中文正名对照名录（站点）

多页结构化的 GitHub Pages 站点。将本目录内全部文件放入仓库根目录即可。

## 页面
| 文件 | 页面 |
|---|---|
| `index.md` | 首页：简介（作者/版本/引用格式）+ 页面导航 + JSON-LD |
| `list.md` | 名录：搜索框（中文/拉丁名/次异名检索）+ 完整对照表（支系—科—亚科—属—种），属级嵌套目录，可靠锚点 |
| `stats.md` | 统计：科/亚科/属级物种数统计表 |
| `data.md` | 数据：机器可读结构化数据（JSON）清单，按支系/科/亚科列出全部 22 个文件并逐文件链接 |
| `download.md` | 下载：自动列出 `downloads/` 文件夹内的全部文件，供直接下载 |
| `guestbook.md` | 留言：Giscus 留言板（GitHub 账号登录） |

## 结构化数据（按类群拆分）
- 页面：`data.md`（/data/，列出全部文件及白蚁科 18 亚科的逐文件链接）
- 入口：`data/index.json`（分类树 + 全部文件清单）
- `data/mastotermitidae.json`、`data/teletisoptera.json`、`data/kalotermitidae.json`、`data/neoisoptera-excl-termitidae.json`
- `data/termitidae/*.json`（白蚁科 18 亚科，逐亚科文件）
- `search-index.json`（检索索引，供名录页搜索框）

## 其它
- `_config.yml`：启用 jekyll-seo-tag 与 jekyll-sitemap
- `robots.txt`：允许主流搜索引擎与 AI 爬虫抓取
- `sitemap.xml`：站点地图，由 jekyll-sitemap 插件在构建时自动生成（含全部页面、文章与物种页）
- `llms.txt`：llmstxt.org 规范的站点说明
- `assets/search.js`、`assets/custom.css`：搜索框脚本与样式

## 下载 / 留言
- **下载页**（`download.md` / `en/download.md`）：把要提供下载的文件放进仓库 `downloads/` 文件夹即可，页面用 Jekyll `site.static_files` 自动列出，无需改页面。占位文件 `downloads/.gitkeep` 可删除。
- **留言页**（`guestbook.md` / `en/guestbook.md`）：使用 Giscus（GitHub Discussions 留言）。
  1. 在仓库 Settings → General → Features 勾选 **Discussions** 并保存（仓库需为公开仓库）。
  2. 打开 https://giscus.app/ ，填写仓库 `bennetgreen-bilibili/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md`。
  3. 在 Discussion Category 里选择一个分类（如 General / Announcements）。
  4. 复制生成的 `data-category` 与 `data-category-id`，替换 `guestbook.md` 和 `en/guestbook.md` 中对应的占位值。

## 物种页（每个物种/亚种一个独立页面）
- `_species/*.md`：Jekyll 集合（collection），共 3071 个文件（3008 种 + 63 亚种），每个物种/亚种一页，URL 为 `/species/<slug>/`（slug 为拉丁学名小写、空格转连字符，如 `mastotermes-darwiniensis`）。
- `_layouts/species.html`：物种页模板（面包屑 + 学名/中文正名 + 模式种标记；正文留空待补充）。
- `list.md` / `en/list.md`：名录中每个物种名已链接到对应物种页。
- 在 `_config.yml` 中通过 `collections.species` 注册（`output: true`，`permalink: /species/:name/`）。
- 如需新增/修改物种页内容，直接编辑对应 `_species/<slug>.md` 的正文（front matter 已含学名、中文正名、分类层级与模式种标记）。
