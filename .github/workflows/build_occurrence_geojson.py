#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build 1-degree occurrence maps for the 13 extant termite families (and the
largest genera) from the GBIF occurrence API.

Outputs (all committed, deterministic):

    assets/geo/family/<family_id>.geojson   13 FeatureCollections, 1 degree grid
    assets/geo/genus/<genus_id>.geojson     optional, >= 12 species, < 60 KB each
    _data/occurrence_summary.json           summary consumed by Liquid
                                            (site.data.occurrence_summary)

Usage (see .github/workflows/pages.yml and _tools/分布图与瓦片使用政策.md):

    python .github/workflows/build_occurrence_geojson.py --check    # default
    python .github/workflows/build_occurrence_geojson.py --write
    python .github/workflows/build_occurrence_geojson.py --write --refresh
    python .github/workflows/build_occurrence_geojson.py --write --limit 300
    python .github/workflows/build_occurrence_geojson.py --write --budget 240
    python .github/workflows/build_occurrence_geojson.py --vendor-leaflet

Design notes
------------
* Family level is mandatory and always produced (13 files).
* Four families have no rank=FAMILY match in the GBIF backbone (as of the
  access date): Hodotermopsidae, Psammotermitidae, Termitogetonidae and
  Heterotermitidae -- GBIF folds them into Archotermopsidae / Rhinotermitidae.
  For those, the map is aggregated from the family's genera (resolution
  "genus_aggregate") so the map still follows *this* checklist's taxonomy.
  The consequence (their records also count towards the host family's map) is
  recorded in properties["note"] and documented in _tools/.
* Each taxon contributes at most CAP records (900). The API returns records in
  stable key order, so the cap is a deterministic sample, not a random sample
  -- sampling bias is documented, not hidden.
* Cache: _tmp/gbif_cache/ (gitignored). A rerun never refetches; --refresh
  wipes the cache. The recorded access date is the cache's fetch date, so a
  rerun from the same cache is byte-identical.
* --check regenerates in memory and compares byte-for-byte; it exits 1 on any
  difference, so CI can guard against hand-edited artefacts.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

try:  # Windows console: never crash on Chinese output
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover - older/odd streams
    pass

ROOT = Path(__file__).resolve().parents[2]
DATA_INDEX = ROOT / "data" / "index.json"
SPECIES_DIR = ROOT / "_species"
GEO_DIR = ROOT / "assets" / "geo"
FAMILY_DIR = GEO_DIR / "family"
GENUS_DIR = GEO_DIR / "genus"
SUMMARY = ROOT / "_data" / "occurrence_summary.json"
CACHE_DIR = ROOT / "_tmp" / "gbif_cache"
VENDOR_DIR = ROOT / "assets" / "vendor" / "leaflet"

GBIF_API = "https://api.gbif.org/v1"
PROJECT_URL = (
    "https://github.com/bennetgreen-bilibili/"
    "-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md"
)
USER_AGENT = (
    "IsopteraChecklistBot/1.0 (termite checklist distribution maps; +%s)" % PROJECT_URL
)

PAGE_LIMIT = 300          # records per API page (GBIF maximum for occurrence/search)
CAP = 900                 # records per family / genus (3 pages) -- documented cap
GRID = 1.0                # degrees; cells are floor(lat)..floor(lat)+1
MIN_INTERVAL = 0.40       # seconds between requests -> ~2.5 req/s

GENUS_MIN_SPECIES = 12    # only genera with >= 12 species (see _data/species_by_genus.json)
GENUS_MAX_FILES = 12      # hard cap on genus-level files (request budget, see _tools/)
GENUS_FILE_MAX_BYTES = 60 * 1024
GENUS_TOTAL_MAX_BYTES = 3 * 1024 * 1024

LEAFLET_VERSION = "1.9.4"
LEAFLET_BASE = "https://cdn.jsdelivr.net/npm/leaflet@%s/" % LEAFLET_VERSION
# (remote path below the package root, local path below assets/vendor/leaflet)
LEAFLET_FILES = (
    ("dist/leaflet.js", "leaflet.js"),
    ("dist/leaflet.css", "leaflet.css"),
    ("LICENSE", "LICENSE"),
    ("dist/images/layers.png", "images/layers.png"),
    ("dist/images/layers-2x.png", "images/layers-2x.png"),
    ("dist/images/marker-icon.png", "images/marker-icon.png"),
    ("dist/images/marker-icon-2x.png", "images/marker-icon-2x.png"),
    ("dist/images/marker-shadow.png", "images/marker-shadow.png"),
)

FM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)[ \t]*:[ \t]*(.*)$")


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
class BudgetExceeded(Exception):
    pass


