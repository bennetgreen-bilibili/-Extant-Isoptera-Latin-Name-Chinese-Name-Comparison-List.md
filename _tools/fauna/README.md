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

## 检索表（目级 / 属级 / 种级）

数据在 `_data/fauna_keys.json`，按页面 URL 分组；渲染在 `_includes/fauna-keys.html`（样式在 `assets/custom.css` 的 `.fauna-keys` 段）。

```
原书 docx（站外）
  └─ _tools/fauna/keys/extract.py → .tmp/keys/raw.txt   遍历 word/document.xml（含 w:sdt 内容控件与表格；python-docx 会漏掉 sdt 里的检索表）
      └─ kp.py                    → 切出 40 个「××检索表」块，解析成二分式 couplet（编号 / 指引号 / 终端）
          └─ res.py               → 站点词表（属、种、亚科、科）与书属→站属归并表
              └─ emit.py          → _data/fauna_keys.json（剪枝 + 重新编号）
                  └─ qa.py / validate.py   结构自检（编号 1..N 连续、无悬空指引、终端 URL 全部存在）
```

手工撰写（非原书）：`_tools/fauna/keys/keys_orders.py` 存 `ORDER_OVR`（目级 13 科，据 Hellemans 等 2024 Note 2 译写）、
`NEOTERMES_OVR`（新白蚁属，据原书逐条复原）、`FAMNOTE` / `NEONOTE` 两个说明页注，以及各表的来源常量
（`ORDSRC` / `SFSRC` / `BOOKSRC`、`HELSHORT` / `BOOKSHORT`）。`emit.py` 从这里导入，不重复书写表体。

- 环境变量：`FZ_KEYS_DOCX`（原书 docx 目录）、`FZ_KEYS_RAW`（抽取文本落盘位置，默认 `.tmp/keys/raw.txt`）。
- 放置：**属级「分属检索表」→ 该属所在科/亚科页；种级「分种检索表」→ 该属自己的属页（`/genus/<slug>/`）**；等翅目目级检索表 → `/list/`。
  种级表不再挂在科页/亚科页；原书属名经归并后落到站内属页的（如蔡白蚁属→散白蚁属页），表题仍用原书属名，并以 `note` 说明归并。
- 剪枝规则：每个终端必须能在站点解析到具体页面（species → `_species/<slug>.md`；genus / family / subfamily → 对应目录下的 md）。
  解析不到的终端（原书记载、本站未列为独立种）从检索表里删除，同时记入该 key 的 `dropped`，页面上以「已剔除」列出；
  删枝后按 DFS 遍历重新编号 1..N，只有一个子节点的组上提一级，整枝空掉则整枝删除。
- 新白蚁属 `Neotermes`：原书该页 OCR 把多组 couplet 黏成整段，无法机读；已按原文逐条人工复原为 17 组、18 个终点，
  表体存 `keys_orders.py` 的 `NEOTERMES_OVR`，挂在 `/genus/neotermes/`。原书写 `N. brachyotum`，本站现行名为
  `N. brachynotum`，故用 `NEONOTE` 在表下注明。
- 属级归并：原书属名与本站现行名不同者走 `emit.py` 的 `MAPPING_LAT`（Tsaitermes→Reticulitermes、Havilanditermes/Mironasutitermes→Nasutitermes、
  Peribulbitermes→Ahmaditermes、Parahypotermes→Hypotermes、Sinotermes→Indotermes、Malaysiocapritermes→Procapritermes），
  页面上用 `note` 说明「原书把这一群放在 X，本站现归入 Y」。
- 目级检索表（`/list/`）：译自 Hellemans 等（2024）电子补充材料 **Note 2**「Key to extant families and subfamilies of Isoptera」，
  分有翅成虫（14 组、15 个终点）与兵蚁（15 组、16 个终点）两套，覆盖本站 13 科；原书把 Stolotermitidae 与 Psammotermitidae 分到亚科，
  本站无这四个亚科页，故亚科名写进条文字句、链接落在科页。原书目级的分科/亚科检索表（6 科方案）**已弃用**，
  不再出现在站上。
- 白蚁科亚科索引：译自 Hellemans 等（2024）电子补充材料 **Note 3**（修订自 Krishna 等 2013 的亚科检索表），以工蚁肠道（混合段、马氏管结、P3 盲囊、肠瓣 P2）
  与颚齿（LMt3 前后缘长度、RMt1 副齿）为特征，17 组、18 个终点，链到本站 18 个亚科页。

### 文本政策（与原书改写规则不同）

检索表正文**只做机械清洗，不做改写**：去图号与 leader dots、修 OCR 错字（蚊→蚁、上频/上颗→上颚、后须→后颏、囱→囟、凹人→凹入、
破折号被印成「一」等）、拆开书页串行、把终端名从正文里切走（终端名一律取站点数据，因此始终带链接、用本站现行名）。
因此检索表条目与原文的连续相同片段远超 30 字符，`verify.py` 的「最长公共子串 < 30、8-gram containment < 0.25」规则**不适用**；
这块按引文处理。**每张表各自标来源**：数据里每个 key 带 `src_short`（角标短名）与 `source`（完整出处），
页面上 summary 行显示短名、页脚按内容拼出完整署名——原书表署「黄复生等（2000）」，目级/亚科表署
「Hellemans 等（2024）」并在页脚给出 `Nature Communications 15: 6724` 与 DOI。

### 未转述的检索表

- 原鼻白蚁属 `Prorhinotermes`：正文与终端被拆到相邻书页、中间夹书眉噪声 → 该属页 `omitted` 里说明。
- 夏氏白蚁属 `Xiaitermes`：原表为黟县夏氏白蚁 / 天台夏氏白蚁二分，后者本站未列为独立种，剔除后只剩 1 个终点 → 该属页 `omitted`。

（`omitted` 与检索表同页：种级说明挂属页，不留在科页/亚科页；空页条目在 emit 时丢弃。）

### 已知残缺（不影响编号与链接）

- 乳白蚁属兵蚁第 3 组：原书两种挤在一行，已按终端拆开；单毛乳白蚁站内无页被剔除后，该组只剩单枝。
- 杆白蚁属第 23 组：书页页码混进正文（`s.orthognathus … 125. 前胸背板宽0.90—1.35 26 …`）。
- 瘤白蚁亚科某组出现三条 lead：书页把下一组的一条并入。

