# 文库研读与页面增补 SOP

本文件是每日自动化任务的执行手册。任务目标、硬约束和验收口径都以这里为准；与 `AGENTS.md` 冲突时，以 `AGENTS.md` 的存档红线和仓库约定为准。

## 0. 任务定义

- **频率**：每天谷时段 01:00（Asia/Shanghai）执行一次。
- **阅读量**：每轮 20 个「阅读单元」，其中默认 **15 个文库 chunk + 5 条仅摘要记录**。一个 chunk 单元 = `_unpublished/文库/manifest.json` 里的一个分卷文件（`full.txt` 或 `part-00N.txt`）；一条仅摘要单元 = `.sources/index.json` 里没有全文、但已存档摘要的论文记录。
- **仅摘要也要读**：`_tools/library_scan.py` 会从 `.sources` 记录中筛出 `fulltext_status: abstract-no-oa` 或有「摘要 / Abstract」证据 locator 的条目，把逐字摘要片段拼成可读文本，作为 `kind: abstract` 单元扫描。只读摘要的条目在草稿和正文里都必须标「据摘要」，不能写成已读全文。
- **产出**：从这 20 个单元中挑出证据最扎实的 **8–15 个页面**（上限 20），每页新增 1–4 段「研究记述」，按用户要求写成：

  > 根据 XXXXX 研究，xxxxxx。

  段末用 `<!-- src:Sxxxx -->` 指向 `.sources` 存档；页面文末列「参考文献」。
- **提交前必须审阅**：每轮先把完整草稿输出到对话，等用户明确说「可以 / 提交 / 通过」后，才允许改 `_data/`、写 `.sources`、跑生成脚本、commit。用户没有明确批准时，**只写 `_tmp/review/`，不碰仓库里的数据文件**。
- **不 push**：除非用户明确要求推送，提交只留在本地。

## 1. 硬约束（违反即停）

