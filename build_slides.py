#!/usr/bin/env python3
"""Generate slides.html: a keyboard-navigable deck of all generated videos + model details.

Reads manifest.json / manifest_demo_42.json / manifest_demo_79.json (built by
build_manifest.py) and lays out one slide per run config with the three samples
side by side. Videos are lazy-loaded when their slide becomes active.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
SAMPLES = [("demo_29", "videos"), ("demo_42", "videos_demo_42"), ("demo_79", "videos_demo_79")]
SAMPLE_LABELS = {"demo_29": "sample 29 — coffee shop", "demo_42": "sample 42", "demo_79": "sample 79"}

MODEL_ORDER = [
    "HY-WorldPlay", "Sana-WM", "LingBot-World", "LingBot-World-v2", "Matrix-Game-3.0",
    "DreamX-World-5B", "DreamX-World-5B-Cam", "Infinite-World",
]
MODEL_BLURB = {
    "HY-WorldPlay": "Tencent HY-WorldPlay on HunyuanVideo-1.5 (480p i2v, 832x480@24fps). Four checkpoints: ar_distill (4-step distilled causal), ar (20-step causal), ar_rl (RL-tuned causal), bi (bidirectional). Camera/action conditioning via pose trajectories.",
    "Sana-WM": "Sana-WM bidirectional 1600M 720p (1280x704@16fps) with refiner; 60 sampling steps, CFG 5, Pi3X-estimated intrinsics. Actions are camera trajectories (c2w) from a WASD/IJKL DSL.",
    "LingBot-World": "LingBot-World i2v-A14B (832x480@16fps). small/fast = distilled chunked-streaming causal pipeline; large/base = 20-step act2cam pipeline. Dual (high/low-noise) 14B Wan-style models.",
    "LingBot-World-v2": "LingBot-World 2.0 / LingBot-World-Infinity (robbyant, arXiv:2607.07534), built on Wan2.2 i2v-A14B (832x480 @ 16fps). Causal pretraining for an unbounded interaction horizon; released variant is the 4-step distilled causal-fast model streaming with a KV window (local_attn 18, sink 6). Code: github.com/robbyant/lingbot-world-v2.",
    "Matrix-Game-3.0": "Skywork Matrix-Game-3.0 interactive streaming world model (1280x704@17fps). efficiency = distilled+int8, quality = base model at 50 steps. One action per 40-frame chunk, KV state persists across the stream (no whole-video mode; runs are one continuous causal video). Run 2-GPU distributed.",
    "DreamX-World-5B": "DreamX-World-5B autoregressive long-horizon variant on Wan2.2-TI2V-5B (1280x704@16fps). One camera+move token per generation; 21 latent frames per clip.",
    "DreamX-World-5B-Cam": "DreamX-World-5B-Cam bidirectional camera-controlled variant (1280x704@16fps), 50 steps, CFG 3. Whole-video run is ~12x its training clip length and needed CPU offload.",
    "Infinite-World": "MeiGen Infinite-World chunk-autoregressive model (~627p bucket@16fps), 30 steps, CFG 5. Fixed 49-frame chunks per action; no whole-video mode.",
}


def load_manifests():
    per_sample = {}
    for sample, _vdir in SAMPLES:
        suf = "" if sample == "demo_29" else f"_{sample}"
        per_sample[sample] = {m["video"].replace(".mp4", ""): m for m in json.loads((ROOT / f"manifest{suf}.json").read_text())}
    return per_sample


def esc(s) -> str:
    return html.escape(str(s))


def main() -> None:
    manifests = load_manifests()
    base = manifests["demo_29"]
    runs = list(base.keys())  # ordered as in build_manifest.RUNS

    slides = []

    # ---- title slide
    slides.append(f"""
<section class="slide title">
  <h1>World-Model Baselines &mdash; Interactive Demo Comparison</h1>
  <p class="sub">7 models &times; all supported settings (causal vs bidirectional, clip-by-clip vs whole-video)</p>
  <p class="sub">3 input samples (29, 42, 79) &middot; 69 videos &middot; ~60&thinsp;s each &middot; shared trajectory</p>
  <p class="dim">Generated with the unmodified <code>baselines/demo</code> server driven over its HTTP API &middot; H200 GPUs</p>
  <p class="dim">&larr;/&rarr; or click edges to navigate &middot; videos autoplay muted &middot; L toggles loop</p>
