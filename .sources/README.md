# 来源存档（Source Archive）

本目录是**可核查的来源账本**：每个被 AI 或人读过、并据以作出事实性判断的网页 / 论文 / 数据集 / 本地文件，
都在这里留下一条记录（元数据 + 逐字摘录 + 定位 + 被用在哪里）。

工作区规则见仓库根目录 `AGENTS.md` §1；本文件是数据格式与维护说明。

## 为什么不是「存网页快照」

- 仓库里不放网页快照、不放出版社 PDF：它们会过期、会膨胀，整篇转载他人作品也有版权问题
  （本站既有政策见 `_tools/文献检索器说明.md` §3）。
- 需要复核的是**判断所依据的那几句原文**，以及它出自哪一版、哪一页。
- 所以本目录存的是证据链：`canonical_key`（身份）+ `sha256`（版本指纹）+ 逐字摘录（内容）+ `locator`（位置）。
- 但如果确实需要反复通读全文（书、论文、报告），**全文放本机文库** `_unpublished/文库/`（下表），
  本目录只指向它。这样既不失原文，也不把受版权保护的全书塞进发布仓库。

## 与 `_unpublished/文库` 的关系：全文库 vs 证据账本

本工作区里「存档」有两层，不要混：

| | `_unpublished/文库/`（全文库） | `.sources/`（证据账本，本目录） |
| --- | --- | --- |
| 存什么 | 5 本书 + 9 篇论文的**全文 txt**（按页或按 20 万字符切块） | 每条来源的**元数据 + 逐字短摘录 + locator** |
| 在哪 | 本机，已被 `.gitignore` 忽略，不发布 | 进仓库，随代码审阅 |
| 谁生成 | 书：`ingest_library.py` / `split_pdf_text.py`；论文：`python _tools/sources.py library-add` | `python _tools/sources.py add / import-library / library-add` |
| 回答什么 | 「这本书第 412 页原文到底怎么写的」 | 「这条判断依据的是哪个来源的哪一句」 |

- 文库里的 5 本书**已经**在账本里登记为 `S0001`–`S0005`（`canonical_key` = `library:<书名>`），
  记录里带 `library.chunks` 分卷清单（每块的页范围、字符数、sha256）。
- 论文 / 报告登记为 `S0006`–`S0017` 共 12 条（9 篇有全文入库，`S0010`、`S0011` 只有摘要，`S0012` 未获全文；`canonical_key` = `doi:`，没有 DOI 时用 `url:` / `library:<slug>`）：
  同一个 DOI 若已有网页记录，`library-add` 会**合并进原记录**，不会多出第二个 id。
- 引用文库书时**不要新开记录**：直接引用对应的 `Sxxxx`，`locator` 写「页码 + 分卷文件」
  （例：`p. 412 / 0401-0600.txt`）；摘录从该书 txt 里逐字拷贝。
- 文库重新生成（manifest 时间戳变化 / 重新切块）后，跑一次 `import-library` 刷新；
  分卷 txt 被改动会报 `[W006]`（`--strict` 下为错误）。
- 中文三本由 PDF OCR 而来，错字与拉丁学名损坏以文库 README 的说明为准；
  正式引用要核对纸本或原书 PDF，并在 `notes` 注明「据 OCR 文本」。

## 目录结构

    .sources/
      index.json          机器可读的权威索引（唯一真源）
      records/S0001.md    每条来源的人读视图（脚本生成，不要手改）
      README.md           本文件

Jekyll 默认忽略以 `.` 开头的目录，所以本目录不会进站点产物；但它**进仓库**，
这样来源可随数据集一起归档、审阅、复现。若不想公开，把 `.sources/` 加进 `.gitignore` 即可（存档逻辑不变，只是不提交）。

## index.json

    {
      "meta": {"version": 1, "count": 2, "updated": "2026-11-07T00:20:00+08:00"},
      "sources": [ {...}, {...} ]
    }

