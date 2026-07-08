#!/usr/bin/env bash
# Final runs: mg3_efficiency (GPUs 4,5) || mg3_quality (GPUs 6,7), then lingbot_large_whole (GPUs 4-7)
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs

echo "QUEUE[final] starting mg3_efficiency + mg3_quality in parallel ($(date +%H:%M:%S))"
env MG3_CKPT_DIR=/mnt/nfs/home/yumingl/models/Matrix-Game-3.0 MG3_DEMO_MODE=efficiency MG3_DEMO_NUM_GPUS=2 \
  bash run_one.sh mg3_efficiency mg3 mg3 4,5 8081 sessions_specs/mg3_efficiency.json &
P1=$!
env MG3_CKPT_DIR=/mnt/nfs/home/yumingl/models/Matrix-Game-3.0 MG3_DEMO_MODE=quality MG3_DEMO_NUM_GPUS=2 \
  bash run_one.sh mg3_quality mg3 mg3 6,7 8082 sessions_specs/mg3_quality.json &
P2=$!
wait $P1; RC1=$?
wait $P2; RC2=$?
echo "QUEUE[final] mg3_efficiency rc=$RC1, mg3_quality rc=$RC2 ($(date +%H:%M:%S))"

echo "QUEUE[final] starting lingbot_large_whole on 4 GPUs ($(date +%H:%M:%S))"
env LINGBOT_WORLD_CKPT_DIR=/mnt/nfs/home/yumingl/models/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=large LINGBOT_DEMO_WARMUP=0 LINGBOT_DEMO_NUM_GPUS=4 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  bash run_one.sh lingbot_large_whole lingbot lingbot 4,5,6,7 8084 sessions_specs/lingbot_large_whole.json
echo "QUEUE[final] lingbot_large_whole rc=$? ($(date +%H:%M:%S))"
echo "QUEUE[final] ALL DONE"
