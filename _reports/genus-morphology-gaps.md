# 属级形态描述缺口（2026-11-19）

站点 326 个属页：`_data/fauna_genera.json` 35 属、《中国动物志》改写；`_data/morphology_genera.json` 242 属、补充描述；两处均无条目者 **49 属**。

## 总数

- 缺属：49（Termitidae 47、Kalotermitidae 1、Hodotermitidae 1）
- 有原始文献出处（Treatise 引证 + 模式种）：43 属
- 连原始文献出处都没有：6 属（Apolemotermes、Dissimulitermes、Koutabatermes、Longicaputermes、Microhodotermes、Palmitermes）
- 在五部描述性文库著作中出现过属名：14 属；其余 35 属未出现

## 文库内的属名出现情况

| 属 | 中名 | 科 | 文库出现（BEL/FAUNA/SANDS/HOLM/MONO） | 性质 |
|---|---|---|---|---|
| Allodontermes | 奇齿白蚁属 | Termitidae | HOLM:2 BEL:8 FAUNA:1 | 检索表/名录/分布行，非属级全形描述 |
| Coxotermes | 基白蚁属 | Termitidae | SANDS:1 | 检索表/名录/分布行，非属级全形描述 |
| Eburnitermes | 象牙白蚁属 | Termitidae | SANDS:2 FAUNA:2 | 检索表/名录/分布行，非属级全形描述 |
| Incolitermes | 子民白蚁属 | Termitidae | FAUNA:2 | 检索表/名录/分布行，非属级全形描述 |
| Labidotermes | 钳白蚁属 | Termitidae | SANDS:6 | 检索表/名录/分布行，非属级全形描述 |
| Lepidotermes | 鳞白蚁属 | Termitidae | SANDS:2 BEL:2 | 检索表/名录/分布行，非属级全形描述 |
| Megagnathotermes | 大颚白蚁属 | Termitidae | BEL:3 | 检索表/名录/分布行，非属级全形描述 |
| Microhodotermes | 小草白蚁属 | Hodotermitidae | BEL:2 | 检索表/名录/分布行，非属级全形描述 |
| Noditermes | 节白蚁属 | Termitidae | BEL:2 | 检索表/名录/分布行，非属级全形描述 |
| Orientotermes | 东方白蚁属 | Termitidae | FAUNA:2 | 检索表/名录/分布行，非属级全形描述 |
| Orthotermes | 直白蚁属 | Termitidae | BEL:4 | 检索表/名录/分布行，非属级全形描述 |
| Rostrotermes | 突吻白蚁属 | Termitidae | SANDS:1 | 检索表/名录/分布行，非属级全形描述 |
| Trichotermes | 发白蚁属 | Termitidae | SANDS:1 BEL:4 | 检索表/名录/分布行，非属级全形描述 |
| Unguitermes | 爪白蚁属 | Termitidae | BEL:2 | 检索表/名录/分布行，非属级全形描述 |

未出现的 35 属：Antillitermes、Apolemotermes、Apsenterotermes、Batillitermes、Caribitermes、Cristatitermes、Dissimulitermes、Divinotermes、Ekphysotermes、Enetotermes、Ephelotermes、Hapsidotermes、Hesperotermes、Invasitermes、Kaudernitermes、Koutabatermes、Longicaputermes、Machadotermes、Malaysiotermes、Megaprotermes、Nasopilotermes、Okavangotermes、Onkotermes、Ovambotermes、Palmitermes、Phoxotermes、Pseudhamitermes、Sabahitermes、Saxatilitermes、Skatitermes、Spatulitermes、Subulioiditermes、Trapellitermes、Unicornitermes、Xylochomitermes。

## 外部原文可达性（已试查）

| 属 | 原始文献 | 结果 |
|---|---|---|
| Dissimulitermes | 10.1163/1876312x-bja10014（2020） | Unpaywall 标 green OA，指向 USP 仓储 hdl.handle.net/11449/208110，仓储 SSL 连接失败 |
| Malaysiotermes、Subulioiditermes | Gathorne-Hardy 2001, 10.1080/002229301317067647 | Unpaywall 仓储链接指向 CheckListBank 数据集（10.48580/dgrfq.v12），非论文 |
| Ephelotermes | Bourguignon et al. 2008, Zootaxa 1769.1.1 | Unpaywall 给 CheckListBank（10.48580/d42yg.v82）与 Zenodo 182093 两个镜像，前者为数据集、后者无文件；mapress 下载跳登录页 |
| Antillitermes、Caribitermes | Roisin et al. 1996, AESA 89(6):775–783 | 付费墙（10.1093/aesa/89.6.775） |
| Apsenterotermes、Hapsidotermes | Miller 1991, Invertebr. Taxon. | 付费墙（10.1071/IT9901147） |
| Batillitermes | Uys 1994b | 未见 OA |
| Kaudernitermes | 1975, 10.1111/j.1365-3113.1975.tb00013.x | 付费墙 |
| Invasitermes | 1984, 10.1111/j.1440-6055.1984.tb01902.x | 付费墙 |
| Orthotermes | 2015, 10.11646/zootaxa.3946.4.9 | 付费墙 |

## 结论与路线

1. 文库现有五部描述性著作对这 49 属只有检索表、属名表或分布行，没有可改写的属级全形描述；属级条目不能靠现有文库补。
2. 43 属有原始文献出处与模式种，可按 `_data/genus_sources.json` 的 refs 逐条索取原文：1900–1940 年代的（Sjöstedt、Holmgren、Emerson、Hill）优先走 BHL / archive.org；1950 年后的走出版社 DOI 或馆际互借。
3. 6 属（Apolemotermes、Dissimulitermes、Koutabatermes、Longicaputermes、Microhodotermes、Palmitermes）连模式种/出处都缺，先查 GBIF、Catalogue of Life、Blattodea Species File 的原始文献字段。
4. 已确认的 OA 通道只有 Dissimulitermes 一篇，但仓储当前不可达；其余试查均付费墙或链接失效。

完整 49 行见 `_reports/genus-morphology-gaps.csv`。

<!-- src:S0481 --><!-- src:S0004 -->
