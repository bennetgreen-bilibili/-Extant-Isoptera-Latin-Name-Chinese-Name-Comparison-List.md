# _tools/fauna — 形态描述改写管线

把《中国动物志·昆虫纲 第十七卷 等翅目》（黄复生等，2000，科学出版社）中物种、属、科的形态记述
**重新组织语言改写**后注入本站页面。**原书文字不入仓、不上站**；仓内只保留改写稿（`_data/fauna_*.json`）。

## 数据流

```
原书 PDF/docx（站外）
  └─ dump.py            → _tmp/dz/fauna_raw.txt        抽取整书文本（python-docx，按页序）
      └─ corpus.py      → _tmp/dz/corpus.json          切出 454 条物种条目（序号+中文名+拉丁名+年份三重锚定）
          └─ resolve.py → _tmp/dz/work.json            把书中条目匹配到 _species/*.md（拉丁名/异名/中文名/属映射 + 人工 OVR 表）
              └─ make_batches.py → _tmp/dz/batches/*.json   合并重复页，按 30 条分批
                  └─ （改写，见 SPEC.md）→ _tmp/dz/out/batch_*.json
                      └─ verify.py                  与原文比对，PASS 才收
                          └─ build_data.py → _data/fauna_species.json
```

属级：`extract_genera.py` → `make_genus_batches.py` → 改写（SPEC_GENUS.md）→ `build_genus_data.py` → `_data/fauna_genera.json`
科级：`extract_families.py` → 改写 → `build_family.py` → `_data/fauna_families.json`

## 验收（防照抄）

```
python _tools/fauna/verify.py <改写稿.json> --src <原文批次.json>
```

PASS 需同时满足：与原文连续相同片段 < 30 字符、8-gram containment < 0.25、条数与页面齐全无重复。
术语串（"前胸背板前缘中央"、拉丁学名、"xx科xx属"）属正常沿用，不必替换。

## 渲染

- `_includes/fauna-species.html`：h2 = 文献出处（《中国动物志》记载）→ h3 = 内容类别（形态描述 / 生物学 / 分布与产地）→ h4 = 品级（兵蚁 / 有翅成虫 / 工蚁 / 若虫）。原书不是专著级别的「形态描述」，出处必须站在最上层，内容类别不能借用它的名字。
- `_includes/fauna-genus.html` / `fauna-family.html`：与物种页同层级——h2 = 文献出处（《中国动物志》记载）→ h3 = 内容类别（形态描述 / 生物学与经济意义 / 分布）→ h4 = 鉴别要点与品级（兵蚁 / 有翅成虫 / 工蚁）。属征/科征不是栏目标题，只能作为「形态描述」下的一个 h4。
- `_layouts/species.html`：以 `site.data.fauna_species[page.url]` 取数据。
- `genus/*.md`、`family/*.md` 由 `.github/workflows/build_taxonomy_pages.py` 生成，生成器内已内置同等 include 块，
  手改生成器后重跑即可；现有页面已直接插入对应 Liquid 块。

## 分批改写要点

- 一批只能有**一个写者**：多个代理同写一个文件会互相追加，产出重复条目。
- 原书量度表在 docx 中被追加到文末，顺序已丢失，正文只保留散文里的量度。
- 图注（"图 268""仿王治国等""1.头及前胸背板背面"）与检索表行一律丢弃。

## 现状与已知问题

### 覆盖

| 层级 | 入站页数 | 说明 |
| --- | --- | --- |
| 物种 | 435 | 原书 454 条物种条目 → 432 条匹配 + 6 条按异名补做；1 页（`/species/hypotermes-mengdingensis/`）原书只有图注、全字段为空，未写入 |
| 属 | 35 | 原书记述 42 属，其中 7 属站内无对应页（蔡白蚁属、壤白蚁属、华白蚁属、马扭白蚁属、歧颚白蚁属、近瓢白蚁属、奇象白蚁属） |
| 科 | 4 | 草白蚁科（今原白蚁科 Hodotermopsidae）、木白蚁科、鼻白蚁科、白蚁科 |

字段覆盖（物种级）：分布与产地 435、英文摘要 435、兵蚁 384、有翅成虫 137、分类说明 104、生物学 101、工蚁 55。
其中 **33 页没有任何品级形态正文**——原书该种只剩图注或量度表，改写稿如实留空，
`_includes/fauna-species.html` 已加守卫（soldier/alate/worker/nymph 全空则整个形态分节不渲染）。

### 原书未能覆盖的 16 条物种

站内没有对应页面，故未改写：恒春新白蚁 `Neotermes koskunensis`、长泰/匙颏/贵州/斜孔/赭黄/苏州/崖县乳白蚁（`Coptotermes` 7 种）、峨嵋/细须/双色散白蚁（`Reticulitermes` 3 种）、`Macrotermes latinotus`、`Hospitalitermes luzonensis`、`Peribulbitermes jinghongensis`。

另有 2 条（`Pseudocapritermes largus`、`Xiaitermes tiantaiensis`）站内页面已按各自的现行学名写过形态描述，
原书这两条是**异名下的独立条目**，为避免两种描述混入同一页面，未合并；如需保留，可另建异名页或写进对应页的异名注。

### 原书文本质量问题（改写时已逐一处理）

