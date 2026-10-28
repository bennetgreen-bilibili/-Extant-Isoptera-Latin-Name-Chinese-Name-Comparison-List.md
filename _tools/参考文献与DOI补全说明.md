# 参考文献与 DOI 补全说明

> 适用对象：本仓库（现存等翅下目白蚁名录站点）。目标：把名录末尾的 **77 条参考文献**从"论文式的一串文字"变成**可复制、可解析、可下载**的书目条目——逐条 DOI、Crossref 记录、GB/T 7714 式 / APA 7 / Vancouver 引用格式，外加 BibTeX / RIS / CSL-JSON，并可选补 BHL 原始描述扫描链接。
>
> 相关文件：`.github/workflows/build_references.py`（唯一生成脚本）、`_data/references.json`（站点数据，已提交）、`data/references.json`（公开下载副本，字节完全相同）、`_includes/references.html`（列表渲染）、`assets/references.css` / `assets/references.js`（样式与交互）、`references.md` / `en/references.md` / `es/references.md`（三语页面）。
>
> 在线页面：`/references/`、`/en/references/`、`/es/references/`。

---

## 0. 一句话结论

77 条中 **46 条原文自带 DOI**，Crossref **全部**能取回书目记录（46/46）；无 DOI 的 31 条里，Crossref 书目检索**自动匹配成功 1 条**（第 37 条 Watson & Perry 1981，相似度 0.90 且年份一致，页面上标「自动匹配待核对」）；最终 **带 DOI 47/77（61%）**，另 **12 条带候选清单**供人工核对；**BHL 0 条**（本机访问 api.biodiversitylibrary.org 时 TLS 握手失败，见 §5）。原文措辞、编号、条数一律不动。

---

## 1. 流水线

    python .github/workflows/build_references.py            # 只统计（会用缓存）
    python .github/workflows/build_references.py --write    # 生成两份 JSON
    python .github/workflows/build_references.py --verify   # 离线自检已提交的 JSON
    python .github/workflows/build_references.py --check    # 校验仓库内 JSON 与生成结果一致
    python .github/workflows/build_references.py --verify   # 离线自检：不联网，只查已提交 JSON 是否自洽
    python .github/workflows/build_references.py --write --bhl        # 额外补 BHL（需 BHL_API_KEY）
    python .github/workflows/build_references.py --write --offline    # 只用缓存，不联网
    python .github/workflows/build_references.py --write --time-budget 120 --limit 10

| 步骤 | 做什么 | 关键约束 |
|---|---|---|
| ① 解析 | 读名录单文件 `*Latin Name * Chinese Name Comparison List.md` 的 `## 参考文献` 区块 | 与 `.github/workflows/build_dataset.py` 的 `load_references()` **逐行等价**：`^\s{0,3}(\d{1,3})\.\s+` 编号行、缩进续行合并、`10\.\d{4,9}/\S+` 取 DOI 并 `rstrip(".,;:")`、SICI 型 DOI（`…2.0.CO` + 换行 `;2`）按原文补全、`\sdoi:\s` 之后从 citation 里切掉。**不改 list.md** |
| ② Crossref 直查 | 有 DOI 的条目请求 `https://api.crossref.org/works/<doi>` | 带 `mailto=` 参数与描述性 User-Agent；404 记为 `crossref_error: "not_found"`，**保留原 DOI**，不补写任何字段 |
| ③ Crossref 检索 | 无 DOI 的条目请求 `/works?query.bibliographic=…&rows=3` | 结果只作候选；命中才算数，规则见 ④ |
| ④ 自动匹配 | 标题**词覆盖/字符相似度 ≥ 0.90** 且**年份一致**才采用 | 采用后 `doi_status = "matched_candidate"`、`doi_note = "自动匹配待核对"`，并在 `meta.notes` 里列出编号；否则 `doi_status` 保持 `none`、`doi` 留空，候选只进 `candidates` |
| ⑤ 格式化 | 由 Crossref 字段拼 GB/T 7714 式、APA 7、Vancouver | Crossref 没有的字段一律留空，**绝不推测**；Crossref 完全没记录时三种格式回退为**原文 citation 逐字** |
| ⑥ 机器格式 | BibTeX、RIS、CSL-JSON | 类型按 Crossref `type` 映射（`journal-article`→`@article`/`article-journal`/`JOUR`，`book-chapter`→`@incollection`/`chapter`/`CHAP`…） |
| ⑦ BHL（可选） | `--bhl` 且有 `BHL_API_KEY` 时按标题检索 BHL | 任何异常都只是 `bhl: null`，**不会让流程失败** |
| ⑧ 输出 | 写 `_data/references.json` 与 `data/references.json` | 两份**字节相同**；`ensure_ascii=False`、`indent=2`、`\n` 换行；内容未变时沿用旧 `meta.generated`，重复运行零 diff |

