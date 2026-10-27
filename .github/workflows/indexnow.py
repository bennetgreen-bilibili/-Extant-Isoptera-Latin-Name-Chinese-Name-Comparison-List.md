#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Submit every URL from the live sitemap to IndexNow.

IndexNow is a single push endpoint shared by Bing, Yandex, Seznam, Naver and
Yep: one POST makes them re-crawl the listed URLs within minutes instead of
waiting for their own discovery schedule. It needs no account or token, only a
key file served from the site root (see the <key>.txt file next to _config.yml).

Callers:
  CI      pages.yml runs this after the deploy job, with no arguments.
  Local   python .github/workflows/indexnow.py --dry-run
          (add --sitemap path/to/sitemap.xml to test against a local file)

Exit codes: 0 submitted, 1 failed, 2 nothing to do.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "_config.yml"
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_FILE_RE = re.compile(r"^([A-Za-z0-9-]{8,128})\.txt$")
USER_AGENT = "bennetgreen-indexnow/1.0 (+https://github.com/bennetgreen-bilibili)"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def read_config_base():
    """Return (site_url_with_base, host) from _config.yml."""
    url = baseurl = ""
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(url|baseurl):\s*(\S.*)$", line)
        if not m:
            continue
        val = m.group(2).strip().strip('"').strip("'")
        if m.group(1) == "url":
            url = val
        else:
            baseurl = val
    if not url:
        sys.exit("_config.yml has no url: entry")
    base = (url + baseurl).rstrip("/")
    host = re.sub(r"^https?://", "", url).split("/")[0]
    return base, host


def read_key():
    """Find the <key>.txt file at the repo root; its content must equal its stem."""
    candidates = [p for p in ROOT.glob("*.txt") if KEY_FILE_RE.match(p.name)]
    if not candidates:
        sys.exit("no <key>.txt file found at the repo root (IndexNow key file)")
    if len(candidates) > 1:
        sys.exit("multiple <key>.txt files found: %s" % ", ".join(p.name for p in candidates))
    path = candidates[0]
    key = KEY_FILE_RE.match(path.name).group(1)
    content = path.read_text(encoding="utf-8").strip()
    if content != key:
        sys.exit("%s must contain exactly %r (it contains %r)" % (path.name, key, content))
    return path, key


def load_urls(sitemap):
    if re.match(r"^https?://", sitemap):
        req = urllib.request.Request(sitemap, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    else:
        data = Path(sitemap).read_bytes()
    root = ET.fromstring(data)
    urls = [el.text.strip() for el in root.iter() if el.tag.endswith("loc") and el.text]
    if not urls:
        sys.exit("sitemap has no <loc> entries: %s" % sitemap)
    return urls


def wait_for_key(key_location, key, attempts=12, delay=10):
    """The key file must be live before IndexNow accepts the submission."""
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(key_location, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", "replace").strip()
            if body == key:
                print("key file live: %s (%d chars)" % (key_location, len(body)))
                return True
            print("key file content mismatch on attempt %d/%d" % (attempt, attempts))
        except urllib.error.HTTPError as exc:
            print("key file not live yet (HTTP %s) attempt %d/%d" % (exc.code, attempt, attempts))
        except Exception as exc:  # noqa: BLE001 - network flakiness is expected
            print("key file check failed (%s) attempt %d/%d" % (exc, attempt, attempts))
        if attempt < attempts:
            time.sleep(delay)
    return False


def post(urls, host, key, key_location, batch_size, dry_run):
    ok = True
    batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
    for i, batch in enumerate(batches, 1):
        payload = {
            "host": host,
            "key": key,
            "keyLocation": key_location,
            "urlList": batch,
        }
        if dry_run:
            print("would POST batch %d/%d: %d urls" % (i, len(batches), len(batch)))
            continue
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            ENDPOINT, data=body, method="POST",
            headers={"Content-Type": "application/json; charset=utf-8",
                     "User-Agent": USER_AGENT},
        )
        for attempt in range(1, 4):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    print("batch %d/%d: HTTP %s, %d urls submitted"
                          % (i, len(batches), resp.status, len(batch)))
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:300]
                if exc.code in (429, 500, 502, 503) and attempt < 3:
                    print("batch %d/%d: HTTP %s, retrying in %ds" % (i, len(batches), exc.code, 15 * attempt))
                    time.sleep(15 * attempt)
                    continue
                print("batch %d/%d FAILED: HTTP %s %s" % (i, len(batches), exc.code, detail))
                ok = False
                break
            except Exception as exc:  # noqa: BLE001
                if attempt < 3:
                    print("batch %d/%d: %s, retrying" % (i, len(batches), exc))
                    time.sleep(15 * attempt)
                    continue
                print("batch %d/%d FAILED: %s" % (i, len(batches), exc))
                ok = False
                break
    return ok



