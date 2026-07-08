#!/usr/bin/env python3
"""Build manifest.json + README.md for the sample-29 videos.

Static per-run settings (mirroring the env/spec each run was launched with),
merged with ffprobe measurements and latency.csv.
"""
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
VIDEOS = ROOT / "videos"

TRAJ_CLIP = "forward xN, pan-right xN, forward xN, backward xN (equal quarters)"
TRAJ_WHOLE = "single action string: forward, pan-right, forward, backward (equal quarters)"
TRAJ_PUSH = "single action: push-in (w) — DreamX generates one action token per shot"

RUNS = {
    "infworld_clip": dict(
        model="Infinite-World", variant="default", temporal="causal (chunk-autoregressive)",
        protocol="clip-by-clip", clips=20, frames_per_clip=49, fps=16,
        resolution="~627p bucket (ASPECT_RATIO_627_F64)", steps=30, cfg=5.0, seed=42,
        trajectory=TRAJ_CLIP, notes="whole-video mode not supported (fixed 49-frame chunks)",
    ),
    "sana_wm_bidirectional_clip": dict(
        model="Sana-WM", variant="bidirectional 1600M 720p + refiner", temporal="bidirectional",
        protocol="clip-by-clip", clips=20, frames_per_clip=49, fps=16,
        resolution="704x1280", steps=60, cfg=5.0, seed=42,
        trajectory=TRAJ_CLIP, notes="refiner on; Pi3X-estimated intrinsics; flow_shift 8",
    ),
    "sana_wm_bidirectional_whole": dict(
        model="Sana-WM", variant="bidirectional 1600M 720p + refiner", temporal="bidirectional",
        protocol="whole-video", clips=1, frames_per_clip=961, fps=16,
        resolution="704x1280", steps=60, cfg=5.0, seed=42,
        trajectory=TRAJ_WHOLE + " (w-240,l-240,w-240,s-240)", notes="961 frames in one shot",
    ),
    **{
        f"hy_{v}_clip": dict(
            model="HY-WorldPlay", variant=v, temporal=("bidirectional" if v == "bi" else "causal (autoregressive)"),
            protocol="clip-by-clip", clips=12, frames_per_clip=125, fps=24,
            resolution="832x480", steps=(4 if v == "ar_distill" else 20), cfg=None, seed=1,
            trajectory=TRAJ_CLIP,
            notes="chunk_latent_frames=" + ("16" if v == "bi" else "4"),
        )
        for v in ["ar_distill", "ar", "ar_rl", "bi"]
    },
    **{
        f"hy_{v}_whole": dict(
            model="HY-WorldPlay", variant=v, temporal=("bidirectional" if v == "bi" else "causal (autoregressive)"),
            protocol="whole-video", clips=1, frames_per_clip=1441, fps=24,
            resolution="832x480", steps=(4 if v == "ar_distill" else 20), cfg=None, seed=1,
            trajectory=TRAJ_WHOLE + " (w-90,l-90,w-90,s-90; 361 latents)",
            notes="1441 frames in one rollout",
        )
        for v in ["ar_distill", "ar", "ar_rl", "bi"]
    },
    "dreamx_ar_clip": dict(
        model="DreamX-World-5B", variant="ar (long-horizon autoregressive)", temporal="causal (autoregressive)",
        protocol="clip-by-clip", clips=12, frames_per_clip=81, fps=16,
        resolution="704x1280", steps=None, cfg=None, seed=42,
        trajectory=TRAJ_CLIP + " @speed 6", notes="21 latent frames per clip",
    ),
    "dreamx_ar_whole": dict(
        model="DreamX-World-5B", variant="ar (long-horizon autoregressive)", temporal="causal (autoregressive)",
        protocol="whole-video", clips=1, frames_per_clip=969, fps=16,
        resolution="704x1280", steps=None, cfg=None, seed=42,
        trajectory=TRAJ_PUSH, notes="243 latent frames in one rollout",
    ),
    "dreamx_cam_clip": dict(
        model="DreamX-World-5B-Cam", variant="cam", temporal="bidirectional",
        protocol="clip-by-clip", clips=12, frames_per_clip=81, fps=16,
        resolution="704x1280", steps=50, cfg=3.0, seed=42,
        trajectory=TRAJ_CLIP + " @speed 6", notes="shift 3.0",
    ),
    "dreamx_cam_whole": dict(
        model="DreamX-World-5B-Cam", variant="cam", temporal="bidirectional",
        protocol="whole-video", clips=1, frames_per_clip=961, fps=16,
        resolution="704x1280", steps=50, cfg=3.0, seed=42,
        trajectory=TRAJ_PUSH,
        notes="961 frames in one bidirectional shot (~12x training clip length); "
        "required memory workarounds on one H200",
    ),
    **{
        f"lingbot_{s}_clip": dict(
            model="LingBot-World", variant=("small/fast (distilled streaming)" if s == "small" else "large/base (act2cam)"),
            temporal=("causal (chunked streaming)" if s == "small" else "bidirectional per segment"),
            protocol="clip-by-clip", clips=20, frames_per_clip=(57 if s == "small" else 49), fps=16,
            resolution="480x832", steps=(None if s == "small" else 20), cfg=None, seed=42,
            trajectory=TRAJ_CLIP,
            notes="i2v-A14B" + ("; 49-frame request snapped to 57 (3-latent chunking)" if s == "small" else ""),
        )
        for s in ["small", "large"]
    },
    "lingbot_small_whole": dict(
        model="LingBot-World", variant="small/fast (distilled streaming)", temporal="causal (chunked streaming)",
        protocol="whole-video", clips=1, frames_per_clip=961, fps=16,
        resolution="480x832", steps=None, cfg=None, seed=42,
        trajectory=TRAJ_WHOLE + " (w-240,l-240,w-240,s-240)",
        notes="i2v-A14B; KV cache bounded to a 24-latent-frame rolling window "
        "(LINGBOT_DEMO_LOCAL_ATTN_SIZE=24) — full-sequence cache (~300GB) cannot fit one GPU",
    ),
    "lingbot_large_whole": dict(
        model="LingBot-World", variant="large/base (act2cam)", temporal="bidirectional per segment",
        protocol="whole-video", clips=1, frames_per_clip=961, fps=16,
        resolution="480x832", steps=20, cfg=None, seed=42,
        trajectory=TRAJ_WHOLE + " (w-240,l-240,w-240,s-240)",
        notes="i2v-A14B; run distributed on 4 GPUs (FSDP+SP) — 961-frame attention OOMs on 1 and 2 H200s",
    ),
    "mg3_efficiency_clip": dict(
        model="Matrix-Game-3.0", variant="efficiency (distilled + int8)", temporal="causal (streaming interactive)",
        protocol="clip-by-clip", clips=26, frames_per_clip="57 first, then 40", fps=17,
        resolution="704x1280", steps=None, cfg=5.0, seed=42,
        trajectory="forward x7, pan-right x6, forward x7, backward x6",
        notes="run distributed on 2 GPUs (single-GPU interactive path has an upstream device bug); "
        "whole-video mode not supported (streaming only)",
    ),
    "mg3_quality_clip": dict(
        model="Matrix-Game-3.0", variant="quality (base model)", temporal="causal (streaming interactive)",
        protocol="clip-by-clip", clips=26, frames_per_clip="57 first, then 40", fps=17,
        resolution="704x1280", steps=50, cfg=5.0, seed=42,
        trajectory="forward x7, pan-right x6, forward x7, backward x6",
        notes="run distributed on 2 GPUs (single-GPU quality path has an upstream device bug); "
        "whole-video mode not supported",
    ),
}