### 礼貌抓取（公共 API 礼仪）

- User-Agent：`extant-isoptera-checklist-references/1.0 (+<项目 URL>; mailto:<CROSSREF_MAILTO>) Python-urllib`
- 每次请求带 `mailto=<CROSSREF_MAILTO>`（Crossref 的"礼貌池"靠它识别；默认值是仓库 GitHub noreply 地址，**建议维护者改成真实邮箱**：`CROSSREF_MAILTO=you@example.org`）
- 速率：请求间隔 0.5 s（≈2 req/s），单进程串行
- 重试：429 / 500 / 502 / 503 / 504 指数退避 1→2→4 s（尊重 `Retry-After`），最多 4 次；404 直接返回；45 s 超时
- 缓存：`_tmp/references-cache.json`（gitignore）按 URL 存原始 JSON，**命中即不联网**；每抓一条立即落盘，进程被杀也能续跑
- 时间预算：`--time-budget <秒>`，到点停止联网，剩余条目留空（`crossref_error: "skipped_budget"`），只在终端提示、不写进 JSON——否则 `--check` 会把"这次没跑完"误报成"数据不一致"

---

## 2. 覆盖率（本次实际运行）

| 指标 | 运行前 | 运行后 | 说明 |
|---|---|---|---|
| 条目总数 | 77 | 77 | 与名录末尾编号 1–77 一一对应 |
| 带 DOI | 46（59.7%） | **47（61.0%）** | 新增第 37 条（自动匹配） |
| Crossref 有记录 | — | **47（61.0%）** | 原文 46 条 DOI **全部**解析成功（含 SICI 型 DOI 第 73 条） |
| 带候选清单 | — | **12** | 11 条无 DOI 条目 + 已匹配的第 37 条（它的候选也在库里留档） |
| 候选 DOI 个数合计 | — | 22 个 | 12 条条目共 22 个候选（第 37 条含 3 个） |
| BHL 链接 | — | **0** | 未配置 key / 本机 TLS 不可达，见 §5 |

`meta.counts` 的定义（页面统计条直接读它）：`total` 条数、`with_doi` DOI 非空、`crossref_resolved` 拿到完整 Crossref 记录、`candidates` 候选数组非空、`auto_matched` 自动匹配条数、`bhl` BHL 链接非空。这些计数是**分项指标，不是互斥分类**：第 37 条既计入 `with_doi` 也计入 `candidates`（它的候选留档备查），所以四项相加会重复计 1 条，属正常现象。30 条无 DOI 中还有 19 条连候选都没有（网页类，Crossref 本就无记录可搜）。

---

## 3. 没拿到 DOI 的条目：为什么，怎么办

共 30 条无 DOI（另有 1 条自动补上）。按原因分四类：

### 3.1 学术网页 / 机构页面 / 数据库条目（14 条）

