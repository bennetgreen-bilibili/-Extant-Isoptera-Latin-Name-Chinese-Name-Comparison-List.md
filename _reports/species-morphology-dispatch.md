# 种级 / 属级形态补全：派单

> 生成日期：2026-11-20。逐条明细见 `_reports/species-morphology-dispatch.csv`（1325 行 = 45 属 + 1280 种/亚种），
> 本文件只写批次口径与作业方法，具体到每个学名的目标文献、BSF 入口、渠道都在 CSV 里。

## 0 现状与口径

站点现有 3089 个种/亚种页，其中 **1809 个有形态描述**（《中国动物志》435 + 补充描述 1374），覆盖率 58.6%；
326 个属页中 **281 个有属级描述**，缺 45 个。本派单覆盖剩余 **1280 个种/亚种** 与 **45 个属**。

「补上」的判定标准（沿用 B/C 两轮的口径）：

1. 条目至少含 1 个品级小节（鉴别要点 / 兵蚁 / 工蚁 / 有翅成虫 / 若虫 / 其他），小节内有可核对的性状或量度；
2. `sources` 至少 1 条 S 记录，`locator` 写到条目或页码；
3. `note` 写明改写依据与 OCR 残缺；
4. 只有属级描述（如 *Prohamitermes*）不冒充种级；名录行、检索表、图注、比较句、食性表都不算描述。

## 1 总表

| 批次 | 内容 | 条数 | 优先级 | 入口 | 预计工时 |
|---|---|---:|---|---|---|
| G1–G9 | 属级缺描述 | 45 | P0 | 见 §2 | 10–14 人日 |
| S1 | OA 直取 | 192 | P1 | 见 §3 | 35–45 人日 |
| S2 | 有 DOI、需馆际/作者索取 | 141 | P3 | 见 §3 | 20–25 人日 |
| S3 | 有论文题录但无 DOI | 11 | P4 | 见 §3 | 4–5 人日 |
| S4 | pre-1900 原始描述 | 43 | P2 | 见 §3 | 12–15 人日 |
| S5 | 1900–1929 原始描述 | 361 | P2 | 见 §3 | 70–85 人日 |
| S6 | 1930–1989 期刊 | 397 | P4 | 见 §3 | 65–80 人日 |
| S7 | 1990 年后新种 | 135 | P4 | 见 §3 | 20–25 人日 |
| **合计** | | **1325** | | | **约 230–290 人日** |

工时按「1 条 = 读原文 + 写中文 JSON + 补 en/es 译文 + 登记来源」约 1 小时估；属级 1 属 2–4 小时。

建议波次：

- **第 1 波（2–3 周）**：G1/G2/G3/G7/G8/G9（36 属）+ S1（192 种 OA）——一次性补齐这些整属页面，并把免费能拿的种先拿下；
- **第 2 波（4–6 周）**：S4 + S5（404 个 1930 年前老种），BHL/archive 免费，按刊卷批量推进；
- **第 3 波**：S2 + S3（152 种），走馆际与作者索取；
- **第 4 波**：S6 + S7（532 种），旧刊馆际与近二十年新种。

## 2 属级：45 属（G1–G9）

属级描述一次覆盖一个属页，性价比最高；同一篇文献常含多属，按「文献」而非「属」派单。

| 批次 | 文献 | 属数 | 渠道 |
|---|---|---:|---|
| G1 | Miller 1991, *Invertebrate Taxonomy* 4(6):1147–1282 | 5 | 出版社单篇/馆际；先查 BHL 是否收该刊 |
| G2 | Coaton 1971（五属同篇，pp. 1–29 连号） | 5 | 按题录找刊卷；BHL/archive 可能收，否则馆际 |
| G3 | Sjöstedt 1924（四属同篇，p. 257/497） | 4 | BHL/archive 查卷期；文库有 Arkiv för Zoologi 1920 卷可参照 |
| G4 | Noirot 1966, *Insectes Sociaux* 13:329–345；Grassé & Noirot 1955: 380–381 | 3 | Springer 付费墙：馆际/作者索取 |
| G5 | Sands 1995, *J. Nat. Hist.*；Sands & Lamb 1975 | 3 | Taylor & Francis/Wiley 付费墙：馆际/作者索取 |
| G6 | Ahmad 1968；Ahmad 1976 | 3 | 馆际为主；先核 BSF 属页是否给全文链接 |
| G7 | Silvestri 1914, *Boll. Lab. Zool. Portici* 9:1–146 | 2 | BHL/archive（意大利旧刊数字化较好） |
| G8 | 单篇/专著 14 属（见下） | 14 | 逐条按题录取；Sociobiology、AMNH Novitates 多为 OA |
| G9 | 题录缺失 6 属（见下） | 6 | 先补题录再取全文 |