1. 不编造标题、作者、年份、DOI、页码、引文；没读到的行不写。
2. 摘录必须逐字；需要改写就写在正文，并在 `notes` 注明「转述」。
3. 全文只进 `_unpublished/文库/`，不进仓库；`.sources` 只存元数据 + 短摘录（单处 ≤400 字，同一作品累计 ≤2000 字）。
4. 付费墙 / 403 / 只有摘要时，正文标注「据摘要」，`notes` 写 `access: blocked，仅有摘要`。扫描器选中的 `kind: abstract` 单元本身就是摘要，不能因为「不是全文」跳过；但也只能写摘要明确支持的内容。
5. 旧文献必须核对分类学变化：先查 `_data/name_issues.json` 的 `synonym_pairs` 与 `species_authority`，再查当前页面接受的学名。写法用「该研究当时置于 X 属／当时记为 X，现多置于 Y」这类有时间的表述，不能把旧名直接当现行名。
6. 正文里每个事实性判断都要能指回段末的 `Sxxxx`；`references` 只列本页实际用到的来源。
7. `used_in` 必须写真实存在的仓库文件；本任务统一写 `_data/taxon_literature.json`。
8. 不覆盖或改写页面上已有的自动生成区块（`<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 之间）。

## 2. 每轮开始前（Phase 0）

在仓库根目录执行：

```powershell
git status --short
python _tools/library_scan.py --help
```

检查：

- 工作区是否干净；有未提交改动时先问用户，不要混进本轮。
- `_tmp/review/` 下是否有上一轮 `status.json` 标为 `pending` 的草稿。若有，**不要开新一轮**，只在对话里提醒用户先审阅上一轮。
- `_reports/library-reading/progress.json` 是否存在；不存在就按模板重建：

```json
{
  "version": 1,
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "units": {}
}
```

## 3. Phase A：扫描 20 个单元（15 chunk + 5 摘要）

```powershell
python _tools/library_scan.py --limit 20 --abstract 5 --focus auto --date YYYY-MM-DD --top 120
```

输出目录：`_tmp/library-scan/YYYY-MM-DD/`。

先看：

- `summary.json`：实际选中的 `chunk_units` 与 `abstract_units`、`abstract_pool`、扫描字符数、候选数、页面数、科／属／种分布、警告。
- `top.md`：候选段落 + 页面 + 来源 + 行号。它是线索，不是可直接抄的正文。仅摘要候选会排在前面并标「据摘要」；若 `abstract_without_candidates` 大于 0，说明该摘要没有可映射的属／种，`notes.md` 要写明「已读，无可写内容」，不能假装它产出了段落。
- `units.json`：本轮 20 个单元分别来自哪本书／哪篇论文；`kind: abstract` 的条目是仅摘要记录，写审阅包时单独列出。

扫描器的已知噪声（必须人工过滤）：

- 泛泛讨论科／亚科系统发育的段落会被挂到多个属；只有段落确实在讲该属时才用。
- `+` 表格、名录、目录式段落（大量 `....`、`+`、纯学名列表）通常不能改写成散文。
- 同一段可能同时命中多个页面；优先给「段落主语」对应的页面，其余页面只在确有独立信息时才写。
- 中文 OCR 有错字（如 `〃加`、`亜`），改写时按上下文校正，但不要改动引文原文；引文另存 `.sources`。
- 仅摘要单元只覆盖摘要内容，常常没有分布、模式产地、完整异名；不要从摘要里补原文没有的细节，也不要把摘要里的泛泛背景写成该研究的新结论。
- 扫描器会用标题／开头筛掉「只提到白蚁」的非白蚁研究（例如以白蚁为食的蜥蜴、黑猩猩食性论文）。若 `units.json` 里仍有这类条目，人工跳过并在 `notes.md` 说明。

## 4. Phase A：选页与核证

### 4.1 选页

从 `top.md` 里选 10–20 个页面，优先：

- 段落有明确主语（「本属」「该种」「X 属的兵蚁」），不是泛泛综述；
- 有可核对的年份、命名人、模式种、分布、异名、新组合、新记录；
- 页面现在缺这一块内容（属页看 `_data/taxon_literature.json` 是否已有；物种页看正文是否已覆盖）；
- 同一来源不重复堆砌；每页 1–4 段，宁少勿滥。

### 4.2 读原文

不要只读 `top.md` 的截断文本。

- **chunk 单元**：用 `read` 打开对应 chunk，按候选的 `第 X–Y 行 / 文件名` 读前后各 20–40 行，确认：
  - 这段到底在讲哪个分类单元；
  - 年份、作者、命名人、模式产地、分布是否在同一段或相邻段；
  - 是否只是引用别人的观点（「据 X」「X et al. 认为」），不要把二手观点写成该研究自己的结论；
  - 是否是表格／名录／目录，无法改写成完整句子。
- **摘要单元**：打开 `.sources/index.json` 里对应 `id` 的 `evidence` 逐字片段，拼读完整摘要；同时核对标题、年份、作者。摘要没写的细节一律不补，正文句首或句末标「据摘要」。

### 4.3 核对分类学

**先查科级／亚科级，再查种级**：

- `_reports/library-reading/taxonomy-crosswalk.md`：
  - **3 条科级／亚科级／支系级**（优先）：2024 鼻白蚁科拆分、2024 白蚁亚科拆分、2022 Teletisoptera 建立；
  - **8 条种级**异名／组合对照，含「旧名 → 本站现用名」和写作口径；
- `_data/taxonomy_crosswalk.json`：上表的机器可读版本，科级条目在 `higher_ranks`，种级在 `entries`；
- 表里没有的，再用 `read` 工具读 `_data/name_issues.json`，或写 `_tmp/check_name.py` 查询（PowerShell 不支持 `<<'PY'` heredoc，临时脚本用 `write` 落盘再 `python` 执行）。重点：

- **科级**：旧文献的“鼻白蚁科 Rhinotermitidae”若含 `Coptotermes` / `Reticulitermes` / `Heterotermes`，按 2024 年拆分写“当时置于鼻白蚁科（广义），现置于异白蚁科 Heterotermitidae”；`Psammotermes` / `Prorhinotermes` 现置沙白蚁科，`Termitogeton` 现置寡脉白蚁科。只有 `Acorhinotermes`、`Dolichorhinotermes`、`Parrhinotermes`、`Rhinotermes`、`Schedorhinotermes` 仍属鼻白蚁科 sensu novo。
- **亚科级**：旧文献的“白蚁亚科 Termitinae”不能直接当现行亚科；`Termes` 等 Termes-group 才留白蚁亚科，`Amitermes` 等按弓白蚁亚科等处理，`Coptotermes` / `Reticulitermes` 属异白蚁科。2024 年白蚁科共 18 亚科。
- **Teletisoptera**：它是 2022 年 Wang 等所指的 `Stolotermitidae + Hodotermitidae + Archotermopsidae` 支系，不是科／亚科名；`Hodotermopsis` 现置原白蚁科 Hodotermopsidae。S0196 本地无全文，只能据 Crossref 摘要，正文必须标「据摘要」，不得补正文里的种级或分布细节。
- 旧属名 / 旧种名 → 当前页面：`species_authority` 的 `incoming` / `outgoing`；
- 异名对：`synonym_pairs` 的 `our` / `external` / `relation` / `direction`；
- 若旧文献用的名字与当前页面不同，正文必须写出「当时置于…，现置于…」，不能只写旧名；
- 若只是「该研究把某名列为异名」而当前站点未接受，写「该研究将…列为…的异名」，不要写成站点结论；
- 年代核对：`1853`、`1904`、`1911` 这类数字必须能在原文找到，不能凭印象补。
- 对照表列 **3 条科级／亚科级／支系级 + 8 条种级**；属级变动、未列入的种级变动，仍必须回原文和 `name_issues.json` 查，查不到就标「待核」。科级结论不能只靠表里的中文，必须回 `S0008` / `S0196` 的摘录核对。

### 4.4 映射到页面

- 属级研究 / 属的建立、模式种、属征、分布 → `/genus/<id>/`。
- 研究里提到的具体物种例子、种级新记录、种级异名 → `/species/<slug>/`；若同时含属级结论，属页也可写一段，但内容不能重复。
- 科／亚科级分类、系统发育、科级分布 → `/family/<id>/` 或 `/subfamily/<id>/`。
- 一个段落同时讲属和种：属页写属级结论，种页写种级事实；不要在两页复制同一段。

### 4.5 书怎么读：chunk 不是阅读单位

- 这一条适用于**所有书和专著**，不只《白蚁学》：`source_type: book` 的 11 部（S0001、S0002、S0003、S0004、S0005、S0103、S0104、S0105、S0113、S0114、S0118），以及按专著处理的 S0033 Holmgren 1912、S0034 Emerson 1959、S0075 Belgian Congo。`chunk` 只是文件切块，**扫过一个 chunk 不等于读完这本书**；也不要用“书已扫”冒充“书已读”。
- 先读目录／索引，再按书型拆阅读单位：
  - **教材／综述**（如《白蚁学》《白蚁生物学现代研究合集》）：一章或一节 = 一个阅读单位；记章、节、起止行／页、所属 chunk。
  - **志书／专著**（如中国动物志、Treatise、Fauna of India、Monographie）：一个科／属／种的处理（taxonomic treatment）或一个页码段 = 一个阅读单位；有章节的按章节。
  - **名录／目录**（如 Catalog of the Termites）：一个科／属条目或一个页码段 = 一个阅读单位；不要把整页名录当散文硬写。
  - **文集／期刊卷**（如 Arkiv for zoologi 1920）：一篇论文或一个独立 section = 一个阅读单位。
- 每个阅读单位记 `work`、`chapter/section 或 taxon treatment`、起止页／行、所属 chunk；一天 20 个单位里，一个单位就是一节／一个处理，不是一个 200k 字符的 chunk。
- **每节穷尽抽取**：凡是能落到具体分类单元、能回原文核对的事实，全部摘出；**不设 3–8 条上限，有多少算多少**。分类位置、异名、分布、形态、品级、行为、生态、防治、年代都算。
- 每条事实一张卡：`page/taxon`、`claim`、`quote`、`src`、`work`、`unit`、`locator`、`status`（`used` / `queued` / `rejected`）。
- 能落到具体页面的写页面；暂时落不上的写进 `_reports/library-reading/facts/YYYY-MM-DD.json`，下一轮继续用，不要丢。
- 覆盖账本按**节／处理**记 `未读 / 已扫 / 已摘 / 已用`；每部书单独建一行，不能只记《白蚁学》。
- 阅读顺序按书型：教材／综述先分类 → 形态 → 生理／生物学／生态 → 防治 → 文献；志书／名录先按科 → 属 → 种；文集按单篇主题。书目与拆单位方式见 `_reports/library-reading/book-outlines/README.md`。
- 例：《白蚁学》22 章，先读第 6 章「白蚁分类」；《Catalog of the Termites》先按科／属条目推进；《Treatise》先读分类总论与科级处理。示例只是示例，所有书同规。

## 5. Phase A：写草稿

### 5.1 正文格式

每个页面一个条目，建议结构：

```markdown
## /genus/archotermopsis/ — 古白蚁属 Archotermopsis

