#!/usr/bin/env bash
# Sequential run queue for GPU 4
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
G=4
run() { echo "QUEUE[gpu$G] starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "QUEUE[gpu$G] finished $1 rc=$? ($(date +%H:%M:%S))"; }

run infworld \
  bash run_one.sh infworld infworld infworld $G 8040 sessions_specs/infworld.json

run hy_ar_distill \
  env HY_DEMO_MODEL_VARIANT=ar_distill \
  bash run_one.sh hy_ar_distill hy hy $G 8041 sessions_specs/hy_ar_distill.json

run hy_ar \
  env HY_DEMO_MODEL_VARIANT=ar \
  bash run_one.sh hy_ar hy hy $G 8042 sessions_specs/hy_ar.json

run lingbot_small \
  env LINGBOT_WORLD_CKPT_DIR=/mnt/nfs/home/yumingl/models/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=small LINGBOT_DEMO_WARMUP=0 \
  bash run_one.sh lingbot_small lingbot lingbot $G 8043 sessions_specs/lingbot_small.json

run mg3_efficiency \
  env MG3_CKPT_DIR=/mnt/nfs/home/yumingl/models/Matrix-Game-3.0 MG3_DEMO_MODE=efficiency \
  bash run_one.sh mg3_efficiency mg3 mg3 $G 8044 sessions_specs/mg3_efficiency.json

echo "QUEUE[gpu$G] ALL DONE"
