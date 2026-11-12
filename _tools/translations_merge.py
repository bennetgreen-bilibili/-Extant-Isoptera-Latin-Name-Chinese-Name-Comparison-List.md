#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate translation shards and merge them into _data/translations_<lang>.json.

Usage:
    python _tools/translations_merge.py --files fauna_families,fauna_genera,fauna_keys,morphology_genera
    python _tools/translations_merge.py --all
    python _tools/translations_merge.py --all --check-only

Checks per shard: key set, JSON validity, structure identity, empty stays empty,
no CJK left, no numeric token lost, no Latin (genus/author) token lost.
Exit code 1 if any shard is invalid, 0 otherwise (merged files still written from
the shards that did pass, so a partial wave can be delivered).
"""
import argparse
import copy
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_data")
TR = os.path.join(ROOT, "_tmp", "tr")
LANGS = ("en", "es")
ORDER = ["meta", "morphology_genera", "morphology_species", "fauna_families",
         "fauna_genera", "fauna_species", "fauna_keys"]
NAMES = [n for n in ORDER if n != "meta"]

CJK_RE = re.compile(r"[\u3400-\u9fff\uff00-\uffef]")
LATIN_RE = re.compile(r"\b[A-Z][a-z]{2,}\b")
NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")

# Capitalised non-taxonomic words that occur verbatim in the Chinese source
# (field labels, quoted German/English terms). Translating them is correct.
LATIN_IGNORE = {
    "Citation", "Description", "Diagnosis", "Imago", "Untergattung", "Soldat",
    "Arbeiter", "Grössen", "Zwei", "Family", "Subfamily", "Genus", "Subgenus",
    "Species", "Subspecies", "Type", "Holotype", "Paratype", "Lectotype",
    "Neotype", "Figure", "Table", "Plate", "Text", "Original", "Termite",
    "Termites", "Worker", "Soldier", "Alate", "Nymph", "Distribution", "Biology",
    "Note", "Key", "Keys", "Genera", "Synonym", "Synonyms", "Appendix",
    "Section", "Chinese", "English", "Latin", "Greek", "Neotropical",
    "Afrotropical", "Palaearctic", "Nearctic", "Oriental", "Indomalayan",
    "Holocene", "Miocene", "Oligocene", "Eocene", "Cretaceous", "Jurassic",
}

LABELS = {
    "en": {"鉴别要点": "Diagnostic characters", "有翅成虫": "Alate",
           "兵蚁": "Soldier", "工蚁": "Worker", "若虫": "Nymph"},
    "es": {"鉴别要点": "Caracteres diagnósticos", "有翅成虫": "Alado",
           "兵蚁": "Soldado", "工蚁": "Obrero", "若虫": "Ninfa"},
}

# Number words so that "第 3 缘齿" -> "third marginal tooth" and "2 倍" -> "twice"
# are not reported as lost numbers. Only bare integers 1..29 are eligible.
_NUM_WORDS = {
    "en": {
        1: ["one", "first"], 2: ["two", "second", "twice"], 3: ["three", "third", "thrice"],
        4: ["four", "fourth", "quarter", "quarterS"], 5: ["five", "fifth"],
        6: ["six", "sixth"], 7: ["seven", "seventh"], 8: ["eight", "eighth"],
        9: ["nine", "ninth"], 10: ["ten", "tenth"], 11: ["eleven", "eleventh"],
        12: ["twelve", "twelfth"], 13: ["thirteen", "thirteenth"],
        14: ["fourteen", "fourteenth"], 15: ["fifteen", "fifteenth"],
        16: ["sixteen", "sixteenth"], 17: ["seventeen", "seventeenth"],
        18: ["eighteen", "eighteenth"], 19: ["nineteen", "nineteenth"],
        20: ["twenty", "twentieth"], 21: ["twenty-one", "twenty-first"],
        22: ["twenty-two", "twenty-second"], 23: ["twenty-three", "twenty-third"],
        24: ["twenty-four", "twenty-fourth"], 25: ["twenty-five", "twenty-fifth"],
        26: ["twenty-six", "twenty-sixth"], 27: ["twenty-seven", "twenty-seventh"],
        28: ["twenty-eight", "twenty-eighth"], 29: ["twenty-nine", "twenty-ninth"],
    },
    "es": {
        1: ["uno", "un", "una", "primero", "primera"], 2: ["dos", "segundo", "segunda", "veces"],
        3: ["tres", "tercero", "tercera", "tercio"], 4: ["cuatro", "cuarto", "cuarta"],
        5: ["cinco", "quinto", "quinta"], 6: ["seis", "sexto", "sexta"],
        7: ["siete", "séptimo", "séptima", "sétimo"], 8: ["ocho", "octavo", "octava"],
        9: ["nueve", "noveno", "novena"], 10: ["diez", "décimo", "décima"],
        11: ["once", "undécimo"], 12: ["doce", "duodécimo"], 13: ["trece", "decimotercero"],
        14: ["catorce", "decimocuarto"], 15: ["quince", "decimoquinto"],
        16: ["dieciséis", "decimosexto"], 17: ["diecisiete", "decimoséptimo"],
        18: ["dieciocho", "decimoctavo"], 19: ["diecinueve", "decimonoveno"],
        20: ["veinte", "vigésimo"], 21: ["veintiuno", "vigésimo primero"],
        22: ["veintidós", "vigésimo segundo"], 23: ["veintitrés", "vigésimo tercero"],
        24: ["veinticuatro", "vigésimo cuarto"], 25: ["veinticinco", "vigésimo quinto"],
    },
}

for _lang, _table in _NUM_WORDS.items():
    for _n, _forms in list(_table.items()):
        _table[_n] = [f for f in _forms if not f.endswith("S")]


def _words_for(lang, n):
    forms = _NUM_WORDS.get(lang, {}).get(n)
    if forms is None:
        return []
    return list(forms)


def _has_word(lang, dst, n):
    low = fold(dst).lower()
    for form in _words_for(lang, n):
        if re.search(r"(?<![a-z])" + re.escape(form) + r"(?![a-z])", low):
            return True
    return False


def num_runs(s):
    """Digit runs; decimal commas and points are equivalent (es-ES types 0,48)."""
    s = s.replace(",", ".") if re.search(r"\d,\d", s) else s
    return NUM_RE.findall(s)


def missing_numbers(src, dst, lang):
    have = num_runs(dst)
    miss = []
    for tok in num_runs(src):
        if tok in have:
            continue
        if re.fullmatch(r"\d{1,2}", tok) and _has_word(lang, dst, int(tok)):
            continue
        miss.append(tok)
    return sorted(set(miss))


def fold(s):
    """Strip diacritics so that Grassé/Grasse compare equal (author-name check only)."""
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))


def check_string(src, dst, where, problems, lang="en"):
    if not isinstance(dst, str):
        problems.append("%s: not a string" % where)
        return
    if src == "":
        if dst != "":
            problems.append("%s: expected empty string, got %r" % (where, dst[:40]))
        return
    if not dst.strip():
        problems.append("%s: empty translation for non-empty source" % where)
        return
    if CJK_RE.search(dst):
        problems.append("%s: leftover CJK %r" % (where, CJK_RE.search(dst).group(0)))
    miss = missing_numbers(src, dst, lang)
    if miss:
        problems.append("%s: numeric tokens lost %s" % (where, miss))
    flat = fold(dst).replace(" ", "")
    for tok in LATIN_RE.findall(src):
        if tok in LATIN_IGNORE:
            continue
        if tok not in dst and fold(tok) not in flat:
            problems.append("%s: Latin token lost %r" % (where, tok))


def check_tree(src, dst, where, problems, lang="en"):
    if isinstance(src, dict):
        if not isinstance(dst, dict):
            problems.append("%s: expected object" % where)
            return
        if set(src) != set(dst):
            problems.append("%s: key mismatch %s" % (where, sorted(set(src) ^ set(dst))))
        for k in src:
            if k in dst:
                check_tree(src[k], dst[k], where + "." + str(k), problems, lang)
    elif isinstance(src, list):
        if not isinstance(dst, list):
            problems.append("%s: expected array" % where)
            return
        if len(src) != len(dst):
            problems.append("%s: array length %d -> %d" % (where, len(src), len(dst)))
            return
        for i, (a, b) in enumerate(zip(src, dst)):
            check_tree(a, b, "%s[%d]" % (where, i), problems, lang)
    elif isinstance(src, str):
        check_string(src, dst, where, problems, lang)


def validate_shard(name, lang, shard_meta):
    fn = shard_meta["file"]
    in_path = os.path.join(TR, lang, fn)
    out_path = os.path.join(TR, "out", lang, fn)
    problems = []
    if not os.path.exists(out_path):
        return None, ["%s: missing output file" % fn]
    try:
        with open(in_path, encoding="utf-8") as fh:
            src = json.load(fh)
        with open(out_path, encoding="utf-8") as fh:
            dst = json.load(fh, object_pairs_hook=dict)
    except Exception as exc:  # noqa: BLE001
        return None, ["%s: invalid JSON: %s" % (fn, exc)]
    check_tree(src, dst, fn, problems, lang)
    return dst, problems


def build_entry(name, url, src_entry, tr_entry, lang):
    """Splice translated strings back into (a copy of) the source structure."""
    if name.startswith("morphology_"):
        sections = []
        for s_src, s_tr in zip(src_entry["sections"], tr_entry["sections"]):
            label = s_tr.get("label", "")
            canon = LABELS[lang].get(s_src.get("label", ""))
            sections.append({"label": canon or label, "text": s_tr.get("text", "")})
        out = {"sections": sections}
        if "note" in src_entry:
            out["note"] = tr_entry.get("note", "")
        return out
    if name == "fauna_keys":
        out = copy.deepcopy(src_entry)
        for ki, k_tr in enumerate(tr_entry["keys"]):
            k_out = out["keys"][ki]
            for f in ("title", "caste", "note", "source", "src_short"):
                if f in k_out and f in k_tr:
                    k_out[f] = k_tr[f]
            for ci, c_tr in enumerate(k_tr["couplets"]):
                leads_out = k_out["couplets"][ci]["leads"]
                for li, l_tr in enumerate(c_tr["leads"]):
                    leads_out[li]["t"] = l_tr["t"]
        if "omitted" in tr_entry:
            out["omitted"] = tr_entry["omitted"]
        return out
    # fauna_*
    out = {}
    for f, val in src_entry.items():
        if f in ("en", "book_n"):
            continue
        if f in tr_entry:
            out[f] = tr_entry[f]
        else:
            out[f] = val
    return out


def sort_deep(obj):
    if isinstance(obj, dict):
        return {k: sort_deep(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [sort_deep(v) for v in obj]
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--langs", default="en,es")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    names = NAMES if args.all else [x.strip() for x in (args.files or "").split(",") if x.strip()]
    langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    if not names:
        ap.error("give --files or --all")

    total_bad = 0
    report = {}
    merged = {lang: {} for lang in langs}
    for name in names:
        man_path = os.path.join(TR, "manifest_%s.json" % name)
        if not os.path.exists(man_path):
            print("[%s] no manifest - skipped" % name)
            continue
        with open(man_path, encoding="utf-8") as fh:
            man = json.load(fh)
        with open(os.path.join(DATA, name + ".json"), encoding="utf-8") as fh:
            src_all = json.load(fh)
        for lang in langs:
            good = {}
            bad_shards = []
            for shard in man["shards"]:
                dst, problems = validate_shard(name, lang, shard)
                if problems:
                    bad_shards.append(shard["file"])
                    total_bad += 1
                    print("[%s/%s] %s FAILED" % (name, lang, shard["file"]))
                    for p in problems[:8]:
                        print("    -", p)
                    if len(problems) > 8:
                        print("    ... %d more" % (len(problems) - 8))
                else:
                    good.update(dst)
            entries = {}
            missing = [u for u in src_all if u not in good]
            if missing:
                print("[%s/%s] %d keys missing: %s" % (name, lang, len(missing), missing[:5]))
            for url, src_entry in src_all.items():
                if url in good:
                    entries[url] = build_entry(name, url, src_entry, good[url], lang)
            merged[lang][name] = entries
            report[(name, lang)] = {
                "keys": len(src_all), "translated": len(entries),
                "chars": man["total_chars"], "shards": len(man["shards"]),
                "bad_shards": bad_shards,
            }
            print("[%s/%s] %d/%d keys, %d shards, %d bad"
                  % (name, lang, len(entries), len(src_all), len(man["shards"]), len(bad_shards)))

    if args.check_only:
        return 1 if total_bad else 0

    meta = {
        "schema": 1,
        "review": "machine-assisted",
        "note": ("Machine-assisted translation of the Chinese taxonomic prose in _data/*.json. "
                 "Latin names, authorities, years and measurements are kept verbatim; "
                 "the pre-existing English abstracts in the source `en` fields are not duplicated here."),
    }
    for lang in langs:
        root = {"meta": meta}
        cov = {"keys": 0, "chars": 0, "files": {}}
        for name in ORDER[1:]:
            if name in merged[lang]:
                root[name] = sort_deep(merged[lang][name])
                cov["files"][name] = {"keys": len(merged[lang][name]),
                                      "chars": report.get((name, lang), {}).get("chars", 0)}
                cov["keys"] += len(merged[lang][name])
                cov["chars"] += cov["files"][name]["chars"]
        root["meta"] = dict(meta, coverage=cov)
        out_path = os.path.join(DATA, "translations_%s.json" % lang)
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(root, fh, indent=1, ensure_ascii=False, sort_keys=False)
            fh.write("\n")
        size = os.path.getsize(out_path)
        print("wrote %s (%d keys, %d CJK source chars, %d bytes)"
              % (os.path.relpath(out_path, ROOT), cov["keys"], cov["chars"], size))
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
