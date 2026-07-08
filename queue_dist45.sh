#!/usr/bin/env bash
# 2-GPU distributed runs on GPUs 4,5: lingbot_large_whole, mg3_efficiency, mg3_quality
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
run() { echo "QUEUE[dist45] starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "QUEUE[dist45] finished $1 rc=$? ($(date +%H:%M:%S))"; }

run lingbot_large_whole \
  env LINGBOT_WORLD_CKPT_DIR=/mnt/nfs/home/yumingl/models/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=large LINGBOT_DEMO_WARMUP=0 LINGBOT_DEMO_NUM_GPUS=2 \
  bash run_one.sh lingbot_large_whole lingbot lingbot 4,5 8080 sessions_specs/lingbot_large_whole.json

run mg3_efficiency \
  env MG3_CKPT_DIR=/mnt/nfs/home/yumingl/models/Matrix-Game-3.0 MG3_DEMO_MODE=efficiency MG3_DEMO_NUM_GPUS=2 \
  bash run_one.sh mg3_efficiency mg3 mg3 4,5 8081 sessions_specs/mg3_efficiency.json

run mg3_quality \
  env MG3_CKPT_DIR=/mnt/nfs/home/yumingl/models/Matrix-Game-3.0 MG3_DEMO_MODE=quality MG3_DEMO_NUM_GPUS=2 \
  bash run_one.sh mg3_quality mg3 mg3 4,5 8082 sessions_specs/mg3_quality.json

echo "QUEUE[dist45] ALL DONE"
