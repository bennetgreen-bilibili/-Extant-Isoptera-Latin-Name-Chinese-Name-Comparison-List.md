
import re, json
raw = open("_tmp/dz/fauna_raw.txt", encoding="utf-8").read()
FAM = re.compile(r"([\u4e00-\u9fa5]{2,8}白蚁科)\s*([A-Z][A-Za-z]{5,})")
GEN = re.compile(r"[（(]([一二三四五六七八九十百]+)[）)]\s*([\u4e00-\u9fa5]{1,8}白蚁属)\s*([A-Z][A-Za-z]{3,})")
fams = list(FAM.finditer(raw))
gens = list(GEN.finditer(raw))
print("family hits", [(m.group(1), m.group(2), m.start()) for m in fams][:12])
out = []
for i, m in enumerate(fams):
    start = m.end()
    end = len(raw)
    for g in gens:
        if g.start() > start:
            end = min(end, g.start()); break
    body = re.sub(r"\s+", " ", raw[start:end]).strip()
    out.append({"zh": m.group(1), "latin": m.group(2), "body": body[:5000], "chars": len(body)})
for o in out: print(o["zh"], o["latin"], o["chars"])
json.dump(out, open("_tmp/dz/families.json","w",encoding="utf-8"), ensure_ascii=False)
