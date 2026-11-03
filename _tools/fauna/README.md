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

- `_includes/fauna-species.html` / `fauna-genus.html` / `fauna-family.html`：按分节渲染已改写的形态描述。
- `_layouts/species.html`：以 `site.data.fauna_species[page.url]` 取数据。
- `genus/*.md`、`family/*.md` 由 `.github/workflows/build_taxonomy_pages.py` 生成，生成器内已内置同等 include 块，
  手改生成器后重跑即可；现有页面已直接插入对应 Liquid 块。

## 分批改写要点

- 一批只能有**一个写者**：多个代理同写一个文件会互相追加，产出重复条目。
- 原书量度表在 docx 中被追加到文末，顺序已丢失，正文只保留散文里的量度。
- 图注（"图 268""仿王治国等""1.头及前胸背板背面"）与检索表行一律丢弃。