- **OCR 断词**：属名被拆成 "Coptoter mes"、"Reticuliter mes"、"Pseudo capritermes"、"Macrorermes"、"Ahmeditermes" 等。
- **串条**：相邻种/属征/检索表被并入同一条目录（约 20 处，如 #69、#89、#366、#395），改写时只取本条本体。
- **品级错位**：部分条目把兵蚁正文排进"工蚁"段、成虫排进"兵蚁"段（约 13 处），按内容重新归位。
- **仅有图注**：约 25 条只剩图注与量度表，未编造描述。
- **量度表**：docx 转换把表格追加到文末，行序已丢失，故只采信散文中出现的量度。

### 出处与合规

页面上每条描述都标注"据原书第 N 号条目重新整理改写"，并在 `fauna-cite` 中给出原书完整署名；
改写稿与原文的 8-gram 重合率按批控制在 0.05–0.19（阈值 0.25），无 ≥30 字连续相同片段。
原书全文仅存在于 `_tmp/dz/`（已被 `.gitignore` 忽略），不入仓、不上站。

## 检索表（目前仅 3 页）

2025-11 起，据《中国动物志》编制的目级 / 属级 / 种级检索表**全部撤下**。`_data/fauna_keys.json` 只保留三页：

- `/list/`：Hellemans 等（2024）电子补充材料 **Note 2** 的目级表，分有翅成虫与兵蚁两套。
- `/family/termitidae/`：Hellemans 等（2024）**Note 3** 的白蚁科亚科表（17 组、18 个终点）。
- `/family/kalotermitidae/`：Krishna 等（2013）的木白蚁科世界分属表（有翅成虫 18 组、兵蚁 20 组）。

渲染在 `_includes/fauna-keys.html`（样式在 `assets/custom.css` 的 `.fauna-keys` 段）。
`.github/workflows/build_taxonomy_pages.py` 的 `KEYS_PAGES` 是页面白名单：不在这三页的科 / 亚科 / 属页不再输出检索表 include，
避免 300 多个页面各留一个空块。`_tools/fauna/keys/emit.py` 另有一道数据层过滤：`src_short` 含「黄复生」的表一律丢弃，
所以即使原书 docx 抽取链重跑，书表也不会回到 `_data/fauna_keys.json`。

原书抽取链（`extract.py` → `kp.py` → `res.py` → `emit.py` → `qa.py` / `validate.py`）保留为历史工具：
它依赖 `.tmp/keys/raw.txt`（已 gitignore），没有该文件时不能重跑。书表的剪枝、归并、OCR 修复等规则不再维护；
当前唯一需要维护的是上列三张非书表。

### 文本政策（仍适用）

检索表正文**只做机械清洗，不做改写**：去图号与 leader dots、修 OCR 错字、拆开书页串行、把终端名从正文里切走
（终端名一律取站点数据，因此始终带链接、用本站现行名）。检索表按引文处理，`verify.py` 的
「最长公共子串 < 30、8-gram containment < 0.25」规则**不适用**。每张表各自标来源：数据里每个 key 带
`src_short`（角标短名）与 `source`（完整出处），页面上 summary 行显示短名、页脚拼出完整署名。

## 属级形态描述的文献线索

- `_tools/fauna/morphology/extract_genus_sources.py` 从 `_unpublished/文库/treatise-on-the-isoptera/_full.txt`
  抽取 326 个属的原始描述出处、模式种，以及 Treatise 标注为含 characters / key / diagnosis 的参考文献，
  写入 `_data/genus_sources.json`（键为 `/genus/<slug>/`）。
- **Treatise 不是描述正文**：它只登记原始发表信息、模式种和文献线索。不要把它的文献注记改写成形态描述。
- `_tools/fauna/morphology/descriptions/*.json` 是人工核对后写成的中文属级描述，按页面 URL 归档；
  `build_krishna_descriptions.py` 合并为 `_data/morphology_genera.json`，每条含分品级正文与来源 id、locator。
  单条来源可写成 `source: {id, citation, locator}`，多条写成 `sources: [{...}]`；两种都受支持。
- `_includes/genus-morphology.html` 的三层逻辑：`_data/fauna_genera.json` 已有《中国动物志》描述 → 不重复；
  否则 `_data/morphology_genera.json` 有改写稿 → 渲染描述与来源；两者都没有 → 占位，显示原始描述出处与模式种。
- 物种 / 亚种页由 `_layouts/species.html` 统一挂 `_includes/species-morphology.html`，数据在
  `_data/morphology_species.json`（键为 `/species/<slug>/`）。已有《中国动物志》记载的 435 个种/亚种不重复；
  其余先显示三语待补说明并链接属页。单型属可据属级描述生成种级条目，但须在 `note` 写明是属级描述。
- `_tools/fauna/morphology/build_worklist.py` 生成 `_reports/genus-morphology-worklist.md` 与 `.csv`：
  截至 2026-11-07：326 属中 35 属已有《中国动物志》描述、122 属已补文献描述、169 属待补，其中 19 属在 Treatise 中没有独立条目；
  `build_species_worklist.py` 生成 `_reports/species-morphology-worklist.{md,csv}`。
- 补写顺序：先取原始发表或属级修订，核对模式种与品级，再据原文改写；每篇用到的文献按 `AGENTS.md` 存档。
  不要把属级描述直接冒充种级描述（单型属例外，且须注明）。

### 原书表的历史残缺（书表已撤下，仅留档）

- 乳白蚁属兵蚁第 3 组：原书两种挤在一行，已按终端拆开；单毛乳白蚁站内无页被剔除后，该组只剩单枝。
- 杆白蚁属第 23 组：书页页码混进正文（`s.orthognathus … 125. 前胸背板宽0.90—1.35 26 …`）。
- 瘤白蚁亚科某组出现三条 lead：书页把下一组的一条并入。

