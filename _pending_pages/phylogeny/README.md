# 系统发育树页面（暂缓发布）

2026-11-02 起，`/phylogeny/`（三语）页面暂缓发布，等待新的系统发育论文发表后再更新。本目录保留三个 Jekyll 页面源码：

- `phylogeny.md`（中文，permalink `/phylogeny/`）
- `en/phylogeny.md`（英文，`/en/phylogeny/`）
- `es/phylogeny.md`（西语，`/es/phylogeny/`）

页面依赖以下文件（仍在主仓库中，保留未动）：

- `_data/phylogeny.json`：拓扑 + 名称 + 支持值 + 中英备注 + Song 2026 对照（v2.0）
- `_includes/phylogeny.html`：页面主体模板
- `assets/phylogeny.js`、`assets/phylogeny.css`：渲染与样式
- `_data/i18n.yml` 的 `phylogeny:` 段（三语 57 个键）
- `_layouts/default.html` head 里的 `page.phylogeny` 条件样式（保留即可）

## 为什么放进下划线目录 `_pending_pages/`

Jekyll 会忽略下划线开头的目录；`.github/workflows/build_sitemap_txt.py` 在遍历页面时同样跳过下划线路径。因此这些页面不会进入 `_site/`、不会出现在 `sitemap.txt`、也不会被 Pagefind 收录；同时源码仍由 git 正常跟踪，方便以后恢复。注意 `_unpublished/` 是给「不部署、不进仓库」的第三方素材用的（见 .gitignore），不要放这里。

## 恢复步骤

1. 把本目录三个页面移回原位：`phylogeny.md` → 仓库根目录；`en/phylogeny.md` → `en/`；`es/phylogeny.md` → `es/`。
2. 在 `_layouts/default.html` 导航里加回一行（papers 之后）：

   ```
   <a href="{{ site.base_url }}{{ LANGP }}/phylogeny/" class="nav-link{% if page.url contains '/phylogeny' %} active{% endif %}">{{ T.nav_phylogeny }}</a>
   ```

3. 运行 `python .github/workflows/build_sitemap_txt.py` 重新生成 `sitemap.txt`。
4. README 页面表、`llms.txt` 里加回入口（可参考 git 历史）。
5. 若换了新论文：主要改 `_data/phylogeny.json`（拓扑、名称、`note`/`note_en`、`support`/`supportText`、`song` 对照字段），页面代码不需要动。