`6`（Oregon State Extension）、`11`（Blattodea Species File）、`12`（GBIF）、`13`（智汇三农）、`18`、`24`、`31`、`66`（University of Florida IFAS Extension）、`22`（Termite Web）、`23`（Hebrew University）、`25`（ABIS）、`32`（ISSG/IUCN）、`44`（MAPA/AGROFIT）、`65`（Coconut Research Institute）

**原因**：网页没有 DOI，Crossref 只索引有 DOI 的成果（少部分注册了 DataCite DOI 的数据库记录例外）。这些条目的价值是"物种信息来源可追溯"，本来就不该强行配一个 DOI。
**处理**：保留原文 `[Internet]. [cited …]` 措辞；`links.search` 给出 Crossref 检索入口，读者可自行查。其中 `18`、`31`、`66` 命中了同源的 UF/IFAS **EDIS** 出版物（EENY 系列）与 CABI/Springer 条目，作为候选列出，**未被采用**——因为原文没有年份，无法满足"年份一致"。

> 后续可做：`18`/`31`/`66` 若要升级为正式文献，需人工确认 EDIS 编号（如 EENY-083）与版本年份后，直接在 `list.md` 里补 DOI，再重跑本脚本。

### 3.2 中国标准与中文期刊（2 条）

`33`（SN/T 1105-2014 检验检疫行业标准）、`56`（李茅苗 2013《植物医生》）

**原因**：行业标准与中文科普期刊大多没有 DOI；Crossref 覆盖以英文期刊为主。
**处理**：原样保留。若日后有 CNKI/万方 DOI，可在 `list.md` 里补。

### 3.3 早期印刷文献 / 无 DOI 的旧刊（14 条）

`1`（Desneux 1904）、`9`（Khamraev 2007）、`10`（Mitchell 2002）、`14`（Holmgren 1910）、`19`（Thirugnanasuntharan 1989）、`38`（Kumar 1965）、`39`（Abdul Hafiz 2012）、`40`（Malaka 1983）、`41`（Grassé & Noirot 1955）、`42`（Czepak 1993）、`43`（Amaral-Castro 2004）、`46`（Roonwal & Verma 1980）、`50`（Kooyman & Onck 1987）、`53`（ICZN Opinion 2038, 2003）

**原因**：这些刊物的早期卷期从未注册 DOI（1904–1993 的比利时、苏联、印度、巴西、尼日利亚刊物尤其如此），Crossref 无论怎么查都不会有。
**处理**：原样保留 + 候选清单（若 Crossref 恰好有近似记录）。这类恰恰是 **BHL 最可能派上用场的一类**（见 §5）：`1`、`14`、`41` 这类 20 世纪初的卷册多半已由 BHL 数字化。
**注意**：候选里的 `40`、`41`、`46` 明显是**同域不同文**（例如 `46` 的候选是 PNAS 的另一篇 "Evolution of eusociality in termites"，标题词重合但年份/刊名不符），页面已标注"仅供人工核对"，**不要**把它们当成该条目的 DOI。

### 3.4 已自动匹配（1 条，待人工核对）

`37` Watson JAL, Perry DH. The Australian harvester termites of the genus *Drepanotermes* … Aust J Zool Suppl Ser. 1981; 29(78):1-153.
→ Crossref 命中 `10.1071/ajzs078`（Australian Journal of Zoology Supplementary Series, 1981, 29(78):1-153），**标题相似度 0.90、年份一致**，故采用，但页面徽章写「自动匹配待核对」。核对无误后可把 DOI 直接写进 `list.md`，重跑脚本后该条会变成"原文 DOI"。

---

## 4. 引用格式规则（以及已知局限）

