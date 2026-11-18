# -*- coding: utf-8 -*-
"""从《中国动物志》等翅目卷提取量度表 → _data/fauna_measurements.json。

条目按「书名号 N + 中文名」与 _data/fauna_species.json 的 book_n/book_name 对齐，
再在条目范围内取「量度」表。严格 QC：项目名须映射到术语表，数值须为有序区间/整数。
不合格表与原因写 _tmp/_measure_qc.txt。
"""
import io, os, re, json, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LIB = os.path.join(ROOT, "_unpublished", "文库", "中国动物志-昆虫纲-第十七卷-等翅目")

NUM_ENTRY = re.compile(r"^\s*(\d{1,3})\s*[.、]\s*(.+)$")
GENUS_WORD = re.compile(r"\b[A-Z][a-z]{2,}\b")
SPECIES_WORD = re.compile(r"\b[a-z]{3,}\b")


def has_binomial(text):
    """拉丁双名（允许 Coptotermes (P.) formosanus 这类亚属括号）。"""
    return bool(GENUS_WORD.search(text)) and bool(SPECIES_WORD.search(text))

TERMS = collections.OrderedDict([
    ("body_length",              ("体长", "Body length", "Longitud del cuerpo", "mm")),
    ("body_length_with_wings",   ("体长（连翅）", "Body length with wings", "Longitud con alas", "mm")),
    ("body_length_without_wings",("体长（不连翅）", "Body length without wings", "Longitud sin alas", "mm")),
    ("head_length_mandible_base",("头长至上颚基", "Head length to mandible base", "Longitud de la cabeza hasta la base de las mandíbulas", "mm")),
    ("head_length_with_mandibles",("头长连上颚", "Head length with mandibles", "Longitud de la cabeza con mandíbulas", "mm")),
    ("head_length_without_mandibles",("头长不连上颚", "Head length without mandibles", "Longitud de la cabeza sin mandíbulas", "mm")),
    ("head_length_labrum_tip",   ("头长至上唇端", "Head length to labrum tip", "Longitud de la cabeza hasta el ápice del labro", "mm")),
    ("head_length_nasal_tip",    ("头长至鼻端", "Head length to nasus tip", "Longitud de la cabeza hasta el ápice del naso", "mm")),
    ("head_length_with_nasus",   ("头长连象鼻", "Head length with nasus", "Longitud de la cabeza con naso", "mm")),
    ("head_length_without_nasus",("头长不连象鼻", "Head length without nasus", "Longitud de la cabeza sin naso", "mm")),
    ("head_max_width",           ("头最宽", "Maximum head width", "Anchura máxima de la cabeza", "mm")),
    ("head_width",               ("头宽", "Head width", "Anchura de la cabeza", "mm")),
    ("head_width_with_eyes",     ("头宽（连眼）", "Head width with eyes", "Anchura de la cabeza con ojos", "mm")),
    ("head_height",              ("头高", "Head height", "Altura de la cabeza", "mm")),
    ("head_height_without_gula", ("头高（不连后颏）", "Head height without gula", "Altura de la cabeza sin gula", "mm")),
    ("head_width_mandible_base", ("头在颚基宽", "Head width at mandible base", "Anchura de la cabeza en la base de las mandíbulas", "mm")),
    ("head_width_behind_antennae",("头在触角后缘宽", "Head width behind antennal sockets", "Anchura de la cabeza tras las antenas", "mm")),
    ("left_mandible_length",     ("左上颚长", "Left mandible length", "Longitud de la mandíbula izquierda", "mm")),
    ("right_mandible_length",    ("右上颚长", "Right mandible length", "Longitud de la mandíbula derecha", "mm")),
    ("labrum_length",            ("上唇长", "Labrum length", "Longitud del labro", "mm")),
    ("labrum_width",             ("上唇宽", "Labrum width", "Anchura del labro", "mm")),
    ("postmentum_length",        ("后颏长", "Postmentum length", "Longitud del postmentón", "mm")),
    ("postmentum_max_width",     ("后颏最宽", "Postmentum maximum width", "Anchura máxima del postmentón", "mm")),
    ("postmentum_min_width",     ("后颏最狭", "Postmentum minimum width", "Anchura mínima del postmentón", "mm")),
    ("postmentum_width",         ("后颏宽", "Postmentum width", "Anchura del postmentón", "mm")),
    ("hind_tibia_length",        ("后足胫节长", "Hind tibia length", "Longitud de la tibia posterior", "mm")),
    ("hind_femur_length",        ("后足腿节长", "Hind femur length", "Longitud del fémur posterior", "mm")),
    ("hind_femur_width",         ("后足腿节宽", "Hind femur width", "Anchura del fémur posterior", "mm")),
    ("pronotum_length",          ("前胸背板长", "Pronotum length", "Longitud del pronoto", "mm")),
    ("pronotum_mid_length",      ("前胸背板中长", "Pronotum mid-length", "Longitud media del pronoto", "mm")),
    ("pronotum_max_width",       ("前胸背板最宽", "Pronotum maximum width", "Anchura máxima del pronoto", "mm")),
    ("pronotum_width",           ("前胸背板宽", "Pronotum width", "Anchura del pronoto", "mm")),
    ("mesonotum_width",          ("中胸背板宽", "Mesonotum width", "Anchura del mesonoto", "mm")),
    ("metanotum_width",          ("后胸背板宽", "Metanotum width", "Anchura del metanoto", "mm")),
    ("eye_long_diameter",        ("复眼长径", "Eye long diameter", "Diámetro mayor del ojo", "mm")),
    ("eye_short_diameter",       ("复眼短径", "Eye short diameter", "Diámetro menor del ojo", "mm")),
    ("ocellus_long_diameter",    ("单眼长径", "Ocellus long diameter", "Diámetro mayor del ocelo", "mm")),
    ("ocellus_short_diameter",   ("单眼短径", "Ocellus short diameter", "Diámetro menor del ocelo", "mm")),
    ("ocellus_length",           ("单眼长", "Ocellus length", "Longitud del ocelo", "mm")),
    ("ocellus_width",            ("单眼宽", "Ocellus width", "Anchura del ocelo", "mm")),
    ("ocellus_eye_distance",     ("单复眼间距", "Ocellus–eye distance", "Distancia ocelo–ojo", "mm")),
    ("eye_head_lower_margin",    ("复眼至头下缘距", "Eye to lower head margin", "Distancia ojo–margen inferior de la cabeza", "mm")),
    ("forewing_scale_length",    ("前翅鳞长", "Forewing scale length", "Longitud de la escama del ala anterior", "mm")),
    ("hindwing_scale_length",    ("后翅鳞长", "Hindwing scale length", "Longitud de la escama del ala posterior", "mm")),
    ("forewing_length",          ("前翅长", "Forewing length", "Longitud del ala anterior", "mm")),
    ("wing_length",              ("翅长", "Wing length", "Longitud del ala", "mm")),
    ("nasus_length",             ("鼻长", "Nasus length", "Longitud del naso", "mm")),
    ("antennal_segments",        ("触角节数", "Antennal segments", "Segmentos antenales", "count")),
])

