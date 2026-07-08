#!/usr/bin/env bash
# Sequential run queue for GPU 6
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
G=6
run() { echo "QUEUE[gpu$G] starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "QUEUE[gpu$G] finished $1 rc=$? ($(date +%H:%M:%S))"; }

run dreamx_ar_clip \
  env DREAMX_DEMO_MODEL_VARIANT=ar \
  bash run_one.sh dreamx_ar_clip dreamx dreamx $G 8060 sessions_specs/dreamx_ar_clip.json

run dreamx_ar_whole \
  env DREAMX_DEMO_MODEL_VARIANT=ar DREAMX_DEMO_NUM_OUTPUT_FRAMES=243 \
  bash run_one.sh dreamx_ar_whole dreamx dreamx $G 8061 sessions_specs/dreamx_ar_whole.json

run dreamx_cam_clip \
  env DREAMX_DEMO_MODEL_VARIANT=cam \
  bash run_one.sh dreamx_cam_clip dreamx dreamx $G 8062 sessions_specs/dreamx_cam_clip.json

run dreamx_cam_whole \
  env DREAMX_DEMO_MODEL_VARIANT=cam DREAMX_DEMO_VIDEO_LENGTH=961 \
  bash run_one.sh dreamx_cam_whole dreamx dreamx $G 8063 sessions_specs/dreamx_cam_whole.json

run mg3_quality \
  env MG3_CKPT_DIR=/mnt/nfs/home/yumingl/models/Matrix-Game-3.0 MG3_DEMO_MODE=quality \
  bash run_one.sh mg3_quality mg3 mg3 $G 8064 sessions_specs/mg3_quality.json

echo "QUEUE[gpu$G] ALL DONE"