SITEWIDE_PREFIXES = ("_layouts/", "_data/", "_includes/", "assets/", ".github/workflows/")


def changed_paths():
    """Paths changed by HEAD (needs fetch-depth: 2 in CI). None if unavailable."""
    for rev in ("HEAD^",):
        proc = subprocess.run(
            ["git", "diff", "--name-only", rev, "HEAD"],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        if proc.returncode == 0:
            return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return None


def path_to_url(path, base):
    """Map one changed repo path to the public URL it invalidates."""
    p = path.replace("\\", "/").strip()
    if p.startswith("_species/") and p.endswith(".md"):
        return base + "/species/" + Path(p).stem + "/"
    if p.startswith("en/") and p.endswith(".md"):
        stem = Path(p).stem
        return base + "/en/" + ("" if stem == "index" else stem + "/")
    if p.startswith("es/") and p.endswith(".md"):
        stem = Path(p).stem
        return base + "/es/" + ("" if stem == "index" else stem + "/")
    if p.startswith("_posts/") and p.endswith(".md"):
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", Path(p).name)
        if m:
            return "%s/blog/%s/%s/%s/%s/" % (base, m.group(1), m.group(2), m.group(3), m.group(4))
        return None
    if p.endswith(".md") and "/" not in p:
        stem = Path(p).stem
        if stem == "index":
            return base + "/"
        # only pages with front matter are rendered by Jekyll (README etc. are static)
        try:
            head = (ROOT / p).read_text(encoding="utf-8")[:8]
        except OSError:
            return None
        return base + "/" + stem + "/" if head.startswith("---") else None
    if p.startswith("data/") or p in (
        "isoptera-data.json", "search-index.json", "llms.txt", "robots.txt",
    ):
        return base + "/data/"
    return None


def urls_from_git(base):
    """Return (urls, sitewide). sitewide means every page may have changed."""
    paths = changed_paths()
    if paths is None:
        print("warning: git diff unavailable (needs fetch-depth: 2); falling back to full sitemap")
        return None, True
    if any(p.startswith(SITEWIDE_PREFIXES) or p == "_config.yml" for p in paths):
        print("changed paths include templates/config -> every page may be stale")
        return None, True
    urls = []
    for p in paths:
        u = path_to_url(p, base)
        if u and u not in urls:
            urls.append(u)
    return urls, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitemap", default=None,
                    help="sitemap URL or local file (default: <site>/sitemap.xml)")
    ap.add_argument("--dry-run", action="store_true", help="parse and report, do not submit")
    ap.add_argument("--batch-size", type=int, default=10000,
                    help="URLs per request, IndexNow allows up to 10000")
    ap.add_argument("--skip-key-check", action="store_true",
                    help="do not wait for the key file to go live")
    ap.add_argument("--changed", action="store_true",
                    help="submit only URLs touched by HEAD (CI mode); needs fetch-depth: 2")
    args = ap.parse_args()

    base, host = read_config_base()
    key_path, key = read_key()
    sitemap = args.sitemap or (base + "/sitemap.xml")
    key_location = base + "/" + key_path.name

    print("site:        %s" % base)
    print("host:        %s" % host)
    print("key file:    %s" % key_path.name)
    print("sitemap:     %s" % sitemap)

    urls = None
    if args.changed:
        urls, sitewide = urls_from_git(base)
        if urls is not None:
            print("mode:        changed-only (%d urls from git diff)" % len(urls))
    if urls is None:
        urls = load_urls(sitemap)

    foreign = [u for u in urls if not u.startswith(base + "/") and u.rstrip("/") != base]
    if foreign:
        print("warning: %d urls outside %s, dropping them (e.g. %s)"
              % (len(foreign), base, foreign[0]))
        urls = [u for u in urls if u not in set(foreign)]
    print("urls:        %d" % len(urls))
    if not urls:
        sys.exit(2)

    if not args.dry_run and not args.skip_key_check:
        if not wait_for_key(key_location, key):
            print("aborting: %s never served the expected key; deploy may still be propagating"
                  % key_location)
            sys.exit(1)

    if not post(urls, host, key, key_location, args.batch_size, args.dry_run):
        sys.exit(1)
    if not args.dry_run:
        print("done: %d urls pushed to IndexNow (%s)" % (len(urls), ENDPOINT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