VARIANTS = {
    "体长": "body_length", "全长": "body_length", "体全长": "body_length",
    "体长连翅": "body_length_with_wings", "头长连翅": None,
    "体长不连翅": "body_length_without_wings", "体长(不连翅)": "body_length_without_wings",
    "头长至上颚基": "head_length_mandible_base", "头长至颚基": "head_length_mandible_base",
    "头长至颚端": "head_length_mandible_base", "头长(至上颚基)": "head_length_mandible_base",
    "头长(至颚基)": "head_length_mandible_base", "头长至上颚基端": "head_length_mandible_base",
    "头长连上颚": "head_length_with_mandibles", "头长不连上颚": "head_length_without_mandibles",
    "头长至上唇端": "head_length_labrum_tip",
    "头长至鼻端": "head_length_nasal_tip",
    "头长连象鼻": "head_length_with_nasus", "头长不连鼻": "head_length_without_nasus",
    "头最宽": "head_max_width", "头宽": "head_width", "头宽连眼": "head_width_with_eyes",
    "头连复眼宽": "head_width_with_eyes",
    "头高": "head_height", "头高不连后颏": "head_height_without_gula",
    "头在颚基宽": "head_width_mandible_base", "头在触角后缘宽": "head_width_behind_antennae",
    "左上颚长": "left_mandible_length", "右上颚长": "right_mandible_length",
    "上唇长": "labrum_length", "上唇宽": "labrum_width",
    "后颏长": "postmentum_length", "后颏中长": "postmentum_length",
    "后颏最宽": "postmentum_max_width", "后颏最狭": "postmentum_min_width",
    "后颏宽": "postmentum_width", "后颏狭": "postmentum_min_width",
    "后足胫节长": "hind_tibia_length", "后胫长": "hind_tibia_length",
    "后足腿节长": "hind_femur_length", "后足腿节宽": "hind_femur_width",
    "前胸背板长": "pronotum_length", "前胸背板中长": "pronotum_mid_length",
    "前胸背板最宽": "pronotum_max_width", "前胸背板宽": "pronotum_width",
    "中胸背板宽": "mesonotum_width", "后胸背板宽": "metanotum_width",
    "复眼长径": "eye_long_diameter", "复眼短径": "eye_short_diameter",
    "复眼长": "eye_long_diameter",
    "单眼长径": "ocellus_long_diameter", "单眼短径": "ocellus_short_diameter",
    "单眼长": "ocellus_length", "单眼宽": "ocellus_width",
    "单复眼间距": "ocellus_eye_distance", "单复眼距": "ocellus_eye_distance",
    "复眼至头下缘距": "eye_head_lower_margin", "复眼距头下缘": "eye_head_lower_margin",
    "前翅鳞长": "forewing_scale_length", "后翅鳞长": "hindwing_scale_length",
    "前翅长": "forewing_length", "翅长": "wing_length",
    "鼻长": "nasus_length", "触角节数": "antennal_segments",
}