### 2.1 逐属

| 批次 | 属 | 中文名 | 科 | 目标文献（含页码） | 入口 |
|---|---|---|---|---|---|
| G1 | *Apsenterotermes* | 后肠白蚁属 | 白蚁科 | Miller 1991, Invertebrate Taxonomy 4(6):1147–1282（1169–1170） | 整卷单篇：出版社单篇购买/馆际；先查 BHL 是否收 Invertebrate Taxonomy |
| G1 | *Cristatitermes* | 脊突白蚁属 | 白蚁科 | Miller 1991, Invertebrate Taxonomy 4(6):1147–1282（1192–1196） | 整卷单篇：出版社单篇购买/馆际；先查 BHL 是否收 Invertebrate Taxonomy |
| G1 | *Hapsidotermes* | 络白蚁属 | 白蚁科 | Miller 1991, Invertebrate Taxonomy 4(6):1147–1282（1242–1244） | 整卷单篇：出版社单篇购买/馆际；先查 BHL 是否收 Invertebrate Taxonomy |
| G1 | *Saxatilitermes* | 石白蚁属 | 白蚁科 | Miller 1991, Invertebrate Taxonomy 4(6):1147–1282（1240） | 整卷单篇：出版社单篇购买/馆际；先查 BHL 是否收 Invertebrate Taxonomy |
| G1 | *Xylochomitermes* | 木堆白蚁属 | 白蚁科 | Miller 1991, Invertebrate Taxonomy 4(6):1147–1282（1157–1160） | 整卷单篇：出版社单篇购买/馆际；先查 BHL 是否收 Invertebrate Taxonomy |
| G2 | *Okavangotermes* | 奥卡万戈白蚁属 | 白蚁科 | Coaton 1971（五属，同一篇，pp. 1–29 连号）（19–21） | 按题录找刊卷（南非常见期刊，BHL/archive 可能收）；否则馆际 |
| G2 | *Ovambotermes* | 奥万博兰白蚁属 | 白蚁科 | Coaton 1971（五属，同一篇，pp. 1–29 连号）（10–12） | 按题录找刊卷（南非常见期刊，BHL/archive 可能收）；否则馆际 |
| G2 | *Skatitermes* | 洁白蚁属 | 白蚁科 | Coaton 1971（五属，同一篇，pp. 1–29 连号）（2–5） | 按题录找刊卷（南非常见期刊，BHL/archive 可能收）；否则馆际 |
| G2 | *Spatulitermes* | 匙白蚁属 | 白蚁科 | Coaton 1971（五属，同一篇，pp. 1–29 连号）（28–29） | 按题录找刊卷（南非常见期刊，BHL/archive 可能收）；否则馆际 |
| G2 | *Unicornitermes* | 独角白蚁属 | 白蚁科 | Coaton 1971（五属，同一篇，pp. 1–29 连号）（23） | 按题录找刊卷（南非常见期刊，BHL/archive 可能收）；否则馆际 |
| G3 | *Lepidotermes* | 鳞白蚁属 | 白蚁科 | Sjöstedt 1924（四属，同一篇）（497） | BHL/archive 查 Sjöstedt 1924 卷期；文库已有 Arkiv för Zoologi 1920 卷可作版式参照 |
| G3 | *Noditermes* | 节白蚁属 | 白蚁科 | Sjöstedt 1924（四属，同一篇）（257） | BHL/archive 查 Sjöstedt 1924 卷期；文库已有 Arkiv för Zoologi 1920 卷可作版式参照 |
| G3 | *Trichotermes* | 发白蚁属 | 白蚁科 | Sjöstedt 1924（四属，同一篇）（257） | BHL/archive 查 Sjöstedt 1924 卷期；文库已有 Arkiv för Zoologi 1920 卷可作版式参照 |
| G3 | *Unguitermes* | 爪白蚁属 | 白蚁科 | Sjöstedt 1924（四属，同一篇）（257） | BHL/archive 查 Sjöstedt 1924 卷期；文库已有 Arkiv för Zoologi 1920 卷可作版式参照 |
| G4 | *Coxotermes* | 基白蚁属 | 白蚁科 | Noirot 1966, Insectes Sociaux 13:329–345；Coxotermes 见 Grassé & Noirot 1955: 380–381（380–381） | Springer 付费墙：馆际/作者索取；先查这两属是否已被后续修订再描述 |
| G4 | *Eburnitermes* | 象牙白蚁属 | 白蚁科 | Noirot 1966, Insectes Sociaux 13:329–345；Coxotermes 见 Grassé & Noirot 1955: 380–381（336–337） | Springer 付费墙：馆际/作者索取；先查这两属是否已被后续修订再描述 |
| G4 | *Pseudhamitermes* | 伪钩白蚁属 | 白蚁科 | Noirot 1966, Insectes Sociaux 13:329–345；Coxotermes 见 Grassé & Noirot 1955: 380–381（329–330） | Springer 付费墙：馆际/作者索取；先查这两属是否已被后续修订再描述 |
| G5 | *Enetotermes* | 针筒白蚁属 | 白蚁科 | Sands 1995, J. Nat. Hist.（Enetotermes 1508、Trapellitermes 1493–1494）；Sands & Lamb 1975（Kaudernitermes 190–191）（1995: 1508） | Taylor & Francis / Wiley 付费墙：馆际/作者索取 |
| G5 | *Kaudernitermes* | 考登白蚁属 | 白蚁科 | Sands 1995, J. Nat. Hist.（Enetotermes 1508、Trapellitermes 1493–1494）；Sands & Lamb 1975（Kaudernitermes 190–191）（1975: 190–191） | Taylor & Francis / Wiley 付费墙：馆际/作者索取 |
| G5 | *Trapellitermes* | 菱角白蚁属 | 白蚁科 | Sands 1995, J. Nat. Hist.（Enetotermes 1508、Trapellitermes 1493–1494）；Sands & Lamb 1975（Kaudernitermes 190–191）（1995: 1493–1494） | Taylor & Francis / Wiley 付费墙：馆际/作者索取 |
| G6 | *Malaysiotermes* | 马来白蚁属 | 白蚁科 | Ahmad 1968（Malaysiotermes 6、Subulioiditermes 1–2）；Ahmad 1976（Orientotermes 111–112）（1968: 6） | 马来亚大学/巴基斯坦动物学刊，馆际为主；先核 BSF 是否给出全文链接 |
| G6 | *Orientotermes* | 东方白蚁属 | 白蚁科 | Ahmad 1968（Malaysiotermes 6、Subulioiditermes 1–2）；Ahmad 1976（Orientotermes 111–112）（1976: 111–112） | 马来亚大学/巴基斯坦动物学刊，馆际为主；先核 BSF 是否给出全文链接 |
| G6 | *Subulioiditermes* | 似锥白蚁属 | 白蚁科 | Ahmad 1968（Malaysiotermes 6、Subulioiditermes 1–2）；Ahmad 1976（Orientotermes 111–112）（1968: 1–2） | 马来亚大学/巴基斯坦动物学刊，馆际为主；先核 BSF 是否给出全文链接 |
| G7 | *Megagnathotermes* | 大颚白蚁属 | 白蚁科 | Silvestri 1914, Bollettino Lab. Zool. Portici 9:1–146（Megagnathotermes 80–81、Orthotermes 123–124）（80–81） | BHL/archive 查 Portici 学报；意大利旧刊数字化程度较高 |
| G7 | *Orthotermes* | 直白蚁属 | 白蚁科 | Silvestri 1914, Bollettino Lab. Zool. Portici 9:1–146（Megagnathotermes 80–81、Orthotermes 123–124）（123–124） | BHL/archive 查 Portici 学报；意大利旧刊数字化程度较高 |
| G8 | *Antillitermes* | 安的列斯白蚁属 | 白蚁科 | Roisin, Scheffrahn & Křeček 1996, Ann. Entomol. Soc. Am. 89(6):775–787（属 783） | 馆际；ESA 付费墙 |
| G8 | *Batillitermes* | 铲白蚁属 | 白蚁科 | Uys 1994b: 53–54 | 按题录找刊卷 |
| G8 | *Divinotermes* | 迪维努白蚁属 | 白蚁科 | Carrijo & Cancello 2011, Sociobiology 58:539–549 | Sociobiology 多为 OA，先查 |
| G8 | *Ekphysotermes* | 瘤突白蚁属 | 白蚁科 | Gay 1971a: 24–25 | 按题录找刊卷 |
| G8 | *Incolitermes* | 子民白蚁属 | 白蚁科 | Gay 1966: 41 | 按题录找刊卷 |
| G8 | *Invasitermes* | 闯白蚁属 | 白蚁科 | Miller 1984a: 33 | 按题录找刊卷 |
| G8 | *Labidotermes* | 钳白蚁属 | 白蚁科 | Deligne & Pasteels 1969: 147–148 | 按题录找刊卷 |
| G8 | *Machadotermes* | 剑白蚁属 | 白蚁科 | Weidner 1974: 29 | 按题录找刊卷 |
| G8 | *Megaprotermes* | 大前白蚁属 | 白蚁科 | Ruelle 1978b: 17 | 按题录找刊卷 |
| G8 | *Nasopilotermes* | 棘象白蚁属 | 白蚁科 | Gao et al. 1992a: 19（Pilotermes 的 nom. nov.）；形态见《中国动物志》卷十七 547、791–792 | 优先查文库《中国动物志》 |
| G8 | *Onkotermes* | 倒钩白蚁属 | 白蚁科 | Constantino, Liotta & Giacosa 2002, Sociobiology 39:454–456 | Sociobiology 多为 OA，先查 |
| G8 | *Phoxotermes* | 锐白蚁属 | 白蚁科 | Collins 1977a: 95–96 | 按题录找刊卷 |
| G8 | *Rostrotermes* | 突吻白蚁属 | 白蚁科 | Grassé 1943: 71–78 | 旧刊，BHL/archive 优先 |
| G8 | *Sabahitermes* | 沙巴白蚁属 | 白蚁科 | Thapa 1997: 294–298 | 按题录找刊卷 |
| G9 | *Apolemotermes* | 和平白蚁属 | 白蚁科 | Romero Arias et al. 2021, Systematic Entomology 46:741–756 | 先核该文是否含形态（分子系统学为主），不含则查原始属页 |
| G9 | *Dissimulitermes* | 隐藏白蚁属 | 白蚁科 | Constantini et al. 2020, Insect Systematics & Evolution 52:412–427 | 馆际/作者索取；此前已确认有 OA 但仓储不可达 |
| G9 | *Koutabatermes* | 库塔巴白蚁属 | 白蚁科 | Romero Arias et al. 2021, Systematic Entomology 46:741–756 | 同 Apolemotermes |
| G9 | *Longicaputermes* | 头长白蚁属 | 木白蚁科 | Ghesini, Simon & Marini 2014, Insectes Sociaux 61:123–131 | Springer 付费墙；馆际/作者索取 |
| G9 | *Microhodotermes* | 小草白蚁属 | 草白蚁科 | Sands 1998, The Identification of Worker Castes of Termite Genera … (book) | 馆际；书内含非洲属检索与属征 |
| G9 | *Palmitermes* | 棕榈白蚁属 | 白蚁科 | Hellemans et al. 2017, Invertebrate Systematics 31:394–405 | 出版社/馆际 |

