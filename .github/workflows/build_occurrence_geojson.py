#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build 1-degree occurrence maps for every taxon of this checklist from GBIF.

Outputs (all committed, deterministic):

    assets/geo/family/<family_id>.geojson    13 files
    assets/geo/genus/<genus_id>.geojson       one per checklist genus with records
    assets/geo/species/<slug>.geojson         one per checklist species with records
    _data/occurrence_summary.json             summary consumed by Liquid
                                              (site.data.occurrence_summary)

Taxon scope / fossil filter
---------------------------
The maps are maps *of this checklist*, so only records that can be assigned to a
checklist taxon are used:

  * species / subspecies with a GBIF accepted usage key -> species map
  * records identified only to a genus                 -> genus / family maps
  * records of species that are NOT in the checklist    -> dropped.
    This includes every extinct / fossil species that GBIF keeps in the same
    family or genus (amber inclusions, compression fossils), which is what used
    to mix fossil dots into the family maps.
  * records whose basisOfRecord is FOSSIL_SPECIMEN or MATERIAL_CITATION are
    dropped as well (belt and braces: a fossil specimen wrongly identified as
    an extant species never reaches the maps).

Aggregation
-----------
Occurrences are pulled per checklist genus (taxonKey=<GBIF genus key>), so every
genus gets its own pull. A genus is fetched completely (all coordinate records
GBIF returns for it, hard safety stop 30000); the full set matters because a
sampled genus starves its rare species and those species pages would have no
map. Records are binned to a 1 degree grid (floor(lat), floor(lon)); a cell
stores the number of records n.

Cache / resume
--------------
_tmp/gbif_cache/ (gitignored) keeps the parsed records of every genus plus the
species/genus matches. A rerun never refetches a complete genus; --refresh
wipes the cache. The recorded access date is the cache fetch date, so a rerun
from the same cache is byte-identical.

Usage
-----
    python .github/workflows/build_occurrence_geojson.py --check
    python .github/workflows/build_occurrence_geojson.py --write
    python .github/workflows/build_occurrence_geojson.py --write --refresh
    python .github/workflows/build_occurrence_geojson.py --write --budget 21600
    python .github/workflows/build_occurrence_geojson.py --write --only mastotermes
    python .github/workflows/build_occurrence_geojson.py --vendor-leaflet