| 格式 | 作者 | 其余 |
|---|---|---|
| **GB/T 7714 式** | 姓在前、名用首字母且不缩写加点（`Bourguignon T`）；**>3 人取前 3 位 + `et al.`** | `作者. 题名[类型标识]. 刊名, 年, 卷(期): 页码. doi: …`；类型标识 `[J]` 期刊、`[M]` 专著/章节、`[C]` 会议录、`[D]` 学位论文、`[R]` 报告、`[DS]` 数据集、`[Z]` 其他 |
| **APA 7** | `Bourguignon, T., Lo, N., …, & Evans, T. A.`；**≤20 人全列，≥21 人前 19 + `…` + 末位** | `作者 (年). 题名. 刊名, 卷(期), 起–止页. https://doi.org/…`，页码范围用连接号（en dash） |
| **Vancouver** | `Bourguignon T, Lo N, …`；**>6 人取前 6 位 + `et al.`** | `作者. 题名. 刊名. 年;卷(期):起-止页. doi: …` |

**刻意不做的事（都属于"不编造"）**

- 缺字段就留空：Crossref 没有 `volume`/`page`/`author` 就不写，不猜、不补、不跨记录拼。第 **5** 条（Engel, Grimaldi & Krishna 2009）的 Crossref 记录本身没有 `author` 字段，所以格式化结果没有作者名——这是 Crossref 的数据现状，不是脚本 bug。
- 不做句子大小写转换（APA 规范要求题名 sentence case）：机械转换会把 `Isoptera`、`Termitidae` 等分类学名降成小写，宁可保留出版方大小写。
- 不改写题名里的空格与标点（如 Crossref 记录的 `(Isoptera : Termitinae)`），也不翻译。
- 作者名只在**整串全大写**时做首字母大写归一（`ENGEL, MICHAEL S.` → `Engel, Michael S.`）；`JAL`、`DH` 这类连写缩写按首字母串处理。
- GB/T 的图书章节未采用 `[M]//书名` 的双层结构，统一用 `[M]` + 书名；需要严格 7714 排版时请以原文/出版方信息为准。
- 三种格式与 BibTeX/RIS/CSL-JSON 都由 Crossref 字段生成，**与页面显示逐字一致**；`formatted` 里没有的数据，页面上也不会出现。
- 年份统一取「纸本/定稿日期」（`published-print`），缺失才退回 `issued`：Crossref 的 `issued` 常是 online-first（比卷期年份早一年，如 msu308 的 2014 与卷 32(2) 的 2015）。原始 `issued` 仍完整保存在 `crossref.issued_parts` 里，两种口径都查得到。

---

## 5. BHL 原始描述扫描（可选，本次为 0 条）

**做什么**：为早期分类学文献补一个 BHL 书目级链接（`bhl.url`），不下载扫描件、不复制 OCR 文本。

**申请 key（免费，5 分钟）**

1. 打开 <https://about.biodiversitylibrary.org/tools-and-services/developer-and-data-tools/>，找到 **BHL API**（"Apply for an API key"）；
2. 填邮箱与用途（"non-commercial taxonomic checklist; link to bibliography records only"），key 会邮件发回；
3. 存进环境变量，不要写进仓库：

       # PowerShell（当前会话）
       $env:BHL_API_KEY = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
       python .github/workflows/build_references.py --write --bhl

**脚本行为**：调用 `https://www.biodiversitylibrary.org/api3?op=TitleSearch&title=…&format=json&apikey=…`（每条约 1 次请求，同样 0.5 s 间隔），取前 5 条结果中标题相似度最高且 ≥0.60 的一条，写入：

    "bhl": {
      "title_id": 12345,
      "title": "…",
      "publication_date": "1904",
      "url": "https://www.biodiversitylibrary.org/bibliography/12345",
      "match": "auto",
      "similarity": 0.87
    }

**预期命中**：`1`（Desneux 1904, Ann Soc Entomol Belg）、`14`（Holmgren 1910, Zool Anz）、`41`（Grassé & Noirot 1955, Ann Sci Nat Zool）、`53`（ICZN 2003 不太可能）这类 1900–1960 年代的欧洲刊物；`37–43` 的印度/巴西/尼日利亚刊物命中率较低。