### 2.2 G9：题录缺失的 6 属

这 6 属连「哪篇文献建立」都不确定，先补题录，不要直接写描述：

1. *Apolemotermes*、*Koutabatermes*：Romero Arias et al. 2021（*Systematic Entomology* 46:741–756）——先核该文是否含形态，分子系统学为主则另找原始属页；
2. *Dissimulitermes*：Constantini et al. 2020（*Insect Systematics & Evolution* 52:412–427），此前查到有 OA 但仓储不可达；
3. *Longicaputermes*：Ghesini et al. 2014（*Insectes Sociaux* 61:123–131）；
4. *Microhodotermes*：Sands 1998《The Identification of Worker Castes of Termite Genera…》书内含非洲属检索；
5. *Palmitermes*：Hellemans et al. 2017（*Invertebrate Systematics* 31:394–405）。

## 3 种级：1280 种/亚种（S1–S7）

CSV 每行给出：拉丁名、中文名、科、属、命名人年代、模式产地、页面 URL、BSF 入口、目标文献（含 DOI/OA 链接）、获取渠道。

注意：`目标文献` 是按「属名 + 种加词」在 `_data/papers/genera/` 里匹配出来的，可能是原始描述、修订再描述，也可能是同名误配；
拿到全文后必须先核对是否真含该种（标题双名 + 命名人 + 模式产地），再决定写或不写。

