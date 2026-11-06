# AGENTS.md — 本工作区的固定约定

本仓库是「现存等翅下目（白蚁）拉丁学名—中文正名对照名录」站点源码（Jekyll + GitHub Pages，三语）。
站点上的每个学名、分布、异名、年代、文献都要能被追溯，所以本工作区有一条**跨会话的硬约定**：

## 1. 来源存档（Source Archive）

> **原则：先存档，再下结论。** 你读过、并据以写出任何事实性内容（学名、异名、分布、年代、分类位置、
> 统计数字、术语译名、图片授权）的来源，必须在同一轮任务里落成一条存档记录；正文里给出的每个此类
> 判断，都要能指回某条记录。

**两层要分清**：`_unpublished/文库/` 是**全文库**（本机 5 本书 + 9 篇论文的全文 txt，被 gitignore，不发布）；
`.sources/` 是**证据账本**（进仓库：元数据 + 逐字短摘录 + locator + used_in）。
文库里的书在账本里已有 `S0001`–`S0005`、论文 `S0006`–`S0017`（12 条记录，其中 9 篇有全文，`S0010`/`S0011` 只有摘要，`S0012` 无全文）——引用它们时**不要新开记录**，直接引用这些 id，
`locator` 写「页码 + 分卷文件」（如 `p. 412 / 0401-0600.txt`）。读文库 `_full.txt` 或分卷 txt 也算「必须存档」
的一次阅读：摘录逐字拷自该书，`used_in` 写用到它的文件。

### 1.1 必须存档

- `web_fetch` / 搜索抓到的网页、在线 PDF、HTML 全文；
- API 返回的结构化数据（OpenAlex、Crossref、GBIF、Catalogue of Life、Blattodea Species File、BHL、Zenodo…），
  只要其中的字段被写进了 `_data/`、`_species/`、文章或答复；
- 用 `pdf_extract_text`、`office_read`、`read` 读到的本地 PDF / docx / xlsx / md / json，且其内容支撑了判断；
- 用户或 Issue 里给的证据链接（哪怕只读了一部分，也要记「读到哪」）。

### 1.2 不必存档

- 只跑构建、改模板、排版、看 diff、执行 `_tools/*.py`；
- 搜索结果列表页——它只是线索，除非你引用了它的摘要；
- 同一来源已存过：`sources.py add` 会按 `canonical_key` 自动合并（复用原 `Sxxxx`，不新建）。

### 1.3 每条记录写什么

| 字段 | 要求 |
| --- | --- |
| `title` | 原文标题，不改写、不翻译（译文放 `notes`） |
| `source_type` | `web` / `paper` / `book` / `report` / `dataset` / `database` / `file` / `other` |
| `reliability` | `primary`（原始记录/模式标本/官方名录）、`peer_reviewed`、`official`（机构或数据库官方页）、`reference`（百科、教科书）、`secondary`（新闻、博客、二手综述）、`unverified`（未核实/有冲突） |
| `url` / `doi` / `file_path` | 至少一个；本地文件给仓库内相对路径，脚本自动算 sha256，文件被改会报警 |
| `authors` `year` `publisher` `lang` `license` | 有就填；许可未知写 `unknown` |
| `evidence` | **逐字摘录**（不改写、不翻译、不拼接），每处 ≤400 字；`locator` 写页码/章节/段落/表行；`note` 写它支撑了什么 |
| `used_in` | 用到它的仓库内文件（相对路径），可多个 |
| `notes` | 排除理由、矛盾点、只读到摘要等 |

### 1.4 命令

清单写在 `_tmp/`（已 gitignore），一次可提交多条：

    cat > _tmp/sources-task.json <<'JSON'
    [
      {"title": "Mitochondrial phylogenomics of termites",
       "source_type": "paper", "reliability": "peer_reviewed",
       "doi": "10.1038/s41467-024-51028-y", "year": 2024,
       "retrieved_via": "pdf_extract_text",
       "evidence": [{"quote": "……逐字……", "locator": "p.4 ¶2",
                     "note": "支撑：Coptotermes 属内分化时间"}],
       "used_in": ["_posts/2026-11-05-xxx.md"]}
    ]
    JSON
    python _tools/sources.py add --json _tmp/sources-task.json
    python _tools/sources.py check --strict      # 交付前必跑
    python _tools/sources.py list                # 先查已有什么，再存
    python _tools/sources.py import-library      # 文库重新生成/切块后才需要跑（幂等）

> Windows 上不要用 `/tmp`；一律 `_tmp/`。

### 1.4.1 论文 / 报告全文入库（`library-add`）

拿到 PDF、JATS/TEI 全文 XML、docx 或已抽好的 txt 时，一条命令把全文放进文库并同步登记来源：

    # 出版社 PDF / OA PDF
    python _tools/sources.py library-add --file ~/Downloads/xxx.pdf \
        --title "原文标题（不改写、不翻译）" --kind paper --reliability peer_reviewed \
        --doi 10.1038/xxxx --year 2024 --lang en --authors "Hellemans S.; Rocha M. M." \
        --used-in "白蚁基础知识-中文稿-修订-v5.docx"

    # Europe PMC 的 JATS 全文（比双栏 PDF 抽取干净得多）
    curl -sL "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4622179/fullTextXML" -o _tmp/a.xml
    python _tools/sources.py library-add --file _tmp/a.xml --doi 10.1093/jisesa/iev130 ...

    # 已经抽好的纯文本（扫描件 OCR、网页正文）；--no-copy 表示不复制原件
    python _tools/sources.py library-add --text _tmp/paper.txt --no-copy --kind paper ...

