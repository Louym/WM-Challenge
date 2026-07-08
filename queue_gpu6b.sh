#!/usr/bin/env bash
# Follow-up queue for GPU 6: hy_ar_distill re-run, dreamx_cam_whole retry with offload
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
G=6
run() { echo "QUEUE[gpu$G] starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "QUEUE[gpu$G] finished $1 rc=$? ($(date +%H:%M:%S))"; }

run hy_ar_distill \
  env HY_DEMO_MODEL_VARIANT=ar_distill \
  bash run_one.sh hy_ar_distill hy hy $G 8065 sessions_specs/hy_ar_distill.json

run dreamx_cam_whole \
  env PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True DREAMX_DEMO_MODEL_VARIANT=cam DREAMX_DEMO_VIDEO_LENGTH=961 DREAMX_DEMO_GPU_MEMORY_MODE=sequential_cpu_offload \
  bash run_one.sh dreamx_cam_whole dreamx dreamx $G 8066 sessions_specs/dreamx_cam_whole.json

echo "QUEUE[gpu$G] ALL DONE"