### S1 OA 直取（192 条，P1）

192 条命中论文带 OA 链接，可直接下载：ZooKeys、EJT、JOTT、Plazi treatments、Sociobiology、AMNH Novitates 等。

科分布：白蚁科 150、木白蚁科 19、异白蚁科 8、鼻白蚁科 6；年代：1900–1929 65、2010+ 50、1950–1989 31、1990–2009 25、pre-1900 15、1930–1949 6。

执行：先 `_tools/fetch_fulltext.py --queue` 小批（20 条/次）跑，命中即入库；未命中转 S2 的馆际清单。

### S2 有 DOI、需馆际/作者索取（141 条，P3）

有 DOI 题录但 OpenAlex 未给 OA 链接；多为 Zootaxa、Systematic Entomology、Insectes Sociaux、J. Nat. Hist.。

科分布：白蚁科 109、木白蚁科 26、鼻白蚁科 2、草白蚁科 1；年代：1950–1989 38、1990–2009 37、1900–1929 33、1930–1949 13、2010+ 10、pre-1900 10。

执行：导出 DOI 清单交馆际；同时按作者单位发索取邮件（模板见 §5）。

### S3 有论文题录但无 DOI（11 条，P4）

OpenAlex 记录缺 DOI（旧刊、会议集、地方学报）。