- 落到 `_unpublished/文库/<slug>/`：`full.txt`（超过 20 万字符才切成 `part-001.txt`…）+
  `source/<原件>`；同时在 `_unpublished/文库/manifest.json` 追加 `kind: paper` 的条目。
- `--doi` / `--url` 决定 `canonical_key`：**与已有网页/文件记录同一来源时自动合并**，不会多出第二个 Sxxxx。
- 引用文库内论文时 `locator` 写「页码 + 分卷文件」，例如 `p. 12 / full.txt`。
- 只有摘要（订阅墙、SSRN 403）时**不要硬编全文**：记录照留，`notes` 写「access: blocked，仅有摘要」。
- 预印本与正式版是**两条记录**（DOI 不同），两边 `notes` 互相指认，引用以正式版为准。
- PDF 文本不是排版原貌（上标引文编号、表格、图注会错位），正式引用前核对出版方原文。

### 1.4.2 文库的加密备份（`.library-vault/`）

`_unpublished/文库/` 被 gitignore，所以仓库里另存一份**密文备份**，克隆仓库即可恢复文库：

    python _tools/library_vault.py pack                 # 文库 → .library-vault/（AES-256-CTR + HMAC-SHA256）
    python _tools/library_vault.py info                 # 只读 manifest
    python _tools/library_vault.py verify               # 分块 sha256 + HMAC（需要口令）
    python _tools/library_vault.py unpack --target _tmp/vrestore   # 恢复并逐文件校验

- 口令从 `LIBRARY_VAULT_KEY` 环境变量或 `--key-file`（默认 `_tmp/vault.key`，已 gitignore）读取。
  **口令文件绝不提交**；丢了口令 = 备份报废，提交了口令 = 没加密。
- `pack` 是确定性的（gzip/tar mtime 归零、路径排序），同一文库重复 `pack` 产出同一密文；
  文库变了要重新 `pack` 并提交 `.library-vault/`。
- 加密只解决「仓库里不出现明文全文」，**不改变版权边界**：恢复出的全文仍然只在本地用、不再分发；
  弱口令可被离线爆破，别拿它当机密保险箱。
- `manifest.json` 里只有 salt/iv/HMAC/哈希与统计，没有标题以外的可读信息。

### 1.5 正文里怎么标

- Markdown 正文：在论断句末或段末放 ``<!-- src:S0001 -->``（HTML 注释，渲染不可见、可被 check 校验）。
  一个注释只放一个 id；需要两个就并排写两个注释。
- Word / docx / pptx 等二进制交付物：文末加「来源」小节列出 `Sxxxx` + 标题 + URL/DOI，
  并把该文档路径写进对应记录的 `used_in`。
- 旧文已有参考文献编号（如 `list.md` 的 `[12]`）时**不要重编号**；在新记录 `notes` 里写「对应参考文献 [12]」即可。

### 1.6 红线（违反即视为未完成）

1. **不得编造**标题、作者、年份、DOI、URL、页码、引文；没打开过的页面不许存档。
2. **摘录必须逐字**；需要改写就放在 `notes` 并注明「转述」。
3. **全文只进文库，不进仓库**：论文 / 报告 / 书的全文本地存在 `_unpublished/文库/`（已被 `.gitignore`
   排除、不发布、不再分发），用 `library-add` 入库；`.sources/` 里只留元数据 + 短摘录
   （单处 ≤400 字，同一版权作品累计 ≤2000 字）。网页 HTML、知网 / Google Books 页面不要整篇存，
   只存摘录——与 `_tools/文献检索器说明.md` §3 的出版社 PDF 政策一致。
4. **读不到正文就说读不到**：付费墙 / 403 / 只有摘要时，在 `notes` 记「access: blocked，仅有摘要」，
   正文里标注「据摘要」，不得当作已读全文。
5. **不可靠来源也要留痕**：查过但结论是「不能用」的来源，同样记一条 `reliability: unverified` +
   `notes` 写排除原因，免得下一轮再被它误导。
6. **存档不是装饰**：`used_in` 里的每个文件必须真有对应论述；`check --strict` 会对缺摘录/缺 notes 报错。

### 1.7 交付前自检

    python _tools/sources.py check --strict

- 有错误 → 先修再交付；
- 提示（`[W001]` 文件不存在、`[W004]` 日期格式）可解释一句后放过；
- 用户没问就不列存档清单；被问到「来源 / 出处 / 存档」时才用 `list` / `stats` 汇报。

## 2. 其它既有约定（摘要，细节见 CONTRIBUTING.md）

- **只改源文件**，页面由 `_tools/regen_all.sh` 生成；改了源文件要重跑并提交产物。
- 三语（zh-CN / en / es）文案与 i18n key 必须同步。
- 提交前：`python _tools/check_site.py --ci`、`python _tools/check_liquid.py`。
- `_species/*.md` 的 `<!-- AUTO:BEGIN -->` 与 `<!-- AUTO:END -->` 之间不要手改。
- 外部权威库缓存（`_data/authority_links.json` 等）只在需要刷新时跑，刷完必须重跑 `build_name_issues.py`。
