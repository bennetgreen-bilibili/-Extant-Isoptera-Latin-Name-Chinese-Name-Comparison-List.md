
import json, os
ids = {"hodotermopsidae","kalotermitidae","rhinotermitidae","termitidae"}
MARK = '<section class="taxon-section">'
def block(tid):
    return ('{%%- assign fz = site.data.fauna_families["/family/%s/"] -%%}{%%- if fz %%}\n'
            '{%% include fauna-family.html fauna=fz %%}\n{%%- endif %%}\n' % tid)
n = 0
for tid in sorted(ids):
    p = os.path.join("family", tid + ".md")
    t = open(p, encoding="utf-8").read()
    if "fauna-family.html" in t:
        continue
    i = t.find(MARK)
    assert i > 0, p
    t = t[:i] + block(tid) + t[i:]
    open(p, "w", encoding="utf-8", newline="\n").write(t)
    n += 1
print("family patched", n)

# 数据文件
fams = json.load(open("_tmp/dz/out/family.json", encoding="utf-8"))
out = {}
ref = {"/family/hodotermopsidae/": "（原书草白蚁科 Hodotermitidae 一节）",
       "/family/kalotermitidae/": "（原书木白蚁科 Kalotermitidae 一节）",
       "/family/rhinotermitidae/": "（原书鼻白蚁科 Rhinotermitidae 一节）",
       "/family/termitidae/": "（原书白蚁科 Termitidae 一节）"}
for f in fams:
    rec = {k: (f.get(k) or "").strip() for k in ("diagnosis","soldier","alate","worker","biology","distribution","taxonomy_note","en")}
    rec["book_ref"] = ref[f["page"]]
    out[f["page"]] = rec
json.dump(out, open("_data/fauna_families.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("families data", len(out))
