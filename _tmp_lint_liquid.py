
import glob, re, sys

PAIRS = {
    "if": "endif", "unless": "endunless", "for": "endfor", "case": "endcase",
    "capture": "endcapture", "comment": "endcomment", "raw": "endraw",
    "tablerow": "endtablerow", "form": "endform", "block": "endblock",
    "highlight": "endhighlight",
}
KNOWN_SINGLE = {"assign","include","increment","decrement","cycle","break","continue","echo","liquid","render"}

def lint(path):
    src = open(path, encoding="utf-8").read()
    # strip comment/raw bodies (they may hold arbitrary text)
    src2 = re.sub(r"{%-?\s*comment\s*-?%}.*?{%-?\s*endcomment\s*-?%}", "", src, flags=re.S)
    src2 = re.sub(r"{%-?\s*raw\s*-?%}.*?{%-?\s*endraw\s*-?%}", "", src2, flags=re.S)
    stack = []
    problems = []
    for m in re.finditer(r"{%(.*?)%}|{{(.*?)}}", src2, flags=re.S):
        tag = m.group(1)
        if tag is None:
            continue
        body = tag.strip(" -")
        name = body.split()[0] if body.split() else ""
        if name in PAIRS:
            stack.append((name, m.start()))
        elif name.startswith("end"):
            if name in PAIRS.values():
                if not stack:
                    problems.append(f"unexpected {name}")
                else:
                    op, pos = stack.pop()
                    if PAIRS[op] != name:
                        problems.append(f"{op} closed by {name}")
        # closing handled; singles ignored
    for op, pos in stack:
        line = src2[:pos].count("\n") + 1
        problems.append(f"unclosed {op} at line {line}")
    # unterminated opening delimiters
    opens = len(re.findall(r"{%", src2)) + len(re.findall(r"{{", src2))
    closes = len(re.findall(r"%}", src2)) + len(re.findall(r"}}", src2))
    if opens != closes:
        problems.append(f"delimiter count {opens}!={closes}")
    return problems

files = sorted(glob.glob("_layouts/*.html") + glob.glob("_includes/*.html") + glob.glob("*.md") + glob.glob("en/*.md") + glob.glob("es/*.md"))
total = 0
for f in files:
    p = lint(f)
    if p:
        total += 1
        print(f, "->", "; ".join(p[:5]))
print("checked", len(files), "files; problems in", total)
