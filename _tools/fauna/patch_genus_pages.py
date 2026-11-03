
import json, os, re
gens = json.load(open("_tmp/dz/gbatches/gbatch_01.json", encoding="utf-8")) + json.load(open("_tmp/dz/gbatches/gbatch_02.json", encoding="utf-8"))
ids = [g["genus_id"] for g in gens]
MARK = '<section class="taxon-section">'
def block(kind, tid):
    return ('{%%- assign fz = site.data.fauna_%s["/%s/%s/"] -%%}{%%- if fz %%}\n'
            '{%% include fauna-%s.html fauna=fz %%}\n{%%- endif %%}\n' % (kind, kind, tid, kind))
changed = 0
for gid in ids:
    p = os.path.join("genus", gid + ".md")
    if not os.path.isfile(p):
        print("MISSING", p); continue
    t = open(p, encoding="utf-8").read()
    if "fauna-genus.html" in t:
        continue
    i = t.find(MARK)
    if i < 0:
        print("NO SECTION", p); continue
    t = t[:i] + block("genus", gid) + t[i:]
    open(p, "w", encoding="utf-8", newline="\n").write(t)
    changed += 1
print("genus patched", changed, "of", len(ids))
