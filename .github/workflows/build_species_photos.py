#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collect openly licensed photos (CC0 / CC BY / CC BY-SA) for every taxon.

Sources
-------
iNaturalist        https://api.inaturalist.org/v1/observations
Wikimedia Commons  https://commons.wikimedia.org/w/api.php

Only CC0, CC BY x.y and CC BY-SA x.y are accepted.  NC / ND / public-domain /
GFDL / unknown files are rejected on purpose: the checklist itself is CC BY 4.0
and the gallery has to stay reusable under the same terms (see
_tools/图片授权与署名说明.md).

Output
------
_data/species_photos.json  (committed; doubles as the resumable cache)

    {"meta": {"generated", "license_policy", "sources", "counts", "no_photos"},
     "species": {"<latin>": [{source, src, thumb, width, height,
                              credit, license, licenseUrl, page}, ...]}}

"meta.no_photos" is the per-source negative cache: a sorted list of taxa that
were queried against that source and produced no acceptable photo.  Without it a
rerun would hammer both APIs again for the thousands of taxa that simply have no
freely licensed image.  Presence in "species" plus these lists is what makes a
rerun cheap and --write idempotent.

Determinism
-----------
Keys and lists are sorted, the JSON layout is fixed and the "generated"
timestamp is only refreshed when the payload actually changes, so rerunning with
a warm cache produces a byte-identical file.

Usage
-----
    python .github/workflows/build_species_photos.py --check
    python .github/workflows/build_species_photos.py --write --limit 50
    python .github/workflows/build_species_photos.py --write --budget 3600
    python .github/workflows/build_species_photos.py --write --refresh --only inat
    python .github/workflows/build_species_photos.py --write --all-names _tmp/names.txt

Exit codes: 0 ok, 1 validation failure / bad usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "_species"
OUT = ROOT / "_data" / "species_photos.json"

PROJECT_URL = ("https://bennetgreen-bilibili.github.io/"
               "-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md")
USER_AGENT = ("IsopteraChecklistBot/1.0 (+%s; species photo gallery collector; "
              "contact: open an issue on the repository)" % PROJECT_URL)

INAT_API = "https://api.inaturalist.org/v1/observations"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# --- licence policy -------------------------------------------------------
INAT_ALLOWED = ("cc0", "cc-by", "cc-by-sa")
INAT_LABEL = {"cc0": "CC0", "cc-by": "CC BY", "cc-by-sa": "CC BY-SA"}
INAT_LICENSE_URL = {
    "cc0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "cc-by": "https://creativecommons.org/licenses/by/4.0/",
    "cc-by-sa": "https://creativecommons.org/licenses/by-sa/4.0/",
}
ALLOWED_LABELS = ("CC0", "CC BY", "CC BY-SA")

COMMONS_CC0_RE = re.compile(r"^cc0(?:[ -]?1\.0)?$", re.I)
COMMONS_CC_BY_RE = re.compile(
    r"^cc[\s-]+by(?:[\s-]*sa)?[\s-]+\d\.\d(?:\s+[a-z][a-z .]{0,14})?$", re.I)
COMMONS_DENY_RE = re.compile(r"\b(?:nc|nd|non-?commercial|no-?deriv\w*)\b", re.I)

MAX_PHOTOS = 6
INAT_PER_PAGE = 10
COMMONS_LIMIT = 8
COMMONS_THUMB_WIDTH = 800
SOURCE_ORDER = {"inaturalist": 0, "commons": 1}
SOURCE_SITE = {
    "inaturalist": "https://www.inaturalist.org",
    "commons": "https://commons.wikimedia.org",
}
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp")

# be polite: iNat asks for <= 60 req/min, Wikimedia for serial requests
MIN_INTERVAL = {"inaturalist": 1.05, "commons": 0.34}
MAX_RETRIES = 4

FM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)[ \t]*:[ \t]*(.*)$")

PHOTO_KEYS = ("source", "src", "thumb", "width", "height",
              "credit", "license", "licenseUrl", "page")