**本次为 0 条的原因**：没有 `BHL_API_KEY`。本机最初访问 `api.biodiversitylibrary.org` 时曾报 TLS 握手失败（`UNEXPECTED_EOF_WHILE_READING`），但收尾复测该域名已能建连：无 key 的 `TitleSearch` 返回 **200 空 body**，带假 key 返回 `401 {"Status":"unauthorized","is an invalid or unauthorized API key"}` —— 说明是"缺 key"，不是网络问题。脚本对这两种情况都只记 `bhl: null`（空 2xx 不重试、异常不抛出），**不会中断生成**；页面照常渲染，只显示"BHL 0 条"。
**补的办法**：配好 `BHL_API_KEY` 后重跑 `--write --bhl`（本机或 CI runner 均可），JSON 与页面会自动更新；缓存里已有的 Crossref 结果不会重抓。若该域名对某些网络不可达，脚本同样只是 `bhl: null`。

**版权**：BHL 扫描件版权归原藏馆，本项目只保存**书目级元数据 + 链接**（`bhl.url`），不镜像任何页面内容。

---

## 6. 为什么没有 vendor citation-js

- **不需要**：三种引用格式、BibTeX、RIS、CSL-JSON 全部在**服务端 Python** 里生成好了，页面是静态 HTML——禁用 JavaScript 依然完整可读、可复制、可下载。citation-js 只能提供"更多样式"（Chicago、MLA…），对一份分类学名录不是刚需。
- **体积超标**：citation-js 当前浏览器包（npm `citation-js@0.9.0` 的 `build/citation.min.js`）实测 **2.91 MB**（未压缩 `build/citation.js` 3.56 MB），已超过任务允许 vendor 的 1.5 MB 上限，也远大于整站其余 JS+CSS 之和；而它只服务一个页面的一次性"换样式"操作。
- **没有构建链**：仓库没有 npm/bundler，vendor 进去就是一份无法随依赖升级的文件，长期是负担。
- **替代方案已够用**：页面上有 **「导出 CSL-JSON」** 按钮（`assets/references.js` 里约 30 行原生代码，`fetch` `data/references.json` → 取每条的 `csl` → 下载数组），Zotero / EndNote / Mendeley / pandoc 都能直接吃 CSL-JSON；无 JS 时还有 `/data/references.json` 静态链接。

**如果以后确实要加**（例如想在前端切 Chicago/MLA）：

1. 下载 <https://cdn.jsdelivr.net/npm/citation-js@0.9.0/build/citation.min.js>（2.91 MB）到 `assets/vendor/citation-js/citation.min.js`（并保留 `LICENSE`，MIT）；
2. 在 `_includes/references.html` 的列表之后加 `<script src="{{ site.base_url }}/assets/vendor/citation-js/citation.min.js" defer></script>`（**仅**在 references 页加载）；
3. 在 `assets/references.js` 里 `var Cite = window.Cite;`，`new Cite(cslArray).format('bibliography', { template: 'chicago-author-date', lang: 'en-US' })` 填进一个容器；
4. 记得保持"无 JS 时仍显示服务端 GB/T 结果"的回退，别把静态内容换成 JS 动态渲染。

---

## 7. 重新生成 / CI 接线

    python .github/workflows/build_references.py            # 统计（默认不写文件）
    python .github/workflows/build_references.py --write    # 写入两份 JSON（然后提交）
    python .github/workflows/build_references.py --verify   # CI 的离线步骤用这个：不联网、几百毫秒
    python .github/workflows/build_references.py --check    # 逐字段回归：需要缓存或联网，不一致时 exit 1
    python .github/workflows/build_references.py --check --offline   # 有缓存且不联网时校验

