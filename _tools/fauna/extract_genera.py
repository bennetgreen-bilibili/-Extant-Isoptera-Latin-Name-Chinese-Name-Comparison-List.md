
import re, json, os
raw = open("_tmp/dz/fauna_raw.txt", encoding="utf-8").read()
GEN = re.compile(r"[（(]([一二三四五六七八九十百]+)[）)]\s*([\u4e00-\u9fa5]{1,8}白蚁属)\s*([A-Z][A-Za-z]{3,})")
heads = list(GEN.finditer(raw))
print("genera", len(heads))
# species heads to bound each genus
HEAD = re.compile(r"(?<![\d])(\d{1,3})\s*[\.．]\s*(?=[\u4e00-\u9fa5]{3,12}\s*[A-Z])")
sheads = [m.start() for m in HEAD.finditer(raw)]
pages = []
for fn in os.listdir("_species"):
    if not fn.endswith(".md"): continue
    txt = open(os.path.join("_species", fn), encoding="utf-8").read()
    fm = {}
    if txt.startswith("---"):
        end = txt.find("\n---", 3)
        for line in txt[3:end].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
    pages.append({"fn": fn, "fm": fm})
gid = {}
for p in pages:
    gl = p["fm"].get("genus_latin")
    if gl: gid.setdefault(gl, p["fm"].get("genus_id"))

out = []
for i, m in enumerate(heads):
    start = m.end()
    end = heads[i+1].start() if i+1 < len(heads) else len(raw)
    for s in sheads:
        if start < s < end:
            end = s; break
    body = raw[start:end]
    body = re.sub(r"\s+", " ", body).strip()
    out.append({"i": i, "zh": m.group(2), "latin": m.group(3), "genus_id": gid.get(m.group(3)),
                "body": body[:6000], "chars": len(body)})
print("with page", sum(1 for o in out if o["genus_id"]), "/", len(out))
for o in out:
    print(o["i"], o["zh"], o["latin"], "->", o["genus_id"], o["chars"])
json.dump(out, open("_tmp/dz/genera.json", "w", encoding="utf-8"), ensure_ascii=False)
