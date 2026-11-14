# 生物学篇（已从站点移除）

2026-11-15 起，`/basics/biology/`（三语）从站点移除。本目录保留三个 Jekyll 页面源码：

- `biology.md`（中文，permalink `/basics/biology/`）
- `en/biology.md`（英文，`/en/basics/biology/`）
- `es/biology.md`（西语，`/es/basics/biology/`）

## 为什么放进下划线目录 `_pending_pages/`

Jekyll 会忽略下划线开头的目录；`.github/workflows/build_sitemap_txt.py` 在遍历页面时同样跳过下划线路径。因此这些页面不会进入 `_site/`、不会出现在 `sitemap.txt`、也不会被 Pagefind 收录；同时源码仍由 git 正常跟踪，方便以后恢复。注意 `_unpublished/` 是给「不部署、不进仓库」的第三方素材用的（见 `.gitignore`），不要放这里。

## 同一轮改动（页面之外）

移除时顺带把站内所有指向生物学篇的入口删掉，恢复时要一并加回：

1. `basics/index.md`、`en/basics/index.md`、`es/basics/index.md`：入口页重写为只列形态篇一篇；恢复时在「正文 / The page / La página」列表里加回生物学篇的 `<li>`，标题改回「— 形态与生物学」，并恢复 front matter 的 `description`、`keywords` 与「两篇」措辞。
2. `basics/morphology.md:15`（返回索引行）与 `:331`（页脚）、`en/basics/morphology.md:326`、`es/basics/morphology.md:326`：删去「生物学部分……见生物学篇」的句子；恢复时加回。
3. `index.md`、`en/index.md`、`es/index.md` 的「基础知识 / Basics / Fundamentos」卡片：删去 biology 子句；恢复时加回。
4. `README.md` 页面表与 `dataset/CHANGELOG.md`：按新状态改写，恢复时同步改回。

具体原文都可以从 git 历史取（移除这次提交之前的版本）。

## 恢复步骤

1. 把本目录三个页面移回原位：`biology.md` → `basics/`；`en/biology.md` → `en/basics/`；`es/biology.md` → `es/basics/`。
2. 按上一节把入口与链接加回（或用 `git checkout <移除前提交> -- basics/index.md en/basics/index.md es/basics/index.md basics/morphology.md en/basics/morphology.md es/basics/morphology.md`）。
3. 运行 `python .github/workflows/build_sitemap_txt.py` 重新生成 `sitemap.txt`。
4. 运行 `python _tools/build_changelog.py` 与 `python _tools/check_site.py --ci`、`python _tools/check_liquid.py`。