### 分类与分布
根据何银竹等（2009）对云南古白蚁的记述，古白蚁属 Archotermopsis 由 Holmgren 于 1911 年以 Termopsis wroughtoni Desneux, 1904 为模式种建立；该研究首次记录该属在中国云南分布，并记述中国新记录种罗夫顿古白蚁 A. wroughtoni。<!-- src:S0110 -->

### 参考文献
- S0110 何银竹, 周鲁们, 侯清柏. 2009. 中国新记录属——古白蚁属及一新记录种. …
```

要求：

- 中文正文；学名用 `<i>Genus species</i>`，不要用 Markdown 星号（数据里会按 HTML 渲染）。
- 「根据 XXXX 研究」中的 XXXX 用「作者（年份）」或「作者等（年份）」，与 `.sources` 的 `authors`/`year` 一致；不要写「研究表明」这种无主语句。
- 一段只承担一个中心意思；长段落拆成 2–3 段，每段都要有 `src`。
- 只写原文支持的内容；推断性句子（「推测」「可能」）要么删掉，要么明确标为原文的推测。
- 旧文献加时间限定：「当时」「该研究采用」「现多置于」。
- 仅摘要来源要在句首或句末写「据摘要」；不要把摘要里的背景句写成该研究的新发现。
- 不写「我国」这类脱离页面语境的词；用「中国」「云南」等明确地名。
- 不把参考文献编号写进正文（如 `[12]`）；用段末注释。

### 5.2 数据形状

最终要合并进 `_data/taxon_literature.json`：

```json
{
  "/genus/archotermopsis/": {
    "updated": "2026-11-12",
    "sections": [
      {
        "heading": "分类与分布",
        "paragraphs": [
          {"text": "根据……", "src": ["S0110"]}
        ]
      }
    ],
    "references": [
      {"id": "S0110", "citation": "何银竹, 周鲁们, 侯清柏. 2009. ……", "url": "……"}
    ]
  }
}
```

- key 必须是页面真实 URL（`/genus/.../`、`/species/.../`、`/family/.../`、`/subfamily/.../`）。
- `src` 里每个 id 都要在 `.sources/index.json` 存在；没有存档先补存档。
- `references[].citation` 用中文可读格式：作者. 年份. 标题. 刊名/出版社, 卷(期): 页码. 有 DOI/URL 就放在 `url`。
- 同一个页面多次运行时**追加**新 section 或新段落，不要覆盖旧段落；同一段不要重复。

### 5.3 审阅包

写到 `_tmp/review/YYYY-MM-DD/`：

- `draft.md`：给人看的完整草稿（按页面分组，含正文、来源、待核点）。
- `draft.json`：可直接合并的 JSON（尚未写入 `_data/`）。
- `status.json`：`{"status":"pending","date":"YYYY-MM-DD","pages":N}`；获批准后改 `approved`，应用完改 `applied`。
- `notes.md`：本轮读了哪 20 个单元（chunk 与仅摘要分开列）、哪些候选被丢弃及原因、哪些地方拿不准。

写完先跑：

```powershell
python _tools/check_taxon_literature.py --file _tmp/review/YYYY-MM-DD/draft.json
```

有 ERROR 先修 JSON，再输出到对话；WARN 可在 `notes.md` 解释。

`draft.md` 开头写：

```markdown
# 文库增补草稿 YYYY-MM-DD