</section>""")

    # ---- protocol slide
    slides.append("""
<section class="slide">
  <h2>Protocol</h2>
  <ul>
    <li><b>Inputs:</b> <code>SANA_WM_dev/playground/dataset</code> samples demo_29 (coffee shop), demo_42 (car dashboard), demo_79 &mdash; image + text prompt.</li>
    <li><b>Shared camera trajectory (~60s):</b> forward &rarr; pan right &rarr; forward &rarr; backward, equal quarters.
        DreamX whole-video runs are push-in only (its API takes one action token per shot).</li>
    <li><b>clip-by-clip:</b> one action per segment; each segment restarts from the last frame of the previous one
        (temporal context lost at boundaries). Exceptions: MG3 and Infinite-World stream continuously with persistent state.</li>
    <li><b>whole-video:</b> a single action string / one long rollout in one generation call.</li>
    <li><b>Reported latency</b> is generation wall-time on H200 (excl. model load); see <code>latency*.csv</code>.</li>
  </ul>
</section>""")

    current_model = None
    for run in runs:
        cfg = base[run]
        model = cfg["model"]
        if model != current_model:
            current_model = model
            variants = sorted({manifests["demo_29"][r]["variant"] for r in runs if base[r]["model"] == model})
            slides.append(f"""
<section class="slide model">
  <h2>{esc(model)}</h2>
  <p class="blurb">{esc(MODEL_BLURB.get(model, ""))}</p>
  <table>
    <tr><th>variants run</th><td>{esc(", ".join(variants))}</td></tr>
    <tr><th>temporal</th><td>{esc(cfg["temporal"])}</td></tr>
    <tr><th>resolution / fps</th><td>{esc(cfg.get("measured_resolution", cfg["resolution"]))} @ {esc(cfg["fps"])} fps</td></tr>
  </table>
</section>""")

        vids = []
        for sample, vdir in SAMPLES:
            m = manifests[sample].get(run, {})
            gen = m.get("total_generation_s")
            gen_str = f"{gen/60:.1f} min gen" if gen else "n/a"
            dur = m.get("duration_s", "?")
            vids.append(f"""
    <figure>
      <video preload="none" muted loop playsinline data-src="{vdir}/{run}.mp4"></video>
      <figcaption>{esc(SAMPLE_LABELS[sample])} &middot; {esc(dur)}s &middot; {esc(gen_str)}</figcaption>
    </figure>""")

        steps = f" &middot; {cfg['steps']} steps" if cfg.get("steps") else ""
        cfgs = f" &middot; CFG {cfg['cfg']}" if cfg.get("cfg") else ""
        slides.append(f"""
<section class="slide videos">
  <h3><span class="model-tag">{esc(model)}</span> {esc(cfg['variant'])} &mdash; {esc(cfg['protocol'])}</h3>
  <div class="vidrow">{''.join(vids)}</div>
  <p class="meta">{esc(cfg['temporal'])} &middot; {esc(cfg['clips'])} &times; {esc(cfg['frames_per_clip'])} frames @ {esc(cfg['fps'])} fps{steps}{cfgs} &middot; seed {esc(cfg['seed'])}<br>
  <span class="dim">{esc(cfg['trajectory'])}</span><br>
  <span class="dim note">{esc(cfg['notes'])}</span></p>
</section>""")

    # ---- latency summary slide
    rows = []
    for run in runs:
        cells = []
        for sample, _ in SAMPLES:
            g = manifests[sample].get(run, {}).get("total_generation_s")
            cells.append(f"<td>{g/60:.1f}</td>" if g else "<td>-</td>")
        rows.append(f"<tr><td class='l'>{esc(run)}</td>{''.join(cells)}</tr>")
    slides.append(f"""
