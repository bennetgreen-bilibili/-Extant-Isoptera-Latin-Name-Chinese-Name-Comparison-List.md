# 分类学变动对照表

> 本表由 `_tools/build_taxonomy_crosswalk.py` 生成；不要手改，重跑即可。科级／亚科级条目来自人工核定的文献修订，种级条目来自 `_data/name_issues.json`。
> 数据缓存日期：2026-10-31；科级／亚科级 3 条，种级 8 条。未列入的属级／种级变动仍须回原文核对。

## 怎么用

1. **先查“科级／亚科级变动”**：旧文献里的科名、亚科名不能直接当现行分类，先确认它属于哪一次修订（2022 Teletisoptera、2024 鼻白蚁科拆分、2024 白蚁亚科拆分）。
2. 再查“种级异名／组合对照”：按旧名或现用名找一行；没有命中就查 `_data/name_issues.json` 的 `issues`，仍没有就标「待核」，不要凭记忆改分类位置。
3. 「旧名」指文献里可能遇到的组合；「本站现用」是当前页面接受的名字。两者不同时，正文必须带时间限定（「当时置于…」「本站现置于…」），不能把旧名直接当现行名。
4. 表中「争议／未定」的条目不要写成学界共识；「可记录（待处理）」表示三大库一致、但站内尚未合并，写作时只陈述差异，不要擅自合并页面。
5. 本表只解决**命名／组合与高层级归属对照**，不替代年代、模式产地、分布的原位核对。

## 科级／亚科级变动（优先查）

> 2022–2024 年高层级修订。本站科／亚科页面已按新分类生成；写旧文献先查本节，再查下面的种级表。每行的证据 locator 指向 `.sources` 里的逐字摘录；没有摘要全文的来源已注明。

| 类群 | 旧分类（文献中可能遇到） | 现分类（本站已采用） | 变动 | 证据 |
| --- | --- | --- | --- | --- |
| **Rhinotermitidae（鼻白蚁科）** | Rhinotermitidae sensu lato：Heterotermitinae、Coptotermitinae、Psammotermitinae、Prorhinotermitinae、Rhinotermitinae、Termitogetoninae | Heterotermitidae（异白蚁科）、Psammotermitidae（沙白蚁科）、Termitogetonidae（寡脉白蚁科）、Rhinotermitidae sensu novo（鼻白蚁科，仅 5 属） | 2024 年基于 UCE 的基因组分类把广义鼻白蚁科拆成四个单系支系，均提升为科；Coptotermitinae 归入 Heterotermitinae，Rhinotermitidae 仅保留 Rhinotermitinae 五属。 | `S0008` p. 2 ¶1 / full.txt:15；`S0008` p. 1 摘要 / full.txt:3；`S0008` p. 7 / full.txt:267–269 |
| **Termitinae（白蚁亚科）** | Termitinae sensu lato（旧白蚁亚科，常含 Termes-group 以外的多个类群） | Termitinae sensu novo（仅 Termes-group）+ Amitermitinae、Microcerotermitinae、Mirocapritermitinae、Crepititermitinae、Cylindrotermitinae、Forficulitermitinae、Neocapritermitinae、Protohamitermitinae、Promirotermitinae；Termitidae 共 18 亚科 | 2024 年确认旧白蚁亚科为多系，白蚁科扩展到 18 个亚科；6 个新亚科、3 个恢复亚科，Termitinae 收窄到 Termes-group。 | `S0008` p. 1 摘要 / full.txt:3；`S0008` p. 4 / full.txt:168；`S0008` p. 7 / full.txt:267 |
| **Teletisoptera（早期分化支系）** | Stolotermitidae、Hodotermitidae、Archotermopsidae 三科并列；Archotermopsidae 含 Archotermopsis、Zootermopsis、Hodotermopsis | Teletisoptera = Stolotermitidae + Hodotermitidae + Archotermopsidae；Archotermopsidae 收窄为 Archotermopsis + Zootermopsis；Hodotermopsidae（原白蚁科）stat. nov. 含 Hodotermopsis | 2022 年 Wang 等以 Teletisoptera 指称三个早期分化科组成的支系，确认其单系性；解决 Archotermopsidae 并系，建立 Hodotermopsidae。 | `S0196` Crossref abstract（Teletisoptera 定义与单系性）；`S0196` Crossref abstract（Archotermopsidae 收窄）；`S0008` p. 12 参考文献 / full.txt:363 |

### 科级／亚科级逐条说明

#### Rhinotermitidae（鼻白蚁科）（科，2024）

