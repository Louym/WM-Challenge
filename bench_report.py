#!/usr/bin/env python3
"""Build benchmark.csv from the isolated bench_*.driver.log runs.

Reports, per config: model load time, first-clip latency (includes per-session
warmup/intrinsics), steady-state per-clip latency (mean over clips after the
first), realtime factor (generation seconds per output-video second), and
whole-video wall time for the 60s single-shot runs. Long whole-video configs
that were not re-run reuse the delivery-run timing and are marked as such.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).parent
LOGS = ROOT / "logs"

# seconds of output video per clip (steady state)
CLIP_SECONDS = {
    "hy_ar_distill": 125 / 24, "hy_ar": 125 / 24, "hy_ar_rl": 125 / 24, "hy_bi": 125 / 24,
    "infworld": 49 / 16, "sana": 49 / 16,
    "dreamx_ar": 81 / 16, "dreamx_cam": 81 / 16,
    "lingbot_small": 57 / 16, "lingbot_large": 49 / 16, "lingbot_v2": 57 / 16,
    "mg3_efficiency": 40 / 17, "mg3_quality": 40 / 17,
}
WHOLE_SECONDS = {
    "hy_ar_distill": 1441 / 24, "hy_ar": 1441 / 24, "hy_ar_rl": 1441 / 24, "hy_bi": 1441 / 24,
    "sana": 961 / 16, "dreamx_ar": 969 / 16, "dreamx_cam": 961 / 16,
    "lingbot_small": 961 / 16, "lingbot_large": 961 / 16, "lingbot_v2": 969 / 16,
}
GPUS = {"mg3_efficiency": 2, "mg3_quality": 2, "lingbot_large_whole": 4}

# delivery-run timings reused for configs too long to re-run in isolation
DELIVERY_WHOLE = {"hy_ar": 4510.0, "hy_ar_rl": 4506.0, "hy_bi": 10419.0, "dreamx_cam": 9880.0}

TS = re.compile(r"^\[driver (\d\d:\d\d:\d\d)\] (.*)$")


def parse_log(path: Path):
    load_s = None
    segs = []
    for line in path.read_text(errors="replace").splitlines():
        m = TS.match(line)
        if not m:
            continue
        msg = m.group(2)
        if "ready after" in msg:
            load_s = float(re.search(r"ready after (\d+)s", msg).group(1))
        sm = re.search(r"segment (\d+) done \((\d+)s elapsed\)", msg)
        if sm:
            segs.append(float(sm.group(2)))
    return load_s, segs


def main() -> None:
    rows = []
    for log in sorted(LOGS.glob("bench_*.driver.log")):
        name = log.stem.replace(".driver", "").replace("bench_", "")
        base = name.rsplit("_", 1)[0]  # strip _clip/_whole
        kind = name.rsplit("_", 1)[1]
        load_s, segs = parse_log(log)
        row = dict(config=base, kind=kind, gpus=GPUS.get(base, GPUS.get(name, 1)),
                   load_s=load_s, source="isolated")
        if kind == "clip" and segs:
            deltas = [b - a for a, b in zip(segs, segs[1:])]
            steady = sum(deltas) / len(deltas) if deltas else None
            out_s = CLIP_SECONDS.get(base)
            row.update(
                first_clip_s=round(segs[0], 1),
                steady_clip_s=round(steady, 1) if steady else None,
                clip_out_s=round(out_s, 2) if out_s else None,
                realtime_factor=round(steady / out_s, 2) if steady and out_s else None,
            )
        elif kind == "whole" and segs:
            out_s = WHOLE_SECONDS.get(base)
            row.update(
                whole_gen_s=round(segs[0], 1),
                whole_out_s=round(out_s, 1) if out_s else None,
                realtime_factor=round(segs[0] / out_s, 2) if out_s else None,
            )
        rows.append(row)

    for base, t in DELIVERY_WHOLE.items():
        out_s = WHOLE_SECONDS[base]
        rows.append(dict(config=base, kind="whole", gpus=1, load_s=None, source="delivery-run",
                         whole_gen_s=t, whole_out_s=round(out_s, 1),
                         realtime_factor=round(t / out_s, 2)))

    rows.sort(key=lambda r: (r["config"], r["kind"]))
    fields = ["config", "kind", "gpus", "source", "load_s", "first_clip_s", "steady_clip_s",
              "clip_out_s", "whole_gen_s", "whole_out_s", "realtime_factor"]
    with (ROOT / "benchmark.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    hdr = f"{'config':<18}{'kind':<7}{'gpus':>5}{'load_s':>8}{'clip1_s':>9}{'steady_s':>9}{'whole_s':>9}{'xRT':>7}  source"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['config']:<18}{r['kind']:<7}{r['gpus']:>5}{r.get('load_s') or '-':>8}"
              f"{r.get('first_clip_s') or '-':>9}{r.get('steady_clip_s') or '-':>9}"
              f"{r.get('whole_gen_s') or '-':>9}{r.get('realtime_factor') or '-':>7}  {r['source']}")
    print(f"\nwrote {ROOT / 'benchmark.csv'}  (xRT = generation seconds per second of output video)")


if __name__ == "__main__":
    main()
