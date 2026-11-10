# 事实卡（facts ledger）

书按章／节精读时，先把这一节里所有能核实的**具体事实**抽成卡；能写进页面的写页面，暂时落不上的留在这里，下一轮继续用。

- 文件：`YYYY-MM-DD.json`，一天一个；同一天多次写就合并 `facts` 数组。
- 不设条数上限：一节有多少条可核实事实就记多少条。
- 每条必须能回原文：`quote` 逐字、`locator` 到页码／行／chunk 文件。

```json
{
  "date": "YYYY-MM-DD",
  "book": "白蚁学",
  "chapter": "第六章 白蚁分类",
  "section": "第九节 等翅目分类概述",
  "locator": "p. 120–153 / 001-200.txt",
  "facts": [
    {
      "page": "/genus/kalotermes/",
      "claim": "木白蚁属 Kalotermes 由 Hagen 于 1853 年命名。",
      "quote": "逐字原文……",
      "src": "S0001",
      "locator": "p. 1224 / 001-200.txt",
      "status": "used",
      "note": "支撑属页命名史"
    }
  ]
}
```

`status`：

- `used`：已写进页面；
- `queued`：事实可靠，但本轮页面没写或写不下；
- `rejected`：核证不通过（旧名、年代冲突、原文不足），在 `note` 写原因。
