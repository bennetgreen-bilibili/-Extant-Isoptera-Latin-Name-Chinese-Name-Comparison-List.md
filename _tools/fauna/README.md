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

