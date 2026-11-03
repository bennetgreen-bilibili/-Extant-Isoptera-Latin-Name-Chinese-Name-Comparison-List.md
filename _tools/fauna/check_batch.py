
"""用法: python _tmp/dz/check_batch.py _tmp/dz/out/batch_03.json [--n 12]
逐条比对改写稿与原文，报告最长共同片段 >= n 的字段（照抄风险）。exit 1 表示仍有问题。
"""
import json, re, sys, difflib, os

N = 12
args = [a for a in sys.argv[1:]]
if "--n" in args:
    i = args.index("--n"); N = int(args[i+1]); del args[i:i+2]
out_path = args[0]
batch_path = os.path.join(os.path.dirname(os.path.dirname(out_path)), "batches", os.path.basename(out_path))
FIELDS = ["soldier", "alate", "worker", "nymph", "biology", "distribution", "taxonomy_note"]

def norm(s):
    return re.sub(r"\s+", "", s or "")

items = json.load(open(out_path, encoding="utf-8"))
batch = {it["page"]: it for it in json.load(open(batch_path, encoding="utf-8"))}
bad = 0
for it in items:
    ex = batch.get(it.get("page"), {})
    for fld in FIELDS:
        a, b = norm(ex.get(fld)), norm(it.get(fld))
        if not a or not b:
            continue
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        m = sm.find_longest_match(0, len(a), 0, len(b))
        if m.size >= N:
            bad += 1
            print("HARD %2d字 %s %s | %s" % (m.size, it["page"], fld, a[m.a:m.a+m.size]))
print("---- hard fields:", bad, "/ entries:", len(items))
sys.exit(1 if bad else 0)