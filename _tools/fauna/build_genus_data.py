
import json, glob, os
out = {}
for f in sorted(glob.glob("_tmp/dz/gout/gbatch_*.json")):
    for it in json.load(open(f, encoding="utf-8")):
        gid = it.get("genus_id")
        if not gid: continue
        rec = {
            "book_ref": ("（原书%s %s 一节的属级记述重新整理改写）" % (it.get("book_zh") or "", it.get("book_latin") or "")).strip(),
            "book_name": ((it.get("book_zh") or "") + " " + (it.get("book_latin") or "")).strip(),
            "diagnosis": (it.get("diagnosis") or "").strip(),
            "soldier": (it.get("soldier") or "").strip(),
            "alate": (it.get("alate") or "").strip(),
            "worker": (it.get("worker") or "").strip(),
            "biology": (it.get("biology") or "").strip(),
            "distribution": (it.get("distribution") or "").strip(),
            "taxonomy_note": (it.get("taxonomy_note") or "").strip(),
            "en": (it.get("en") or "").strip(),
        }
        if not any(rec[k] for k in ("diagnosis","soldier","alate","worker","biology","distribution")): continue
        out["/genus/%s/" % gid] = rec
json.dump(out, open("_data/fauna_genera.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("genera", len(out), "bytes", os.path.getsize("_data/fauna_genera.json"))
