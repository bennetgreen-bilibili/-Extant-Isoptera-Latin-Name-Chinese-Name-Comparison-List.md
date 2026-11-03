
import json, re, os
gens = json.load(open("_tmp/dz/genera.json", encoding="utf-8"))
# site genus info from genus/*.md front matter
site = {}
for fn in os.listdir("genus"):
    if not fn.endswith(".md"): continue
    gid = fn[:-3]
    txt = open(os.path.join("genus", fn), encoding="utf-8").read()
    fm = {}
    if txt.startswith("---"):
        end = txt.find("\n---", 3)
        for line in txt[3:end].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
    site[gid] = fm

KEEP = ["Hodotermopsis","Cryptotermes","Kalotermes","Incisitermes","Glyptotermes","Neotermes",
        "Prorhinotermes","Parrhinotermes","Schedorhinotermes","Coptotermes","Reticulitermes",
        "Stylotermes","Microcerotermes","Odontotermes","Hypotermes","Macrotermes","Euhamitermes",
        "Speculitermes","Indotermes","Globitermes","Microtermes","Ancistrotermes","Dicuspiditermes",
        "Sinocapritermes","Pericapritermes","Pseudocapritermes","Hospitalitermes","Arcotermes",
        "Cucurbitermes","Periaciculitermes","Pilotermes","Xiaitermes","Nasutitermes",
        "Sinonasutitermes","Ahmaditermes"]

out = []
for it in gens:
    if it["latin"] not in KEEP or not it["genus_id"]:
        continue
    fm = site.get(it["genus_id"], {})
    out.append({
        "page": "/genus/%s/" % it["genus_id"],
        "genus_id": it["genus_id"],
        "book_zh": it["zh"],
        "book_latin": it["latin"],
        "page_zh": fm.get("title", "").split(" ")[0],
        "family_zh": fm.get("family_zh", ""),
        "family_latin": fm.get("family_latin", ""),
        "body": it["body"],
    })
print("genus entries", len(out))
os.makedirs("_tmp/dz/gbatches", exist_ok=True)
half = 18
for i in range(0, len(out), half):
    chunk = out[i:i+half]
    p = "_tmp/dz/gbatches/gbatch_%02d.json" % (i//half + 1)
    json.dump(chunk, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(p, len(chunk), sum(len(c["body"]) for c in chunk))
