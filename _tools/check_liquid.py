#!/usr/bin/env python3
"""Liquid 模板静态检查：抓语法类错误，让 CI 在 Jekyll 之前就给出可读的 file:line。

为什么需要这个脚本
------------------
Liquid 4（GitHub Pages 用的是 4.0.4）在**解析阶段**就会因为一个语法错的标签
直接让整个构建失败，错误形如：

    Liquid Exception: Liquid syntax error (.../_includes/x.html line 3):
    Syntax Error in 'capture' - Valid syntax: capture [var]

上面这个真实案例里，缺变量名的 capture 标签写在一个 comment 注释块内部——
**注释块内部依然会被 Liquid 解析**，所以「写给人看的示例」同样会炸掉构建。
这类错误只有构造一次真实构建才会暴露，代价是几分钟加一条 Ruby 堆栈；
本脚本把同一类错误提前到毫秒级，不需要 Ruby，也不联网。

检查项
------
1. 标签定界符 {% %} 与变量定界符 {{ }} 各自开闭数量一致；
2. 成对标签（if/unless/for/case/capture/comment/tablerow/form/block/
   highlight/schema）开闭配对，且闭合标签不带参数；
3. 标签参数个数：capture/increment/decrement 必须恰好 1 个；
   if/unless 必须有条件；for 必须形如 x in y；assign 必须形如 a = b；
   include 必须带文件名；
4. **注释块内部一并检查**——这是本脚本存在的主要原因，与 Liquid 4 行为一致。

例外：raw 块内部不解析，脚本同样跳过。

用法
----
    python _tools/check_liquid.py            # 检查全站，退出码 0 = 通过
    python _tools/check_liquid.py --quiet    # 只输出失败项

退出码：0 无问题；1 有问题（逐条打印 file:line: 说明）。
"""

from __future__ import annotations

import argparse
import os
import re
import sys

# 成对标签：开标签 -> 闭标签
PAIRS = {
    "if": "endif",
    "unless": "endunless",
    "for": "endfor",
    "case": "endcase",
    "capture": "endcapture",
    "comment": "endcomment",
    "tablerow": "endtablerow",
    "form": "endform",
    "block": "endblock",
    "highlight": "endhighlight",
    "schema": "endschema",
}
END_TAGS = set(PAIRS.values())
ONE_ARG_TAGS = {"capture", "increment", "decrement"}

# 不进入检查的目录：VCS、构建产物、依赖，以及生成链/工作流脚本自带的说明文档
SKIP_DIRS = {
    ".git",
    "_site",
    "node_modules",
    "vendor",
    "downloads",
    "_tmp",
    "_tools",
    ".github",
    ".tmp",
    ".tmp_pkgs",
}

TAG_RE = re.compile(r"{%(.*?)%}|{{(.*?)}}", re.S)
RAW_RE = re.compile(r"{%-?\s*raw\s*-?%}.*?{%-?\s*endraw\s*-?%}", re.S)


def _strip(raw: str) -> str:
    """去掉首尾的 Liquid 空白控制标记与空格。"""
    body = raw.strip()
    if body.startswith("-"):
        body = body[1:]
    if body.endswith("-"):
        body = body[:-1]
    return body.strip()


