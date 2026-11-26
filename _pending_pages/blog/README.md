# 博客页面（已从站点移除）

2026-11-26 起，博客页面（`/blog/` 及英、西语版）与 `_posts/` 下的文章从站点撤下并封存：博客没有需要长期展示的内容。本目录保留全部页面源码：

- `blog.md`（中文，permalink `/blog/`）
- `en/blog.md`（英文，`/en/blog/`）
- `es/blog.md`（西语，`/es/blog/`）
- `posts/2026-10-22-welcome.md`（唯一一篇文章，原路径 `_posts/2026-10-22-welcome.md`，permalink `/blog/2026/10/22/welcome/`）

页面依赖以下文件（仍在主仓库中，保留未动）：

- `_layouts/post.html`：文章布局（含 BlogPosting JSON-LD 与「返回博客列表」链接）
- `_layouts/default.html`：文章页三语切换特例（`url_en = '/en/blog/'`、`url_es = '/es/blog/'`）
- `_config.yml` 的 `_posts` defaults（layout `post`、lang `zh-CN`、permalink `/blog/:year/:month/:day/:slug/`）
- `feed.xml`、`feed.json`：订阅源文件本身保留（`check_site.py` 要求存在）；无文章时输出空条目
- `_data/i18n.yml` 的 `nav_blog` 三语键
- `_tools/新文章模板.md`、`_drafts/README.md`：写新文章的模板与说明

## 为什么放进下划线目录 `_pending_pages/`

Jekyll 会忽略下划线开头的目录；`.github/workflows/build_sitemap_txt.py` 在遍历页面时同样跳过下划线路径。因此这些页面不会进入 `_site/`、不会出现在 `sitemap.txt`、也不会被 Pagefind 收录；同时源码仍由 git 正常跟踪，方便以后恢复。注意 `_unpublished/` 是给「不部署、不进仓库」的第三方素材用的（见 .gitignore），不要放这里。

`_posts/` 目录本身保留（加一份无扩展名的 `README` 说明，刻意不叫 `README.md`：`build_sitemap_txt.py` 遍历 `_posts/*.md` 时对不符合日期规则的文件名直接报错退出），因为 `_tools/make_lang_sources.py` 会把不存在的 `_posts` 记为缺失项，`_tools/merge_lang_sites.py` 也要读它来算共享产物。

## 恢复步骤

1. 把页面移回原位：`blog.md` → 仓库根目录；`en/blog.md` → `en/`；`es/blog.md` → `es/`；`posts/2026-10-22-welcome.md` → `_posts/`。
2. 在 `_layouts/default.html` 导航里加回一行（`/download/` 之后、`/guestbook/` 之前）：

   ```
   <a href="{{ site.base_url }}{{ LANGP }}/blog/" class="nav-link{% if page.url contains '/blog' %} active{% endif %}">{{ T.nav_blog }}</a>
   ```

3. 运行 `python .github/workflows/build_sitemap_txt.py` 重新生成 `sitemap.txt`。
4. 加回入口：`index.md` / `en/index.md` / `es/index.md` 的博客卡片、`llms.txt`、`README.md` 与 `_meta/LAYOUT.md` 的页面表。
5. 加回文案里的博客字样：`_data/i18n.yml` 三条 `search_overlay_placeholder`、`_data/list_index_blocks.json` 三条检索提示（改完跑 `python _tools/build_list_index.py`，或整链 `bash _tools/regen_all.sh`）、`search.md` / `en/search.md` / `es/search.md` 的正文与 `description`。
6. 需要订阅源在页面头部自动发现时，在 `_layouts/default.html` head 里加回：

   ```
   <link rel="alternate" type="application/atom+xml" title="{{ site.title_zh }}" href="{{ site.base_url }}/feed.xml">
   <link rel="alternate" type="application/feed+json" title="{{ site.title_zh }}" href="{{ site.base_url }}/feed.json">
   ```

## 同一轮改动（页面之外）

- `_layouts/default.html`：删博客导航行、删 head 的两个订阅源 `<link>`（feed 文件保留）
- `index.md`、`en/index.md`、`es/index.md`：删博客卡片，全文搜索卡片描述去掉「与博客」「blog posts」「blog」字样
- `llms.txt`：全文搜索那一行去掉博客
- `_data/i18n.yml`：三条 `search_overlay_placeholder` 去掉博客字样（`nav_blog` 键保留）
- `_data/list_index_blocks.json`：三条检索提示去掉博客，重新生成 `list.md` 三语页
- `search.md`、`en/search.md`、`es/search.md`：正文与 `description` 去掉博客
- `feed.xml`：`<link rel="alternate" type="text/html">` 由 `/blog/` 改指 `/changelog/`
- `assets/search-page.js`：三处 `placeholder`（全站搜索页输入框）去掉博客
- `_posts/README`（新增，无扩展名）：说明 `_posts/` 为什么留空目录、为什么不放 `README.md`
- `README.md`、`_meta/LAYOUT.md`、`_meta/DOCS.md`、`CONTRIBUTING.md`、`_drafts/README.md`：注明博客已封存
