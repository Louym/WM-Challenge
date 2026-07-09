#!/usr/bin/env python3
"""Parse *.driver.log files into a per-run generation latency report (CSV + table)."""
from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime, timedelta
from pathlib import Path

_ap = argparse.ArgumentParser()
_ap.add_argument("--sample", default="demo_29")
_ARGS = _ap.parse_args()
LOGS = Path(__file__).parent / "logs"
_suffix = "" if _ARGS.sample == "demo_29" else f"_{_ARGS.sample}"
OUT_CSV = Path(__file__).parent / f"latency{_suffix}.csv"
_GLOB = "*.driver.log" if _ARGS.sample == "demo_29" else f"{_ARGS.sample}_*.driver.log"

TS = re.compile(r"^\[driver (\d\d:\d\d:\d\d)\] (.*)$")


def parse_time(s: str) -> datetime:
    return datetime.strptime(s, "%H:%M:%S")


def main() -> None:
    rows = []
    for log in sorted(LOGS.glob(_GLOB)):
        if _ARGS.sample == "demo_29" and log.name.startswith("demo_"):
            continue
        load_s = None
        session = None
        session_start = None
        seg_times = []  # (index, elapsed_s)
        for line in log.read_text(errors="replace").splitlines():
            m = TS.match(line)
            if not m:
                continue
            t, msg = parse_time(m.group(1)), m.group(2)
            if "ready after" in msg:
                load_s = float(re.search(r"ready after (\d+)s", msg).group(1))
            elif msg.startswith("=== session"):
                session = re.search(r"=== session (\S+):", msg).group(1)
                seg_times = []
            elif msg.startswith("queued"):
                session_start = t
            elif msg.startswith("segment") and "done" in msg:
                sm = re.search(r"segment (\d+) done \((\d+)s elapsed\)", msg)
                seg_times.append((int(sm.group(1)), float(sm.group(2))))
            elif msg.startswith("saved") and session:
                total = seg_times[-1][1] if seg_times else None
                n = len(seg_times)
                per_seg = None
                if n > 1:
                    # deltas between consecutive segments (excludes first-segment warmup/intrinsics)
                    deltas = [b - a for (_, a), (_, b) in zip(seg_times, seg_times[1:])]
                    per_seg = sum(deltas) / len(deltas)
                size_m = re.search(r"([\d.]+) MB\)", msg)
                rows.append(
                    dict(
                        run=session,
                        model_load_s=load_s,
                        segments=n,
                        first_segment_s=seg_times[0][1] if seg_times else None,
                        avg_per_segment_s=round(per_seg, 1) if per_seg else None,
                        total_generation_s=total,
                        video_mb=float(size_m.group(1)) if size_m else None,
                    )
                )
                session = None

    rows.sort(key=lambda r: r["run"])
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    hdr = f"{'run':<34}{'load_s':>8}{'segs':>6}{'seg1_s':>8}{'avg_seg_s':>10}{'total_s':>9}{'MB':>8}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(
            f"{r['run']:<34}{r['model_load_s'] or '-':>8}{r['segments']:>6}"
            f"{r['first_segment_s'] or '-':>8}{r['avg_per_segment_s'] or '-':>10}"
            f"{r['total_generation_s'] or '-':>9}{r['video_mb'] or '-':>8}"
        )
    print(f"\nwrote {OUT_CSV}")


if __name__ == "__main__":
    main()
