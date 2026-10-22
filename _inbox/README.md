# 这个文件夹怎么用（_inbox）

把 Word 文档（.docx）或纯文本（.txt / .md）放进本文件夹，推送到 GitHub 后，云端会自动把每个文件转成一篇文章，发布到网站的博客页：

https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md/blog/

## 规则

- 文件名建议带日期前缀：2026-10-23-文章标题.docx
  - 不带日期也行，会自动用「提交日期」当作发布日期。
- 标题来源：
  - .docx → 文档里第一个「标题」样式的文字；
  - .txt → 文件第一行；
  - .md → 文件头的 title，或第一个 # 一级标题。
- 支持的内容：
  - .docx → 标题、正文、加粗、斜体、表格、列表；
  - .txt → 纯文本，空行分段；
  - .md → 完整 Markdown（标题 / 加粗 / 表格 / 列表等）。

## 例子

把下面这个文件拖进本文件夹，然后提交（Commit）：

    2026-10-23-关于收录范围.docx

提交后 GitHub 会自动运行流水线，几十秒后这篇文章就会出现在博客页，不需要在本地装任何软件。
