# Generation latency benchmark (H200, dedicated GPUs)

**Protocol.** Every config ran **sequentially in isolation** — one job at a time, benchmark GPUs
exclusively ours (a guard logged any foreign GPU process; the few that appeared were on GPUs
outside the benchmark set). Sample: demo_29. Clip configs ran 4 actions (5 for MG3);
**steady_clip_s** is the mean over clips after the first (the first clip includes per-session
warmup / Pi3X intrinsics and is reported separately). **xRT** = generation seconds per second of
output video (lower is better; 1.0 = realtime). Whole-video configs generate the full ~60s in one
call. Four long whole-video configs were not re-run and reuse delivery-run timings
(`source=delivery-run`): hy_ar/hy_ar_rl/hy_bi whole, dreamx_cam whole. Model-load times vary
heavily with NFS page cache (cold vs warm) and are indicative only.

| config | kind | GPUs | load_s | first_clip_s | steady_clip_s | whole_s | xRT | source |
|---|---|---|---|---|---|---|---|---|
| dreamx_ar | clip | 1 | 553.0 | 38.0 | 27.3 | - | 5.4 | isolated |
| dreamx_ar | whole | 1 | 140.0 | - | - | 241.0 | 3.98 | isolated |
| dreamx_cam | clip | 1 | 416.0 | 169.0 | 167.0 | - | 32.99 | isolated |
| dreamx_cam | whole | 1 | - | - | - | 9880.0 | 164.5 | delivery-run |
| hy_ar | clip | 1 | 586.0 | 318.0 | 310.0 | - | 59.52 | isolated |
| hy_ar | whole | 1 | - | - | - | 4510.0 | 75.11 | delivery-run |
| hy_ar_distill | clip | 1 | 1654.0 | 92.0 | 58.7 | - | 11.26 | isolated |
| hy_ar_distill | whole | 1 | 60.0 | - | - | 828.0 | 13.79 | isolated |
| hy_ar_rl | clip | 1 | 591.0 | 317.0 | 310.3 | - | 59.58 | isolated |
| hy_ar_rl | whole | 1 | - | - | - | 4506.0 | 75.05 | delivery-run |
| hy_bi | clip | 1 | 591.0 | 480.0 | 477.7 | - | 91.71 | isolated |
| hy_bi | whole | 1 | - | - | - | 10419.0 | 173.53 | delivery-run |
| infworld | clip | 1 | 205.0 | 53.0 | 41.3 | - | 13.5 | isolated |
| lingbot_large | clip | 1 | 1516.0 | 122.0 | 111.7 | - | 36.46 | isolated |
| lingbot_large | whole | 4 | 190.0 | - | - | 3395.0 | 56.52 | isolated |
| lingbot_small | clip | 1 | 986.0 | 44.0 | 25.3 | - | 7.11 | isolated |
| lingbot_small | whole | 1 | 91.0 | - | - | 385.0 | 6.41 | isolated |
| lingbot_v2 | clip | 1 | 876.0 | 34.0 | 24.7 | - | 6.92 | isolated |
| lingbot_v2 | whole | 1 | 100.0 | - | - | 350.0 | 5.78 | isolated |
| mg3_efficiency | clip | 2 | 850.0 | 50.0 | 14.8 | - | 6.27 | isolated |
| mg3_quality | clip | 2 | 355.0 | 231.0 | 225.2 | - | 95.73 | isolated |
| sana | clip | 1 | 977.0 | 256.0 | 33.3 | - | 10.88 | isolated |
| sana | whole | 1 | 121.0 | - | - | 907.0 | 15.1 | isolated |

Reproduce: `bash bench_queue.sh` (sequential; see script for per-config envs), then `python bench_report.py`.
