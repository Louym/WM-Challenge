# Bidirectional clip-by-clip — per-sibling clip length (= causal sibling's per-inference output)

Each bidirectional model generates clips whose length equals its **causal sibling's per-inference
(per-generation-call) output**, chained to ~60s — so the bidirectional model runs at the same temporal
granularity the causal model commits per inference.

| Bidirectional model | Causal sibling | Sibling per-inference | Clip length used | fps | #clips | Steps | Res | Video |
|---|---|---|---|---|---|---|---|---|
| HY-WorldPlay **bi**       | HY-ar                 | 125 f (5.21 s)          | **125 f = 5.21 s** | 24 | 12 | 20 | 832×480  | `hy_bi_clip.mp4` (reuse) |
| **DreamX-World-5B-Cam**   | DreamX-ar             | 81 f (5.06 s)           | **81 f = 5.06 s**  | 16 | 12 | 50 | 704×1280 | `dreamx_cam_clip.mp4` (reuse) |
| **LingBot-World large**   | LingBot-small / v2    | 57 f (3.56 s)           | **57 f = 3.56 s**  | 16 | 17 | 20 | 480×832  | `lingbot_large_clip57.mp4` (NEW) |
| **Sana-WM** (bidirectional)| **SANA-WM_streaming**| 3 latent f = 17 raw f (1.06 s) | **17 f = 1.06 s** | 16 | 57 | 60 | 704×1280 | `sana_bidirectional_clip17.mp4` (NEW) |

Sana's causal sibling is **SANA-WM_streaming** (LTX2 causal VAE, temporal stride 8; StreamingGenerationConfig
`num_frame_per_block = 3` latent frames → (3-1)*8+1 = 17 raw frames per inference).

Reference — causal models' per-inference output:
| Causal model | Per-inference |
|---|---|
| Matrix-Game-3 (streaming)   | 40 f @17fps = 2.35 s |
| HY-ar / ar_distill / ar_rl  | 125 f @24fps = 5.21 s |
| DreamX-ar                   | 81 f @16fps = 5.06 s |
| Infinite-World              | 49 f @16fps = 3.06 s |
| LingBot-small / v2 (causal) | 57 f @16fps = 3.56 s |
| SANA-WM_streaming           | 3 lat = 17 f @16fps = 1.06 s |

Each row × 3 samples (demo_29 → videos/, demo_42 → videos_demo_42/, demo_79 → videos_demo_79/).
Also available: fixed-0.5s single-denoising-chunk runs (`*_clip05.mp4`) and whole-video runs (`*_whole.mp4`).
