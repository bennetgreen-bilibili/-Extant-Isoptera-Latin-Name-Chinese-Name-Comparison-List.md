
import re, sys, glob, yaml
bad = []
fm = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(\r?\n|$)", re.S)
for path in sorted(glob.glob("**/*.md", recursive=True)):
    if path.startswith(("_site/", ".tmp", "node_modules/")):
        continue
    text = open(path, encoding="utf-8").read()
    m = fm.match(text)
    if not m: continue
    try:
        d = yaml.safe_load(m.group(1))
        if d is not None and not isinstance(d, dict):
            bad.append((path, "NOT_DICT"))
    except Exception as e:
        bad.append((path, "ERR " + str(e).replace("\n", " ")[:200]))
print("md files scanned:", len(glob.glob('**/*.md', recursive=True)))
print("bad front matter:", len(bad))
for p, e in bad[:40]: print(" ", p, "->", e)
try:
    cfg = yaml.safe_load(open("_config.yml", encoding="utf-8"))
    print("config ok, top keys:", len(cfg))
except Exception as e:
    print("CONFIG_ERR", str(e)[:400])
