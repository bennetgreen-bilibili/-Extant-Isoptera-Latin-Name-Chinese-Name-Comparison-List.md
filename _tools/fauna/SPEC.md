# 任务：把《中国动物志·昆虫纲 第十七卷 等翅目》(2000) 的条目改写成站内形态描述

输入：`_tmp/dz/batches/batch_NN.json`（数组，每元素一种白蚁）
输出：`_tmp/dz/out/batch_NN.json`（数组，顺序与输入一致）

## 输入字段
- `book_n`：原书条目序号；`page`：本站物种页 URL（输出必须原样带回）
- `page_latin` / `page_zh`：本站现用学名与中文名
- `book_zh` / `book_latin`：原书使用的名称（可能与现名不同）
- `note`：属名变更等已知分类变动提示（可能为空）
- `soldier` / `alate` / `worker` / `nymph`：原书对应品级的描述正文（可能为空串）
- `syn`：原书异名与文献引证；`dist`：原书记录的分布；`host` / `other`：寄主与生物学

## 输出格式（严格 JSON 数组，无注释无 markdown 围栏）
```json
[
  {
    "page": "/species/xxx/",
    "soldier": "……",
    "alate": "……",
    "worker": "",
    "biology": "",
    "distribution": "……",
    "taxonomy_note": "",
    "en": "……"
  }
]
```
字段为纯文本（不带 markdown、不带 HTML、不带 `**`），空内容写空字符串。

## 写作要求（重要）
1. **必须重写，不得照抄**：重新组织句子与句序，改变断句、语序与用词；与原文不得出现连续 10 个以上汉字的相同串。术语（如"囟""后颏""上唇""前胸背板""胫节"）可保留，但整句必须重写。绝不要粘贴原文。
2. **只写原文有的内容**：不臆造分布、寄主、量度。原文出现的"图 268""（仿王治国等）""兵蚁量度(mm)""1.头及前胸背板背面；2.头侧面"这类图注、量度表头、图版说明一律丢弃。
3. **品级分段**：`soldier`（兵蚁）、`alate`（有翅成虫）、`worker`（工蚁）分别成段，每段 80–260 个汉字；原文缺某品级就留空串（不要写"未见描述"之类的话）。
4. **颜色与形态**按原文改述，保留可核对的细节（毛被、刻点、齿位、节数、比例），但不要搬运数字量度表；原文散文里出现的"体长 5—6 mm"这类可以保留。
5. `biology`：由 `host`/`other` 中的寄主、筑巢、取食、危害记录改写成 1–3 句；无内容留空。
6. `distribution`：由 `dist` 整理成一句，保留省名与具体地点，去掉重复括号与 OCR 噪声；不要加原文没有的地点。
7. `taxonomy_note`：仅当 `book_latin` 与 `page_latin` 的属名不同、或 `note` 非空时，写 1 句说明（例："原书将该种置于蔡白蚁属 *Tsaitermes*，现归入散白蚁属 *Reticulitermes*。"）；否则空串。不要写"本站"以外的臆测。
8. `en`：60–90 词英文摘要，概述兵蚁与有翅成虫的主要形态，不逐句对译中文，不写分布与文献。
9. 语言风格：中文为客观陈述的学术说明文，第三人称，不用"我们""本文"；避免"该书指出"这类元话语。

## 交付
- 一次写完整批（30 条），使用 write 工具输出到 `_tmp/dz/out/batch_NN.json`。
- 文件必须是合法 JSON（可用 `python -c "import json;json.load(open(...))"` 自检）。
- 完成后回报：条数、空 soldier 数、空 alate 数、是否有异常条目（原文残缺等）。

## 自检闭环（必须做到 0 条 HARD 才算完成）

写完 `_tmp/dz/out/batch_NN.json` 后运行：

```
PYTHONIOENCODING=utf-8 "<python>" _tmp/dz/check_batch.py _tmp/dz/out/batch_NN.json --n 12
```

（python 路径见 `load_workspace_dependencies`；也可直接 `python`。）

报告里每行 `HARD 18字 /species/xxx/ soldier | 共同片段` 表示该字段与原文有一段 **12 个字符以上完全相同**的文字（含标点），
这就是"照抄"，必须改写：

- 合并/拆分句子，改变叙述顺序（例如先讲量度再讲颜色，或先讲后缘再讲前缘）；
- 换连接词与句式（"呈…状"↔"…形"、"长为宽的 1.5 倍"↔"宽约等于长的三分之二"）；
- 把并列枚举改写成带层级的长句，或反之拆成短句；
- 同义的形态学术语可换（"近长方形"↔"略作长方形"、"几相等"↔"约略相等"），但**术语所指不能变**；
- 数字统一写成汉字（"1.55 倍"→"一点五五倍"），这既能避免雷同也更符合志书体例。

改完再跑一次。

## 最终验收（唯一判定标准，必须 PASS）

```
PYTHONIOENCODING=utf-8 "C:\Users\32304\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" _tmp/dz/verify.py _tmp/dz/out/batch_NN.json --src _tmp/dz/batches/batch_NN.json
```

PASS 的条件（三条同时满足）：
1. 每条输出里，与原文**连续相同**的最长片段 < **30 个字符**（含标点）—— 报告里会列出 `LONG 33字 /species/xxx/:soldier | 共同片段` 这样的行，这些就是必须改写的位置；
2. 8-gram containment < **0.25**（整体雷同率）；
3. `entries N / src N | dup 0 | missing 0`。

只看最后一行 `VERDICT: PASS`。若为 FAIL，按报告逐条改写后再跑，直到 PASS。
**注意**：连续 30 字以下的技术术语串（如"前胸背板前缘中央"、拉丁学名、"xx科xxx属"）属正常沿用，不必强行替换。
