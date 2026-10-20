# 站点 AI/爬虫友好化改造包

将本目录内全部文件放入 GitHub Pages 仓库根目录（与原有 `_config.yml` 同级）即可。
`index.md` 已替换为优化版本；`isoptera-data.json`、`llms.txt`、`robots.txt`、`sitemap.xml` 为新增文件。

## 域名配置（已完成）
全部文件（含 `index.md` / `llms.txt` / `robots.txt` / `sitemap.xml`）中的站点地址
已配置为 `https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/`。
配套文件请放入该仓库根目录，即可在主页同路径下访问（如 `.../robots.txt`、`.../sitemap.xml`）。

## 文件说明
| 文件 | 作用 |
|---|---|
| `index.md` | 优化后的主页：完整 front matter（title/description/lang/author/date/keywords，GitHub Pages 的 jekyll-seo-tag 会自动生成 `<head>` meta 与 OG 标签）、JSON-LD Dataset 结构化数据、可点击目录锚点、科/亚科/属级稳定锚点、参考文献 DOI 链接、引用格式说明 |
| `isoptera-data.json` | 机器可读结构化数据（JSON-LD Dataset）：科—亚科—属—种 全层级，含中文/拉丁名、模式种、分布、亚种；由 `index.md` 程序化提取，数量已与正文核对一致（13 科 / 323 属 / 3008 种 / 63 亚种） |
| `llms.txt` | llmstxt.org 规范的站点说明文件，供 GPT/Claude/Perplexity 等 AI 助手直接读取站点概览与关键资源 |
| `robots.txt` | 允许主流搜索引擎与 AI 爬虫（GPTBot、ClaudeBot、PerplexityBot、Google-Extended、CCBot 等）抓取 |
| `sitemap.xml` | 站点地图，帮助搜索引擎收录 |
| `build_optimized.py` | 本改造的构建脚本，可复现/重新生成全部产物 |

## 推荐后续动作（可选）
1. **自定义域名**：如需绑定自定义域名，在 GitHub Pages 设置中配置后，将本文档内地址一并更新。
2. **站点地图插件**：在 `_config.yml` 添加 `plugins: [jekyll-sitemap]`（GitHub Pages 已内置支持），自动维护 sitemap。
3. **验证**：上线后用 Google Search Console 提交 sitemap；用 Bing Webmaster 提交；AI 爬虫可用
   `https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/robots.txt` 自行验证允许规则。
4. **结构数据测试**：用 Google Rich Results Test 或 schema.org validator 校验 JSON-LD。