class FetchError(Exception):
    pass


def utc_today():
    return time.strftime("%Y-%m-%d", time.gmtime())


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def parse_front_matter(text):
    """Minimal YAML parser for the flat front matter used in _species/*.md."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = {}
    for line in text[3:end].splitlines():
        m = FM_RE.match(line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
            raw = raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        elif len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
            raw = raw[1:-1].replace("''", "'")
        data[key] = raw
    return data


def walk_families(tree):
    """Families in document (classification) order."""
    out = []

    def walk(node):
        if node.get("type") == "family":
            out.append(node)
        for child in node.get("children") or []:
            walk(child)

    walk(tree)
    return out


def load_genera_by_family():
    """family_id -> [ {id, latin, zh, species} ] from _species front matter."""
    if not SPECIES_DIR.is_dir():
        sys.exit("missing directory: %s" % SPECIES_DIR)
    buckets = {}
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        if str(fm.get("rank", "species")).lower() == "subspecies":
            continue
        family_id = (fm.get("family_id") or "").strip()
        genus_id = (fm.get("genus_id") or "").strip()
        if not family_id or not genus_id:
            continue
        bucket = buckets.setdefault(family_id, {})
        entry = bucket.setdefault(
            genus_id,
            {
                "id": genus_id,
                "latin": (fm.get("genus_latin") or "").strip(),
                "zh": (fm.get("genus_zh") or "").strip(),
                "species": 0,
            },
        )
        entry["species"] += 1
    return {
        family_id: sorted(genus.values(), key=lambda g: g["latin"] or g["id"])
        for family_id, genus in buckets.items()
    }


# --------------------------------------------------------------------------
# GBIF client: polite, cached, resumable, budgeted
# --------------------------------------------------------------------------
class GBIFClient:
    def __init__(self, refresh=False, budget=1200.0, offline=False):
        self.cache = CACHE_DIR
        self.refresh = refresh
        self.budget = float(budget)
        self.offline = offline
        self.started = time.monotonic()
        self.network_requests = 0
        self.cache_hits = 0
        self._last_request = 0.0
        if refresh:
            shutil.rmtree(self.cache, ignore_errors=True)
        self.cache.mkdir(parents=True, exist_ok=True)

    # -- budget / throttle -------------------------------------------------
    def remaining(self):
        return self.budget - (time.monotonic() - self.started)

    def _throttle(self):
        wait = MIN_INTERVAL - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    # -- cache -------------------------------------------------------------
    def read_cache(self, name):
        path = self.cache / name
        if self.refresh or not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return None
        self.cache_hits += 1
        return payload

    def write_cache(self, name, payload):
        path = self.cache / name
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".part")
        tmp.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8"
        )
        tmp.replace(path)

    # -- GET ---------------------------------------------------------------
    def get(self, path, params, cache_name):
        cached = self.read_cache(cache_name)
        if cached is not None:
            return cached
        if self.offline:
            raise FetchError("offline mode and no cache for %s" % cache_name)
        if self.remaining() <= 0:
            raise BudgetExceeded(cache_name)

        url = GBIF_API + path + "?" + urllib.parse.urlencode(params)
        delay = 1.0
        last_error = None
        for attempt in range(6):
            self._throttle()
            if self.remaining() <= 0:
                raise BudgetExceeded(cache_name)
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                    # gzip matters: one 300-record page is ~1.8 MB of JSON
                    "Accept-Encoding": "gzip",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    raw = response.read()
                    if (response.headers.get("Content-Encoding") or "").lower() == "gzip":
                        raw = gzip.decompress(raw)
                self.network_requests += 1
                payload = json.loads(raw.decode("utf-8"))
                self.write_cache(cache_name, payload)
                return payload
            except urllib.error.HTTPError as exc:
                last_error = "HTTP %s" % exc.code
                if exc.code in (429, 500, 502, 503, 504) and attempt < 5:
                    time.sleep(delay)
                    delay = min(delay * 2, 32.0)
                    continue
                raise FetchError("%s -> %s (%s)" % (url, last_error, cache_name))
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                last_error = str(exc)
                if attempt < 5:
                    time.sleep(delay)
                    delay = min(delay * 2, 32.0)
                    continue
                raise FetchError("%s -> %s (%s)" % (url, last_error, cache_name))
        raise FetchError("%s -> %s (%s)" % (url, last_error, cache_name))


# --------------------------------------------------------------------------
# GBIF queries
# --------------------------------------------------------------------------
def match_taxon(client, name, rank):
    """species/match for a name+rank; returns the JSON (may be matchType NONE)."""
    return client.get(
        "/species/match",
        {"name": name, "rank": rank},
        "match_%s_%s.json" % (re.sub(r"[^A-Za-z0-9]+", "_", name).upper(), rank),
    )


def pull_occurrences(client, taxon_key, cap):
    """Up to cap occurrences with coordinates -> [(lat, lon, country), ...]."""
    records = []
    offset = 0
    while len(records) < cap:
        page = client.get(
            "/occurrence/search",
            {
                "taxonKey": taxon_key,
                "hasCoordinate": "true",
                "hasGeospatialIssue": "false",
                "limit": PAGE_LIMIT,
                "offset": offset,
            },
            "occurrence_%s_%s_%s.json" % (taxon_key, offset, PAGE_LIMIT),
        )
        results = page.get("results") or []
        for item in results:
            lat = item.get("decimalLatitude")
            lon = item.get("decimalLongitude")
            if lat is None or lon is None:
                continue
            try:
                lat = float(lat)
                lon = float(lon)
            except (TypeError, ValueError):
                continue
            if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
                continue
            country = item.get("countryCode") or item.get("country") or ""
            records.append((lat, lon, str(country)))
        offset += PAGE_LIMIT
        if page.get("endOfRecords") or len(results) < PAGE_LIMIT:
            break
    return records[:cap]


# --------------------------------------------------------------------------
# aggregation
# --------------------------------------------------------------------------
def bin_records(records, size=GRID):
    """1 degree binning; key = (lat_index, lon_index), cell centre = index+0.5."""
    cells = Counter()
    countries = Counter()
    for lat, lon, country in records:
        cells[(int(math.floor(lat / size)), int(math.floor(lon / size)))] += 1
        if country:
            countries[country] += 1
    return cells, countries


def features_from_cells(cells, size=GRID):
    features = []
    for lat_index, lon_index in sorted(cells):
        lat = round(lat_index * size + size / 2.0, 3)
        lon = round(lon_index * size + size / 2.0, 3)
        lon = max(-180.0, min(179.999, lon))
        lat = max(-90.0, min(89.999, lat))
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {"n": cells[(lat_index, lon_index)]},
            }
        )
    return features


def render_geojson(properties, features):
    body = ",\n".join(
        "    " + json.dumps(f, ensure_ascii=False, separators=(",", ":"))
        for f in features
    )
    return (
        "{\n"
        '"type":"FeatureCollection",\n'
        '"properties":%s,\n'
        '"features":[\n%s\n'
        "]\n"
        "}\n"
    ) % (
        json.dumps(properties, ensure_ascii=False, separators=(",", ":")),
        body,
    )


def source_line(access_date):
    return (
        "GBIF occurrence search API (https://api.gbif.org/v1/occurrence/search), "
        "hasCoordinate=true, hasGeospatialIssue=false, accessed %s; "
        "aggregated to a 1 degree grid by this site" % access_date
    )


def top_countries(countries, limit=8):
    ordered = sorted(countries.items(), key=lambda kv: (-kv[1], kv[0]))
    return {code: count for code, count in ordered[:limit]}


# --------------------------------------------------------------------------
# Leaflet vendoring
# --------------------------------------------------------------------------
def vendor_leaflet():
    """Download the pinned Leaflet build into assets/vendor/leaflet (never at runtime)."""
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    digests = []
    for remote, local in LEAFLET_FILES:
        url = LEAFLET_BASE + remote
        raw = None
        for attempt in range(4):
            request = urllib.request.Request(
                url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"}
            )
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    raw = response.read()
                break
            except (urllib.error.HTTPError, urllib.error.URLError, OSError):
                if attempt == 3:
                    raise
                time.sleep(1.0 * (2 ** attempt))
        target = VENDOR_DIR / local
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        digests.append((local, len(raw), sha256_bytes(raw)))
        print("vendored %-28s %7d bytes" % (local, len(raw)))
        time.sleep(MIN_INTERVAL)
    readme = [
        "# Leaflet %s (vendored)" % LEAFLET_VERSION,
        "",
        "Downloaded from %s"
        % ("https://cdn.jsdelivr.net/npm/leaflet@%s/" % LEAFLET_VERSION),
        "by .github/workflows/build_occurrence_geojson.py (run with --vendor-leaflet).",
        "Never loaded from a CDN at runtime.",
        "",
        "Leaflet is BSD-2-Clause -- see LICENSE in this folder.",
        "",
        "| file | bytes | sha256 |",
        "| --- | --- | --- |",
    ]
    for relative, size, digest in digests:
        readme.append("| %s | %d | %s |" % (relative, size, digest))
    readme.append("")
    (VENDOR_DIR / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print("wrote %s" % (VENDOR_DIR / "README.md").relative_to(ROOT))


# --------------------------------------------------------------------------
# main build
# --------------------------------------------------------------------------
def build_genera_index(by_family):
    """Flat candidate list for genus-level files, largest genera first."""
    candidates = []
    for family_id, genera in by_family.items():
        for genus in genera:
            if genus["species"] >= GENUS_MIN_SPECIES and genus["latin"]:
                candidates.append((genus, family_id))
    candidates.sort(key=lambda item: (-item[0]["species"], item[0]["id"]))
    return candidates


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write artefacts")
    mode.add_argument("--check", action="store_true", help="compare artefacts (default)")
    parser.add_argument("--refresh", action="store_true", help="wipe cache, refetch GBIF")
    parser.add_argument("--limit", type=int, default=CAP, help="records per taxon (default 900)")
    parser.add_argument("--budget", type=float, default=1200.0, help="network time budget, seconds")
    parser.add_argument("--date", help="override the recorded access date (YYYY-MM-DD)")
    parser.add_argument("--no-genera", action="store_true", help="family level only")
    parser.add_argument("--max-genera", type=int, default=GENUS_MAX_FILES, help="max genus files")
    parser.add_argument("--offline", action="store_true", help="never touch the network")
    parser.add_argument("--vendor-leaflet", action="store_true", help="download Leaflet and exit")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if args.vendor_leaflet:
        vendor_leaflet()
        return 0

    write = args.write
    cap = max(PAGE_LIMIT, min(int(args.limit), 30000))

    index = json.loads(DATA_INDEX.read_text(encoding="utf-8"))
    families = walk_families(index["tree"])
    if len(families) != 13:
        sys.exit("expected 13 families in data/index.json, found %d" % len(families))

    by_family = load_genera_by_family()

    client = GBIFClient(refresh=args.refresh, budget=args.budget, offline=args.offline)
    cache_meta_path = client.cache / "_meta.json"
    if args.refresh:
        cache_meta_path.write_text(
            json.dumps({"access_date": utc_today()}, ensure_ascii=False), encoding="utf-8"
        )
    if args.date:
        access_date = args.date
    elif cache_meta_path.is_file():
        try:
            access_date = json.loads(cache_meta_path.read_text(encoding="utf-8"))["access_date"]
        except (ValueError, KeyError):
            access_date = utc_today()
    else:
        access_date = utc_today()
        cache_meta_path.write_text(
            json.dumps({"access_date": access_date}, ensure_ascii=False), encoding="utf-8"
        )

    family_outputs = {}
    family_summary = []
    total_records = 0
    total_cells = 0

    try:
        for node in families:
            family_id = node["id"]
            latin = (node.get("latin") or "").strip()
            zh = (node.get("zh") or "").strip()
            genera = by_family.get(family_id) or []

            match = match_taxon(client, latin, "FAMILY")
            key = match.get("usageKey") if match.get("matchType") != "NONE" else None
            resolution = "family_key"
            keys = [key] if key else []

            records = []
            if key:
                records = pull_occurrences(client, key, cap)
            else:
                # GBIF backbone folds this family into a broader one: aggregate the
                # family's own genera instead, so the map matches this checklist.
                resolution = "genus_aggregate"
                keys = []
                remaining = cap
                for genus in genera:
                    if remaining <= 0:
                        break
                    genus_match = match_taxon(client, genus["latin"], "GENUS")
                    genus_key = genus_match.get("usageKey")
                    if not genus_key:
                        continue
                    keys.append(genus_key)
                    got = pull_occurrences(client, genus_key, remaining)
                    records.extend(got)
                    remaining -= len(got)
                records = records[:cap]

            if not records:
                sys.exit(
                    "no GBIF records for family %s (key=%s) -- refusing to write an empty map"
                    % (latin, key)
                )

            cells, countries = bin_records(records)
            features = features_from_cells(cells)
            properties = {
                "family": latin.capitalize(),
                "family_zh": zh,
                "family_id": family_id,
                "gbif_key": key,
                "gbif_keys": keys,
                "resolution": resolution,
                "records": len(records),
                "cells": len(cells),
                "grid": "1 degree",
                "generated": access_date,
                "source": source_line(access_date),
            }
            if resolution == "genus_aggregate":
                properties["note"] = (
                    "GBIF backbone has no rank=FAMILY match for this name; the map "
                    "aggregates the occurrences of the genera this checklist places in "
                    "the family. Its records also count towards the GBIF host family."
                )
            text = render_geojson(properties, features)
            json.loads(text)  # sanity check
            family_outputs[family_id] = (text, FAMILY_DIR / ("%s.geojson" % family_id))

            total_records += len(records)
            total_cells += len(cells)
            family_summary.append(
                {
                    "id": family_id,
                    "latin": latin.capitalize(),
                    "zh": zh,
                    "gbif_key": key,
                    "gbif_keys": keys,
                    "resolution": resolution,
                    "records": len(records),
                    "cells": len(cells),
                    "species": (node.get("counts") or {}).get("species"),
                    "genera": (node.get("counts") or {}).get("genera"),
                    "file": "assets/geo/family/%s.geojson" % family_id,
                    "gbif_url": ("https://www.gbif.org/species/%s" % key) if key else None,
                    "countries": top_countries(countries),
                }
            )
            if not args.quiet:
                print(
                    "family %-18s key=%-9s records=%4d cells=%4d %6.1f KB (%s)"
                    % (
                        family_id,
                        key or "-",
                        len(records),
                        len(cells),
                        len(text.encode("utf-8")) / 1024.0,
                        resolution,
                    )
                )

        # ---- genus level --------------------------------------------------
        genus_outputs = {}
        genus_summary = []
        if not args.no_genera:
            candidates = build_genera_index(by_family)
            pulled = 0
            for genus, family_id in candidates:
                if pulled >= args.max_genera:
                    break
                match = match_taxon(client, genus["latin"], "GENUS")
                key = match.get("usageKey") if match.get("matchType") != "NONE" else None
                if not key:
                    continue
                records = pull_occurrences(client, key, cap)
                if not records:
                    continue
                cells, countries = bin_records(records)
                features = features_from_cells(cells)
                family_node = next((f for f in families if f["id"] == family_id), {})
                properties = {
                    "genus": genus["latin"],
                    "genus_zh": genus["zh"],
                    "genus_id": genus["id"],
                    "family": (family_node.get("latin") or "").capitalize(),
                    "family_zh": family_node.get("zh") or "",
                    "family_id": family_id,
                    "gbif_key": key,
                    "resolution": "genus_key",
                    "records": len(records),
                    "cells": len(cells),
                    "grid": "1 degree",
                    "generated": access_date,
                    "source": source_line(access_date),
                }
                text = render_geojson(properties, features)
                json.loads(text)
                if len(text.encode("utf-8")) > GENUS_FILE_MAX_BYTES:
                    if not args.quiet:
                        print("genus %-22s skipped: %d bytes > %d"
                              % (genus["latin"], len(text.encode("utf-8")), GENUS_FILE_MAX_BYTES))
                    continue
                pulled += 1
                genus_outputs[genus["id"]] = (text, GENUS_DIR / ("%s.geojson" % genus["id"]))
                genus_summary.append(
                    {
                        "id": genus["id"],
                        "latin": genus["latin"],
                        "zh": genus["zh"],
                        "family_id": family_id,
                        "family_zh": family_node.get("zh") or "",
                        "gbif_key": key,
                        "records": len(records),
                        "cells": len(cells),
                        "species": genus["species"],
                        "file": "assets/geo/genus/%s.geojson" % genus["id"],
                        "gbif_url": "https://www.gbif.org/species/%s" % key,
                        "countries": top_countries(countries),
                    }
                )
                if not args.quiet:
                    print(
                        "genus  %-22s key=%-9s records=%4d cells=%4d %6.1f KB"
                        % (
                            genus["latin"],
                            key,
                            len(records),
                            len(cells),
                            len(text.encode("utf-8")) / 1024.0,
                        )
                    )

            # total size budget: drop the smallest genera until under 3 MB
            while genus_summary:
                total = sum(
                    len(genus_outputs[g["id"]][0].encode("utf-8")) for g in genus_summary
                )
                if total <= GENUS_TOTAL_MAX_BYTES:
                    break
                dropped = genus_summary.pop()
                genus_outputs.pop(dropped["id"], None)
                if not args.quiet:
                    print("genus %-22s dropped to keep the total under 3 MB" % dropped["latin"])
    except BudgetExceeded as exc:
        print(
            "time budget of %.0fs exhausted while fetching %s; nothing written.\n"
            "Rerun with a larger --budget (the cache resumes where this run stopped)."
            % (args.budget, exc),
            file=sys.stderr,
        )
        return 2
    except FetchError as exc:
        print("GBIF request failed: %s" % exc, file=sys.stderr)
        return 2

    summary = {
        "meta": {
            "access_date": access_date,
            "generated": access_date,
            "source": "GBIF occurrence search API",
            "source_url": GBIF_API + "/occurrence/search",
            "citation": "https://www.gbif.org/citation-guidelines",
            "license": "CC BY 4.0 (GBIF occurrence records)",
            "grid": "1 degree",
            "cell_centre": True,
            "cap_per_taxon": cap,
            "page_limit": PAGE_LIMIT,
            "family_files": len(family_summary),
            "genus_files": len(genus_summary),
            "records_families": total_records,
            "cells_families": total_cells,
            "genus_min_species": GENUS_MIN_SPECIES,
            "genus_max_files": args.max_genera,
            "tile_provider": "GBIF base map tiles (tile.gbif.org), OSM fallback",
            "note": (
                "Records are a deterministic capped sample of GBIF occurrence records, "
                "binned to a 1 degree grid; presence-only and strongly biased towards "
                "North America and Europe. Not a distribution boundary."
            ),
        },
        "families": family_summary,
        "genera": genus_summary,
    }
    summary_text = json.dumps(summary, ensure_ascii=False, indent=1) + "\n"
    json.loads(summary_text)

    outputs = list(family_outputs.values()) + list(genus_outputs.values())
    outputs.append((summary_text, SUMMARY))

    if write:
        for text, path in family_outputs.values():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
        if genus_outputs:
            GENUS_DIR.mkdir(parents=True, exist_ok=True)
            for text, path in genus_outputs.values():
                path.write_text(text, encoding="utf-8", newline="\n")
        SUMMARY.parent.mkdir(parents=True, exist_ok=True)
        SUMMARY.write_text(summary_text, encoding="utf-8", newline="\n")
        # remove stale artefacts (e.g. a genus dropped by --max-genera)
        for folder, keep in (
            (FAMILY_DIR, {p.name for _, p in family_outputs.values()}),
            (GENUS_DIR, {p.name for _, p in genus_outputs.values()}),
        ):
            if not folder.is_dir():
                continue
            for stale in sorted(folder.glob("*.geojson")):
                if stale.name not in keep:
                    stale.unlink()
                    print("removed stale %s" % stale.relative_to(ROOT))

        family_bytes = sum(len(t.encode("utf-8")) for t, _ in family_outputs.values())
        genus_bytes = sum(len(t.encode("utf-8")) for t, _ in genus_outputs.values())
        print(
            "\nwrote %d family files (%.0f KB, %d records, %d cells), "
            "%d genus files (%.0f KB), summary %d bytes"
            % (
                len(family_outputs),
                family_bytes / 1024.0,
                total_records,
                total_cells,
                len(genus_outputs),
                genus_bytes / 1024.0,
                len(summary_text.encode("utf-8")),
            )
        )
        print(
            "GBIF requests: %d network, %d cache hits, %.0fs elapsed"
            % (client.network_requests, client.cache_hits, time.monotonic() - client.started)
        )
        return 0

    # ---- check ------------------------------------------------------------
    problems = []
    for text, path in outputs:
        label = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            problems.append("%s: missing" % label)
            continue
        current = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if current != text:
            problems.append("%s: differs (rerun --write)" % label)
    expected = {p.name for _, p in family_outputs.values()} | {
        p.name for _, p in genus_outputs.values()
    }
    for folder, prefix in ((FAMILY_DIR, "family"), (GENUS_DIR, "genus")):
        if not folder.is_dir():
            continue
        for extra in sorted(folder.glob("*.geojson")):
            if extra.name not in expected:
                problems.append("%s/%s: stale file" % (prefix, extra.name))

    if problems:
        print("occurrence artefacts are out of date:", file=sys.stderr)
        for line in problems:
            print("  " + line, file=sys.stderr)
        return 1
    print("occurrence artefacts OK: %d files, %d records" % (len(outputs), total_records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