FIX = {
    "后频长": "后颏长", "后频最宽": "后颏最宽", "后频最狭": "后颏最狭", "后频宽": "后颏宽",
    "后频狭": "后颏最狭", "后须长": "后颏长", "后须最宽": "后颏最宽",
    "后额长": "后颏长", "后颏最狄": "后颏最狭", "后颏最窄": "后颏最狭",
    "前胸背中长": "前胸背板中长", "前胸背宽": "前胸背板宽",
    "上屑长": "上唇长", "⊥唇长": "上唇长",
}


def norm_key(s):
    s = re.sub(r"\s+", "", s)
    s = s.replace("（", "(").replace("）", ")")
    s = FIX.get(s, s)
    return VARIANTS.get(s)


def norm_value(v):
    s = v.replace(",", ".").replace("，", ".").replace("～", "-").replace("~", "-")
    s = s.replace("—", "-").replace("–", "-").replace("‐", "-").replace("−", "-").replace("一", "-")
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"-{2,}", "-", s)
    if not s:
        return None, "empty"
    if "(" in s or ")" in s:
        return s, "paren"
    m = re.fullmatch(r"(\d+\.\d{2})(\d+\.\d{2})", s)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        return ("%s–%s" % (m.group(1), m.group(2))), ("ok" if a < b else "reverse")
    if re.fullmatch(r"\d+", s):
        return s, "ok"
    if re.fullmatch(r"\d+\.\d+", s):
        return s, "ok"
    m = re.fullmatch(r"(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)", s)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        if a >= b:
            return s, "reverse"
        return "%s–%s" % (m.group(1), m.group(2)), "ok"
    return s, "shape"


HEADER_CHARS = "项目日范围平均量度 \t()（）mm"


def is_header_line(s):
    """「项 目 范 围 平 均 项 目 量 度」这类表头被误当量度标题时返回 True。"""
    rest = s
    for ch in HEADER_CHARS:
        rest = rest.replace(ch, "")
    return not rest.strip()


