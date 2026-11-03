
import json, re, difflib
N = 12
fams = json.load(open("_tmp/dz/out/family.json", encoding="utf-8"))
diag = {d["zh"]: d["body"] for d in json.load(open("_tmp/dz/fam_diag.json", encoding="utf-8"))}
key = {"/family/hodotermopsidae/": "草白蚁科", "/family/kalotermitidae/": "木白蚁科",
       "/family/rhinotermitidae/": "鼻白蚁科", "/family/termitidae/": "白蚁科"}
def norm(s): return re.sub(r"\s+", "", s or "")
bad = 0
for f in fams:
    a = norm(diag.get(key[f["page"]], ""))
    for fld in ("diagnosis","soldier","alate","worker","biology","distribution","taxonomy_note"):
        b = norm(f.get(fld))
        if not a or not b: continue
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        m = sm.find_longest_match(0, len(a), 0, len(b))
        if m.size >= N:
            bad += 1; print("HARD", m.size, f["page"], fld, "|", a[m.a:m.a+m.size])
print("hard", bad)