# ---------------------------------------------------------------- utilities
class _TextExtractor(HTMLParser):
    """Collect the visible text of a small HTML fragment."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in ("br", "p", "div", "li"):
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("p", "div", "li"):
            self.parts.append(" ")


def strip_html(value):
    """Turn an extmetadata HTML blob (e.g. Artist) into plain text."""
    if not value:
        return ""
    text = value if isinstance(value, str) else str(value)
    if "<" in text or "&" in text:
        parser = _TextExtractor()
        try:
            parser.feed(text)
            parser.close()
            text = "".join(parser.parts)
        except Exception:  # malformed markup - fall back to a crude strip
            text = re.sub(r"<[^>]*>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def first_value(extmetadata, key):
    entry = extmetadata.get(key) or {}
    value = entry.get("value")
    return value if isinstance(value, str) else ("" if value is None else str(value))


def strip_utm(url):
    """Drop the utm_* tracking query that upload.wikimedia.org appends."""
    if not url:
        return ""
    parts = urllib.parse.urlsplit(url)
    if not parts.query:
        return url
    keep = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
            if not k.lower().startswith("utm_")]
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(keep), ""))


def commons_license_ok(short_name):
    """CC0 / CC BY x.y / CC BY-SA x.y only.  Everything else is refused."""
    name = re.sub(r"\s+", " ", (short_name or "").strip())
    if not name:
        return False
    if COMMONS_DENY_RE.search(name):
        return False
    return bool(COMMONS_CC0_RE.match(name) or COMMONS_CC_BY_RE.match(name))


def display_license(short_name):
    name = re.sub(r"\s+", " ", (short_name or "").strip())
    if COMMONS_CC0_RE.match(name):
        return "CC0"
    return name


def default_license_url(label):
    """Best-effort deed URL for a Commons licence short name."""
    low = (label or "").strip().lower()
    if low in ("cc0", "cc0 1.0"):
        return INAT_LICENSE_URL["cc0"]
    match = re.match(r"^cc[\s-]+by([\s-]*sa)?[\s-]+(\d[\.]\d)", low)
    if match:
        kind = "by-sa" if match.group(1) else "by"
        return "https://creativecommons.org/licenses/%s/%s/" % (kind, match.group(2))
    return ""


def https_url(url):
    url = (url or "").strip()
    if url.startswith("http://"):
        url = "https://" + url[len("http://"):]
    return url


class PoliteClient(object):
    """Serial HTTP client with a minimum interval and exponential backoff."""

    def __init__(self, source):
        self.source = source
        self.min_interval = MIN_INTERVAL[source]
        self.last = 0.0
        self.requests = 0
        self.retries = 0
        self._gate = threading.Lock()

    def _sleep_until_slot(self):
        # the gate serialises request *starts*, so -w N never exceeds the
        # per-source rate even though N requests can be in flight together
        with self._gate:
            wait = self.min_interval - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.monotonic()

    def get_json(self, url):
        """Return the decoded JSON body, or None on an unrecoverable error."""
        attempt = 0
        while True:
            self._sleep_until_slot()
            try:
                self.requests += 1
                request = urllib.request.Request(url, headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                })
                with urllib.request.urlopen(request, timeout=45) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                code = exc.code
                if code == 429 or 500 <= code < 600:
                    if attempt >= MAX_RETRIES:
                        print("  ! %s HTTP %s after %d retries - skipping this taxon"
                              % (self.source, code, attempt), file=sys.stderr)
                        return None
                    delay = min(120.0, 4.0 * (2 ** attempt))
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    if retry_after and retry_after.isdigit():
                        delay = min(120.0, max(delay, float(retry_after)))
                    print("  ! %s HTTP %s - backing off %.0fs"
                          % (self.source, code, delay), file=sys.stderr)
                    time.sleep(delay)
                    attempt += 1
                    self.retries += 1
                    continue
                print("  ! %s HTTP %s for %s" % (self.source, code, url), file=sys.stderr)
                return None
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                if attempt >= MAX_RETRIES:
                    print("  ! %s network error after %d retries: %s"
                          % (self.source, attempt, exc), file=sys.stderr)
                    return None
                delay = min(60.0, 2.0 * (2 ** attempt))
                print("  ! %s network error (%s) - retrying in %.0fs"
                      % (self.source, exc, delay), file=sys.stderr)
                time.sleep(delay)
                attempt += 1
                self.retries += 1


# ------------------------------------------------------------ iNaturalist
def inat_query(latin):
    return INAT_API + "?" + urllib.parse.urlencode({
        "taxon_name": latin,
        "photos": "true",
        "quality_grade": "research",
        "per_page": str(INAT_PER_PAGE),
        "photo_license": ",".join(INAT_ALLOWED),
    })


def inat_photo_dims(photo):
    """Pixel size of the 'large' rendition (iNat caps the long edge at 1024)."""
    dims = photo.get("original_dimensions") or {}
    width, height = dims.get("width"), dims.get("height")
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        return None
    long_edge = max(width, height)
    if long_edge > 1024:
        scale = 1024.0 / long_edge
        width = max(1, int(round(width * scale)))
        height = max(1, int(round(height * scale)))
    return width, height


def fetch_inaturalist(client, latin):
    """One request per taxon; only observations of *exactly* this taxon are used.

    Two photos per observation at most on the first pass - one uploader often
    posts a burst of near-identical frames, which would fill the whole grid with
    the same specimen - then top up to MAX_PHOTOS from the remaining candidates.
    """
    data = client.get_json(inat_query(latin))
    if data is None:
        return None
    candidates = []
    for obs in data.get("results") or []:
        taxon = obs.get("taxon") or {}
        if (taxon.get("name") or "") != latin:
            continue  # descendant or sibling taxon returned by the search
        obs_id = obs.get("id")
        if not isinstance(obs_id, int):
            continue
        quality = obs.get("quality_grade")
        if quality and quality != "research":
            continue
        observer = (obs.get("user") or {}).get("login") or ""
        page = "%s/observations/%d" % (SOURCE_SITE["inaturalist"], obs_id)
        for photo in obs.get("photos") or []:
            code = (photo.get("license_code") or "").lower()
            if code not in INAT_ALLOWED:
                continue
            if photo.get("hidden"):
                continue
            url = photo.get("url") or ""
            if not url:
                continue
            dims = inat_photo_dims(photo)
            if not dims:
                continue
            credit = strip_html(photo.get("attribution") or "")
            if not credit or credit.lower() in ("no rights reserved", "no copyright"):
                # CC0 uploads carry no author in the attribution string
                credit = (("iNaturalist observer " + observer).strip() if observer
                          else "iNaturalist observer")
            candidates.append((obs_id, {
                "source": "inaturalist",
                "src": url.replace("square", "large"),
                "thumb": url.replace("square", "medium"),
                "width": dims[0],
                "height": dims[1],
                "credit": credit,
                "license": INAT_LABEL[code],
                "licenseUrl": INAT_LICENSE_URL[code],
                "page": page,
            }))
    # newest observations first: stable and independent of the API's own order
    candidates.sort(key=lambda item: -item[0])
    picked = []
    per_observation = {}
    for obs_id, entry in candidates:
        if per_observation.get(obs_id, 0) >= 2:
            continue
        per_observation[obs_id] = per_observation.get(obs_id, 0) + 1
        picked.append(entry)
    taken = set(entry["src"] for entry in picked)
    for _obs_id, entry in candidates:
        if len(picked) >= MAX_PHOTOS:
            break
        if entry["src"] in taken:
            continue
        taken.add(entry["src"])
        picked.append(entry)
    return picked


# ---------------------------------------------------------------- Commons
def commons_query(latin):
    return COMMONS_API + "?" + urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": '"%s"' % latin,
        "gsrnamespace": "6",
        "gsrlimit": str(COMMONS_LIMIT),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size",
        "iiurlwidth": str(COMMONS_THUMB_WIDTH),
        "format": "json",
        "formatversion": "2",
    })


def commons_name_match(latin, title, ext):
    """Commons search is full text - insist that the binomial really appears.

    Without this, a generic "termite queen" file shows up for Macrotermes
    bellicosus and would be credited to a species it may not even show.
    Subspecies are usually filed under the binomial, so compare the first two
    words for trinomials.
    """
    key = " ".join(latin.split()[:2])
    haystack = " ".join([
        title,
        strip_html(first_value(ext, "ImageDescription")),
        strip_html(first_value(ext, "Categories")),
    ])
    haystack = re.sub(r"[_\s]+", " ", haystack).lower().strip()
    return key.lower() in haystack


def fetch_commons(client, latin):
    """One request per taxon; files outside CC0 / CC BY / CC BY-SA are dropped."""
    data = client.get_json(commons_query(latin))
    if data is None:
        return None
    pages = (data.get("query") or {}).get("pages") or []
    picked = []
    for page in pages:
        title = page.get("title") or ""
        if not title.lower().endswith(IMAGE_EXTS):
            continue  # PDFs / SVG logos / DjVu scans cannot go into PhotoSwipe
        info = (page.get("imageinfo") or [{}])[0]
        ext = info.get("extmetadata") or {}
        short_name = strip_html(first_value(ext, "LicenseShortName"))
        if not commons_license_ok(short_name):
            continue
        if not commons_name_match(latin, title, ext):
            continue
        src = strip_utm(info.get("url") or "")
        thumb = strip_utm(info.get("thumburl") or "")
        page_url = info.get("descriptionurl") or ""
        width, height = info.get("width"), info.get("height")
        if not src or not thumb or not page_url:
            continue
        if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
            continue
        license_url = https_url(strip_html(first_value(ext, "LicenseUrl")))
        if not license_url.startswith("https://creativecommons.org/"):
            license_url = default_license_url(display_license(short_name))
        if not license_url.startswith("https://creativecommons.org/"):
            continue  # cannot state the licence properly -> leave it out
        artist = strip_html(first_value(ext, "Artist"))
        if not artist:
            artist = "Wikimedia Commons"
        if len(artist) > 160:
            artist = artist[:157].rstrip() + "..."
        picked.append({
            "source": "commons",
            "src": src,
            "thumb": thumb,
            "width": width,
            "height": height,
            "credit": artist,
            "license": display_license(short_name),
            "licenseUrl": license_url,
            "page": page_url,
        })
    return picked


# ---------------------------------------------------------------- payload
def parse_front_matter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = {}
    for line in text[3:end].splitlines():
        match = FM_RE.match(line)
        if not match:
            continue
        key, raw = match.group(1), match.group(2).strip()
        if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
            raw = raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        elif len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
            raw = raw[1:-1].replace("''", "'")
        data[key] = raw
    return data


def list_species_names():
    """All taxa from _species/*.md: species alphabetically, subspecies last."""
    if not SPECIES_DIR.is_dir():
        sys.exit("missing directory: %s" % SPECIES_DIR)
    rows = []
    for path in sorted(SPECIES_DIR.glob("*.md")):
        front_matter = parse_front_matter(path.read_text(encoding="utf-8"))
        latin = (front_matter.get("latin") or "").strip()
        if not latin:
            sys.exit("bad front matter in %s (latin missing)" % path.name)
        rank = str(front_matter.get("rank") or "species").lower()
        rows.append((1 if rank == "subspecies" else 0, latin, path.name))
    rows.sort()
    seen = set()
    names = []
    for _rank, latin, _path in rows:
        if latin in seen:
            continue
        seen.add(latin)
        names.append(latin)
    return names


def read_names_file(path):
    names = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.append(line)
    return names


def load_existing():
    if not OUT.is_file():
        return {}, {key: set() for key in ("inaturalist", "commons")}, {}
    with OUT.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    meta = payload.get("meta") or {}
    no_photos = meta.get("no_photos") or {}
    return (payload.get("species") or {},
            {key: set(no_photos.get(key) or []) for key in ("inaturalist", "commons")},
            meta)


def dedupe(photos):
    seen = set()
    out = []
    for photo in photos:
        key = photo.get("src")
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(photo)
    return out


def ordered(photos):
    """iNaturalist first, Commons second, stable inside each source; max 6."""
    indexed = list(enumerate(photos))
    indexed.sort(key=lambda item: (SOURCE_ORDER.get(item[1].get("source"), 9), item[0]))
    return [photo for _index, photo in indexed][:MAX_PHOTOS]


def build_meta(species, searched, no_photos, generated):
    photos_inat = sum(1 for plist in species.values() for p in plist
                      if p["source"] == "inaturalist")
    photos_commons = sum(1 for plist in species.values() for p in plist
                         if p["source"] == "commons")
    return {
        "generated": generated,
        "license_policy": "CC0 / CC BY / CC BY-SA only",
        "sources": {
            "inaturalist": {
                "name": "iNaturalist",
                "site": SOURCE_SITE["inaturalist"],
                "api": INAT_API,
                "query": ("taxon_name=<latin>&photos=true&quality_grade=research"
                          "&per_page=%d&photo_license=%s"
                          % (INAT_PER_PAGE, ",".join(INAT_ALLOWED))),
                "licenses": ["CC0", "CC BY", "CC BY-SA"],
                "accepted_license_codes": list(INAT_ALLOWED),
                "taxon_match": "observation.taxon.name must equal the checklist name exactly",
            },
            "commons": {
                "name": "Wikimedia Commons",
                "site": SOURCE_SITE["commons"],
                "api": COMMONS_API,
                "query": ('action=query&generator=search&gsrsearch="<latin>"&gsrnamespace=6'
                          "&gsrlimit=%d&prop=imageinfo&iiprop=url|extmetadata|size"
                          "&iiurlwidth=%d&format=json" % (COMMONS_LIMIT, COMMONS_THUMB_WIDTH)),
                "licenses": ["CC0", "CC BY x.y", "CC BY-SA x.y"],
                "accepted_license_names": "LicenseShortName matching CC0 / CC BY x.y / CC BY-SA x.y",
                "taxon_match": "full-text file search; the licence whitelist is the gate",
            },
        },
        "counts": {
            "species_with_photos": len(species),
            "species_searched": len(searched),
            "photos": {"inaturalist": photos_inat, "commons": photos_commons},
        },
        "no_photos": {key: sorted(no_photos[key]) for key in ("inaturalist", "commons")},
    }


def comparable(payload):
    """Payload without the volatile timestamp, for change detection."""
    clone = json.loads(json.dumps(payload))
    (clone.get("meta") or {}).pop("generated", None)
    return clone


def assemble(species, searched, no_photos, generated):
    ordered_species = {}
    for name in sorted(species):
        photos = ordered(dedupe(species[name]))
        if photos:
            ordered_species[name] = photos
    return {"meta": build_meta(ordered_species, searched, no_photos, generated),
            "species": ordered_species}


def write_payload(payload):
    if OUT.is_file():
        try:
            with OUT.open("r", encoding="utf-8") as handle:
                previous = json.load(handle)
            if comparable(previous) == comparable(payload):
                payload["meta"]["generated"] = (previous.get("meta") or {}).get("generated") \
                    or payload["meta"]["generated"]
        except (json.JSONDecodeError, OSError, AttributeError):
            pass
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # atomic replace: a checkpoint must never be seen half-written by Jekyll or
    # --check, and a hard kill cannot leave a stray file next to the data file
    scratch = ROOT / "_tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    temporary = scratch / (OUT.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=1, sort_keys=False)
        handle.write("\n")
    temporary.replace(OUT)


# ------------------------------------------------------------- validation
def validate(payload, known_names=None):
    """Return a list of human-readable violations (empty list == valid)."""
    problems = []
    if not isinstance(payload, dict):
        return ["top-level value is not a JSON object"]
    meta = payload.get("meta")
    species = payload.get("species")
    if not isinstance(meta, dict):
        problems.append("meta missing or not an object")
        meta = {}
    if not isinstance(species, dict):
        problems.append("species missing or not an object")
        species = {}
    for key in ("generated", "license_policy", "sources", "counts"):
        if key not in meta:
            problems.append("meta.%s missing" % key)
    if meta.get("license_policy") != "CC0 / CC BY / CC BY-SA only":
        problems.append("meta.license_policy unexpected: %r" % (meta.get("license_policy"),))
    counts = meta.get("counts") or {}
    total_inat = total_commons = 0
    for name, photos in species.items():
        if not isinstance(photos, list) or not photos:
            problems.append("species[%r] is not a non-empty list" % name)
            continue
        if len(photos) > MAX_PHOTOS:
            problems.append("species[%r] has %d photos (max %d)"
                            % (name, len(photos), MAX_PHOTOS))
        seen_src = set()
        for photo in photos:
            if not isinstance(photo, dict):
                problems.append("species[%r] contains a non-object photo" % name)
                continue
            label = "species[%r] %s" % (name, photo.get("src") or "?")
            missing = [k for k in PHOTO_KEYS if photo.get(k) in (None, "")]
            if missing:
                problems.append("%s missing fields: %s" % (label, ", ".join(missing)))
                continue
            source = photo["source"]
            if source not in SOURCE_ORDER:
                problems.append("%s unknown source %r" % (label, source))
                continue
            if source == "inaturalist":
                total_inat += 1
                if photo["license"] not in ALLOWED_LABELS:
                    problems.append("%s licence not allowed: %r" % (label, photo["license"]))
                if "inaturalist" not in urllib.parse.urlsplit(photo["src"]).netloc:
                    problems.append("%s src is not an iNaturalist URL: %s"
                                    % (label, photo["src"]))
                if not photo["page"].startswith(SOURCE_SITE["inaturalist"] + "/observations/"):
                    problems.append("%s page is not an observation URL: %s"
                                    % (label, photo["page"]))
            else:
                total_commons += 1
                if not commons_license_ok(photo["license"]):
                    problems.append("%s licence not allowed: %r" % (label, photo["license"]))
                if not photo["src"].startswith("https://upload.wikimedia.org/"):
                    problems.append("%s src is not a Commons upload URL: %s"
                                    % (label, photo["src"]))
                if not photo["page"].startswith(SOURCE_SITE["commons"] + "/wiki/"):
                    problems.append("%s page is not a Commons file page: %s"
                                    % (label, photo["page"]))
            if not str(photo["licenseUrl"]).startswith("https://creativecommons.org/"):
                problems.append("%s licenseUrl is not a Creative Commons deed: %s"
                                % (label, photo["licenseUrl"]))
            if not (isinstance(photo["width"], int) and isinstance(photo["height"], int)
                    and photo["width"] > 0 and photo["height"] > 0):
                problems.append("%s width/height invalid" % label)
            for key in ("src", "thumb", "page"):
                if not str(photo[key]).startswith("https://"):
                    problems.append("%s %s is not https" % (label, key))
            if photo["src"] in seen_src:
                problems.append("%s duplicate src" % label)
            seen_src.add(photo["src"])
    expected_species = len(species)
    expected_photos = {"inaturalist": total_inat, "commons": total_commons}
    if counts.get("species_with_photos") != expected_species:
        problems.append("meta.counts.species_with_photos=%r but %d species"
                        % (counts.get("species_with_photos"), expected_species))
    if (counts.get("photos") or {}) != expected_photos:
        problems.append("meta.counts.photos=%r but counted %r"
                        % (counts.get("photos"), expected_photos))
    no_photos = meta.get("no_photos") or {}
    for key, values in no_photos.items():
        if key not in ("inaturalist", "commons"):
            problems.append("meta.no_photos has unknown source %r" % (key,))
            continue
        if not isinstance(values, list) or values != sorted(values):
            problems.append("meta.no_photos.%s is not a sorted list" % key)
            continue
        for value in values:
            if any(p.get("source") == key for p in (species.get(value) or [])):
                problems.append("meta.no_photos.%s lists %r which has photos from that source"
                                % (key, value))
    if known_names is not None:
        unknown = sorted(set(species) - set(known_names))
        if unknown:
            print("warning: %d names are not present in _species: %s"
                  % (len(unknown), ", ".join(unknown[:5])), file=sys.stderr)
    return problems


# ------------------------------------------------------------------- main
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Collect CC0 / CC BY / CC BY-SA photos for the termite checklist.")
    parser.add_argument("--write", action="store_true",
                        help="write _data/species_photos.json")
    parser.add_argument("--check", action="store_true",
                        help="re-validate the committed JSON (schema, licence allowlist, counts)")
    parser.add_argument("--limit", type=int, default=0, help="process at most N taxa this run")
    parser.add_argument("--budget", type=float, default=0.0,
                        help="wall-clock budget in seconds (0 = unlimited)")
    parser.add_argument("--refresh", action="store_true",
                        help="ignore the cache and refetch every selected taxon")
    parser.add_argument("--only", choices=("inat", "commons"),
                        help="query a single source")
    parser.add_argument("--all-names", metavar="FILE",
                        help="read the latin names from FILE instead of scanning _species/")
    parser.add_argument("--checkpoint", type=int, default=250,
                        help="with --write, persist progress every N taxa (0 disables)")
    parser.add_argument("--workers", type=int, default=3,
                        help="fetch concurrency (<=3 keeps both APIs inside their rate limits)")
    parser.add_argument("--inat-interval", type=float, default=MIN_INTERVAL["inaturalist"],
                        help="minimum seconds between iNaturalist requests (default 1.05 = 57/min)")
    parser.add_argument("--commons-interval", type=float, default=MIN_INTERVAL["commons"],
                        help="minimum seconds between Commons requests (default 0.34)")
    args = parser.parse_args(argv)

    if args.write and args.check:
        parser.error("--write and --check are mutually exclusive")
    if args.limit < 0:
        parser.error("--limit must be >= 0")
    started = time.monotonic()
    MIN_INTERVAL["inaturalist"] = max(0.2, args.inat_interval)
    MIN_INTERVAL["commons"] = max(0.1, args.commons_interval)

    known = list_species_names() if args.all_names is None else None
    names = list(known) if known is not None else read_names_file(args.all_names)
    sources = ["inaturalist", "commons"]
    if args.only:
        sources = ["inaturalist" if args.only == "inat" else "commons"]

    species, no_photos, old_meta = load_existing()

    if args.check:
        if not OUT.is_file():
            print("%s does not exist" % OUT.relative_to(ROOT), file=sys.stderr)
            return 1
        try:
            with OUT.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (json.JSONDecodeError, OSError) as exc:
            print("invalid JSON: %s" % exc, file=sys.stderr)
            return 1
        problems = validate(payload, known)
        if problems:
            print("FAIL: %d problem(s)" % len(problems), file=sys.stderr)
            for problem in problems[:60]:
                print("  - %s" % problem, file=sys.stderr)
            return 1
        counts = payload["meta"]["counts"]
        print("OK: %s - %d species with photos (%d iNaturalist + %d Commons), "
              "%d taxa searched"
              % (OUT.relative_to(ROOT), counts["species_with_photos"],
                 counts["photos"]["inaturalist"], counts["photos"]["commons"],
                 counts.get("species_searched", 0)))
        return 0

    def done(name, source):
        """True when this source needs no request for this taxon.

        A taxon whose gallery already holds MAX_PHOTOS images is finished for
        every source too: the cap would drop anything new, and without this an
        entry that is full of iNaturalist photos would look "missing Commons"
        on every rerun and be re-queried forever.
        """
        if args.refresh:
            return False
        photos = species.get(name) or []
        if any(photo.get("source") == source for photo in photos):
            return True
        if len(photos) >= MAX_PHOTOS:
            return True
        return name in no_photos[source]

    # plan[name] = the sources this taxon still misses; a source that already has
    # photos is never re-queried (and therefore never accidentally emptied) unless
    # --refresh says so
    plan = {}
    for name in names:
        todo = [source for source in sources if not done(name, source)]
        if todo:
            plan[name] = todo
    pending = list(plan)
    print("%d taxa in list, %d already cached, %d to query (%s)%s"
          % (len(names), len(names) - len(pending), len(pending), "+".join(sources),
             ", budget %ds" % args.budget if args.budget else ""))
    if args.limit:
        pending = pending[:args.limit]

    clients = {source: PoliteClient(source) for source in sources}
    searched = set()
    processed = 0
    found = 0
    errors = 0
    stopped = False

    def fetch_taxon(latin):
        """Worker: query the sources this taxon still misses (runs in a thread)."""
        results = {}
        for source in plan[latin]:
            if source == "inaturalist":
                results[source] = fetch_inaturalist(clients[source], latin)
            else:
                results[source] = fetch_commons(clients[source], latin)
        return latin, results

    executor = None
    if args.workers > 1 and len(pending) > 1:
        executor = ThreadPoolExecutor(max_workers=args.workers)
        stream = executor.map(fetch_taxon, pending)
    else:
        stream = map(fetch_taxon, pending)

    try:
        for index, (latin, results) in enumerate(stream, 1):
            if args.budget and processed and (time.monotonic() - started) > args.budget:
                print("budget reached after %d taxa - stopping; the cache keeps the progress"
                      % processed)
                stopped = True
                break
            failed = False
            for source in plan[latin]:
                result = results[source]
                if result is None:
                    failed = True
                    continue
                searched.add(latin)
                if result:
                    no_photos[source].discard(latin)
                else:
                    no_photos[source].add(latin)
                kept = [photo for photo in (species.get(latin) or [])
                        if photo.get("source") != source]
                merged = dedupe(kept + result)
                if merged:
                    species[latin] = merged
                else:
                    species.pop(latin, None)
            if failed:
                errors += 1
                continue
            processed += 1
            if species.get(latin):
                found += 1
            if args.write and args.checkpoint and processed % args.checkpoint == 0:
                partial = assemble(species, searched | set(no_photos["inaturalist"])
                                   | set(no_photos["commons"]), no_photos,
                                   datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
                write_payload(partial)
                print("  checkpoint: %d taxa with photos on disk"
                      % len(partial["species"]))
                sys.stdout.flush()
            if processed % 25 == 0 or index == len(pending):
                elapsed = time.monotonic() - started
                rate = processed / elapsed if elapsed else 0.0
                print("[%d/%d] %s: %d photos | %d taxa with photos | %.2f taxa/s"
                      % (index, len(pending), latin, len(species.get(latin) or []),
                         found, rate))
                sys.stdout.flush()
    finally:
        if executor is not None:
            executor.shutdown(wait=False, cancel_futures=True)

    if errors:
        print("warning: %d taxa could not be queried and stay pending for the next run"
              % errors, file=sys.stderr)

    searched |= set(no_photos["inaturalist"]) | set(no_photos["commons"])
    payload = assemble(species, searched, no_photos,
                       datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    problems = validate(payload, known)
    if problems:
        print("refusing to write: %d problem(s)" % len(problems), file=sys.stderr)
        for problem in problems[:20]:
            print("  - %s" % problem, file=sys.stderr)
        return 1

    if args.write:
        write_payload(payload)
        counts = payload["meta"]["counts"]
        print("wrote %s: %d species with photos (%d iNaturalist + %d Commons), "
              "%d taxa searched, %.1f KB"
              % (OUT.relative_to(ROOT), counts["species_with_photos"],
                 counts["photos"]["inaturalist"], counts["photos"]["commons"],
                 counts["species_searched"], OUT.stat().st_size / 1024))
    else:
        counts = payload["meta"]["counts"]
        print("dry-run (no --write): %d species with photos (%d iNaturalist + %d Commons), "
              "%d taxa searched"
              % (counts["species_with_photos"], counts["photos"]["inaturalist"],
                 counts["photos"]["commons"], counts["species_searched"]))

    pending_left = len(names) - len(payload["species"])
    if pending_left > 0:
        print("%d taxa still have no gallery entry - rerun the same command to resume"
              % pending_left)
    if stopped:
        print("stopped by --budget; rerun the same command to continue")
    print("resume: python .github/workflows/build_species_photos.py --write --budget 3600")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("interrupted - the last checkpoint is already on disk", file=sys.stderr)
        sys.exit(130)