def check_text(src: str) -> list:
    """返回该文本里的 Liquid 语法问题（不带文件名）。"""
    problems: list = []

    open_tag = len(re.findall(r"{%", src))
    close_tag = len(re.findall(r"%}", src))
    if open_tag != close_tag:
        problems.append("标签定界符不配对：%d 个 {%% vs %d 个 %%}" % (open_tag, close_tag))
    open_var = len(re.findall(r"{{", src))
    close_var = len(re.findall(r"}}", src))
    if open_var != close_var:
        problems.append("变量定界符不配对：%d 个 {{ vs %d 个 }}" % (open_var, close_var))

    # Liquid 4 只在 raw 块里跳过解析；comment 块内部照常解析（因此不做剥离）
    clean = RAW_RE.sub(lambda m: "\n" * m.group(0).count("\n"), src)

    stack: list = []
    for match in TAG_RE.finditer(clean):
        if match.group(1) is None:  # {{ ... }}：上面已统计定界符
            continue
        body = _strip(match.group(1))
        line = clean.count("\n", 0, match.start()) + 1
        parts = body.split()
        name = parts[0] if parts else ""
        args = parts[1:]

        if name in PAIRS:
            stack.append((name, line))
            if name in ONE_ARG_TAGS and len(args) != 1:
                problems.append(
                    "第 %d 行：%s 需要恰好 1 个参数，实际 %d 个（%r）" % (line, name, len(args), body[:60])
                )
            elif name in ("if", "unless") and not args:
                problems.append("第 %d 行：%s 缺条件（%r）" % (line, name, body[:60]))
            elif name == "for" and not re.match(r"^[\w.\[\]'\"]+\s+in\s+\S", body[3:].strip()):
                problems.append("第 %d 行：for 语法应为 x in y（%r）" % (line, body[:60]))
        elif name in END_TAGS:
            if args:
                problems.append("第 %d 行：%s 不接受参数（%r）" % (line, name, body[:60]))
            if not stack:
                problems.append("第 %d 行：多余的 %s" % (line, name))
            else:
                opener, opener_line = stack.pop()
                if PAIRS[opener] != name:
                    problems.append(
                        "第 %d 行：%s 被 %s 关闭（应为 %s）" % (opener_line, opener, name, PAIRS[opener])
                    )
        elif name == "assign":
            if not re.match(r"^[\w.-]+\s*=", body[6:].strip()):
                problems.append("第 %d 行：assign 语法应为 x = y（%r）" % (line, body[:60]))
        elif name == "include" and not args:
            problems.append("第 %d 行：include 缺文件名" % line)

    for opener, opener_line in stack:
        problems.append("第 %d 行：%s 没有闭合（缺 %s）" % (opener_line, opener, PAIRS[opener]))

    return problems


def iter_files(roots: list) -> list:
    """列出需要检查的文件：_layouts / _includes 全部，加站内带 front matter 的页面。"""
    found: list = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
            for name in sorted(filenames):
                if not name.endswith((".md", ".html")):
                    continue
                path = os.path.join(dirpath, name)
                rel = path.replace(os.sep, "/")
                if rel.startswith("./"):
                    rel = rel[2:]
                if not rel.startswith("_"):
                    try:
                        with open(path, encoding="utf-8", errors="replace") as handle:
                            if not handle.read(4).startswith("---"):
                                continue  # 没有 front matter = 静态文件，Liquid 不解析
                    except OSError:
                        continue
                found.append(rel)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Liquid 模板静态检查（成对标签 / 参数 / 定界符）")
    parser.add_argument("--quiet", action="store_true", help="只输出失败项")
    parser.add_argument("paths", nargs="*", help="要检查的根目录，默认当前目录")
    args = parser.parse_args(argv)

    roots = args.paths or ["."]
    files = iter_files(roots)
    failures = 0
    for rel in files:
        try:
            with open(rel, encoding="utf-8", errors="replace") as handle:
                src = handle.read()
        except OSError as exc:
            print("%s: 读取失败：%s" % (rel, exc), file=sys.stderr)
            failures += 1
            continue
        problems = check_text(src)
        if problems:
            failures += 1
            print(rel)
            for problem in problems[:10]:
                print("    " + problem)
            if len(problems) > 10:
                print("    … 另有 %d 条" % (len(problems) - 10))

    if failures:
        print("\n失败：%d/%d 个文件有 Liquid 语法问题（见上）。" % (failures, len(files)), file=sys.stderr)
        print("提示：comment 块内部同样会被 Liquid 解析，示例标签要么参数完整、要么用 raw 包裹。", file=sys.stderr)
        return 1
    if not args.quiet:
        print("Liquid 检查通过：%d 个文件（成对标签、参数个数、定界符）。" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
