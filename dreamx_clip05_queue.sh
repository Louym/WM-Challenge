#!/usr/bin/env bash
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
run(){ echo "DXCLIP05 starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "DXCLIP05 finished $1 rc=$? ($(date +%H:%M:%S))"; }
dx(){ run "dreamx_cam_clip05_$1" env SAMPLE=$1 DREAMX_DEMO_MODEL_VARIANT=cam DREAMX_DEMO_VIDEO_LENGTH=9 \
  bash run_one.sh dreamx_cam_clip05 dreamx dreamx $2 $3 sessions_specs/dreamx_cam_clip05.json; }
dx demo_29 0 8620 & 
dx demo_42 1 8621 & 
dx demo_79 2 8622 & 
wait
echo "DXCLIP05 ALL DONE ($(date +%H:%M:%S))"