科分布：白蚁科 10、沙白蚁科 1；年代：1990–2009 4、1900–1929 3、2010+ 2、pre-1900 1、1950–1989 1。

执行：Crossref `query.bibliographic` 逐条补 DOI；补不到转 S6。

### S4 pre-1900 原始描述（43 条，P2）

43 条中的 110 条无任何库内外论文题录，需从 BSF 页的原始描述题录定位到 19 世纪刊卷。

科分布：白蚁科 26、木白蚁科 10、异白蚁科 5、鼻白蚁科 1；年代：pre-1900 43。

执行：BHL/archive.org/Gallica 按刊名+卷期取全文；旧组合按 BSF 的 original combination 检索。

### S5 1900–1929 原始描述（361 条，P2）

361 条；这是数量最大、也最可能一次拿到的一批（BHL 对 1900–1929 的覆盖最好）。

科分布：白蚁科 274、木白蚁科 61、异白蚁科 8、鼻白蚁科 7；年代：1900–1929 361。

执行：按 BSF 题录的刊名/卷期在 BHL 批量取；同卷多属可一次处理。

### S6 1930–1989 期刊（397 条，P4）

397 条；BHL 覆盖下降，需馆际或出版社旧档。

科分布：白蚁科 291、木白蚁科 70、异白蚁科 27、鼻白蚁科 4；年代：1950–1989 263、1930–1949 134。

执行：先查 BHL 是否收该卷；否则馆际；同刊多篇合并申请。

### S7 1990 年后新种（135 条，P4）

135 条；多为 Zootaxa / 地方刊的新种描述，线上有 DOI 但常付费。

科分布：白蚁科 95、木白蚁科 22、异白蚁科 10、草白蚁科 4；年代：1990–2009 91、2010+ 44。

执行：Crossref/DOI 定位 → 出版社/作者索取；OA 刊直接取。

## 4 单条作业流程

