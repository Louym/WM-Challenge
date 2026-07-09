# World-model demo comparison on sample demo_29

Input: `SANA_WM_dev/playground/dataset/dataset/demo_29.png` + `demo_29.txt` prompt.
Shared camera trajectory (~60s): forward, pan right, forward, backward — equal quarters.
All runs drive the unmodified `baselines/demo` server through its HTTP API (one GPU per run
unless noted). `clip-by-clip` = one action per segment, chained on the last frame;
`whole-video` = a single action string / long rollout in one generation call.

| video | model | variant | temporal | protocol | clips x frames | fps | res | duration_s | gen_time_s | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| infworld_clip.mp4 | Infinite-World | default | causal (chunk-autoregressive) | clip-by-clip | 20 x 49 | 16 | 896x448 | 61.26 | 770.0 | whole-video mode not supported (fixed 49-frame chunks) |
| sana_wm_bidirectional_clip.mp4 | Sana-WM | bidirectional 1600M 720p + refiner | bidirectional | clip-by-clip | 20 x 49 | 16 | 1280x704 | 60.0 | 1110.0 | refiner on; Pi3X-estimated intrinsics; flow_shift 8 |
| sana_wm_bidirectional_whole.mp4 | Sana-WM | bidirectional 1600M 720p + refiner | bidirectional | whole-video | 1 x 961 | 16 | 1280x704 | 60.0 | 927.0 | 961 frames in one shot |
| hy_ar_distill_clip.mp4 | HY-WorldPlay | ar_distill | causal (autoregressive) | clip-by-clip | 12 x 125 | 24 | 832x480 | 62.51 | 627.0 | chunk_latent_frames=4 |
| hy_ar_clip.mp4 | HY-WorldPlay | ar | causal (autoregressive) | clip-by-clip | 12 x 125 | 24 | 832x480 | 62.51 | 3679.0 | chunk_latent_frames=4 |
| hy_ar_rl_clip.mp4 | HY-WorldPlay | ar_rl | causal (autoregressive) | clip-by-clip | 12 x 125 | 24 | 832x480 | 62.51 | 3683.0 | chunk_latent_frames=4 |
| hy_bi_clip.mp4 | HY-WorldPlay | bi | bidirectional | clip-by-clip | 12 x 125 | 24 | 832x480 | 62.51 | 5731.0 | chunk_latent_frames=16 |
| hy_ar_distill_whole.mp4 | HY-WorldPlay | ar_distill | causal (autoregressive) | whole-video | 1 x 1441 | 24 | 832x480 | 60.04 | 824.0 | 1441 frames in one rollout |
| hy_ar_whole.mp4 | HY-WorldPlay | ar | causal (autoregressive) | whole-video | 1 x 1441 | 24 | 832x480 | 60.04 | 4510.0 | 1441 frames in one rollout |
| hy_ar_rl_whole.mp4 | HY-WorldPlay | ar_rl | causal (autoregressive) | whole-video | 1 x 1441 | 24 | 832x480 | 60.04 | 4506.0 | 1441 frames in one rollout |
| hy_bi_whole.mp4 | HY-WorldPlay | bi | bidirectional | whole-video | 1 x 1441 | 24 | 832x480 | 60.04 | 10419.0 | 1441 frames in one rollout |
| dreamx_ar_clip.mp4 | DreamX-World-5B | ar (long-horizon autoregressive) | causal (autoregressive) | clip-by-clip | 12 x 81 | 16 | 1280x704 | 60.76 | 488.0 | 21 latent frames per clip |
| dreamx_ar_whole.mp4 | DreamX-World-5B | ar (long-horizon autoregressive) | causal (autoregressive) | whole-video | 1 x 969 | 16 | 1280x704 | 60.56 | 307.0 | 243 latent frames in one rollout |
| dreamx_cam_clip.mp4 | DreamX-World-5B-Cam | cam | bidirectional | clip-by-clip | 12 x 81 | 16 | 1280x704 | 60.76 | 2095.0 | shift 3.0 |
| dreamx_cam_whole.mp4 | DreamX-World-5B-Cam | cam | bidirectional | whole-video | 1 x 961 | 16 | 1280x704 | 60.06 | 9880.0 | 961 frames in one bidirectional shot (~12x training clip length); required memory workarounds on one H200 |
| lingbot_small_clip.mp4 | LingBot-World | small/fast (distilled streaming) | causal (chunked streaming) | clip-by-clip | 20 x 57 | 16 | 832x464 | 71.26 | 570.0 | i2v-A14B; 49-frame request snapped to 57 (3-latent chunking) |
| lingbot_large_clip.mp4 | LingBot-World | large/base (act2cam) | bidirectional per segment | clip-by-clip | 20 x 49 | 16 | 832x464 | 61.26 | 2282.0 | i2v-A14B |
| lingbot_small_whole.mp4 | LingBot-World | small/fast (distilled streaming) | causal (chunked streaming) | whole-video | 1 x 961 | 16 | 832x464 | 60.56 | 418.0 | i2v-A14B; KV cache bounded to a 24-latent-frame rolling window (LINGBOT_DEMO_LOCAL_ATTN_SIZE=24) — full-sequence cache (~300GB) cannot fit one GPU |
| lingbot_large_whole.mp4 | LingBot-World | large/base (act2cam) | bidirectional per segment | whole-video | 1 x 961 | 16 | 832x464 | 60.06 | 3376.0 | i2v-A14B; run distributed on 4 GPUs (FSDP+SP) — 961-frame attention OOMs on 1 and 2 H200s |
| lingbot_v2_fast_clip.mp4 | LingBot-World-v2 | 14B causal-fast (distilled streaming) | causal (chunked streaming, KV window) | clip-by-clip | 20 x 57 | 16 | 832x464 | 71.26 | 660.0 | LingBot-World-Infinity (arXiv:2607.07534); i2v-A14B single transformer; 4-step distilled, no CFG; local_attn_size=18, sink_size=6 (official run_fast.sh); 49-frame request snapped to 57 (3-latent chunking) |
| lingbot_v2_fast_whole.mp4 | LingBot-World-v2 | 14B causal-fast (distilled streaming) | causal (chunked streaming, KV window) | whole-video | 1 x 969 | 16 | 832x464 | 60.56 | 346.0 | single 969-frame stream (unbounded-horizon design); local_attn_size=18, sink_size=6 |
| mg3_efficiency_clip.mp4 | Matrix-Game-3.0 | efficiency (distilled + int8) | causal (streaming interactive) | clip-by-clip | 26 x 57 first, then 40 | 17 | 1280x704 | 62.18 | 446.0 | run distributed on 2 GPUs (single-GPU interactive path has an upstream device bug); whole-video mode not supported (streaming only) |
| mg3_quality_clip.mp4 | Matrix-Game-3.0 | quality (base model) | causal (streaming interactive) | clip-by-clip | 26 x 57 first, then 40 | 17 | 1280x704 | 62.18 | 5908.0 | run distributed on 2 GPUs (single-GPU quality path has an upstream device bug); whole-video mode not supported |

Latency detail: `latency.csv` (model load, first-segment, avg per-segment, total).