- 阅读单元：20（15 chunk + 5 摘要，见 units.json）
- 拟增补页面：N
- 待用户确认：是（尚未写入 _data/，未提交）
```

## 6. Phase A：输出到对话

把 `draft.md` 的**完整内容**贴到对话里（不是只给摘要），并在最后列出：

- 本轮 20 个单元的清单（书名/论文名 + chunk；仅摘要条目注明「据摘要」）；
- 拟增补的页面列表；
- 需要用户特别注意的 3–5 个核证点（尤其是旧名、年代、分类变动）；
- 明确一句：「请审阅；确认后我再写入 `_data/taxon_literature.json`、补 `.sources`、跑检查并提交。」

然后停止。**不要**在等待审阅时改仓库数据或跑生成脚本。

## 7. Phase B：用户批准后应用

### 7.1 合并数据

- 读现有 `_data/taxon_literature.json`，按 URL 合并；保留已有 section，追加新段落。
- 同一页面段落顺序：分类/分布在前，形态/行为/生态在后；参考文献按正文出现顺序。
- 更新 `_meta.updated` 为当天。
- 合并后跑一次 JSON 解析检查。

### 7.2 补 `.sources`

对每个新用到的来源，写 `_tmp/sources-task.json`，再执行：

```powershell
python _tools/sources.py add --json _tmp/sources-task.json
```

最小记录示例（文库已有记录时用 `canonical_key` 合并，不要新开 Sxxxx）：

```json
[
  {
    "canonical_key": "library:he2009-archotermopsis-wroughtoni",
    "title": "he2009-archotermopsis-wroughtoni",
    "source_type": "paper",
    "reliability": "peer_reviewed",
    "evidence": [
      {
        "quote": "逐字摘录，≤400 字",
        "locator": "第 32–35 行 / 0001-0003.txt",
        "note": "支撑：Archotermopsis 的建立与中国新记录"
      }
    ],
    "used_in": ["_data/taxon_literature.json"]
  }
]
```

- 先 `python _tools/sources.py list --limit 400` 查已有 id；文库 36 部作品都已有记录（S0001–S0005、S0033、S0034、S0074、S0075、S0103–S0119 等），**不要重复建档**。
- `canonical_key` 用 `library:<manifest 的 book 字段>`；不确定时用 `python _tools/sources.py list` 找。
- 摘录逐字，不要拼接两处；`locator` 写「第 X–Y 行 / 文件名」。
- 如果正文用的是转述，`note` 写「转述：……」；`evidence.quote` 仍放原文短句。

### 7.3 登记阅读账本

草稿应用后：

```powershell
python _tools/library_scan.py mark --date YYYY-MM-DD
```

这会把本轮 `units.json` 里的 20 个单元（含仅摘要条目）记为已读。**只有应用后才 mark**；未批准的轮次不 mark。

### 7.4 生成与检查

按顺序：

```powershell
python _tools/check_taxon_literature.py
python _tools/check_site.py --ci
python _tools/check_liquid.py
python _tools/sources.py check --strict
```

`check_taxon_literature.py` 会校验页面 URL、`src`/`references` id、重复段落和参考文献覆盖关系；草稿阶段可先用 `--file _tmp/review/YYYY-MM-DD/draft.json` 跑一遍。

若本机有 Git Bash，再跑：

```powershell
bash _tools/regen_all.sh
```

没有 Git Bash 时，按 `_tools/regen_all.sh` 的顺序逐个跑 Python 脚本（先 `extract_taxon_data.py --check`，再 `build_list_index.py`、`build_taxonomy_data.py --write`、`build_genus_index.py`、`build_species_body.py --write`、`build_photo_pages.py`、`build_taxonomy_pages.py`、`build_sitemap_txt.py`、`build_search_index.py`、`build_dataset.py`、`build_changelog.py`、`build_name_issues.py`）。生成后重跑三项检查。

检查通过后：

- 用 `office_render` 或本地预览确认至少一个属页、一个种页出现「研究记述」且参考文献正常；没有 Jekyll 时至少检查生成的 HTML/Markdown 片段。
- 确认段末 `<!-- src:Sxxxx -->` 能被 `sources.py check --strict` 解析。

### 7.5 提交

```powershell
git add _data/taxon_literature.json .sources _reports/library-reading/progress.json _layouts/species.html _includes/taxon-literature.html .github/workflows/build_taxonomy_pages.py assets/custom.css
git commit -m "content: add literature notes from library reading YYYY-MM-DD"
```

不要 `git push`，除非用户明确要求。

## 8. 质量红线（审阅时逐条自查）

- [ ] 每段都有明确主语，读者知道在讲哪个属／种。
- [ ] 每段至少一个 `src`，且 `src` 指向真实存档。
- [ ] 年份、作者、命名人、模式种、分布能在原文对应行找到。
- [ ] 旧名已核对 `name_issues.json`，正文有时间限定。
- [ ] 没有把「某研究认为」写成「学界公认」。
- [ ] 没有把表格／名录硬改成散文。
- [ ] 每段至少包含一个可核验的具体事实（分类位置、年代、产地、数量、形态或行为特征）；不写只有「多个空间尺度」「整体视角」「重要节点」这类框架性判断的段落。摘要只有框架性表述时，不据此单独立页。
- [ ] 没有重复页面已有内容。
- [ ] 参考文献与正文来源一一对应，没有列了不用的。
- [ ] 中文通顺，学名斜体，标点统一。
- [ ] 每个拉丁名第一次及以后每次出现，都带中文正名（如“尖齿白蚁属（Acutidentitermes）”“奥斯本尖齿白蚁（Acutidentitermes osborni）”）；中文正名以 `_data/taxonomy.json`、`_data/species_by_genus.json`、`_species/*.md` 为准，不临时造名。
- [ ] 属名一律写全，不写 `A. osborni`、`L. buttel-reepeni` 这类缩写；旧组合没有本站中文正名时，写“（无中文正名，旧组合/旧属/旧异名）”，不要只留拉丁名。
- [ ] 计数用“1 头兵蚁”“2 头工蚁”，不写“一头士兵”。
- [ ] 只改了 `_data/taxon_literature.json` 和本轮必要的源文件；没有手改生成页。

## 9. 故障处理

- **扫描器选中的单元文件不存在**：检查 `manifest.json` 的 `out` 与 `_unpublished/文库/<book>/`；缺文件就在 `summary.json` 的 warnings 里记录，换下一个单元，不要伪造内容。
- **来源记录找不到**：先 `sources.py list` 按 `library.book` 找；确实没有就补一条 `library-add` 或 `add`，不要空着 `src`。
- **`sources.py check` 报 E010**：说明正文引用了未存档 id；补存档或删掉该引用。
- **旧名对应不到当前页面**：查 `species_authority`／`synonym_pairs`；仍不确定就在草稿里标「待核」，不要硬写。
- **生成脚本覆盖了手工内容**：属／科／亚科页只能通过 `_data/taxon_literature.json` + include 注入；物种页只能放在 AUTO 区块之外。若发现被覆盖，检查 include 是否在生成模板里。

## 10. 当前基线（2026-11-11）

- 文库：36 部作品 / 94 个 chunk / 20,930,481 字符。每天 15 个 chunk，约 7 天走完第一遍。
- 仅摘要：`.sources/index.json` 中筛出 20 条白蚁／等翅目相关的仅摘要记录（另有非白蚁论文会因标题/开头不相关被排除）；每天 5 条，约 4 天轮完，之后按 `auto` focus 复读。
- 第一遍 focus 以 `taxonomy` 为主；第二遍起再按 `morphology`、`ecology` 轮换。
- 页面：326 属、13 科、18 亚科、3089 种。
- 已有渲染入口：`_includes/taxon-literature.html`、`_data/taxon_literature.json`；属／科／亚科页由 `.github/workflows/build_taxonomy_pages.py` 注入，种页由 `_layouts/species.html` 注入。
- 已有扫描器：`_tools/library_scan.py`；账本：`_reports/library-reading/progress.json`。
- 分类学对照表：`_reports/library-reading/taxonomy-crosswalk.md`（3 条科级／亚科级／支系级 + 8 条种级）；生成器：`_tools/build_taxonomy_crosswalk.py`；机器版：`_data/taxonomy_crosswalk.json`。S0196（Teletisoptera）仅存 Crossref 摘要，本地无全文，正文标「据摘要」。
