
import json, re, sys, difflib
OUTF = ["soldier","alate","worker","nymph","biology","distribution","taxonomy_note","diagnosis"]
LIMIT = 30
def norm(s): return re.sub(r"\s+","", s or "")
b = sys.argv[1]
items = json.load(open("_tmp/dz/out_clean/batch_%s.json" % b, encoding="utf-8"))
srcs = {it["page"]: it for it in json.load(open("_tmp/dz/batches/batch_%s.json" % b, encoding="utf-8"))}
rows = []
for it in items:
    ex = srcs[it["page"]]
    for f in OUTF:
        bb = norm(it.get(f))
        if not bb: continue
        for sk in ("soldier","alate","worker","nymph","biology","distribution","taxonomy_note"):
            a = norm(ex.get(sk))
            if not a: continue
            for m in difflib.SequenceMatcher(None, a, bb, autojunk=False).get_matching_blocks():
                if m.size >= LIMIT:
                    rows.append((m.size, it["page"], f, bb[m.b:m.b+m.size]))
rows.sort(reverse=True)
print("runs>=%d: %d" % (LIMIT, len(rows)))
for r in rows: print("%d\t%s\t%s\t%s" % r)
