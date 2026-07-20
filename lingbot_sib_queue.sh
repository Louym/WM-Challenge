#!/usr/bin/env bash
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
MODELS=/mnt/nfs/home/yumingl/models
run(){ echo "SIB starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "SIB finished $1 rc=$? ($(date +%H:%M:%S))"; }
lb(){ run "lingbot_large_clip57_$1" env SAMPLE=$1 LINGBOT_WORLD_CKPT_DIR=$MODELS/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=large \
  LINGBOT_DEMO_ACTION_NUM_FRAMES=57 LINGBOT_DEMO_WARMUP=0 \
  bash run_one.sh lingbot_large_clip57 lingbot lingbot $2 $3 sessions_specs/lingbot_large_clip57.json; }
lb demo_29 0 8640 &
lb demo_42 1 8641 &
lb demo_79 2 8642 &
wait
echo "SIB ALL DONE ($(date +%H:%M:%S))"
