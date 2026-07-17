# Video index — all world-model outputs (samples 29 / 42 / 79)

Three temporal protocols per bidirectional model:
- **A. whole-video** — one generation call for the full ~60s.
- **B. 3s clip-by-clip** — one action per ~3s segment, chained (each restarts from prev last frame).
- **C. 0.5s causal-chunk clip (NEW)** — clip length forced to the causal models' atomic per-inference chunk
  (~0.5s: HY 13f@24fps, Sana/LingBot/DreamX 9f@16fps), chained ~108-112x. Apples-to-apples vs the causal models.

Causal / streaming models (single protocol, listed under B) generate their atomic chunk continuously.


## Sample demo_29 (coffee shop)

### whole-video (1 call)
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/dreamx_ar_whole.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/dreamx_cam_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/hy_ar_distill_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/hy_ar_rl_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/hy_ar_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/hy_bi_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/lingbot_large_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/lingbot_small_whole.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/lingbot_v2_fast_whole.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/sana_wm_bidirectional_whole.mp4`  — 60s

### 3s clip-by-clip (existing)
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/dreamx_ar_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/dreamx_cam_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/hy_ar_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/hy_ar_distill_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/hy_ar_rl_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/hy_bi_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/infworld_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/lingbot_large_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/lingbot_small_clip.mp4`  — 71s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/lingbot_v2_fast_clip.mp4`  — 71s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/mg3_efficiency_clip.mp4`  — 62s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/mg3_quality_clip.mp4`  — 62s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/sana_wm_bidirectional_clip.mp4`  — 60s

### 0.5s causal-chunk clip (NEW)
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/hy_bi_clip05.mp4`  — 61s  _(13 frames @24fps = 0.54s x112 clips (= HY-ar causal chunk))_
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/lingbot_large_clip05.mp4`  — 61s  _(9 frames @16fps = 0.56s x108 clips (= LingBot causal chunk))_
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos/sana_bidirectional_clip05.mp4`  — 54s  _(9 frames @16fps = 0.56s x108 clips)_


## Sample demo_42 (car dashboard)

### whole-video (1 call)
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/dreamx_ar_whole.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/dreamx_cam_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/hy_ar_distill_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/hy_ar_rl_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/hy_ar_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/hy_bi_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/lingbot_large_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/lingbot_small_whole.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/lingbot_v2_fast_whole.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/sana_wm_bidirectional_whole.mp4`  — 60s

### 3s clip-by-clip (existing)
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/dreamx_ar_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/dreamx_cam_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/hy_ar_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/hy_ar_distill_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/hy_ar_rl_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/hy_bi_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/infworld_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/lingbot_large_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/lingbot_small_clip.mp4`  — 71s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/lingbot_v2_fast_clip.mp4`  — 71s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/mg3_efficiency_clip.mp4`  — 62s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/mg3_quality_clip.mp4`  — 62s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/sana_wm_bidirectional_clip.mp4`  — 60s

### 0.5s causal-chunk clip (NEW)
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/hy_bi_clip05.mp4`  — 61s  _(13 frames @24fps = 0.54s x112 clips (= HY-ar causal chunk))_
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/lingbot_large_clip05.mp4`  — 61s  _(9 frames @16fps = 0.56s x108 clips (= LingBot causal chunk))_
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_42/sana_bidirectional_clip05.mp4`  — 54s  _(9 frames @16fps = 0.56s x108 clips)_


## Sample demo_79

### whole-video (1 call)
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/dreamx_ar_whole.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/dreamx_cam_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/hy_ar_distill_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/hy_ar_rl_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/hy_ar_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/hy_bi_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/lingbot_large_whole.mp4`  — 60s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/lingbot_small_whole.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/lingbot_v2_fast_whole.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/sana_wm_bidirectional_whole.mp4`  — 60s

### 3s clip-by-clip (existing)
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/dreamx_ar_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/dreamx_cam_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/hy_ar_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/hy_ar_distill_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/hy_ar_rl_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/hy_bi_clip.mp4`  — 63s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/infworld_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/lingbot_large_clip.mp4`  — 61s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/lingbot_small_clip.mp4`  — 71s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/lingbot_v2_fast_clip.mp4`  — 71s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/mg3_efficiency_clip.mp4`  — 62s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/mg3_quality_clip.mp4`  — 62s
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/sana_wm_bidirectional_clip.mp4`  — 60s

### 0.5s causal-chunk clip (NEW)
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/hy_bi_clip05.mp4`  — 61s  _(13 frames @24fps = 0.54s x112 clips (= HY-ar causal chunk))_
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/lingbot_large_clip05.mp4`  — 61s  _(9 frames @16fps = 0.56s x108 clips (= LingBot causal chunk))_
- `/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/videos_demo_79/sana_bidirectional_clip05.mp4`  — 54s  _(9 frames @16fps = 0.56s x108 clips)_