- **环境变量**：`CROSSREF_MAILTO`（联系邮箱）、`BHL_API_KEY`（可选）、`SOURCE_DATE_EPOCH_DATE`（覆盖 `meta.generated`，可写 `2026-10-17` 固定日期）。
- **确定性**：`--check` 比较时忽略 `meta.generated`；`--write` 在内容未变时沿用旧时间戳，所以 CI 每天跑也不会造出无意义 diff。
- **缓存**：`_tmp/references-cache.json`（≈1.5 MB，gitignore）。CI 若想避免每次全量抓取，用 `actions/cache` 挂这个路径，key 取 `references-cache-v1`。
- **CI 插入位置**（由 Lead 在 `.github/workflows/pages.yml` 里加，本文件不做改动）：放在 Jekyll build **之前**。`pages.yml` 现有那一步是**离线**校验（`continue-on-error: true`），建议把那行换成 `--verify`（不联网、不抓 Crossref，只查 JSON 自洽与两份文件字节相同）；`--check` 留给本地或带缓存的 CI（全量抓取约 80 个请求、60–90 秒，且 Crossref 抖动会让步骤变红）。
- **`--verify` 查什么**：JSON 可解析、两份文件字节相同、`meta.counts` 与重算值一致、编号 1..N 连续、`doi_status` 合法且与 `doi` 自洽、三种格式与 BibTeX/RIS/CSL 非空、`links` 以 `https://doi.org/` 与 Crossref API 开头、`crossref` 字段齐全、BHL 链接指向 BHL。
- **改了 `list.md` 之后**：重跑 `--write`，并人工看一眼新条目的 `doi_status` 与 `candidates`。

---

## 8. 许可

| 内容 | 许可 / 说明 |
|---|---|
| 本仓库生成的 `references.json`、页面与脚本 | CC BY 4.0（与数据集一致）；脚本本身可视为同一许可 |
| Crossref 元数据 | 事实性书目数据，Crossref 服务条款允许再利用；本页保留 Crossref 来源链接 |
| BHL | 扫描件版权归原藏馆；本项目只存书目级链接与标题 |
| citation-js（未引入） | MIT；若将来 vendor，需随包保留 `LICENSE` |

---

## 9. 文件清单

| 文件 | 作用 |
|---|---|
| `.github/workflows/build_references.py` | 唯一生成脚本（解析 → Crossref → 格式化 → JSON，支持 `--write`/`--check`/`--verify`/`--bhl`/`--offline`/`--time-budget`） |
| `_data/references.json` | 站点数据（Liquid: `site.data.references`），已提交 |
| `data/references.json` | 公开下载副本，与上一份**字节相同**；`data.md` 可以加一条下载链接 |
| `_includes/references.html` | 编号列表 + GB/T 引用 + DOI/Crossref 链接 + 复制按钮 + `<details>` 里的 APA/Vancouver/BibTeX/RIS/原文/候选 |
| `assets/references.css` | 只服务本页的 `.refs-*` 样式（复用全站 CSS 变量，含打印样式） |
| `assets/references.js` | 复制（clipboard + `execCommand` 兜底）与「导出 CSL-JSON」，无框架、无依赖 |
| `references.md` / `en/references.md` / `es/references.md` | 三语页面（`/references/`、`/en/references/`、`/es/references/`），正文 + `{% include references.html %}` |
| 本文件 | 流水线、覆盖率、未匹配原因、BHL 步骤、重跑方法、许可 |

**改模板时的两个坑**

1. `_includes/references.html` 里 `<div class="refs">` 到 `</div>` 之间**故意不留空行**：Jekyll 的 kramdown 在空行处结束 HTML 块，块内空行会被当成 Markdown 重新解析（`<p>` 自动包裹、`<li>` 嵌套被打断）。要加内容请贴着写，不要插入空行；Liquid 的 `{%-` / `-%}` 会吃掉标签两侧的换行，所以模板里看到的换行不一定出现在输出里。
2. 复制按钮复制的是目标元素（`data-refs-copy="#ref-12-gbt"`）的 `textContent`，因此所有 Crossref 字段都必须 `| escape` 输出——第 73 条的 DOI 含 `<0001:FNFTI>`，不转义会被浏览器当成标签吞掉。
