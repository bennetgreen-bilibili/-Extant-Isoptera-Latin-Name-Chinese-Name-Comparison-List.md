# 种级形态描述 B/C 类复核（2026-11-19）

对象：`_reports/species-morphology-coverage.csv` 里状态为 `B-paper`（459 种）与 `C`（149 种）的物种。前一轮的 401 条形态条目由 A 类（326）与旧基线构成；本轮只处理剩余部分。逐种处置见 `_reports/species-morphology-bd-disposition.csv`。

## 1. 方法

1. 以 `_unpublished/文库/manifest.json` 为底，把 CSV 的 `sources` 字段（`book` 名，分号分隔）映射到 341 个书目；DOI 类目录名做了 `/`→`-` 截断，匹配时按前缀归一化。
2. **种加词级扫描**：每本书只扫一遍行首标题，同时匹配「属名 + 种加词」，种加词允许编辑距离 1–2（OCR 变体如 `fletcheri`→`tletcheri`、`rubidus`→`rabidus`）；接受条件为标题内含该种命名人姓氏，或块内出现现属名；再按品级小标题、`Description`、量度串数量（`\d{1,2}[.,]\d{1,2}`）打分。
3. **只看「种级条目」**：块内须有本种的鉴别特征/描述段与至少一个品级（有翅成虫、兵蚁、工蚁、若虫）的性状或量度。名录、命名索引、检索表、区系比较句、食性表、图注、分子表一律判无。
4. **召回自检**：从 A 类随机 60 种跑同一检测器，命中 51（85%）。漏检 9 种均为「描述标题用原始组合、属名与现属不同」的情形（如 *Termes koenigi* → *Odontotermes koenigi*），本轮已用命名人姓氏+种加词补回 182 条候选。
5. 判定后由子代理逐条读原文，中文改写写入 `_data/morphology_species/<属 id>/<slug>.json`，量度照录、OCR 残缺处写入 `note`，`sources` 指回 `.sources` 的 S 编号。

## 2. B-paper 459 种

| 处置 | 数量 |
| --- | --- |
| 已写条目（种级描述） | 45 |
| 文库有条目但无形态描述 | 149 |
| 文库无该种条目 | 265 |

已写条目的来源分布：*Termites of the Belgian Congo and the Cameroon*（Emerson 1928，S0075）21 条、*The Fauna of India … Volume II*（S0104）13 条、《白蚁生物学现代研究合集》4 条、*The soldierless termites of Africa*（Sands 1972，S0005）3 条、《中国动物志 昆虫纲 第十七卷 等翅目》3 条、*The Harvester Termites of the Indian Region*（S0463）2 条、Zootaxa 5428 2 条，其余 Arkiv for zoologi、Holmgren 1912、Hill 1927、ZooKeys 1059、Zootaxa 5219、JOTT、Entomon 等各 1 条。

「有条目但无形态描述」的 149 种集中在 Snyder 1949 世界名录（模式标本与文献行）、ZooKeys 623 分子表、ZooKeys 148 检索表、insects10050122 采集表、《白蚁学》与《白蚁生物学现代研究合集》的生理/行为/名录段落。

「文库无该种条目」的 265 种，其原描述多在 1930 年以前（BHL/archive.org 可及）或 1990 年以后的付费期刊。

## 3. C 类 149 种

| 处置 | 数量 |
| --- | --- |
| 已写条目（种级描述） | 31 |
| 文库有条目但无形态描述 | 4 |
| 文库无该种条目 | 114 |

- 已写的 31 条中 14 条来自 Isognathotermes 修订（Josens et al. 2025，EJT，CC BY 4.0，S0025），11 条来自 2018–2023 年的 ZooKeys 新种描述（Rugitermes、Cryptotermes pugnus、Neotermes costaseca、Rhynchotermes armatus、Uncitermes almeriae、Anenteotermes cherubimi、Hospitalitermes nigriantennalis；S0495–S0506），其余来自 Belgian Congo、Fauna of India。
- 149 种的 `synonym_count` 全为 0，站内没有可桥接的异名；其中 101 种为 2010 年后描述的新种，文库（341→356 本）不可能覆盖。
- 用 `_data/papers/genera/<属>.json` 按「属 + 种加词」匹配，82 种有候选论文（73 个有 `oa_url`），去重得 52 个 DOI，经 `_tools/fetch_fulltext.py` 走合法 OA 通道（Unpaywall / OpenAlex / Europe PMC）：处理 32 条，归档 11 条，其余因站点拦截或无 PDF 直链失败（core.ac.uk、sciencedirect、wiley、hindawi 已进入 120 天冷却）。
- 未匹配的 67 种改走 Crossref `query.bibliographic`，53 种有候选；老种噪声大（如 *Nitiditermes aemulus* 命中拉丁语词典），新种命中可用（Zootaxa、ZooKeys、JOTT、Entomon 等，多为付费墙或需作者索取）。

## 4. 边界判定

- *Pericapritermes urgens* 与 *P. urgens urgens*：原文只有一段描述，两页正文相同、仅 `note` 不同（指名亚种页说明原文未分亚种）。两条均保留，避免指名亚种页空置。
- *Prohamitermes mirabilis*：S0033 只有属级描述（该属 2 种，仅描述 mirabilis，无量度），未按种级写；处置表记为「文库有条目但无形态描述」。

## 5. 未完成部分与后续入口

- B 类 265 种、C 类 114 种仍需站外原文：前者按 BSF 派单把 1930 年前描述按刊卷送 BHL/archive.org；后者按 `_reports/species-morphology-bd-disposition.csv` 的「可获取文献DOI」列逐条走出版商 OA、作者索取或馆际互借。
- D 类第二批 OA 抓取（Crossref 收紧后的 18 个 DOI）在 `_tools/fetch_fulltext.py` 中执行，归档结果会追加到文库；新入库的书目需重跑种加词扫描再补条目。
- 中文形态条目由 401 增至 477（本轮 +76）；`_data/translations_en|es/morphology_species/` 各补 76 条译文，三语当前均为 477，`check_translations.py --ci` 通过。缺译文的条目在英/西页面整节省略，故译文须与中文条目同步新增。

## 6. 复现

    python _tmp/bd_epithet.py            # 种加词级扫描 → _tmp/bd_epithet_cands.json
    python _tmp/d_scan.py                # 全库按现属+种加词扫 → _tmp/d_candidates.json
    python _tmp/make_disposition.py      # 生成本报告配套的 disposition.csv

`.sources` 相关：S0005、S0075、S0104、S0025、S0463、S0105、S0491 等。交付前已跑 `python _tools/sources.py check --strict`。
