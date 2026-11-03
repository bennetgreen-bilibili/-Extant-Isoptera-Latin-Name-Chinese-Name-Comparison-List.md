
import json, urllib.request, sys, zipfile, io, os
meta = json.load(urllib.request.urlopen("https://pypi.org/pypi/PyYAML/json", timeout=30))
vers = meta["info"]["version"]
print("latest", vers)
files = meta["releases"][vers]
cands = [f for f in files if f["filename"].endswith(".whl") and "cp314" in f["filename"] and "win_amd64" in f["filename"]]
print("cp314 win wheels:", [f["filename"] for f in cands])
if not cands:
    cands = [f for f in files if f["filename"].endswith(".whl") and "win_amd64" in f["filename"]]
    print("fallback:", [f["filename"] for f in cands][:5])
if cands:
    url = cands[0]["url"]; print("downloading", cands[0]["filename"])
    data = urllib.request.urlopen(url, timeout=60).read()
    os.makedirs(".tmp_pkgs", exist_ok=True)
    zipfile.ZipFile(io.BytesIO(data)).extractall(".tmp_pkgs")
    print("extracted; yaml dir:", os.path.isdir(".tmp_pkgs/yaml"))
