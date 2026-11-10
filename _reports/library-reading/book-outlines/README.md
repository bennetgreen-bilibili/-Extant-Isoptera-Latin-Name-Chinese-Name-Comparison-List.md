# 书目与阅读单位（所有书／专著）

`chunk` 是文库的文件切块，不是阅读单位。每部书先按目录／索引拆成“节／分类处理”，再一节一节读；扫过 chunk 不算读完。

| 来源 | 书／专著 | 书型 | chunks | 阅读单位 | 起始顺序 |
| --- | --- | --- | ---: | --- | --- |
| S0001 | 白蚁学（2014） | 教材 | 3 | 章／节 | 第 6 章「白蚁分类」→ 形态 → 生理／生态 → 防治 → 文献 |
| S0002 | 白蚁生物学现代研究合集 | 文集／教材 | 5 | 章／专题 | 分类与演化 → 生物学 → 生态 → 应用 |
| S0003 | 中国动物志·昆虫纲·第十七卷·等翅目 | 志书 | 10 | 科／属／种处理 | 科级总论 → 属征 → 种级处理 |
| S0004 | Treatise on the Isoptera of the World（2013） | 专著 | 14 | 章／科／属处理 | 分类总论 → 科级处理 → 属级处理 |
| S0005 | The soldierless termites of Africa（1972） | 专著／修订 | 2 | 属／种处理 | Apicotermitinae → 属征 → 种级处理 |
| S0103 | Catalog of the Termites (Isoptera) of the World（1949） | 名录／目录 | 9 | 科／属条目或页码段 | 科 → 属 → 种条目，按名录顺序 |
| S0104 | The Fauna of India… Volume II（1997） | 志书 | 8 | 科／属／种处理 | 科级检索 → 属征 → 种级处理 |
| S0105 | The Harvester Termites (Anacanthotermes)…（1988） | 专著 | 1 | 种级处理／页码段 | 属征 → 种级处理 |
| S0113 | Arkiv for zoologi. Band 12（1920） | 文集／期刊卷 | 7 | 单篇论文／独立 section | 先分类／修订类，后区系记录 |
| S0114 | Termites (Isoptera) from the Australian Region（1942） | 区域志 | 1 | 科／属／种记录 | 科 → 属 → 种记录 |
| S0118 | Monographie der Termiten Afrikas（1900） | 专著 | 4 | 属／种处理 | 属征 → 种级处理 |

同型专著即使 `source_type` 标成 `paper`，也按“书”的规则拆单位：S0033 Holmgren 1912（3 chunks）、S0034 Emerson 1959（1）、S0075 Termites of the Belgian Congo（2）、S0005 Sands 1972 等。不要把 `source_type` 当成是否精读的唯一判据。

## 怎么记

- 每个单位记：`work`、`chapter/section 或 taxon treatment`、起止页／行、所属 chunk。
- 事实不设上限；一节／一个分类处理能核实多少条就记多少条。
- 事实卡写进 `_reports/library-reading/facts/YYYY-MM-DD.json`；覆盖账本按单位记 `未读 / 已扫 / 已摘 / 已用`。
- 只有“这一节已读、事实已摘”才算读过；`chunk` 扫过不等于书读过。