<section class="slide">
  <h2>Generation latency (minutes, H200, excl. model load)</h2>
  <table class="lat">
    <tr><th class='l'>run</th><th>sample 29</th><th>sample 42</th><th>sample 79</th></tr>
    {''.join(rows)}
  </table>
  <p class="dim">Multi-GPU runs: mg3_* (2 GPUs), lingbot_large_whole (4 GPUs), sample-29 dreamx_cam_whole (CPU offload). Details: latency*.csv / manifest*.json.</p>
</section>""")

    n = len(slides)
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>World-Model Baselines — Video Comparison</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0e1116; color: #e8edf2; overflow: hidden; }}
  .slide {{ display: none; position: fixed; inset: 0; padding: 4vh 5vw; flex-direction: column; justify-content: center; }}
  .slide.active {{ display: flex; }}
  h1 {{ font-size: 2.6em; margin-bottom: .5em; }}
  h2 {{ font-size: 2em; margin-bottom: .8em; color: #7fc4ff; }}
  h3 {{ font-size: 1.35em; margin-bottom: .6em; }}
  .model-tag {{ color: #7fc4ff; }}
  .title {{ text-align: center; }}
  .sub {{ font-size: 1.25em; margin: .3em 0; }}
  .dim {{ color: #93a1b0; font-size: .92em; margin-top: .6em; }}
  .blurb {{ font-size: 1.15em; line-height: 1.55; max-width: 62em; margin-bottom: 1.2em; }}
  ul {{ font-size: 1.12em; line-height: 1.7; max-width: 64em; }} li {{ margin-bottom: .5em; }}
  table {{ border-collapse: collapse; font-size: 1.05em; }}
  th, td {{ padding: .35em .9em; text-align: center; border-bottom: 1px solid #2a3542; }}
  th {{ color: #93a1b0; font-weight: 600; }} .l {{ text-align: left; }}
  table.lat {{ font-size: .78em; }} table.lat td, table.lat th {{ padding: .12em .8em; }}
  .vidrow {{ display: flex; gap: 1.2vw; align-items: flex-start; }}
  figure {{ flex: 1; min-width: 0; }}
  video {{ width: 100%; background: #000; border-radius: 6px; }}
  figcaption {{ font-size: .85em; color: #93a1b0; margin-top: .35em; text-align: center; }}
  .meta {{ margin-top: .8em; font-size: .95em; line-height: 1.45; }}
  .note {{ font-style: italic; }}
  #counter {{ position: fixed; bottom: 12px; right: 16px; color: #93a1b0; font-size: .85em; z-index: 5; }}
  #navL, #navR {{ position: fixed; top: 0; bottom: 0; width: 12vw; z-index: 4; cursor: pointer; }}
  #navL {{ left: 0; }} #navR {{ right: 0; }}
  code {{ background: #1b2430; padding: .1em .35em; border-radius: 4px; }}
</style></head><body>
{''.join(slides)}
<div id="counter"></div><div id="navL"></div><div id="navR"></div>
<script>
  const slides = document.querySelectorAll('.slide');
  let cur = Math.min(parseInt(location.hash.slice(1)) || 0, slides.length - 1);
  let loop = true;
  function show(i) {{
    cur = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach((s, j) => {{
      s.classList.toggle('active', j === cur);
      s.querySelectorAll('video').forEach(v => {{
        if (j === cur) {{
          if (!v.src) v.src = v.dataset.src;
          v.loop = loop; v.play().catch(() => {{}});
        }} else {{ v.pause(); }}
      }});
    }});
    document.getElementById('counter').textContent = (cur + 1) + ' / ' + slides.length;
    location.hash = cur;
  }}
  document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') show(cur + 1);
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') show(cur - 1);
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(slides.length - 1);
    else if (e.key.toLowerCase() === 'l') {{ loop = !loop; show(cur); }}
  }});
  document.getElementById('navL').onclick = () => show(cur - 1);
  document.getElementById('navR').onclick = () => show(cur + 1);
  show(cur);
</script>
</body></html>"""
    out = ROOT / "slides.html"
    out.write_text(page)
    print(f"wrote {out} ({n} slides)")


if __name__ == "__main__":
    main()