- 旧分类：Rhinotermitidae sensu lato：Heterotermitinae、Coptotermitinae、Psammotermitinae、Prorhinotermitinae、Rhinotermitinae、Termitogetoninae
- 现分类：Heterotermitidae（异白蚁科）、Psammotermitidae（沙白蚁科）、Termitogetonidae（寡脉白蚁科）、Rhinotermitidae sensu novo（鼻白蚁科，仅 5 属）
- 变动：2024 年基于 UCE 的基因组分类把广义鼻白蚁科拆成四个单系支系，均提升为科；Coptotermitinae 归入 Heterotermitinae，Rhinotermitidae 仅保留 Rhinotermitinae 五属。 <!-- src:S0008 -->
- 写作口径：旧文献的“鼻白蚁科”若含 Coptotermes / Reticulitermes / Heterotermes，写“当时置于鼻白蚁科（广义），2024 年移至异白蚁科 Heterotermitidae”；Psammotermes / Prorhinotermes 现置沙白蚁科；Termitogeton 现置寡脉白蚁科；只有 Acorhinotermes、Dolichorhinotermes、Parrhinotermes、Rhinotermes、Schedorhinotermes 仍属鼻白蚁科 sensu novo。
- 状态：已发表（2024）；本站 13 科分类已采用四科拆分。
- 注意：这是作者基于分子系统学的修订，不是 ICZN 裁定；旧数据库、旧检索表可能仍用广义鼻白蚁科。
- 证据：
  - `S0008` p. 2 ¶1 / full.txt:15：四支提升为科；Rhinotermitidae 收窄为五属；Coptotermitinae 并入 Heterotermitinae <!-- src:S0008 -->
  - `S0008` p. 1 摘要 / full.txt:3：Heterotermitidae、Psammotermitidae、Termitogetonidae 由亚科提升为科 <!-- src:S0008 -->
  - `S0008` p. 7 / full.txt:267–269：Rhinotermitidae 曾为并系；Coptotermes/Reticulitermes 现归 Heterotermitidae <!-- src:S0008 -->

#### Termitinae（白蚁亚科）（亚科，2024）

- 旧分类：Termitinae sensu lato（旧白蚁亚科，常含 Termes-group 以外的多个类群）
- 现分类：Termitinae sensu novo（仅 Termes-group）+ Amitermitinae、Microcerotermitinae、Mirocapritermitinae、Crepititermitinae、Cylindrotermitinae、Forficulitermitinae、Neocapritermitinae、Protohamitermitinae、Promirotermitinae；Termitidae 共 18 亚科
- 变动：2024 年确认旧白蚁亚科为多系，白蚁科扩展到 18 个亚科；6 个新亚科、3 个恢复亚科，Termitinae 收窄到 Termes-group。 <!-- src:S0008 -->
- 写作口径：旧文献的“白蚁亚科 Termitinae”不能直接当现行亚科；先看属：Termes 等 Termes-group 才留白蚁亚科；Amitermes 等按弓白蚁亚科等新组合写；Coptotermes/Reticulitermes 不是白蚁亚科，而是异白蚁科。Syntermitinae 纳入 Genuotermes，但该亚科诊断不变。
- 状态：已发表（2024）；本站 18 亚科已采用。
- 注意：部分新亚科主要按分子界定，形态鉴别不一定有单一 synapomorphy；作者自己指出部分节点支持度低。
- 证据：
  - `S0008` p. 1 摘要 / full.txt:3：6 个新亚科、3 个恢复亚科；Termitidae 18 亚科 <!-- src:S0008 -->
  - `S0008` p. 4 / full.txt:168：旧 Termitinae 为多系；新亚科与 Termitinae sensu novo <!-- src:S0008 -->
  - `S0008` p. 7 / full.txt:267：Termitinae 多系；新分类把 18 个亚科处理为单系 <!-- src:S0008 -->

#### Teletisoptera（早期分化支系）（支系，2022）

