# 种级形态描述覆盖统计（站内文库口径）

生成日期：2026-11-18。统计对象：`_species/*.md` 全部 3089 个种/亚种页。

| 状态 | 数量 | 说明 |
| --- | ---: | --- |
| 已有《中国动物志》描述 | 435 | `_data/fauna_species.json` |
| 已有补充描述 | 81 | `_data/morphology_species.json`，多为单型属据属级描述改写 |
| **待补合计** | **2573** | 可写 326、待核 464、仅名录 1632、对不上号 151 |

## 待补 2573 的细分

| 类别 | 数量 | 判据 |
| --- | ---: | --- |
| A 有可用种级描述 | 326 | 文库全文中有编号种级条目或新种描述，含量度，可直接改写 |
| B 待核 | 464 | 在文库论文/专著中被提及，但未确认有描述，需逐篇核 |
| C 仅名录/教材 | 1632 | 只出现在 Treatise、Catalog、教材、地区名录的名单里，无描述可摘 |
| D 对不上号 | 151 | 文库全文无该双名（含 front matter 异名）；部分可能以老组合存在，需异名桥接复核 |

## A 类来源（可重叠，去重后 326）

| 文献 | 存档 | 命中待补种数 |
| --- | --- | ---: |
| The Fauna of India … Vol. II（Chhotani 1997） | S0104 | 215 |
| The soldierless termites of Africa（Sands 1972，两 OCR 副本） | S0005 / S0074 | 92（去重 52） |
| Monographie der Termiten Afrikas（Sjöstedt 1900） | S0118 | 23 |
| Termites of the Belgian Congo and the Cameroon（Emerson 1928） | S0075 | 18 |
| Arkiv för Zoologi Bd 12（Mjöberg 1920） | S0113 | 6 |
| 其他 8 篇论文 | 见 CSV 的 sources 列 | 13 |

注 1：Fauna of India 另有 3 个种因 OCR 属名拼写（如 Acieulitermes）漏判，已人工补入。
注 2：Arkiv 卷内白蚁部分为 Mjöberg 澳洲区系修订（51 种、36 新种），老组合与今名不同，自动对号只 6 例；同卷另有约 7 例需人工核条目。
注 3：A 类按「有编号条目 + 品级正文 + 量度」判定；仅有摘要的论文（如 S0300 Compositermes bani 的存档只有摘要）不计入。

## 按科分布

| 科 | 待补 | A 可写 | B 待核 | C 仅名录 | D 对不上号 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Termitidae | 1916 | 316 | 279 | 1199 | 122 |
| Kalotermitidae | 419 | 6 | 88 | 304 | 21 |
| Heterotermitidae | 114 | 1 | 49 | 59 | 5 |
| Rhinotermitidae | 57 | 0 | 20 | 35 | 2 |
| Hodotermitidae | 21 | 2 | 6 | 13 | 0 |
| Psammotermitidae | 14 | 0 | 4 | 9 | 1 |
| Stylotermitidae | 11 | 0 | 3 | 8 | 0 |
| Stolotermitidae | 10 | 1 | 8 | 1 | 0 |
| Archotermopsidae | 7 | 0 | 5 | 2 | 0 |
| Serritermitidae | 2 | 0 | 1 | 1 | 0 |
| Termitogetonidae | 2 | 0 | 1 | 1 | 0 |

## B 类（待核）涉及的论文（已排除名录/教材）

| 文献 | 待核种数 |
| --- | ---: |
| Termites-of-the-Belgian-Congo-and-the-Cameroon | 54 |
| 10.11609-jott.5781.13.6.18598-18613 | 44 |
| 10.1038-s41598-021-04574-0 | 31 |
| 10.13102-sociobiology.v62i3.793 | 27 |
| Oceanic-dispersal,-vicariance-and-human-introduction-shaped-the-modern-distribut | 25 |
| The-Fauna-of-India-and-the-Adjacent-Countries-Isoptera-(Termites),-Volume-II-(Fa | 24 |
| 10.1186-s12862-019-1459-3 | 17 |
| 10.1603-0013-8746(2003)096[0181-tdanot]2.0.co;2 | 16 |
| Developmental-Pathways-of-Psammotermes-hybostoma-(Isoptera-Rhinotermitidae)-Old- | 14 |
| 10.1590-s0103-90162004000600016 | 13 |

## D 类对不上号（151）按属

| 属 | 种数 |
| --- | ---: |
| Isognathotermes | 14 |
| Ternicubitermes | 13 |
| Nitiditermes | 12 |
| Ruptitermes | 10 |
| Polyspathotermes | 7 |
| Rugitermes | 5 |
| Anhangatermes | 4 |
| Cryptotermes | 4 |
| Silvestritermes | 4 |
| Amitermes | 3 |
| Glyptotermes | 3 |
| Labiocapritermes | 3 |
| Mapinguaritermes | 3 |
| Neotermes | 3 |
| Termes | 3 |

## 建议批次

1. 第一批：Fauna of India 的 215 种（印度区系，条目含兵蚁/成虫/量度，结构最整齐）。
2. 第二批：Sands 1972（52 种，去重）、Belgian Congo（18）、Monographie（23，德文老组合需桥接）。
3. 第三批：Arkiv 澳洲种（先人工核条目）与其他论文的零散种。
4. B 类 464 种逐篇排查是否含描述；D 类 151 种在文库中对不上号，需异名桥接复核或外部文献。

数据文件：`_reports/species-morphology-coverage.csv`（逐种，status = A / B-paper / B-only / C）；对不上号清单：`_reports/species-morphology-no-source.md`。

<!-- src:S0104 --><!-- src:S0005 --><!-- src:S0118 --><!-- src:S0075 --><!-- src:S0113 -->
