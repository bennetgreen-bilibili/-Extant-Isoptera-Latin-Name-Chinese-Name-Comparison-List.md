#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loop the photo collector until every taxon has a gallery, or until it stops paying off.

Why a loop?
-----------
build_species_photos.py already checkpoints into _data/species_photos.json and is
idempotent, so a full crawl can be spread over any number of bounded runs.  This
wrapper simply calls it again and again:

  * each round is bounded by --round-budget (passed through as --budget), so the
    process can be killed at any moment and the next run picks up the cache;
  * after every round the crawl plan is recomputed from the file on disk; a round
    that makes no progress (same pending count and same photo count) is counted
    as idle, and --max-idle-rounds idle rounds in a row stop the loop so a dead
    API cannot spin forever;
  * when nothing is pending any more it prints a summary and exits 0.

Intended use
------------
    # 本地/CI：先补完没有图的物种，每轮 15 分钟，轮间休息 20 秒
    python .github/workflows/crawl_species_photos_loop.py \
        --round-budget 900 --sleep 20 --workers 4

    # 只补 Commons（例如刚把公有领域加入白名单后重扫）
    python .github/workflows/species_photos_crawl.yml  # 或见下方 --refresh

    # 一次性重扫某个源：--refresh 会让每轮都忽略缓存，因此只跑一轮
    python .github/workflows/build_species_photos.py --write --refresh --only commons

Exit codes: 0 finished (or stopped as planned), 1 bad usage / collector failure,
130 interrupted.

The GitHub Actions counterpart is .github/workflows/species_photos_crawl.yml,
which runs this script on a schedule and commits the updated cache.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_species_photos as collector  # noqa: E402  (path set up above)

ALL_SOURCES = ("inaturalist", "commons")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_names(all_names=None):
    """The taxonomy list: _species/*.md by default, or the --all-names file."""
    if all_names is None:
        return collector.list_species_names()
    return collector.read_names_file(all_names)


def load_state(sources, refresh, all_names=None):
    """Return (names, species, count of pending taxa, plan)."""
    names = load_names(all_names)
    species, no_photos, _meta = collector.load_existing()
    plan = collector.plan_pending(names, list(sources), species, no_photos,
                                  refresh=refresh)
    return names, species, len(plan), plan


def photo_total(species):
    return sum(len(photos) for photos in species.values())


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Keep crawling open-licence photos (CC0 / CC BY / CC BY-SA / PD) "
                    "until every taxon is covered.")
    parser.add_argument("--round-budget", type=float, default=900.0,
                        help="wall-clock seconds per round (passed to --budget; 0 = unlimited)")
    parser.add_argument("--max-rounds", type=int, default=0,
                        help="stop after N rounds (0 = keep going until nothing is pending)")
    parser.add_argument("--sleep", type=float, default=20.0,
                        help="seconds to sleep between rounds (default 20)")
    parser.add_argument("--max-idle-rounds", type=int, default=3,
                        help="stop after N rounds in a row without progress (default 3)")
    parser.add_argument("--workers", type=int, default=4,
                        help="fetch concurrency passed to the collector (default 4)")
    parser.add_argument("--checkpoint", type=int, default=100,
                        help="persist progress every N taxa (default 100)")
    parser.add_argument("--limit", type=int, default=0,
                        help="process at most N taxa per round (0 = the whole plan)")
    parser.add_argument("--only", choices=("inat", "commons"),
                        help="crawl one source only")
    parser.add_argument("--refresh", action="store_true",
                        help="ignore the cache (one-shot licence rescan; forces a single round)")
    parser.add_argument("--all-names", metavar="FILE",
                        help="read latin names from FILE instead of scanning _species/")
    args = parser.parse_args(argv)

    if args.max_idle_rounds < 1:
        parser.error("--max-idle-rounds must be >= 1")
    if args.max_rounds < 0:
        parser.error("--max-rounds must be >= 0")

    sources = ALL_SOURCES if not args.only else (
        ("inaturalist",) if args.only == "inat" else ("commons",))
    max_rounds = args.max_rounds
    if args.refresh:
        if max_rounds == 0:
            max_rounds = 1
        print("note: --refresh ignores the cache, so the loop is limited to %d round(s)"
              % max_rounds, flush=True)

    started = time.monotonic()
    round_no = 0
    idle = 0
    previous = None

    while True:
        round_no += 1
        names, species, pending_count, plan = load_state(sources, args.refresh,
                                                          args.all_names)
        if not plan:
            print("%s all %d taxa are covered - nothing left to crawl (%d species, %d photos)"
                  % (now(), len(names), len(species), photo_total(species)), flush=True)
            break
        if max_rounds and round_no > max_rounds:
            print("%s reached --max-rounds %d - stopping with %d taxa still pending"
                  % (now(), max_rounds, pending_count), flush=True)
            break

        print("%s round %d/%s: %d/%d taxa pending, %d species with %d photos - crawling..."
              % (now(), round_no, max_rounds or "∞", pending_count, len(names),
                 len(species), photo_total(species)), flush=True)

        crawl_argv = ["--write", "--workers", str(args.workers),
                      "--checkpoint", str(args.checkpoint)]
        if args.round_budget:
            crawl_argv += ["--budget", str(args.round_budget)]
        if args.limit:
            crawl_argv += ["--limit", str(args.limit)]
        if args.only:
            crawl_argv += ["--only", args.only]
        if args.refresh:
            crawl_argv += ["--refresh"]
        if args.all_names:
            crawl_argv += ["--all-names", args.all_names]

        code = collector.main(crawl_argv)
        if code:
            print("%s collector failed with exit code %d - stopping" % (now(), code),
                  flush=True)
            return code

        names, species, pending_count, plan = load_state(sources, args.refresh,
                                                          args.all_names)
        progress = (pending_count, photo_total(species))
        print("%s round %d done: %d/%d taxa pending, %d species, %d photos"
              % (now(), round_no, pending_count, len(names), len(species), progress[1]),
              flush=True)

        if not plan:
            print("%s coverage complete after %d round(s)" % (now(), round_no), flush=True)
            break
        if progress == previous:
            idle += 1
            print("%s no progress this round (%d idle round(s) in a row)"
                  % (now(), idle), flush=True)
            if idle >= args.max_idle_rounds:
                print("%s stopping after %d idle rounds - rerun later if the APIs recover"
                      % (now(), idle), flush=True)
                break
        else:
            idle = 0
        previous = progress

        if max_rounds and round_no >= max_rounds:
            print("%s reached --max-rounds %d - stopping with %d taxa pending"
                  % (now(), max_rounds, pending_count), flush=True)
            break
        if args.sleep:
            time.sleep(args.sleep)

    elapsed = time.monotonic() - started
    names, species, pending_count, _plan = load_state(sources, args.refresh,
                                                       args.all_names)
    print("%s finished in %.0fs: %d/%d taxa pending, %d species with %d photos"
          % (now(), elapsed, pending_count, len(names), len(species), photo_total(species)),
          flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("interrupted - progress up to the last checkpoint is on disk", file=sys.stderr)
        sys.exit(130)
