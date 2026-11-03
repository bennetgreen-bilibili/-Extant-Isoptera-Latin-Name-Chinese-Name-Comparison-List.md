
import re, sys, os

PAIRS = {"if":"endif","unless":"endunless","for":"endfor","case":"endcase","capture":"endcapture",
         "comment":"endcomment","raw":"endraw","tablerow":"endtablerow","form":"endform","block":"endblock","highlight":"endhighlight"}

def lint(src):
    s = re.sub(r"{%-?\s*comment\s*-?%}.*?{%-?\s*endcomment\s*-?%}", "", src, flags=re.S)
    s = re.sub(r"{%-?\s*raw\s*-?%}.*?{%-?\s*endraw\s*-?%}", "", s, flags=re.S)
    stack, probs = [], []
    for m in re.finditer(r"{%(.*?)%}|{{(.*?)}}", s, flags=re.S):
        if m.group(1) is None: continue
        body = m.group(1).strip(" -")
        parts = body.split()
        name = parts[0] if parts else ""
        if name in PAIRS: stack.append((name, m.start()))
        elif name in PAIRS.values():
            if not stack: probs.append("unexpected " + name)
            else:
                op, pos = stack.pop()
                if PAIRS[op] != name: probs.append(op + " closed by " + name)
    for op, pos in stack:
        probs.append("unclosed %s at line %d" % (op, s[:pos].count("\n") + 1))
    o = len(re.findall(r"{%", s)) + len(re.findall(r"{{", s))
    c = len(re.findall(r"%}", s)) + len(re.findall(r"}}", s))
    if o != c: probs.append("delims %d!=%d" % (o, c))
    return probs, (o + c)

files = [l.rstrip("\n") for l in open("_tmp_files.txt", encoding="utf-8", errors="surrogateescape") if l.strip()]
checked = 0; bad = []
for f in files:
    if not (f.endswith(".md") or f.endswith(".html")): continue
    if f.startswith(".github/") or f.startswith("_tools/") or f.startswith("node_modules/"): continue
    try:
        src = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    if not src.startswith("---"):
        continue
    checked += 1
    probs, ntok = lint(src)
    if probs:
        bad.append((f, probs[:4], ntok))
print("files with front matter checked:", checked, "| liquid problems:", len(bad))
for f, p, n in bad[:40]:
    print("  ", f, "->", p)
