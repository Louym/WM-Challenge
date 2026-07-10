#!/usr/bin/env bash
# Isolated latency benchmark: every config runs SEQUENTIALLY with the whole node
# otherwise idle. Clip configs run 4 actions (5 for MG3); whole configs run the
# full 60s generation. Sample: demo_29. Videos go to bench_videos/ (timing only).
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
export BENCH_VIDEO_DIR=/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs/bench_videos
mkdir -p "$BENCH_VIDEO_DIR"
MODELS=/mnt/nfs/home/yumingl/models

guard() {  # refuse to start a run if any GPU is busy (dedicated-GPU guarantee)
  busy=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)
  if [ "$busy" -gt 0 ]; then
    echo "BENCH WARNING: $busy foreign GPU process(es) present before $1 ($(date +%H:%M:%S))"
    nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader
  fi
}

run() {
  local name=$1; shift
  guard "$name"
  echo "BENCH starting $name ($(date +%H:%M:%S))"
  "$@"
  echo "BENCH finished $name rc=$? ($(date +%H:%M:%S))"
}

# ---- HY-WorldPlay
for v in ar_distill ar ar_rl bi; do
  run bench_hy_${v}_clip env HY_DEMO_MODEL_VARIANT=$v \
    bash run_one.sh bench_hy_${v}_clip hy hy 0 8400 sessions_specs/bench_hy_${v}_clip.json
done
run bench_hy_ar_distill_whole env HY_DEMO_MODEL_VARIANT=ar_distill \
  bash run_one.sh bench_hy_ar_distill_whole hy hy 0 8401 sessions_specs/bench_hy_ar_distill_whole.json

# ---- Infinite-World
run bench_infworld_clip \
  bash run_one.sh bench_infworld_clip infworld infworld 0 8402 sessions_specs/bench_infworld_clip.json

# ---- Sana-WM
SANA_ENV="SANA_WM_ROOT=$MODELS/SANA-WM_bidirectional SANA_STAGE1_TEXT_ENCODER_ROOT=$MODELS/gemma-2-2b-it SANA_DEMO_NUM_FRAMES=961 SANA_DEMO_WARMUP=0 SANA_DEMO_OVERLAY=0"
run bench_sana_clip env $SANA_ENV \
  bash run_one.sh bench_sana_clip sana sana 0 8403 sessions_specs/bench_sana_clip.json
run bench_sana_whole env $SANA_ENV \
  bash run_one.sh bench_sana_whole sana sana 0 8404 sessions_specs/bench_sana_whole.json

# ---- DreamX
run bench_dreamx_ar_clip env DREAMX_DEMO_MODEL_VARIANT=ar \
  bash run_one.sh bench_dreamx_ar_clip dreamx dreamx 0 8405 sessions_specs/bench_dreamx_ar_clip.json
run bench_dreamx_ar_whole env DREAMX_DEMO_MODEL_VARIANT=ar DREAMX_DEMO_NUM_OUTPUT_FRAMES=243 \
  bash run_one.sh bench_dreamx_ar_whole dreamx dreamx 0 8406 sessions_specs/bench_dreamx_ar_whole.json
run bench_dreamx_cam_clip env DREAMX_DEMO_MODEL_VARIANT=cam \
  bash run_one.sh bench_dreamx_cam_clip dreamx dreamx 0 8407 sessions_specs/bench_dreamx_cam_clip.json

# ---- LingBot v1
LB="LINGBOT_WORLD_CKPT_DIR=$MODELS/lingbot-world-base-cam LINGBOT_DEMO_WARMUP=0"
run bench_lingbot_small_clip env $LB LINGBOT_DEMO_MODEL_SIZE=small \
  bash run_one.sh bench_lingbot_small_clip lingbot lingbot 0 8408 sessions_specs/bench_lingbot_small_clip.json
run bench_lingbot_small_whole env $LB LINGBOT_DEMO_MODEL_SIZE=small LINGBOT_DEMO_LOCAL_ATTN_SIZE=24 \
  bash run_one.sh bench_lingbot_small_whole lingbot lingbot 0 8409 sessions_specs/bench_lingbot_small_whole.json
run bench_lingbot_large_clip env $LB LINGBOT_DEMO_MODEL_SIZE=large \
  bash run_one.sh bench_lingbot_large_clip lingbot lingbot 0 8410 sessions_specs/bench_lingbot_large_clip.json
run bench_lingbot_large_whole env $LB LINGBOT_DEMO_MODEL_SIZE=large LINGBOT_DEMO_NUM_GPUS=4 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  bash run_one.sh bench_lingbot_large_whole lingbot lingbot 0,1,2,3 8411 sessions_specs/bench_lingbot_large_whole.json

# ---- LingBot v2
LBV2="WM_DEMO_ADAPTER=ext_adapters.lingbot_world_v2:LingBotWorldV2Adapter PYTHONPATH=/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs LINGBOT_WORLD_ROOT=/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/lingbot-world-v2 LINGBOT_WORLD_CKPT_DIR=$MODELS/lingbot-world-v2-14b-causal-fast LINGBOT_DEMO_MODEL_SIZE=small LINGBOT_DEMO_LOCAL_ATTN_SIZE=18 LINGBOT_DEMO_SINK_SIZE=6 LINGBOT_DEMO_WARMUP=0"
run bench_lingbot_v2_clip env $LBV2 \
  bash run_one.sh bench_lingbot_v2_clip lingbot lingbot 0 8412 sessions_specs/bench_lingbot_v2_clip.json
run bench_lingbot_v2_whole env $LBV2 \
  bash run_one.sh bench_lingbot_v2_whole lingbot lingbot 0 8413 sessions_specs/bench_lingbot_v2_whole.json

# ---- Matrix-Game-3 (2 GPUs: single-process interactive path has an upstream device bug)
for m in efficiency quality; do
  run bench_mg3_${m}_clip env MG3_CKPT_DIR=$MODELS/Matrix-Game-3.0 MG3_DEMO_MODE=$m MG3_DEMO_NUM_GPUS=2 \
    bash run_one.sh bench_mg3_${m}_clip mg3 mg3 0,1 8414 sessions_specs/bench_mg3_${m}_clip.json
done

echo "BENCH ALL DONE ($(date +%H:%M:%S))"