"""

from __future__ import annotations

import argparse
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
AUTHORITY_FILE = ROOT / "_data" / "authority_links.json"
GEO_DIR = ROOT / "assets" / "geo"
FAMILY_DIR = GEO_DIR / "family"
GENUS_DIR = GEO_DIR / "genus"
SPECIES_GEO_DIR = GEO_DIR / "species"
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
GRID = 1.0                # degrees; cells are floor(lat)..floor(lat)+1
MIN_INTERVAL = 0.5        # seconds between requests
MAX_RECORDS_PER_GENUS = 30000  # hard safety stop per genus (GBIF offset-safe)

FOSSIL_BASIS = ("FOSSIL_SPECIMEN", "MATERIAL_CITATION")
SPECIES_RANKS = ("SPECIES", "SUBSPECIES", "VARIETY", "FORM", "INFRASPECIFIC_NAME")

LEAFLET_VERSION = "1.9.4"
LEAFLET_BASE = "https://cdn.jsdelivr.net/npm/leaflet@%s/" % LEAFLET_VERSION
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


def dump_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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


def walk_families(node, out):
    """Families in document (classification) order."""
    if node.get("type") == "family":
        out.append(node)
    for child in node.get("children") or []:
        walk_families(child, out)


def genus_cap(species_count):  # noqa: ARG001 - kept for a stable call signature
    """Fetch every coordinate record of the genus, up to the safety stop.

    The first versions of this script sampled each genus (300-3000 records).
    Sampling starved rare species: their few records were never reached, so
    their species pages had no map. Pulling the full genus (still bounded by
    MAX_RECORDS_PER_GENUS) fixes that; the total is still small (~125k records
    for all termites) because occurrence/search caps pages at 300 records.
    """
    return MAX_RECORDS_PER_GENUS


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

    def remaining(self):
        return self.budget - (time.monotonic() - self.started)

    def _throttle(self):
        wait = MIN_INTERVAL - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

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
        tmp.write_text(dump_json(payload), encoding="utf-8")
        tmp.replace(path)

    def get(self, path, params, cache_name=None):
        """GET a JSON document; cache_name=None keeps it out of the disk cache."""
        if cache_name is not None:
            cached = self.read_cache(cache_name)
            if cached is not None:
                return cached
        if self.offline:
            raise FetchError("offline mode and no cache for %s" % (cache_name or path))
        if self.remaining() <= 0:
            raise BudgetExceeded(cache_name or path)

        url = GBIF_API + path + "?" + urllib.parse.urlencode(params)
        delay = 2.0
        last_error = None
        for attempt in range(7):
            self._throttle()
            if self.remaining() <= 0:
                raise BudgetExceeded(cache_name or path)
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=240) as response:
                    raw = response.read()
                self.network_requests += 1
                payload = json.loads(raw.decode("utf-8"))
                if cache_name is not None:
                    self.write_cache(cache_name, payload)
                return payload
            except urllib.error.HTTPError as exc:
                last_error = "HTTP %s" % exc.code
                if exc.code in (429, 500, 502, 503, 504) and attempt < 6:
                    time.sleep(delay)
                    delay = min(delay * 1.8, 30.0)
                    continue
                raise FetchError("%s -> %s (%s)" % (url, last_error, cache_name or path))
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                last_error = str(exc)
                if attempt < 6:
                    time.sleep(delay)
                    delay = min(delay * 1.8, 30.0)
                    continue
                raise FetchError("%s -> %s (%s)" % (url, last_error, cache_name or path))
        raise FetchError("%s -> %s (%s)" % (url, last_error, cache_name or path))


# --------------------------------------------------------------------------
# taxonomy + authority keys
# --------------------------------------------------------------------------
def load_taxonomy():
    index = json.loads(DATA_INDEX.read_text(encoding="utf-8"))
    nodes = []
    walk_families(index["tree"], nodes)
    families = []
    for node in nodes:
        families.append(
            {
                "id": node["id"],
                "latin": (node.get("latin") or "").strip(),
                "zh": (node.get("zh") or "").strip(),
                "counts": node.get("counts") or {},
            }
        )
    family_ids = {f["id"] for f in families}
    family_order = {f["id"]: i for i, f in enumerate(families)}

    species = {}
    if not SPECIES_DIR.is_dir():
        sys.exit("missing directory: %s" % SPECIES_DIR)
    for path in sorted(SPECIES_DIR.glob("*.md")):
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        slug = path.stem
        family_id = (fm.get("family_id") or "").strip()
        genus_id = (fm.get("genus_id") or "").strip()
        if family_id not in family_ids or not genus_id:
            sys.exit("species %s has an unknown family/genus" % path.name)
        subspecies = (fm.get("rank") or "species").strip().lower() == "subspecies"
        species[slug] = {
            "slug": slug,
            "latin": (fm.get("latin") or "").strip(),
            "zh": (fm.get("zh") or "").strip(),
            "rank": "subspecies" if subspecies else "species",
            "family_id": family_id,
            "genus_id": genus_id,
            "type": (fm.get("type") or "").strip().lower() == "true",
            "genus_latin": (fm.get("genus_latin") or "").strip(),
            "genus_zh": (fm.get("genus_zh") or "").strip(),
        }

    genera = {}
    for slug, info in species.items():
        gid = info["genus_id"]
        entry = genera.get(gid)
        if entry is None:
            entry = genera[gid] = {
                "id": gid,
                "latin": info["genus_latin"],
                "zh": info["genus_zh"],
                "family_id": info["family_id"],
                "species": [],
            }
        if info["rank"] == "species":
            entry["species"].append(slug)
    ordered = sorted(
        genera.values(),
        key=lambda g: (family_order.get(g["family_id"], 999), g["latin"] or g["id"]),
    )
    for g in ordered:
        g["species"].sort(key=lambda s: species[s]["latin"])
        g["species_count"] = len(g["species"])
    return families, ordered, species


def load_authorities(species):
    """Map checklist species -> GBIF accepted species key (and back)."""
    latin_to_slug = {s["latin"]: slug for slug, s in species.items() if s["latin"]}
    data = json.loads(AUTHORITY_FILE.read_text(encoding="utf-8"))
    taxa = data.get("taxa") or {}
    items = []
    for name, entry in taxa.items():
        gbif = entry.get("gbif") or {}
        status = (gbif.get("status") or "").upper()
        rank = (gbif.get("rank") or "").upper()
        key = gbif.get("key")
        accepted = gbif.get("accepted") or {}
        if status == "SYNONYM" and accepted.get("key"):
            use_key = accepted["key"]
            order = 1
        elif status == "ACCEPTED" and key and rank in ("SPECIES", "SUBSPECIES"):
            use_key = key
            order = 0
        else:
            continue
        slug = latin_to_slug.get(name)
        if not slug:
            continue
        items.append((order, name, slug, int(use_key)))
    key_to_slug = {}
    slug_to_key = {}
    for _order, name, slug, use_key in sorted(items):
        if use_key in key_to_slug:
            continue
        key_to_slug[use_key] = slug
        slug_to_key[slug] = use_key
    return key_to_slug, slug_to_key


def match_taxon(client, name, rank):
    """species/match for a name+rank; returns the JSON (may be matchType NONE)."""
    return client.get(
        "/species/match",
        {"name": name, "rank": rank},
        "match_%s_%s.json" % (re.sub(r"[^A-Za-z0-9]+", "_", name).upper(), rank),
    )


# --------------------------------------------------------------------------
# occurrence pull (per genus, compact cache)
# --------------------------------------------------------------------------
def compact_record(item):
    lat = item.get("decimalLatitude")
    lon = item.get("decimalLongitude")
    if lat is None or lon is None:
        return None
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return None
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        return None
    if (item.get("occurrenceStatus") or "").upper() == "ABSENT":
        return None
    return [
        item.get("key"),
        round(lat, 4),
        round(lon, 4),
        (item.get("basisOfRecord") or "").upper(),
        (item.get("taxonRank") or "").upper(),
        item.get("acceptedTaxonKey"),
        item.get("speciesKey"),
        item.get("genusKey"),
        (item.get("countryCode") or ""),
    ]


def pull_genus(client, genus_key, cap):
    """Occurrence records of one GBIF genus (compact tuples), resumable.

    A cached genus is reused when it already holds at least min(count, cap)
    records, so a cache widened by hand (a full uncapped pull for a big genus)
    is not refetched and every record it holds is used. An incomplete cache is
    extended from where it stopped (pages_fetched * page size).
    """
    cache_name = "occ_genus_%s.json" % genus_key
    cached = client.read_cache(cache_name)
    records = []
    count = None
    offset = 0
    if cached is not None:
        raw_count = cached.get("count")
        count = None if raw_count is None else int(raw_count)
        records = list(cached.get("records") or [])
        if count == 0:
            return 0, []
        if count is not None and len(records) >= min(count, cap):
            return count, records
        offset = int(cached.get("pages_fetched") or 0) * PAGE_LIMIT

    while True:
        if count is not None and len(records) >= min(count, cap):
            break
        if count is None and len(records) >= cap:
            break
        page = client.get(
            "/occurrence/search",
            {
                "taxonKey": genus_key,
                "hasCoordinate": "true",
                "hasGeospatialIssue": "false",
                "limit": PAGE_LIMIT,
                "offset": offset,
            },
        )
        if count is None:
            count = int(page.get("count") or 0)
        results = page.get("results") or []
        for item in results:
            rec = compact_record(item)
            if rec is not None:
                records.append(rec)
        offset += PAGE_LIMIT
        if page.get("endOfRecords") or len(results) < PAGE_LIMIT:
            break
    if count is None:
        count = len(records)
    client.write_cache(
        cache_name,
        {"genus_key": genus_key, "cap": cap, "count": count,
         "records": records, "pages_fetched": offset // PAGE_LIMIT},
    )
    return count, records


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------
def features_from_cells(cells):
    features = []
    for lat_index, lon_index in sorted(cells):
        lat = round(lat_index * GRID + GRID / 2.0, 3)
        lon = round(lon_index * GRID + GRID / 2.0, 3)
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
        "hasCoordinate=true, hasGeospatialIssue=false, checklist extant taxa only, "
        "fossil basisOfRecord excluded, accessed %s; aggregated to a 1 degree grid "
        "by this site" % access_date
    )


# --------------------------------------------------------------------------
# Leaflet vendoring (unchanged helper)
# --------------------------------------------------------------------------
def vendor_leaflet():
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
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write artefacts")
    mode.add_argument("--check", action="store_true", help="compare artefacts (default)")
    parser.add_argument("--refresh", action="store_true", help="wipe cache, refetch GBIF")
    parser.add_argument("--budget", type=float, default=1200.0,
                        help="network time budget, seconds (default 1200)")
    parser.add_argument("--date", help="override the recorded access date (YYYY-MM-DD)")
    parser.add_argument("--only", help="comma separated checklist genus ids (debug)")
    parser.add_argument("--offline", action="store_true", help="never touch the network")
    parser.add_argument("--vendor-leaflet", action="store_true",
                        help="download Leaflet and exit")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if args.vendor_leaflet:
        vendor_leaflet()
        return 0

    write = args.write
    only = {g.strip() for g in (args.only or "").split(",") if g.strip()}

    families, genera, species = load_taxonomy()
    key_to_slug, slug_to_key = load_authorities(species)
    family_by_id = {f["id"]: f for f in families}
    genus_by_id = {g["id"]: g for g in genera}

    client = GBIFClient(refresh=args.refresh, budget=args.budget, offline=args.offline)
    meta_path = client.cache / "_meta.json"
    if args.refresh and meta_path.is_file():
        meta_path.unlink()
    if args.date:
        access_date = args.date
    elif meta_path.is_file():
        try:
            access_date = json.loads(meta_path.read_text(encoding="utf-8"))["access_date"]
        except (ValueError, KeyError):
            access_date = utc_today()
    else:
        access_date = utc_today()
        client.write_cache("_meta.json", {"access_date": access_date})

    # GBIF genus keys -------------------------------------------------------
    genus_keys = {}
    genus_key_to_id = {}
    missing_genus_keys = []
    for genus in genera:
        if not genus["latin"]:
            missing_genus_keys.append(genus["id"])
            continue
        match = match_taxon(client, genus["latin"], "GENUS")
        key = match.get("usageKey") if match.get("matchType") != "NONE" else None
        if not key:
            missing_genus_keys.append(genus["id"])
            continue
        genus_keys[genus["id"]] = int(key)
        genus_key_to_id.setdefault(int(key), genus["id"])
    if not args.quiet:
        print(
            "genus matches: %d/%d (missing %d)"
            % (len(genus_keys), len(genera), len(missing_genus_keys))
        )

    # pull + aggregate ------------------------------------------------------
    species_cells = {}
    species_records = {}
    genus_cells = {}
    genus_records = {}
    family_cells = {}
    family_records = {}
    seen_records = 0
    seen_ids = set()
    pulled_genera = 0
    budget_hit = False

    try:
        for genus in genera:
            gid = genus["id"]
            if only and gid not in only:
                continue
            gkey = genus_keys.get(gid)
            if not gkey:
                continue
            cap = genus_cap(genus["species_count"] or 1)
            try:
                total, records = pull_genus(client, gkey, cap)
            except FetchError as exc:
                # one unreachable genus must not abort a multi-hour build:
                # the cache keeps every completed genus, so a rerun retries it
                print("genus %-26s skipped: %s" % (genus["latin"], exc),
                      file=sys.stderr)
                continue
            pulled_genera += 1
            if not args.quiet:
                print(
                    "genus %-26s key=%-9s cap=%4d got=%4d /%5d"
                    % (genus["latin"], gkey, cap, len(records), total)
                )
            for rec in records:
                rid, lat, lon, basis, rank, accepted, sp_key, genus_key, country = rec
                if basis in FOSSIL_BASIS:
                    continue
                if rid is not None and rid in seen_ids:
                    continue
                slug = key_to_slug.get(accepted) or key_to_slug.get(sp_key)
                if slug:
                    info = species[slug]
                    cell = (int(math.floor(lat / GRID)), int(math.floor(lon / GRID)))
                    species_cells.setdefault(slug, Counter())[cell] += 1
                    species_records[slug] = species_records.get(slug, 0) + 1
                    genus_cells.setdefault(info["genus_id"], Counter())[cell] += 1
                    genus_records[info["genus_id"]] = (
                        genus_records.get(info["genus_id"], 0) + 1
                    )
                    family_cells.setdefault(info["family_id"], Counter())[cell] += 1
                    family_records[info["family_id"]] = (
                        family_records.get(info["family_id"], 0) + 1
                    )
                    if rid is not None:
                        seen_ids.add(rid)
                    seen_records += 1
                    continue
                if rank in SPECIES_RANKS:
                    # a species that is not in the checklist (extinct / fossil /
                    # unlisted extant species): never shown on these maps
                    continue
                owner = genus_key_to_id.get(int(genus_key)) if genus_key else None
                if owner:
                    cell = (int(math.floor(lat / GRID)), int(math.floor(lon / GRID)))
                    genus_cells.setdefault(owner, Counter())[cell] += 1
                    genus_records[owner] = genus_records.get(owner, 0) + 1
                    fam_id = genus_by_id[owner]["family_id"]
                    family_cells.setdefault(fam_id, Counter())[cell] += 1
                    family_records[fam_id] = family_records.get(fam_id, 0) + 1
                    if rid is not None:
                        seen_ids.add(rid)
                    seen_records += 1
    except BudgetExceeded as exc:
        budget_hit = True
        print(
            "time budget of %.0fs exhausted while fetching %s; writing what is "
            "already aggregated. Rerun with a larger --budget (the cache resumes "
            "where this run stopped)." % (args.budget, exc),
            file=sys.stderr,
        )
    except FetchError as exc:
        print("GBIF request failed: %s" % exc, file=sys.stderr)
        return 2

    # render artefacts ------------------------------------------------------
    family_outputs = []
    genus_outputs = []
    species_outputs = []

    for family in families:
        fid = family["id"]
        cells = family_cells.get(fid)
        if not cells:
            continue
        props = {
            "level": "family",
            "family": family["latin"],
            "family_zh": family["zh"],
            "family_id": fid,
            "records": family_records.get(fid, 0),
            "cells": len(cells),
            "genera": (family.get("counts") or {}).get("genera"),
            "species": (family.get("counts") or {}).get("species"),
            "grid": "1 degree",
            "taxon_scope": "checklist_extant",
            "generated": access_date,
            "source": source_line(access_date),
        }
        text = render_geojson(props, features_from_cells(cells))
        json.loads(text)
        family_outputs.append(
            (text, FAMILY_DIR / ("%s.geojson" % fid),
             "assets/geo/family/%s.geojson" % fid, props)
        )

    for genus in genera:
        gid = genus["id"]
        cells = genus_cells.get(gid)
        if not cells:
            continue
        fam = family_by_id[genus["family_id"]]
        props = {
            "level": "genus",
            "genus": genus["latin"],
            "genus_zh": genus["zh"],
            "genus_id": gid,
            "family": fam["latin"],
            "family_zh": fam["zh"],
            "family_id": fam["id"],
            "gbif_key": genus_keys.get(gid),
            "records": genus_records.get(gid, 0),
            "cells": len(cells),
            "species": genus["species_count"],
            "grid": "1 degree",
            "taxon_scope": "checklist_extant",
            "generated": access_date,
            "source": source_line(access_date),
        }
        text = render_geojson(props, features_from_cells(cells))
        json.loads(text)
        genus_outputs.append(
            (text, GENUS_DIR / ("%s.geojson" % gid),
             "assets/geo/genus/%s.geojson" % gid, props)
        )

    for slug in sorted(species):
        cells = species_cells.get(slug)
        if not cells:
            continue
        info = species[slug]
        genus = genus_by_id.get(info["genus_id"]) or {}
        fam = family_by_id[info["family_id"]]
        props = {
            "level": "species",
            "species": info["latin"],
            "species_zh": info["zh"],
            "slug": slug,
            "rank": info["rank"],
            "type_species": bool(info["type"]),
            "genus": genus.get("latin") or "",
            "genus_zh": genus.get("zh") or "",
            "genus_id": info["genus_id"],
            "family": fam["latin"],
            "family_zh": fam["zh"],
            "family_id": fam["id"],
            "gbif_key": slug_to_key.get(slug),
            "records": species_records.get(slug, 0),
            "cells": len(cells),
            "grid": "1 degree",
            "taxon_scope": "checklist_extant",
            "generated": access_date,
            "source": source_line(access_date),
        }
        text = render_geojson(props, features_from_cells(cells))
        json.loads(text)
        species_outputs.append(
            (text, SPECIES_GEO_DIR / ("%s.geojson" % slug),
             "assets/geo/species/%s.geojson" % slug, props)
        )

    family_summary = [
        {
            "id": props["family_id"],
            "latin": props["family"],
            "zh": props["family_zh"],
            "records": props["records"],
            "cells": props["cells"],
            "genera": props.get("genera"),
            "species": props.get("species"),
            "file": rel,
        }
        for _text, _path, rel, props in family_outputs
    ]
    genus_summary = [
        {
            "id": props["genus_id"],
            "latin": props["genus"],
            "zh": props["genus_zh"],
            "family_id": props["family_id"],
            "family_latin": props["family"],
            "family_zh": props["family_zh"],
            "gbif_key": props.get("gbif_key"),
            "records": props["records"],
            "cells": props["cells"],
            "species": props.get("species"),
            "file": rel,
        }
        for _text, _path, rel, props in genus_outputs
    ]
    species_summary = {
        props["slug"]: {
            "latin": props["species"],
            "zh": props["species_zh"],
            "rank": props["rank"],
            "family_id": props["family_id"],
            "genus_id": props["genus_id"],
            "gbif_key": props.get("gbif_key"),
            "records": props["records"],
            "cells": props["cells"],
            "file": rel,
        }
        for _text, _path, rel, props in species_outputs
    }
    species_without_key = sorted(set(species) - set(slug_to_key))

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
            "page_limit": PAGE_LIMIT,
            "max_records_per_genus": MAX_RECORDS_PER_GENUS,
            "taxon_scope": "checklist_extant",
            "fossil_filter": {
                "excluded_basis_of_record": list(FOSSIL_BASIS),
                "excluded_taxa": "GBIF species that are not part of this checklist "
                "(which only contains extant taxa, so extinct / fossil species and "
                "amber inclusions are dropped)",
            },
            "partial": budget_hit,
            "family_files": len(family_summary),
            "genus_files": len(genus_summary),
            "species_files": len(species_summary),
            "records_total": seen_records,
            "genera_total": len(genera),
            "genera_with_records": len(genus_summary),
            "species_total": len(species),
            "species_with_map": len(species_summary),
            "species_without_gbif_key": len(species_without_key),
            "genera_without_gbif_key": len(missing_genus_keys),
            "pulled_genera": pulled_genera,
            "note": (
                "Only occurrences assignable to a taxon of this checklist are used: "
                "species maps from GBIF accepted species keys, genus/family maps also "
                "include records identified to the genus only. Extinct / fossil species "
                "in the same GBIF genus or family are excluded, and FOSSIL_SPECIMEN / "
                "MATERIAL_CITATION records are dropped. Per-genus record caps make this "
                "a reproducible sample, not a random one; presence-only data is strongly "
                "biased towards North America and Europe."
            ),
        },
        "families": family_summary,
        "genera": genus_summary,
        "species": species_summary,
    }
    summary_text = json.dumps(summary, ensure_ascii=False, indent=1) + "\n"
    json.loads(summary_text)

    geo_outputs = (
        [(text, path) for text, path, _rel, _props in family_outputs]
        + [(text, path) for text, path, _rel, _props in genus_outputs]
        + [(text, path) for text, path, _rel, _props in species_outputs]
    )
    outputs = geo_outputs + [(summary_text, SUMMARY)]

    if write:
        for folder in (FAMILY_DIR, GENUS_DIR, SPECIES_GEO_DIR):
            folder.mkdir(parents=True, exist_ok=True)
        for text, path in geo_outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
        SUMMARY.parent.mkdir(parents=True, exist_ok=True)
        SUMMARY.write_text(summary_text, encoding="utf-8", newline="\n")

        if not only:
            keep = {(path.parent, path.name) for _text, path in geo_outputs}
            for folder in (FAMILY_DIR, GENUS_DIR, SPECIES_GEO_DIR):
                for stale in sorted(folder.glob("*.geojson")):
                    if (folder, stale.name) not in keep:
                        stale.unlink()
                        print("removed stale %s" % stale.relative_to(ROOT))

        family_bytes = sum(len(t.encode("utf-8")) for t, _p in
                           [(t, p) for t, p, _rel, _props in family_outputs])
        genus_bytes = sum(len(t.encode("utf-8")) for t, _p in
                          [(t, p) for t, p, _rel, _props in genus_outputs])
        species_bytes = sum(len(t.encode("utf-8")) for t, _p in
                            [(t, p) for t, p, _rel, _props in species_outputs])
        print(
            "\nwrote %d family files (%.0f KB), %d genus files (%.0f KB), "
            "%d species files (%.0f KB), summary %d bytes, %d unique records"
            % (
                len(family_outputs),
                family_bytes / 1024.0,
                len(genus_outputs),
                genus_bytes / 1024.0,
                len(species_outputs),
                species_bytes / 1024.0,
                len(summary_text.encode("utf-8")),
                seen_records,
            )
        )
        print(
            "GBIF requests: %d network, %d cache hits, %.0fs elapsed"
            % (client.network_requests, client.cache_hits,
               time.monotonic() - client.started)
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
    if problems:
        print("occurrence artefacts are out of date:", file=sys.stderr)
        for line in problems:
            print("  " + line, file=sys.stderr)
        return 1
    print(
        "occurrence artefacts OK: %d files, %d records"
        % (len(outputs), seen_records)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
