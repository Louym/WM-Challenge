#!/usr/bin/env bash
# Bidirectional models, clip-by-clip at CAUSAL-chunk granularity (~0.5s/clip):
#   HY-bi 13f@24fps, Sana-WM 9f@16fps, LingBot-large 9f@16fps.
# 3 models x 3 samples = 9 runs across GPUs 0-7 (8 in parallel, 9th queued).
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
MODELS=/mnt/nfs/home/yumingl/models

run() { echo "CLIP05 starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "CLIP05 finished $1 rc=$? ($(date +%H:%M:%S))"; }

hy() {  # sample gpu port
  run "hy_bi_clip05_$1" env SAMPLE=$1 HY_DEMO_MODEL_VARIANT=bi HY_DEMO_NUM_FRAMES=13 \
    bash run_one.sh hy_bi_clip05 hy hy $2 $3 sessions_specs/hy_bi_clip05.json
}
sana() {
  run "sana_clip05_$1" env SAMPLE=$1 SANA_WM_ROOT=$MODELS/SANA-WM_bidirectional SANA_STAGE1_TEXT_ENCODER_ROOT=$MODELS/gemma-2-2b-it \
    SANA_DEMO_ACTION_NUM_FRAMES=9 SANA_DEMO_NUM_FRAMES=9 SANA_DEMO_WARMUP=0 SANA_DEMO_OVERLAY=0 \
    bash run_one.sh sana_bidirectional_clip05 sana sana $2 $3 sessions_specs/sana_bidirectional_clip05.json
}
lingbot() {
  run "lingbot_large_clip05_$1" env SAMPLE=$1 LINGBOT_WORLD_CKPT_DIR=$MODELS/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=large \
    LINGBOT_DEMO_ACTION_NUM_FRAMES=9 LINGBOT_DEMO_WARMUP=0 \
    bash run_one.sh lingbot_large_clip05 lingbot lingbot $2 $3 sessions_specs/lingbot_large_clip05.json
}

# GPU map: HY-bi on 0,1,2 ; Sana on 3,4,5 ; LingBot-large on 6,7 (+ demo_79 queued on 6 after)
hy      demo_29 0 8600 &  P1=$!
hy      demo_42 1 8601 &  P2=$!
hy      demo_79 2 8602 &  P3=$!
sana    demo_29 3 8603 &  P4=$!
sana    demo_42 4 8604 &  P5=$!
sana    demo_79 5 8605 &  P6=$!
lingbot demo_29 6 8606 &  P7=$!
lingbot demo_42 7 8607 &  P8=$!
wait $P7            # free GPU6 before starting the 9th run there
lingbot demo_79 6 8608 &  P9=$!
wait $P1 $P2 $P3 $P4 $P5 $P6 $P8 $P9
echo "CLIP05 ALL DONE ($(date +%H:%M:%S))"
