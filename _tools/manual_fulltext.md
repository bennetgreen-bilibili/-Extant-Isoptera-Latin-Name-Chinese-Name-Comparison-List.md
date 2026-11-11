# 待人工获取清单（自动生成，勿手改）

由 `_tools/fetch_fulltext.py` 在每次抓取后重建：收录**自动下载已被出版方拦掉**、
或**OA 只给落地页而没有 PDF 直链**的文献。拿到全文后（下一轮自动下到，或本地
`library-add` 入库）该条会自动从清单里消失，不需要手工删。
查不到任何 OA 全文的条目不在本表（那是「没有合法 OA」，只能走图书馆），
它们的标记在 `.sources` 的 `fulltext_status = abstract-no-oa`。

- 更新时间：2026-11-11 20:23（清单内容不变时不刷新）
- 共 **37** 条：站点拦截 37 ／ 仅有落地页 0
- 结构化版本：`_data/fulltext_manual.json`（同一次运行写出的同一份数据）

| # | 引用 | 年 | 标题 | DOI | 上次撞到的站点 | 建议取法 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 96 | 2016 | Oceanic dispersal, vicariance and human introduction shaped the modern distribution of the ter… | [10.1098/rspb.2016.0179](https://doi.org/10.1098/rspb.2016.0179) | Royal Society | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 2 | 80 | 2003 | Solution structure of termicin, an antimicrobial peptide from the termite Pseudacanthotermes s… | [10.1110/ps.0228303](https://doi.org/10.1110/ps.0228303) | Wiley | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 3 | 67 | 2009 | Phylogeography of Coptotermes gestroi and Coptotermes formosanus (Isoptera: Rhinotermitidae) i… | [10.1603/008.102.0413](https://doi.org/10.1603/008.102.0413) | Oxford Academic | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 4 | 50 | 2011 | Nitrate reduction, nitrous oxide formation, and anaerobic ammonia oxidation to nitrite in the … | [10.1111/j.1462-2920.2011.02648.x](https://doi.org/10.1111/j.1462-2920.2011.02648.x) | Wiley | Wiley，需机构网络；分类学类可先试 BHL 的散见抽印本 |
| 5 | 48 | 1980 | Differences in Nest Architecture Between the Neotropical Arboreal Termites Nasutitermes Cornig… | [10.1155/1980/12305](https://doi.org/10.1155/1980/12305) | Hindawi（旧域名，已迁移 Wiley） | Hindawi 旧刊已迁 Wiley；先试 PMC / Europe PMC 副本，再 archive.org |
| 6 | 47 | 2016 | Facultative asexual reproduction and genetic diversity of populations in the humivorous termit… | [10.1098/rspb.2016.0196](https://doi.org/10.1098/rspb.2016.0196) | Royal Society | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 7 | 44 | 1998 | Developmental Pathways and Polyethism of Neuter Castes in the Processional Nasute Termite Hosp… | [10.2108/zsj.15.843](https://doi.org/10.2108/zsj.15.843) | BioOne | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 8 | 43 | 2009 | Diverse Rhinotermitidae and Termitidae (Isoptera) in Dominican Amber | [10.1206/633.1](https://doi.org/10.1206/633.1) | BioOne | AMNH 数字图书馆 digitallibrary.amnh.org（Novitates 系列多数免费） |
| 9 | 30 | 1959 | Beobachtungen beim Spritzakt der Nasutitermes-Soldaten | [10.5962/bhl.part.75218](https://doi.org/10.5962/bhl.part.75218) | BHL | BHL 条目页（biodiversitylibrary.org/item/…），同一册常在 archive.org 有扫描本 |
| 10 | 29 | 1981 | Laboratory Evaluation of Within‐Species, Between‐Species, and ParthenogeneticReproduction in R… | [10.1155/1981/36030](https://doi.org/10.1155/1981/36030) | Hindawi（旧域名，已迁移 Wiley） | Hindawi 旧刊已迁 Wiley；先试 PMC / Europe PMC 副本，再 archive.org |
| 11 | 26 | 1991 | Isolation of facultatively aerobic actinomycetes from the gut, parent soil and mound materials… | [10.1111/j.1574-6941.1991.tb01719.x](https://doi.org/10.1111/j.1574-6941.1991.tb01719.x) | Oxford Academic | Wiley，需机构网络；分类学类可先试 BHL 的散见抽印本 |
| 12 | 25 | 2013 | Overview And Current Status of Non-Native Termites (Isoptera) in Florida§ | [10.1653/024.096.0311](https://doi.org/10.1653/024.096.0311) | BioOne | Florida Entomologist 存档 journals.flvc.org，或 archive.org 同名卷期 |
| 13 | 25 | 1988 | Intercolonial Aggression in the Subterranean Termite Heterotermes Aureus (Isoptera: Rhinotermi… | [10.1155/1988/28452](https://doi.org/10.1155/1988/28452) | Hindawi（旧域名，已迁移 Wiley） | Hindawi 旧刊已迁 Wiley；先试 PMC / Europe PMC 副本，再 archive.org |
| 14 | 23 | 2018 | Microbial Communities of the Gut and Nest of the Humus- and Litter-Feeding Termite Procorniter… | [10.1007/s00284-018-1567-0](https://doi.org/10.1007/s00284-018-1567-0) | Springer | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 15 | 21 | 1977 | Pairing Behavior in Hodotermes Mossambicus (Isoptera) | [10.1155/1977/64060](https://doi.org/10.1155/1977/64060) | Hindawi（旧域名，已迁移 Wiley） | Hindawi 旧刊已迁 Wiley；先试 PMC / Europe PMC 副本，再 archive.org |
| 16 | 20 | 2008 | Genetic variability of the soil‐feeding termite Labiotermes labralis (Termitidae, Nasutitermit… | [10.1111/j.1752-4598.2008.00040.x](https://doi.org/10.1111/j.1752-4598.2008.00040.x) | Wiley | Wiley，需机构网络；分类学类可先试 BHL 的散见抽印本 |
| 17 | 20 | 1966 | Colonizing Flights and Associated Activities of Termites. I. TheDesert Damp‐Wood Termite Paran… | [10.1155/1966/59080](https://doi.org/10.1155/1966/59080) | Hindawi（旧域名，已迁移 Wiley） | Hindawi 旧刊已迁 Wiley；先试 PMC / Europe PMC 副本，再 archive.org |
| 18 | 19 | 2003 | Evaluation of chemical control measures for termites in maize | [10.1080/02571862.2003.10634896](https://doi.org/10.1080/02571862.2003.10634896) | Taylor & Francis | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 19 | 19 | 1990 | Queen replacement in the termite Microcerotermes papuanus | [10.1111/j.1570-7458.1990.tb01383.x](https://doi.org/10.1111/j.1570-7458.1990.tb01383.x) | Wiley | Wiley，需机构网络；分类学类可先试 BHL 的散见抽印本 |
| 20 | 19 | 1980 | ANTS (HYMENOPTERA: FORMICIDAE) IN MOUNDS OF AMITERMES LAURENSIS (ISOPTERA: TERMITIDAE) | [10.1111/j.1440-6055.1979.tb00866.x](https://doi.org/10.1111/j.1440-6055.1979.tb00866.x) | Wiley | Wiley，需机构网络；分类学类可先试 BHL 的散见抽印本 |
| 21 | 19 | 1966 | Distribution and Biology of the Primitive Dry‐Wood TermitePterotermes Occidentis (Walker) (Kal… | [10.1155/1966/20139](https://doi.org/10.1155/1966/20139) | Hindawi（旧域名，已迁移 Wiley） | Hindawi 旧刊已迁 Wiley；先试 PMC / Europe PMC 副本，再 archive.org |
| 22 | 18 | 2017 | Food Storage by the Savanna Termite Cornitermes cumulans (Syntermitinae): a Strategy to Improv… | [10.1007/s00248-017-1128-2](https://doi.org/10.1007/s00248-017-1128-2) | Springer | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 23 | 17 | 2018 | Bacteriome-associatedWolbachiaof the parthenogenetic termiteCavitermes tuberosus | [10.1093/femsec/fiy235](https://doi.org/10.1093/femsec/fiy235) | Oxford Academic | Oxford Academic，需机构网络；生物医学类可先试 PMC |
| 24 | 17 | 2006 | FIRST RECORD OF RETICULITERMES FLAVIPES AND RETICULITERMES HAGENI IN OREGON (ISOPTERA: RHINOTE… | [10.1653/0015-4040(2006)89[541:frorfa]2.0.co;2](https://doi.org/10.1653/0015-4040(2006)89[541:frorfa]2.0.co;2) | BioOne | Florida Entomologist 存档 journals.flvc.org，或 archive.org 同名卷期 |
| 25 | 17 | 1997 | Secretion of Salivary Glands of the Brazilian Termite Serritermes Serrifer Hagen & Bates (Isop… | [10.1080/21686351.1997.12279175](https://doi.org/10.1080/21686351.1997.12279175) | Taylor & Francis | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 26 | 16 | 1969 | Western Drywood Termite, Incisitermes minor (Hagen) (Insecta: Isoptera: Kalotermitidae) | [10.32473/edis-in526-2005](https://doi.org/10.32473/edis-in526-2005) | Florida Entomologist（FLVC） | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 27 | 13 | 2016 | Dehiscent organs used for defensive behavior of kamikaze termites of the genus Ruptitermes (Te… | [10.1016/j.micron.2015.12.011](https://doi.org/10.1016/j.micron.2015.12.011) | ScienceDirect | Elsevier（ScienceDirect），需机构网络；可试作者主页 / 机构库 |
| 28 | 11 | 2019 | Aparatermes thornatus (Isoptera: Termitidae: Apicotermitinae), a New Species of Soldierless Te… | [10.1653/024.102.0123](https://doi.org/10.1653/024.102.0123) | BioOne | Florida Entomologist 存档 journals.flvc.org，或 archive.org 同名卷期 |
| 29 | 10 | 2019 | Mercury species in the nests and bodies of soil-feeding termites, Silvestritermes spp. (Termit… | [10.1016/j.envpol.2019.113064](https://doi.org/10.1016/j.envpol.2019.113064) | ScienceDirect | Elsevier（ScienceDirect），需机构网络；可试作者主页 / 机构库 |
| 30 | 10 | 1994 | Nests and Queen Migration in Schedorhinotermes actuosus (Hill), Schedorhinotermes breinli (Hil… | [10.1111/j.1440-6055.1994.tb01236.x](https://doi.org/10.1111/j.1440-6055.1994.tb01236.x) | Wiley | Wiley，需机构网络；分类学类可先试 BHL 的散见抽印本 |
| 31 | 9 | 2017 | Secondary queens in the parthenogenetic termite Cavitermes tuberosus develop through a transit… | [10.1111/ede.12240](https://doi.org/10.1111/ede.12240) | Wiley | Wiley，需机构网络；分类学类可先试 BHL 的散见抽印本 |
| 32 | 9 | 2011 | Redescription of Prorhinotermes japonicus (Isoptera: Rhinotermitidae) from Taiwan | [10.1603/an11064](https://doi.org/10.1603/an11064) | Oxford Academic | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 33 | 9 | 1919 | Observations on the Protozoa Parasitic in the Hind Gut of Archotermopsis wroughtoni Desn: Part… | [10.1242/jcs.s2-63.252.555](https://doi.org/10.1242/jcs.s2-63.252.555) | BHL | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 34 | 8 | 2014 | Development and characterization of microsatellite markers from the humivorous termite Caviter… | [10.1007/s12686-014-0411-5](https://doi.org/10.1007/s12686-014-0411-5) | Springer | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 35 | 8 | 2003 | Evaluation of maize cultivars and rotation crops for resistance to damage by fungus-growing te… | [10.1080/02571862.2003.10634911](https://doi.org/10.1080/02571862.2003.10634911) | doi.org 解析页 / Taylor & Francis | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 36 | 8 | 1969 | Native Subterranean Termites: Reticulitermes flavipes (Kollar), Reticulitermes virginicus (Ban… | [10.32473/edis-in369-2001](https://doi.org/10.32473/edis-in369-2001) | Florida Entomologist（FLVC） | 出版社站点（需机构网络），或 archive.org / 馆际互借 |
| 37 | 7 | 2017 | Morphology of the male reproductive system during post-embryonic development of the termite Si… | [10.1016/j.jcz.2017.11.015](https://doi.org/10.1016/j.jcz.2017.11.015) | ScienceDirect | Elsevier（ScienceDirect），需机构网络；可试作者主页 / 机构库 |

## 怎么用这张表

1. 按「引用」从高到低处理（表已排好序：先站点拦截、后仅有落地页）。
2. 拿到 PDF 后在本地跑 `python _tools/sources.py library-add --file <pdf> --title "…" --doi <doi> …`，
   入库即从本站与清单里消失；CI 下一轮也不会再下载。
3. 拿不到就让它留着——拦站点已进 `_data/fulltext_hosts.json` 的 120 天冷却，不会拖慢抓取。
4. 不要手工编辑本文件：下次 `--write` 会用 `_data/fulltext_manual.json` 覆盖它。
