#!/usr/bin/env bash
# Sequential run queue for GPU 5
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
G=5
run() { echo "QUEUE[gpu$G] starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "QUEUE[gpu$G] finished $1 rc=$? ($(date +%H:%M:%S))"; }

run sana_wm \
  env SANA_WM_ROOT=/mnt/nfs/home/yumingl/models/SANA-WM_bidirectional SANA_STAGE1_TEXT_ENCODER_ROOT=/mnt/nfs/home/yumingl/models/gemma-2-2b-it SANA_DEMO_NUM_FRAMES=961 SANA_DEMO_WARMUP=0 SANA_DEMO_OVERLAY=0 \
  bash run_one.sh sana_wm sana sana $G 8050 sessions_specs/sana.json

run hy_ar_rl \
  env HY_DEMO_MODEL_VARIANT=ar_rl \
  bash run_one.sh hy_ar_rl hy hy $G 8051 sessions_specs/hy_ar_rl.json

run hy_bi \
  env HY_DEMO_MODEL_VARIANT=bi \
  bash run_one.sh hy_bi hy hy $G 8052 sessions_specs/hy_bi.json

run lingbot_large \
  env LINGBOT_WORLD_CKPT_DIR=/mnt/nfs/home/yumingl/models/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=large LINGBOT_DEMO_WARMUP=0 \
  bash run_one.sh lingbot_large lingbot lingbot $G 8053 sessions_specs/lingbot_large.json

echo "QUEUE[gpu$G] ALL DONE"
