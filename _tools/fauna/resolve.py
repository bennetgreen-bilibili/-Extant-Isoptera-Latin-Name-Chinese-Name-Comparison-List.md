
import json, re, unicodedata, collections, os
corp = json.load(open("_tmp/dz/corpus.json", encoding="utf-8"))
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

OVR = {
 10:"Incisitermes inamurai", 24:"Glyptotermes fujianensis", 36:"Glyptotermes nadaensis",
 45:"Glyptotermes yingdeensis", 73:"Schedorhinotermes ganlanbaensis", 81:"Coptotermes cyclocoryphus",
 105:"Reticulitermes brachygnathus", 180:"Reticulitermes longigulus",
 212:"Reticulitermes ampliceps", 213:"Reticulitermes hunanensis", 214:"Reticulitermes mangshanensis",
 215:"Reticulitermes oocephalus", 216:"Reticulitermes oreophilus", 217:"Reticulitermes yingdeensis",
 254:"Microcerotermes periminutus",
 289:"Hypotermes manyunensis", 290:"Hypotermes ruiliensis", 291:"Hypotermes sumatrensis", 292:"Hypotermes yingjiangensis",
 294:"Macrotermes annandalei", 334:"Indotermes hainanensis", 335:"Indotermes luxiensis", 336:"Indotermes yunnanensis",
 354:"Procapritermes huananensis", 355:"Procapritermes zhangfengensis", 382:"Pseudocapritermes jiangchengensis",
 396:"Nasutitermes communis", 397:"Nasutitermes orthonasus",
 399:"Ahmaditermes dinghuensis", 401:"Ahmaditermes parafulvus", 402:"Nasopilotermes jiangxiensis",
 451:"Nasutitermes bashanensis", 452:"Nasutitermes changningensis", 454:"Nasutitermes huangshanensis",
 455:"Nasutitermes longwangshanensis", 456:"Nasutitermes machengensis", 457:"Nasutitermes qimenensis",
 458:"Nasutitermes shangchengensis", 459:"Nasutitermes tianmuensis", 460:"Nasutitermes xingshanensis",
 467:"Ahmaditermes lipingensis",
}
SKIP = {4, 57, 67, 305, 356, 375, 392, 78, 80, 87, 95, 98, 100, 166, 259, 276, 383, 400, 403}

def norm(s): return re.sub(r"[^a-z ]", " ", unicodedata.normalize("NFKD", s or "")).lower()
byLatin = {}
for p in pages:
    k = " ".join(norm(p["fm"].get("latin", "")).split())
    byLatin.setdefault(k, []).append(p)
synMap = {}
for p in pages:
    for s in (p["fm"].get("synonyms", "") or "").split(";"):
        k = " ".join(norm(s).split())
        if k: synMap.setdefault(k, []).append(p)
def zhn(s):
    s = re.sub(r"[^\u4e00-\u9fa5]", "", s or "")
    return s.replace("蚊", "蚁")
zhMap = {}
for p in pages:
    z = zhn(p["fm"].get("zh", ""))
    if z: zhMap.setdefault(z, []).append(p)

GENMAP = {"蔡白蚁属":"Reticulitermes","壤白蚁属":"Hypotermes","奇象白蚁属":"Nasutitermes","歧颚白蚁属":"Nasutitermes",
 "近瓢白蚁属":"Ahmaditermes","马扭白蚁属":"Procapritermes","棘白蚁属":"Nasopilotermes","华白蚁属":"Indotermes",
 "木白蚁属":"Incisitermes"}

def find_page(e):
    if e["n"] in OVR:
        return byLatin.get(" ".join(norm(OVR[e["n"]]).split())), "override"
    k = " ".join(norm(e.get("latin") or "").split()).split()
    key = " ".join(k[:2]) if len(k) >= 2 else ""
    if key in byLatin: return byLatin[key], "latin"
    if key in synMap: return synMap[key], "synonym"
    z = zhn(e.get("zh") or "")
    if z in zhMap: return zhMap[z], "zh"
    gz = (e.get("gen") or {}).get("zh", "")
    ep = k[1] if len(k) >= 2 else ""
    if gz in GENMAP and len(ep) >= 5:
        for p in pages:
            if p["fm"].get("genus_latin") == GENMAP[gz]:
                pl = norm(p["fm"].get("latin", "")).split()
                if len(pl) >= 2 and pl[1][:5] == ep[:5]:
                    return [p], "genmap"
    return None, "none"

out, unresolved = [], []
for e in corp:
    if e["n"] in SKIP: continue
    ps, via = find_page(e)
    if not ps:
        unresolved.append({"n": e["n"], "zh": e.get("zh"), "latin": e.get("latin"), "head": e["raw_head"][:60]}); continue
    p = ps[0]
    out.append({
        "book_n": e["n"], "via": via,
        "page": "/species/" + p["fn"].replace(".md", "") + "/",
        "page_latin": p["fm"].get("latin", ""), "page_zh": p["fm"].get("zh", ""),
        "page_author": p["fm"].get("author_year", ""),
        "book_zh": e.get("zh") or "", "book_latin": e.get("latin") or "",
        "g_zh": (e.get("gen") or {}).get("zh", ""), "g_latin": (e.get("gen") or {}).get("latin", ""),
        "f_latin": (e.get("fam") or {}).get("latin", "") if isinstance(e.get("fam"), dict) else "",
        "soldier": e["soldier"], "alate": e["alate"], "worker": e["worker"], "nymph": e["nymph"],
        "syn": e["syn"], "dist": e["dist"], "host": e["host"], "other": e["other"],
    })
c = collections.Counter(o["page"] for o in out)
print("resolved", len(out), "unresolved", len(unresolved), "dups", [(k, v) for k, v in c.items() if v > 1])
print("via", collections.Counter(o["via"] for o in out))
print("unresolved list", [(u["n"], u["zh"]) for u in unresolved])
json.dump(out, open("_tmp/dz/work.json", "w", encoding="utf-8"), ensure_ascii=False)
print("avg source chars", sum(len(o["soldier"])+len(o["alate"])+len(o["worker"]) for o in out)//len(out))