def ffprobe(path: Path) -> dict:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-show_format", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout
        data = json.loads(out)
        vs = next(s for s in data["streams"] if s["codec_type"] == "video")
        num, den = vs.get("avg_frame_rate", "0/1").split("/")
        fps = round(float(num) / float(den), 2) if float(den) else None
        return dict(
            duration_s=round(float(data["format"]["duration"]), 2),
            measured_resolution=f"{vs['width']}x{vs['height']}",
            measured_fps=fps,
            n_frames=int(vs["nb_frames"]) if vs.get("nb_frames") else None,
            size_mb=round(int(data["format"]["size"]) / 1e6, 1),
        )
    except Exception as exc:  # noqa: BLE001
        return dict(error=repr(exc))


def main() -> None:
    latency = {}
    lat_csv = ROOT / "latency.csv"
    if lat_csv.exists():
        for row in csv.DictReader(lat_csv.open()):
            latency[row["run"]] = row

    manifest = []
    for name, cfg in RUNS.items():
        entry = dict(video=f"{name}.mp4", **cfg)
        vid = VIDEOS / f"{name}.mp4"
        entry["status"] = "ok" if vid.exists() else "missing"
        if vid.exists():
            entry.update(ffprobe(vid))
        lat = latency.get(name)
        if lat:
            entry["model_load_s"] = float(lat["model_load_s"]) if lat["model_load_s"] else None
            entry["total_generation_s"] = float(lat["total_generation_s"]) if lat["total_generation_s"] else None
            entry["avg_per_segment_s"] = float(lat["avg_per_segment_s"]) if lat["avg_per_segment_s"] else None
        manifest.append(entry)

    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"wrote {ROOT / 'manifest.json'} ({sum(1 for m in manifest if m['status'] == 'ok')}/{len(manifest)} videos present)")

    lines = [
        "# World-model demo comparison on sample demo_29 (coffee shop)",
        "",
        "Input: `SANA_WM_dev/playground/dataset/dataset/demo_29.png` + `demo_29.txt` prompt.",
        "Shared camera trajectory (~60s): forward, pan right, forward, backward — equal quarters.",
        "All runs drive the unmodified `baselines/demo` server through its HTTP API (one GPU per run",
        "unless noted). `clip-by-clip` = one action per segment, chained on the last frame;",
        "`whole-video` = a single action string / long rollout in one generation call.",
        "",
        "| video | model | variant | temporal | protocol | clips x frames | fps | res | duration_s | gen_time_s | notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for m in manifest:
        dur = m.get("duration_s", "-")
        gen = m.get("total_generation_s", "-")
        lines.append(
            f"| {m['video']} | {m['model']} | {m['variant']} | {m['temporal']} | {m['protocol']} "
            f"| {m['clips']} x {m['frames_per_clip']} | {m['fps']} | {m.get('measured_resolution', m['resolution'])} "
            f"| {dur if m['status'] == 'ok' else 'MISSING'} | {gen} | {m['notes']} |"
        )
    lines += ["", "Latency detail: `latency.csv` (model load, first-segment, avg per-segment, total).", ""]
    (ROOT / "README.md").write_text("\n".join(lines))
    print(f"wrote {ROOT / 'README.md'}")


if __name__ == "__main__":
    main()