1. **定位**：打开 CSV 里的 BSF 链接（`cockroach.speciesfile.org/otus/<id>/overview`），抄下 original description 的完整题录（作者、年份、刊名、卷期、页码）；若 CSV 已给目标文献，以原文为准复核。
2. **取全文**：按批次渠道取；拿到后先确认卷期页码与题录一致，再引用。
3. **抽段**：找 IMAGO / SOLDIER / WORKER / NYMPH 小标题下的种级段落；量度照录（`0.85–0.95` 原样，不要四舍五入）。
4. **判归属**：标题含该种双名且命名人匹配；旧组合（如 *Termes koenigi*）按 BSF 的 original combination 认；只有属征、他种、名录行、检索表、图注、比较句的一律判「无描述」。
5. **写 JSON**：`_data/morphology_species/<genus_id>/<slug>.json`，结构：

```json
{"zh_name":"中文正名","sections":[{"label":"鉴别要点","text":"…"},{"label":"兵蚁","text":"…"}],
 "note":"据 Xxx (年) 种级描述改写，原文英文；量度为原文照录；OCR 残缺处已注明。",
 "sources":[{"id":"S0xxx","citation":"作者. 年份. 标题. 刊名.","locator":"条目（<book-slug>）/ p. 123"}]}
```

6. **登记来源**：`_tmp/sources-task.json` 写逐字摘录 + locator + `used_in`（指向新 JSON），`python _tools/sources.py add --json _tmp/sources-task.json`；全文按 `library-add` 入文库。
7. **补译文**：`_data/translations_en|es/morphology_species/<同路径>.json`，结构 `{"note","sections"}`，标签映射 en `Diagnostic characters / Alate / Soldier / Worker / Nymph / Other`，es `Caracteres diagnósticos / Alado / Soldado / Obrero / Ninfa / Otros`；数字与量度逐字一致。
8. **校验**：见 §5。

## 5 验收、登记与命令

```bash
python _tools/sources.py check --strict
python _tools/check_translations.py --ci --files morphology_species
python _tools/fauna/morphology/build_species_worklist.py     # 刷新待补计数
bash _tools/regen_all.sh
python _tools/check_site.py --ci
python _tools/check_liquid.py
```

验收标准：CSV 对应行的 `当前状态` 由「待补」变为「已有补充描述」；`_reports/species-morphology-worklist.csv` 的待补数下降；三语条目数一致。

馆际/作者索取邮件模板（英文，可直接用）：

```text
Subject: Request for a PDF of <citation>

Dear <author>,

I am compiling a taxonomic reference list of extant termites and would like to
check the morphological description of <Genus species> in your publication:
<full citation with DOI>. If you can share a PDF, it would help ensure the
diagnosis and measurements on our species page are accurate. We will cite the
original work and link to its DOI.

Thank you very much.
```

## 6 已知陷阱

- **OCR 变体**：f/t、rn/m、连写（`tletcheri` = *fletcheri*）、种名与命名人粘连——检索时用种加词级模糊匹配，不要只搜全名。
- **旧组合**：描述可能挂在旧属名下（*Termes koenigi*、*Mirotermes (Ophiotermes) grandilabius*）；BSF 页的 original combination 是唯一可靠入口。
- **同名异属误配**：`odontotermes-fulleri` 命中的其实是作者名 Fulleri；标题里的双名必须与属名同现或命名人匹配。
- **上游书错配**：`rugitermes-tinto` 的上游条目指向 ZooKeys 1057，但该文只有名录行，真正的描述在 ZooKeys 963（S0497）——拿到全文先核对，不要照抄上游给的出处。
- **亚种同文**：*Pericapritermes urgens* 与 *P. urgens urgens* 原文同段，两条都保留但 note 要说明差异。
- **付费墙红线**：只用出版社、机构库、作者提供的合法副本；不绕过访问控制。拿不到就在处置表写「access: blocked」，不要编造页码。

## 7 复现

```bash
python _tmp/make_dispatch.py      # 由 worklist + papers + BSF + 处置表重算派单 CSV
python _tmp/make_dispatch_md.py   # 由 CSV 汇总本文件
```

数据来源：`_reports/species-morphology-worklist.csv`（1280 待补）、`_reports/species-morphology-bd-disposition.csv`（608 行 B/C 处置）、
`_data/papers/genera/*.json`（326 属论文题录）、`_data/bsf_links/name_map/*.json`（3089 种 BSF 入口）、`_reports/genus-morphology-gaps.csv`（45 属）。
