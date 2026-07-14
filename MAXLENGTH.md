# LingBot-World-v2 — how long a single continuous stream can it generate?

**Question.** The paper (arXiv:2607.07534) advertises an *unbounded interaction
horizon* and demos an hour-long uninterrupted session. The released
`causal-fast` code, run as-is, tops out at **255 s**. Why the gap, and how far
can the released weights actually go on one GPU?

**Answer.** The 255 s cap is **not** a model/horizon limit — the windowed-attention
model (KV window 18 + sink 6 latents) has *constant* per-frame cost and shows no
quality/capability ceiling. The cap is a **stack of independent O(length)
memory/tooling limits in the released inference code**, each liftable. Removing
them one at a time (single NVIDIA H200, 140 GB, sample demo_29) walks the ceiling
out ~5x, to a **12.5-minute continuous video**:

| # | Limit (what allocates O(length)) | Caps at | Fix applied |
|---|---|---|---|
| 1 | **RoPE temporal table** — `rope_params(1024, …)`, absolute frame index | 1023 lat / **255 s** | enlarge table 1024 → 16384 |
| 2 | **CUDA fragmentation** at ~1200 lat during rollout | ~1200 lat / 300 s | `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` |
| 3 | **Full-length VAE decode** — accumulates whole pixel video on GPU (`torch.cat`), 1 contiguous ~29 GB alloc | ~1650–1800 lat / ~450 s | **chunked decode**: keep the per-frame decoder loop + causal `feat_cache`, offload each decoded frame to CPU (identical output) |
| 4 | **Plücker camera-conditioning** — built at pixel resolution for the whole sequence at once (`get_plucker_embeddings` → einops reshape), ~52–78 GB single alloc *before* denoise | 3000–4500 lat | *(not fixed — next liftable limit; chunk the conditioning to go further)* |

Also patched: streaming `save_video` (encode one frame at a time; the original
built the whole `[T,H,W,C]` tensor and OOM'd on long clips).

## Verified ladder (each = one continuous generation call, no restarts)

| latents | video length | outcome | limiting stage |
|---|---|---|---|
| 1023 | 255.6 s | ✅ saves (released code, unmodified) | RoPE table (hard cap) |
| 1200 | 300 s | ✅ saves | needed expandable_segments |
| 1500 | 375 s | ✅ saves | — |
| 1800 | 450 s | ❌ OOM | full-length VAE decode (fix #3 target) |
| 3000 | **749.8 s (12.5 min)** | ✅ **saves — max demonstrated** | cleared decode via chunking |
| 4500 | 1125 s | ❌ OOM | Plücker conditioning (#4) |
| 6000 | 1500 s | ❌ OOM | Plücker conditioning (#4) |

Max saved: `length_test_videos/maxrun_lingbot_v2_3000lat.mp4` — 3000 latents,
749.8 s, 832×464, 11997 frames, 928 MB. Generation ~72 min on one H200
(56.7 min denoise @ ~3.4 s/step × 1000 steps + chunked decode + streaming save);
throughput stays ~constant per frame, consistent with the windowed-attention design.

## Takeaways
- Per-frame **compute** is constant with length (windowed attention) — confirmed
  flat from 60 s to 12.5 min. The horizon is bounded by **peak memory of
  O(length) buffers**, not by the model.
- Each limit above is a tooling/memory-management artifact. Fixing #4 (chunk the
  Plücker conditioning) and streaming the CPU decode buffer would push further;
  the RoPE table already supports 16383 latents (~68 min).
- The paper's hour-long claim is therefore **credible**: it needs their unreleased
  serving stack (relative-position re-anchoring, tiled/streamed VAE decode,
  multi-GPU / offload), not a different model.

*Repro: `sessions_specs/maxrun_*lat.json` + `ropeext_*lat.json`; run via the
`ext_adapters/lingbot_world_v2.py` adapter with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`.
The three source patches were applied to a local clone of `lingbot-world-v2` for
this experiment and then reverted — they are not part of the released repo.*
