# Bidirectional clip-by-clip — per-sibling clip length (matches causal model's per-inference output)

Each bidirectional model generates clips whose length = its **causal sibling's per-inference (per-action) output**,
chained to ~60s. This makes the bidirectional model operate at the same temporal granularity the causal model
commits per generation call.

| Bidirectional model | Causal sibling (per-inference len) | Clip length | fps | #clips | Steps | Res | Video |
|---|---|---|---|---|---|---|---|
| HY-WorldPlay bi        | HY-ar → 125f            | 125 f = 5.21 s | 24 | 12  | 20 | 832×480  | hy_bi_clip.mp4 (reuse) |
| DreamX-World-5B-Cam    | DreamX-ar → 81f         | 81 f = 5.06 s  | 16 | 12  | 50 | 704×1280 | dreamx_cam_clip.mp4 (reuse) |
| LingBot-World large    | LingBot-small/v2 → 57f  | 57 f = 3.56 s  | 16 | 17  | 20 | 480×832  | lingbot_large_clip57.mp4 (NEW) |
| Sana-WM (bidirectional)| none (no causal Sana)   | — unmatched (existing 49f/3.06s clip) | 16 | 20 | 60 | 704×1280 | sana_wm_bidirectional_clip.mp4 |

Reference — CAUSAL models' per-inference output (the value each sibling contributes above):

| Causal model | Per-inference output |
|---|---|
| Matrix-Game-3 (streaming) | 40 f @17fps = 2.35 s |
| HY-ar / ar_distill / ar_rl | 125 f @24fps = 5.21 s |
| DreamX-ar (long-horizon)   | 81 f @16fps = 5.06 s |
| Infinite-World             | 49 f @16fps = 3.06 s |
| LingBot-small / v2 (causal)| 57 f @16fps = 3.56 s |

Per bidirectional model there are 3 samples (demo_29 → videos/, demo_42 → videos_demo_42/, demo_79 → videos_demo_79/).
The earlier fixed-0.5s runs (`*_clip05.mp4`) remain available as the finest (single-denoising-chunk) granularity.