- 旧分类：Stolotermitidae、Hodotermitidae、Archotermopsidae 三科并列；Archotermopsidae 含 Archotermopsis、Zootermopsis、Hodotermopsis
- 现分类：Teletisoptera = Stolotermitidae + Hodotermitidae + Archotermopsidae；Archotermopsidae 收窄为 Archotermopsis + Zootermopsis；Hodotermopsidae（原白蚁科）stat. nov. 含 Hodotermopsis
- 变动：2022 年 Wang 等以 Teletisoptera 指称三个早期分化科组成的支系，确认其单系性；解决 Archotermopsidae 并系，建立 Hodotermopsidae。 <!-- src:S0196 -->
- 写作口径：Teletisoptera 是支系名，不是科/亚科名；写它时注明“2022 年 Wang 等所指的 Stolotermitidae + Hodotermitidae + Archotermopsidae 支系”。Hodotermopsis 旧文献若置于 Archotermopsidae 的 Hodotermopsinae，现置原白蚁科 Hodotermopsidae；中文“原白蚁科”可能指旧 Termopsidae（化石）或新 Hodotermopsidae，必须同时给拉丁名。不要与 Euisoptera/Neoisoptera 混用。
- 状态：已发表（2022）；本站已采用 Hodotermopsidae。S0196 本地全文缺失，只能据 Crossref 摘要；正文标“据摘要”。
- 注意：S0196 的 `.sources` 记录已改为 abstract-no-oa 并移除 `library`；本地没有全文，不能引用正文的种级或分布细节。`_unpublished/文库/10.1111-syen.12548/0001-0023.txt` 不存在，manifest 也没有该 work。
- 证据：
  - `S0196` Crossref abstract（Teletisoptera 定义与单系性）：Teletisoptera = Stolotermitidae + Hodotermitidae + Archotermopsidae；单系性 <!-- src:S0196 -->
  - `S0196` Crossref abstract（Archotermopsidae 收窄）：Archotermopsidae 收窄；Hodotermopsinae 提升为 Hodotermopsidae <!-- src:S0196 -->
  - `S0008` p. 12 参考文献 / full.txt:363：S0008 引用 Wang et al. 2022（Teletisoptera 论文） <!-- src:S0008 -->

## 种级异名／组合对照（次要）

> 这一节只覆盖已进入站内一致性核对的 8 个种级条目；属级变动、未列入的种级变动，仍须回原文和 `name_issues.json` 查。