单条记录：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | `S0001` 递增，全库唯一，**永不复用** |
| `canonical_key` | string | 去重键：`doi:` / `url:` / `file:<path>@<sha256>` / `sha256:` / `title:` |
| `title` | string | 原文标题（不翻译） |
| `source_type` | enum | web / paper / book / report / dataset / database / file / other |
| `reliability` | enum | primary / peer_reviewed / official / reference / secondary / unverified |
| `url` `doi` `file_path` | string | 至少一个；`file_path` 相对仓库根 |
| `body_sha256` | string | 实际读到的字节（本地文件）或文本（网页）的 sha256，用于判定同一 URL 的内容是否已变 |
| `accessed` | string | ISO 8601，带时区 |
| `evidence` | array | `{quote, locator, note}`；quote 逐字、不超过 400 字 |
| `used_in` | array | 仓库内相对路径 |
| `notes` | string | 排除理由 / 矛盾 / 「仅摘要」等 |
| `library` | object | 由 `import-library` / `library-add` 生成：`{book, kind, title, manifest, generated, extraction, source_file, source_sha256, source_bytes, pages, chunks:[{chunk, txt（书）/ source（论文）, sha256, chars, paragraphs, table_rows, source_file}]}` |

## 生命周期

1. **读之前先查**：`python _tools/sources.py list`，同一来源直接复用 `Sxxxx`。
2. **读完立刻存**：`add --json`；同一 `canonical_key` 会合并（补摘录、补 used_in），不新建。
3. **写正文时标注**：Markdown 用 `<!-- src:S0001 -->`；二进制交付物在文末列来源表。
4. **交付前校验**：`python _tools/sources.py check --strict`。
5. **论文全文入库**：`python _tools/sources.py library-add --file paper.pdf --doi ... --kind paper`
   （用法见 `AGENTS.md` §1.4.1）。Europe PMC 的 JATS 全文（`fullTextXML`）比双栏 PDF 抽取干净；
   订阅墙下只有摘要时**不要硬编全文**，`notes` 写「access: blocked，仅有摘要」。
   预印本与正式版 DOI 不同 → 两条记录，互相在 `notes` 指认。
6. **文库刷新**：`python _tools/sources.py import-library`（幂等；只刷新 `S0001`–`S0005` 的
   分卷清单 / 字符数 / notes / accessed，不覆盖你手写的摘录与 used_in）。
7. **来源变化**：本地文件被改动会报 `[W005]`（sha256 不符）；网页改版则重新抓取后 add 新摘录，
   旧摘录**保留**（历史不复写），在 `notes` 注明「2026-11-07 页面已改版」。

## check 的判定

| 代码 | 含义 | 默认严重度 |
| --- | --- | --- |
| E002 / E003 | id 重复 / 格式不对 | 错误 |
| E004 / E005 | 缺必填字段 / 枚举值非法 | 错误 |
| E006 | canonical_key 重复（正常应由 add 合并掉） | 错误 |
| E007 | 摘录超过 400 字 | 错误 |
| E008 | used_in 写成绝对路径或越出仓库 | 错误 |
| E009 | 缺 records/Sxxxx.md | 错误 |
| E010 | 正文 `<!-- src:Sxxxx -->` 指向未存档的 id | 错误 |
| W001 | used_in 指向的文件不存在 | 提示 |
| W002 | 摘录缺 locator / 空摘录 | 提示（`--strict` 下为错误） |
| W003 | 被引用却无摘录、也无 notes | 提示（`--strict` 下为错误） |
| W004 | accessed 不是 ISO 日期 | 提示 |
| W005 | 本地文件 sha256 与存档不符 | 提示（`--strict` 下为错误） |
| W006 | 文库分卷 txt 的 sha256 与 manifest 不符 | 提示（`--strict` 下为错误） |

`--ci` 与默认行为一致（只读、无错即 0），供 `.github/workflows/validate.yml` 使用。
`--strict` 是交付前闸门：要求被引用的来源必须有可核查的摘录。

## 与既有参考文献体系的关系

- `_data/references.json`（77 条，带 DOI 解析）是**名录正文的参考文献**；本存档是**工作过程的事实依据**。
  两者互补：一条 `Sxxxx` 可以在 `notes` 写「= 参考文献 [12]」。
- `_data/papers.json` / `papers-index.json` 是站内缓存，属二手转存；引用其中字段时，
  `source_type` 记 `database`、`reliability` 记 `official`（OpenAlex / Crossref 元数据），并在 `notes` 写原始 DOI。
