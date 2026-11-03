
"""统一验收：python _tmp/dz/verify.py <out.json> --src <batch.json>
PASS：单段最长共同片段 < 30 字 且 8-gram containment < 0.25 且 条数/页面齐全无重复（属级 src 用 body 字段）
"""
import json, re, sys, difflib

OUTF = ["soldier","alate","worker","nymph","biology","distribution","taxonomy_note","diagnosis"]
LIMIT = 30
MAXCONT = 0.25

def norm(s): return re.sub(r"\s+","", s or "")

def grams(s, n=8):
    s = norm(s)
    return set(s[i:i+n] for i in range(len(s)-n+1))

def main():
    out = sys.argv[1]
    src = sys.argv[sys.argv.index("--src")+1]
    items = json.load(open(out, encoding="utf-8"))
    srcs = {it["page"]: it for it in json.load(open(src, encoding="utf-8"))}
    seen, dup = set(), []
    tot = hit = 0
    bad = []
    for it in items:
        p = it.get("page")
        if p in seen: dup.append(p)
        seen.add(p)
        ex = srcs.get(p)
        if not ex: continue
        src_texts = [v for k, v in ex.items() if isinstance(v, str) and k in ("soldier","alate","worker","nymph","biology","distribution","taxonomy_note","diagnosis","body")]
        out_texts = [(f, it.get(f)) for f in OUTF]
        a_all, b_all = set(), set()
        for t in src_texts: a_all |= grams(t)
        for f, t in out_texts: b_all |= grams(t)
        if b_all:
            tot += len(b_all); hit += len(a_all & b_all)
        worst = (0, "", "")
        for sf in src_texts:
            a = norm(sf)
            if not a: continue
            for f, t in out_texts:
                b = norm(t)
                if not b: continue
                m = difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0,len(a),0,len(b))
                if m.size > worst[0]:
                    worst = (m.size, p + ":" + f, b[m.b:m.b+m.size])
        if worst[0] >= LIMIT:
            bad.append(worst)
    missing = [p for p in srcs if p not in seen]
    cont = hit/tot if tot else 0
    print("entries %d / src %d | dup %d | missing %d" % (len(items), len(srcs), len(dup), len(missing)))
    print("8-gram containment %.2f (limit %.2f)" % (cont, MAXCONT))
    for h in sorted(bad, reverse=True)[:20]:
        print("LONG %d字 %s | %s" % h)
    if missing: print("MISSING", missing[:10])
    ok = (not bad) and (not missing) and (not dup) and cont < MAXCONT
    print("VERDICT:", "PASS" if ok else "FAIL")
main()
