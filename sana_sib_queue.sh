#!/usr/bin/env bash
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
MODELS=/mnt/nfs/home/yumingl/models
run(){ echo "SANASIB starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "SANASIB finished $1 rc=$? ($(date +%H:%M:%S))"; }
sn(){ run "sana_clip17_$1" env SAMPLE=$1 SANA_WM_ROOT=$MODELS/SANA-WM_bidirectional SANA_STAGE1_TEXT_ENCODER_ROOT=$MODELS/gemma-2-2b-it \
  SANA_DEMO_ACTION_NUM_FRAMES=17 SANA_DEMO_NUM_FRAMES=17 SANA_DEMO_WARMUP=0 SANA_DEMO_OVERLAY=0 \
  bash run_one.sh sana_bidirectional_clip17 sana sana $2 $3 sessions_specs/sana_bidirectional_clip17.json; }
sn demo_29 3 8650 &
sn demo_42 4 8651 &
sn demo_79 5 8652 &
wait
echo "SANASIB ALL DONE ($(date +%H:%M:%S))"