def fix_mm(s):
    """OCR 掉小数点的毫米值：047 → 0.47、125 → 1.25。"""
    if "." in s or not s.isdigit():
        return s
    n = int(s)
    x = n / 100.0
    if 0.02 <= x <= 40:
        return "%.2f" % x
    x = n / 10.0
    if 0.02 <= x <= 40 and n >= 100:
        return "%.1f" % x
    return s


def find_entries(files, book_map):
    """按 book_n + 中文名定位条目行；返回 {(file, line): entry_no} 与各自区间。"""
    hits = {}
    for fn in files:
        lines = io.open(os.path.join(LIB, fn), encoding="utf-8", errors="replace").read().split("\n")
        for i, ln in enumerate(lines):
            m = NUM_ENTRY.match(ln)
            if not m:
                continue
            n = int(m.group(1))
            if n not in book_map:
                continue
            zh = book_map[n]
            body = m.group(2)
            if zh in body and has_binomial(body):
                hits.setdefault(n, []).append((fn, i))
    return hits


def main():
    fauna = json.load(io.open(os.path.join(ROOT, "_data", "fauna_species.json"), encoding="utf-8"))
    book_map = {}
    url_by_n = {}
    for url, rec in fauna.items():
        try:
            n = int(rec.get("book_n") or 0)
        except (TypeError, ValueError):
            continue
        name = (rec.get("book_name") or "").strip()
        zh = re.sub(r"\s*[A-Z].*$", "", name).strip()
        if n and zh:
            book_map.setdefault(n, zh)
            url_by_n.setdefault(n, url)

    files = sorted(f for f in os.listdir(LIB) if f.endswith(".txt"))
    hits = find_entries(files, book_map)
    # 读取各文件行
    cache = {}
    def lines_of(fn):
        if fn not in cache:
            cache[fn] = io.open(os.path.join(LIB, fn), encoding="utf-8", errors="replace").read().split("\n")
        return cache[fn]

    result = {}
    qc = collections.Counter()
    skipped = []
    unknown_items = collections.Counter()
    for n, places in hits.items():
        fn, st = places[0]
        lines = lines_of(fn)
        # 终点：同一文件里下一条编号更大、且带拉丁双名的「编号. 名称」条目行
        en = len(lines)
        for k in range(st + 1, len(lines)):
            mm2 = NUM_ENTRY.match(lines[k])
            if mm2 and int(mm2.group(1)) > n and has_binomial(mm2.group(2)):
                en = k
                break
        i = st
        while i < en:
            s = lines[i].strip()
            if "量度" in s and len(s) < 80 and "括号" not in s and "。" not in s and not is_header_line(s):
                j = i + 1
                block = []
                while j < en:
                    t = lines[j]
                    ts = t.strip()
                    if not ts:
                        if block:
                            break
                        j += 1
                        continue
                    if "量度" in ts and len(ts) < 80:
                        break
                    if ts.startswith(("分布", "寄主", "生物学", "习性", "图", "注")) or NUM_ENTRY.match(t):
                        break
                    if "\t" not in t and len(ts) > 45 and "。" in ts:
                        break
                    block.append(t)
                    j += 1
                    if len(block) > 40:
                        break
                tbl, why = build_table(s, block, url_by_n.get(n), unknown_items, fn, i + 1)
                if tbl:
                    result.setdefault(url_by_n[n], []).append(tbl)
                    qc["ok_tables"] += 1
                    qc["ok_rows"] += len(tbl["rows"])
                else:
                    qc["skip_" + why.split(":")[0]] += 1
                    skipped.append("#%d %s | %s | %s" % (n, fn, s, why))
                i = j
            else:
                i += 1

    terms = {k: {"zh": v[0], "en": v[1], "es": v[2], "kind": v[3]} for k, v in TERMS.items()}
    out_m = {}
    for url, tables in result.items():
        rec = fauna.get(url) or {}
        out_m[url] = {"book_n": str(rec.get("book_n") or "").strip(),
                      "book_name": rec.get("book_name", ""),
                      "tables": tables}
    io.open(os.path.join(ROOT, "_data", "fauna_measure_terms.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(terms, ensure_ascii=False, indent=1, sort_keys=True))
    io.open(os.path.join(ROOT, "_data", "fauna_measurements.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(out_m, ensure_ascii=False, indent=1, sort_keys=True))
    rep = ["ok_tables=%d ok_rows=%d urls=%d entries_hit=%d" % (qc["ok_tables"], qc["ok_rows"], len(out_m), len(hits))]
    rep += ["%s\t%d" % (k, v) for k, v in sorted(qc.items()) if k.startswith("skip_")]
    rep += ["", "UNKNOWN ITEMS"] + ["%s\t%d" % (k, v) for k, v in unknown_items.most_common(60)]
    rep += ["", "SKIPPED"] + skipped[:250]
    io.open(os.path.join(ROOT, "_tmp", "_measure_qc.txt"), "w", encoding="utf-8").write("\n".join(rep))
    print("ok", qc["ok_tables"], "urls", len(out_m), "hits", len(hits))


def build_table(heading, block, url, unknown_items, fn="", line=0):
    if not url:
        return None, "no_url"
    if not block:
        return None, "empty"
    data = []
    header = None
    for raw in block:
        cells = [re.sub(r"\s+", " ", c).strip() for c in raw.split("\t")]
        cells = [c for c in cells if c]
        if not cells:
            continue
        if not any(re.search(r"\d", c) for c in cells):
            flat = [re.sub(r"\s+", "", c) for c in cells]
            if header is None and all(c in ("项目", "项日", "项月", "范围", "范图", "平均", "量度", "量", "范围平均") for c in flat):
                header = flat
            continue  # 表头或纯文字行
        data.append(cells)
    if not data:
        return None, "nodata"
    six = sum(1 for c in data if len(c) == 6)
    has_mean = bool(header) and any("平" in c for c in header)
    if not has_mean and six * 2 >= len(data):
        has_mean = True
    pairs = []
    kept = dropped = 0
    for ri, cells in enumerate(data):
        if has_mean:
            if len(cells) == 6:
                groups = [(0, 1, 2), (3, 4, 5)]
            elif len(cells) == 3:
                groups = [(0, 1, 2)]
            elif len(cells) == 2:
                groups = [(0, 1, -1)]
            else:
                return None, "mean_width%d" % len(cells)
        else:
            if len(cells) == 4:
                groups = [(0, 1, -1), (2, 3, -1)]
            elif len(cells) == 2:
                groups = [(0, 1, -1)]
            elif len(cells) == 6:
                groups = [(0, 1, 2), (3, 4, 5)]
            elif len(cells) == 3:
                dropped += 1  # 无「平均」列的表出现三格，列归属不可靠，整行丢弃
                continue
            else:
                return None, "width%d" % len(cells)
        for g in groups:
            item_raw = cells[g[0]]
            val, st = norm_value(cells[g[1]])
            mean = None
            if g[2] >= 0 and g[2] < len(cells):
                mv, mst = norm_value(cells[g[2]])
                if mst == "ok":
                    mean = mv
            key = norm_key(item_raw)
            if st != "ok" or not key:
                if not key and re.search(r"[\u4e00-\u9fff]", item_raw):
                    unknown_items[item_raw] += 1
                dropped += 1
                continue
            tkind = TERMS[key][3]
            if tkind == "count":
                if not re.fullmatch(r"\d+(–\d+)?", val):
                    dropped += 1
                    continue
                if mean is not None and not re.fullmatch(r"\d+", mean):
                    mean = None
            else:
                parts = []
                bad = False
                for part in val.split("–"):
                    part = fix_mm(part)
                    try:
                        x = float(part)
                    except ValueError:
                        bad = True
                        break
                    if not (0.02 <= x <= 40):
                        bad = True
                        break
                    parts.append(part)
                if bad:
                    dropped += 1
                    continue
                val = "–".join(parts)
                if mean is not None:
                    mean = fix_mm(mean)
                    try:
                        if not (0.02 <= float(mean) <= 40):
                            mean = None
                    except ValueError:
                        mean = None
            pairs.append({"key": key, "value": val, "_c": 0 if g[0] == 0 else 1, "_r": ri, "_i": len(pairs),
                          **({"mean": mean} if mean else {})})
            kept += 1
    if kept < 3:
        return None, "toofew"
    # 按原书版式重排：左栏自上而下，再右栏自上而下（网页上是单列，交错顺序读起来是乱的）
    pairs.sort(key=lambda p: (p["_c"], p["_r"], p["_i"]))
    for p in pairs:
        p.pop("_c", None), p.pop("_r", None), p.pop("_i", None)
    keys = [p["key"] for p in pairs]
    if len(set(keys)) != len(keys):
        return None, "dupkey"
    title = re.sub(r"\s+", " ", heading).strip()
    title = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", title)
    title = title.replace("脱翅虫蚁", "脱翅成虫").replace("兵型", "兵蚁").replace("兵蚊", "兵蚁")
    title = title.replace("〔", "(").replace("〕", ")").replace("{", "(").replace("}", ")")
    title = re.sub(r"\((?:mm|mn|mns|run|mam|mm\)|mm\})\s*$", "", title, flags=re.I).strip()
    title = re.sub(r"\((?:mm|mn|mns|run|mam)[^)]*\)\s*$", "", title, flags=re.I).strip()
    caste = "soldier"
    if "有翅" in title or "成虫" in title or "脱翅" in title or "长翅" in title:
        caste = "alate"
    elif "工蚁" in title or "工蚊" in title:
        caste = "worker"
    elif "若虫" in title:
        caste = "nymph"
    label_zh, label_en, label_es = caste_label(title)
    return {"caste": caste, "heading": title, "label_zh": label_zh, "label_en": label_en,
            "label_es": label_es, "unit": "mm", "src_file": fn, "src_line": line, "rows": pairs}, ""


DEGREES = [
    ("大兵蚁", "大兵蚁", "Major soldier", "Soldado mayor"),
    ("大兵", "大兵蚁", "Major soldier", "Soldado mayor"),
    ("中兵蚁", "中兵蚁", "Medium soldier", "Soldado mediano"),
    ("中兵", "中兵蚁", "Medium soldier", "Soldado mediano"),
    ("小兵蚁", "小兵蚁", "Minor soldier", "Soldado menor"),
    ("小兵", "小兵蚁", "Minor soldier", "Soldado menor"),
]
CASTES = [
    ("有翅成虫", "有翅成虫", "Alate", "Alado"),
    ("脱翅成虫", "脱翅成虫", "Dealate", "Dealado"),
    ("长翅成虫", "长翅成虫", "Macropterous alate", "Alado macróptero"),
    ("兵蚁", "兵蚁", "Soldier", "Soldado"),
    ("兵蚊", "兵蚁", "Soldier", "Soldado"),
    ("工蚁", "工蚁", "Worker", "Obrera"),
    ("工蚊", "工蚁", "Worker", "Obrera"),
    ("若虫", "若虫", "Nymph", "Ninfa"),
    ("王与后", "王与后", "King and queen", "Rey y reina"),
    ("成虫", "成虫", "Imago", "Imago"),
]


def caste_label(title):
    """标题 → 品级标签（去掉物种名，保留「大兵蚁」这类级别词）。"""
    deg = None
    for zh, z2, en, es in DEGREES:
        if zh in title:
            deg = (z2, en, es)
            break
    for zh, z2, en, es in CASTES:
        if zh in title:
            return (deg[0] if deg else z2) + "量度", \
                   (deg[1] if deg else en) + " measurements", \
                   "Medidas de " + ((deg[2] if deg else es).lower())
    if deg:
        return deg[0] + "量度", deg[1] + " measurements", "Medidas de " + deg[2].lower()
    return "量度", "Measurements", "Medidas"


main()
