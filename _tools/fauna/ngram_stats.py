
import json, re, glob, os
FIELDS = ["soldier","alate","worker","nymph","biology","distribution","taxonomy_note"]
def norm(s): return re.sub(r"\s+","",s or "")
def grams(s,n=8):
    s = norm(s)
    return set(s[i:i+n] for i in range(len(s)-n+1))
for f in sorted(glob.glob("_tmp/dz/out_clean/batch_*.json")):
    batch = {it["page"]: it for it in json.load(open("_tmp/dz/batches/"+os.path.basename(f), encoding="utf-8"))}
    items = json.load(open(f, encoding="utf-8"))
    tot = hit = 0
    per = []
    for it in items:
        ex = batch.get(it["page"], {})
        a = set()
        for fld in FIELDS: a |= grams(ex.get(fld))
        b = set()
        for fld in FIELDS: b |= grams(it.get(fld))
        if not b: continue
        c = len(a & b)
        per.append((c/len(b), it["page"]))
        tot += len(b); hit += c
    per.sort(reverse=True)
    print(os.path.basename(f), "containment %.2f" % (hit/tot), "worst:", ["%.2f %s" % p for p in per[:3]])