| 本站现用名 | 文献中可能遇到的旧名 | 变动 | 旧属 → 现属 | 处理口径 | 状态 | 旧名链接 |
| --- | --- | --- | --- | --- | --- | --- |
| Amitermes californicus （加州弓白蚁） | Amitermes wheeleri (Desneux, 1906) | synonym / external | Amitermes → Amitermes | 本站两页并存：写 Amitermes californicus 时注明 GBIF、COL、BSF 将其列为 Amitermes wheeleri 的异名；写 Amitermes wheeleri 时反向注明。不要删页或改学名，除非用户确认。 | 可记录（待处理） | [GBIF](https://www.gbif.org/species/2007289) / [COL](https://www.checklistbank.org/dataset/3LR/taxon/CSVV) / [BSF](https://cockroach.speciesfile.org/otus/85266/overview) |
| Grigiotermes hageni （哈根灰白蚁） | Anoplotermes hageni Emerson & Snyder, 1949 | combination / site | Anoplotermes → Grigiotermes | 本站现用 Grigiotermes hageni；旧文献用 Anoplotermes hageni Emerson & Snyder, 1949 时写「当时置于 Anoplotermes，本站现置于 Grigiotermes」；该组合仍有争议，不要写成学界共识。 | 争议／未定 | [GBIF](https://www.gbif.org/species/9662984) |
| Mapinguaritermes grandidens （大齿红懒白蚁） | Armitermes grandidens Emerson, 1925 | combination / site | Armitermes → Mapinguaritermes | 本站现用 Mapinguaritermes grandidens；旧文献用 Armitermes grandidens Emerson, 1925 时写「当时置于 Armitermes，本站现置于 Mapinguaritermes」；该组合仍有争议，不要写成学界共识。 | 争议／未定 | [GBIF](https://www.gbif.org/species/8816091) |
| Patawatermes nigripunctatus （黑点帕塔瓦白蚁） | Anoplotermes nigripunctatus Emerson, 1925 | combination / site | Anoplotermes → Patawatermes | 本站现用 Patawatermes nigripunctatus；旧文献用 Anoplotermes nigripunctatus Emerson, 1925 时写「当时置于 Anoplotermes，本站现置于 Patawatermes」；该组合仍有争议，不要写成学界共识。 | 争议／未定 | [GBIF](https://www.gbif.org/species/9339653) |
| Rubeotermes jheringi （耶林变红白蚁） | Anoplotermes jheringi Holmgren, 1906 | combination / site | Anoplotermes → Rubeotermes | 本站现用 Rubeotermes jheringi；旧文献用 Anoplotermes jheringi Holmgren, 1906 时写「当时置于 Anoplotermes，本站现置于 Rubeotermes」；该组合仍有争议，不要写成学界共识。 | 争议／未定 | [GBIF](https://www.gbif.org/species/9082997) |
| Ruptitermes franciscoi （弗朗西斯科腹爆白蚁） | Anoplotermes franciscoi Snyder, 1959 | combination / disputed | Anoplotermes → Ruptitermes | 按原文保留旧名，并注明与本站现用名的关系；不确定时标「待核」。 | 待核 | [GBIF](https://www.gbif.org/species/9070348) |
| Silvestritermes minutus （最小西尔韦斯特里白蚁） | Armitermes minutus Emerson, 1925 | combination / site | Armitermes → Silvestritermes | 本站现用 Silvestritermes minutus；旧文献用 Armitermes minutus Emerson, 1925 时写「当时置于 Armitermes，本站现置于 Silvestritermes」；该组合仍有争议，不要写成学界共识。 | 争议／未定 | [GBIF](https://www.gbif.org/species/9801261) |
| Uncitermes teevani （蒂范弯钩白蚁） | Armitermes teevani Emerson, 1925 | combination / site | Armitermes → Uncitermes | 本站现用 Uncitermes teevani；旧文献用 Armitermes teevani Emerson, 1925 时写「当时置于 Armitermes，本站现置于 Uncitermes」；该组合仍有争议，不要写成学界共识。 | 争议／未定 | [GBIF](https://www.gbif.org/species/9734260) |

## 种级逐条备注

### Amitermes californicus ↔ Amitermes wheeleri

- 本站页面：`/species/amitermes-californicus/`（加州弓白蚁）
- 外部库接收名：Amitermes wheeleri `/species/amitermes-wheeleri/`
- 关系：synonym；方向：external；争议：否
- 处理：本站两页并存：写 Amitermes californicus 时注明 GBIF、COL、BSF 将其列为 Amitermes wheeleri 的异名；写 Amitermes wheeleri 时反向注明。不要删页或改学名，除非用户确认。

### Grigiotermes hageni ↔ Anoplotermes hageni

- 本站页面：`/species/grigiotermes-hageni/`（哈根灰白蚁）
- 关系：combination；方向：site；争议：是
- 处理：本站现用 Grigiotermes hageni；旧文献用 Anoplotermes hageni Emerson & Snyder, 1949 时写「当时置于 Anoplotermes，本站现置于 Grigiotermes」；该组合仍有争议，不要写成学界共识。

### Mapinguaritermes grandidens ↔ Armitermes grandidens

- 本站页面：`/species/mapinguaritermes-grandidens/`（大齿红懒白蚁）
- 关系：combination；方向：site；争议：是
- 处理：本站现用 Mapinguaritermes grandidens；旧文献用 Armitermes grandidens Emerson, 1925 时写「当时置于 Armitermes，本站现置于 Mapinguaritermes」；该组合仍有争议，不要写成学界共识。

### Patawatermes nigripunctatus ↔ Anoplotermes nigripunctatus

- 本站页面：`/species/patawatermes-nigripunctatus/`（黑点帕塔瓦白蚁）
- 关系：combination；方向：site；争议：是
- 处理：本站现用 Patawatermes nigripunctatus；旧文献用 Anoplotermes nigripunctatus Emerson, 1925 时写「当时置于 Anoplotermes，本站现置于 Patawatermes」；该组合仍有争议，不要写成学界共识。

### Rubeotermes jheringi ↔ Anoplotermes jheringi

- 本站页面：`/species/rubeotermes-jheringi/`（耶林变红白蚁）
- 关系：combination；方向：site；争议：是
- 处理：本站现用 Rubeotermes jheringi；旧文献用 Anoplotermes jheringi Holmgren, 1906 时写「当时置于 Anoplotermes，本站现置于 Rubeotermes」；该组合仍有争议，不要写成学界共识。

### Ruptitermes franciscoi ↔ Anoplotermes franciscoi

- 本站页面：`/species/ruptitermes-franciscoi/`（弗朗西斯科腹爆白蚁）
- 关系：combination；方向：disputed；争议：否
- 处理：按原文保留旧名，并注明与本站现用名的关系；不确定时标「待核」。

### Silvestritermes minutus ↔ Armitermes minutus

- 本站页面：`/species/silvestritermes-minutus/`（最小西尔韦斯特里白蚁）
- 关系：combination；方向：site；争议：是
- 处理：本站现用 Silvestritermes minutus；旧文献用 Armitermes minutus Emerson, 1925 时写「当时置于 Armitermes，本站现置于 Silvestritermes」；该组合仍有争议，不要写成学界共识。

### Uncitermes teevani ↔ Armitermes teevani

- 本站页面：`/species/uncitermes-teevani/`（蒂范弯钩白蚁）
- 关系：combination；方向：site；争议：是
- 处理：本站现用 Uncitermes teevani；旧文献用 Armitermes teevani Emerson, 1925 时写「当时置于 Armitermes，本站现置于 Uncitermes」；该组合仍有争议，不要写成学界共识。

## 复核入口

- `_data/name_issues.json`：完整 328 条一致性核对结果（含 `synonym_pairs`、`species_authority`、`issues`）。
- `_data/taxonomy_crosswalk.json`：本表的机器可读版本，供扫描器/后续脚本使用。
- `.sources/index.json`：每条判断对应的来源存档；正文用 `<!-- src:Sxxxx -->`。
