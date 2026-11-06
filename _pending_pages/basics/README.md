# 基础知识页面（暂缓发布）

2026-11-05 起，`/basics/` 索引页、形态篇与生物学篇（中／英／西三语，共九页）暂缓发布，等审稿完成后恢复。本目录保留全部页面源码与 front matter（permalink 不变）：

- `index.md`（中文，`/basics/`）、`morphology.md`（`/basics/morphology/`）、`biology.md`（`/basics/biology/`）
- `en/index.md`、`en/morphology.md`、`en/biology.md`（`/en/basics/…`）
- `es/index.md`、`es/morphology.md`、`es/biology.md`（`/es/basics/…`）

页面依赖、仍在主仓库中且未改动：

- `_data/i18n.yml` 的 `nav_basics`（zh 基础知识 / en Basics / es Fundamentos）
- 页面之间的互链、锚点（`#caste`、`#soldier`、`#internal`、`#revisions`、`#refs`）与三语语言切换逻辑
- 三个首页与主导航里各留了一条说明性 HTML 注释（不含链接，故不会产生死链）；恢复时按下面的片段粘回

已同时移除入口的位置（恢复时需补回）：

- `_layouts/default.html` 主导航的「基础知识」链接
- `index.md`、`en/index.md`、`es/index.md`「页面导航」里各一条入口
- `llms.txt` 三语各一条「白蚁基础知识（形态学）」条目

## 为什么放进下划线目录 `_pending_pages/`

Jekyll 会忽略下划线开头的目录；`.github/workflows/build_sitemap_txt.py` 遍历页面时同样跳过任何以 `_` 开头的路径段。因此这些页面不会进入 `_site/`、不会出现在 `sitemap.txt`、也不会被 Pagefind 收录；源码仍由 git 正常跟踪，方便恢复。`_unpublished/` 是给「不部署、不进仓库」的第三方素材用的（见 `.gitignore`），不要放这里。

## 恢复步骤

1. 移回原位：`index.md`、`morphology.md`、`biology.md` → 仓库根目录的 `basics/`；`en/` 下三页 → `en/basics/`；`es/` 下三页 → `es/basics/`。
2. 在 `_layouts/default.html` 主导航里（`/list/` 那行之后、`/search/` 那行之前）粘回：

   ```html
   <a href="{{ site.base_url }}{{ LANGP }}/basics/" class="nav-link{% if page.url contains '/basics' %} active{% endif %}">{{ T.nav_basics }}</a>
   ```

3. 三个首页「页面导航」里，在 guestbook 条目之后各粘回一条：

   ```html
   <li><a href="{{ site.base_url }}/basics/"><strong>基础知识</strong></a> — 索引：形态篇（头壳、囟、上颚、翅、跗节、腹板、尾须与内部器官的术语与识别要点，附检索表常用特征速查，供阅读少数保留的检索表）与生物学篇（品级发育、筑巢、食性、生活史、防御与生态功能），术语口径与名录及各科属页的形态描述一致。</li>
   ```

   ```html
   <li><a href="{{ site.base_url }}/en/basics/"><strong>Basics</strong></a> — index: morphology (head capsule, fontanelle, mandibles, wings, tarsi, abdominal plates and internal organs, with Latin/English names, caste notes and a quick guide to the features used in descriptions and the remaining keys) and biology (caste development, nesting, feeding, life history, defence and ecosystem roles).</li>
   ```

   ```html
   <li><a href="{{ site.base_url }}/es/basics/"><strong>Fundamentos</strong></a> — índice: morfología (cápsula cefálica, fontanela, mandíbulas, alas, tarzos, placas abdominales y órganos internos, con nombres latinos y una guía rápida para los rasgos usados en las descripciones y en las claves conservadas) y biología (castas, nidificación, alimentación, ciclo vital, defensa y funciones ecológicas).</li>
   ```

4. `llms.txt` 里按语序补回三条「白蚁基础知识（形态学）」条目（中文 / English / Español），可从 git 历史取回原文。
5. 运行 `python .github/workflows/build_sitemap_txt.py` 重新生成 `sitemap.txt`，再跑 `python _tools/check_liquid.py` 与 `python _tools/check_site.py`。

注意：`sitemap.txt` 已在暂缓发布时重新生成（不含这九页）；恢复后必须再生成一次，否则 `--check` 会报不一致。
