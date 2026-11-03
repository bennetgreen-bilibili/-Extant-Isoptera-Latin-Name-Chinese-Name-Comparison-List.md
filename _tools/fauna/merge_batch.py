
"""清理 out/batch_NN.json：按 page 去重（保留与原文最长共同片段最短的一份），输出 out_clean/batch_NN.json"""
import json, re, os, glob, difflib

FIELDS = ["soldier", "alate", "worker", "nymph", "biology", "distribution", "taxonomy_note"]

def norm(s): return re.sub(r"\s+", "", s or "")

def score(item, ex):
    worst = 0
    for fld in FIELDS:
        a, b = norm(ex.get(fld)), norm(item.get(fld))
        if not a or not b: continue
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        m = sm.find_longest_match(0, len(a), 0, len(b))
        worst = max(worst, m.size)
    return worst

os.makedirs("_tmp/dz/out_clean", exist_ok=True)
for f in sorted(glob.glob("_tmp/dz/out/batch_*.json")):
    name = os.path.basename(f)
    batch = {it["page"]: it for it in json.load(open("_tmp/dz/batches/" + name, encoding="utf-8"))}
    try:
        items = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print(name, "BAD", e); continue
    best = {}
    for it in items:
        p = it.get("page")
        if p not in batch: continue
        s = score(it, batch[p])
        if p not in best or s < best[p][0] or (s == best[p][0] and len(json.dumps(it)) > len(json.dumps(best[p][1]))):
            best[p] = (s, it)
    out = [best[p][1] for p in batch if p in best]
    json.dump(out, open("_tmp/dz/out_clean/" + name, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hs = [p for p in best if best[p][0] >= 12]
    print(name, "entries", len(items), "-> unique", len(out), "/", len(batch), "hard pages", len(hs))
