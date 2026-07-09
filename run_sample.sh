#!/usr/bin/env bash
# usage: run_sample.sh <sample> <gpuA> <gpuB> <gpuC> <gpuD>   e.g. run_sample.sh demo_43 0 1 2 3
# Generates all 21 videos for one dataset sample on 4 GPUs using known-good configs.
# Phase A: four parallel single-GPU queues. Phase B: MG3 (2-GPU x2 parallel), then lingbot large whole (4-GPU).
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
export SAMPLE="$1"
GA="$2"; GB="$3"; GC="$4"; GD="$5"
[ -z "$SAMPLE" ] || [ -z "$GD" ] && { echo "usage: run_sample.sh <sample> <gpuA> <gpuB> <gpuC> <gpuD>"; exit 1; }
S="$SAMPLE"
PB=$((8200 + 20 * GA))   # port base, disjoint per GPU set
MODELS=/mnt/nfs/home/yumingl/models

run() { echo "QUEUE[$S] starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "QUEUE[$S] finished $1 rc=$? ($(date +%H:%M:%S))"; }

gpuA_queue() {
  run hy_bi env HY_DEMO_MODEL_VARIANT=bi \
    bash run_one.sh hy_bi hy hy $GA $((PB+0)) sessions_specs/hy_bi.json
}

gpuB_queue() {
  run hy_ar env HY_DEMO_MODEL_VARIANT=ar \
    bash run_one.sh hy_ar hy hy $GB $((PB+1)) sessions_specs/hy_ar.json
  run dreamx_cam_clip env DREAMX_DEMO_MODEL_VARIANT=cam \
    bash run_one.sh dreamx_cam_clip dreamx dreamx $GB $((PB+2)) sessions_specs/dreamx_cam_clip.json
  run hy_ar_distill env HY_DEMO_MODEL_VARIANT=ar_distill \
    bash run_one.sh hy_ar_distill hy hy $GB $((PB+3)) sessions_specs/hy_ar_distill.json
  run infworld \
    bash run_one.sh infworld infworld infworld $GB $((PB+4)) sessions_specs/infworld.json
  run dreamx_ar_clip env DREAMX_DEMO_MODEL_VARIANT=ar \
    bash run_one.sh dreamx_ar_clip dreamx dreamx $GB $((PB+5)) sessions_specs/dreamx_ar_clip.json
  run dreamx_ar_whole env DREAMX_DEMO_MODEL_VARIANT=ar DREAMX_DEMO_NUM_OUTPUT_FRAMES=243 \
    bash run_one.sh dreamx_ar_whole dreamx dreamx $GB $((PB+6)) sessions_specs/dreamx_ar_whole.json
}

gpuC_queue() {
  run hy_ar_rl env HY_DEMO_MODEL_VARIANT=ar_rl \
    bash run_one.sh hy_ar_rl hy hy $GC $((PB+7)) sessions_specs/hy_ar_rl.json
  run dreamx_cam_whole env PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True DREAMX_DEMO_MODEL_VARIANT=cam DREAMX_DEMO_VIDEO_LENGTH=961 DREAMX_DEMO_GPU_MEMORY_MODE=model_cpu_offload \
    bash run_one.sh dreamx_cam_whole dreamx dreamx $GC $((PB+8)) sessions_specs/dreamx_cam_whole.json
}

gpuD_queue() {
  run sana_wm env SANA_WM_ROOT=$MODELS/SANA-WM_bidirectional SANA_STAGE1_TEXT_ENCODER_ROOT=$MODELS/gemma-2-2b-it SANA_DEMO_NUM_FRAMES=961 SANA_DEMO_WARMUP=0 SANA_DEMO_OVERLAY=0 \
    bash run_one.sh sana_wm sana sana $GD $((PB+9)) sessions_specs/sana.json
  run lingbot_small_clip env LINGBOT_WORLD_CKPT_DIR=$MODELS/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=small LINGBOT_DEMO_WARMUP=0 \
    bash run_one.sh lingbot_small_clip lingbot lingbot $GD $((PB+10)) sessions_specs/lingbot_small_clip.json
  run lingbot_small_whole env LINGBOT_WORLD_CKPT_DIR=$MODELS/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=small LINGBOT_DEMO_WARMUP=0 LINGBOT_DEMO_LOCAL_ATTN_SIZE=24 \
    bash run_one.sh lingbot_small_whole lingbot lingbot $GD $((PB+11)) sessions_specs/lingbot_small_whole.json
  run lingbot_large_clip env LINGBOT_WORLD_CKPT_DIR=$MODELS/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=large LINGBOT_DEMO_WARMUP=0 \
    bash run_one.sh lingbot_large_clip lingbot lingbot $GD $((PB+12)) sessions_specs/lingbot_large_clip.json
}

echo "QUEUE[$S] phase A start on GPUs $GA,$GB,$GC,$GD ($(date +%H:%M:%S))"
gpuA_queue & P1=$!
gpuB_queue & P2=$!
gpuC_queue & P3=$!
gpuD_queue & P4=$!
wait $P1 $P2 $P3 $P4
echo "QUEUE[$S] phase A done ($(date +%H:%M:%S))"

echo "QUEUE[$S] phase B start ($(date +%H:%M:%S))"
( run mg3_efficiency env MG3_CKPT_DIR=$MODELS/Matrix-Game-3.0 MG3_DEMO_MODE=efficiency MG3_DEMO_NUM_GPUS=2 \
    bash run_one.sh mg3_efficiency mg3 mg3 $GA,$GB $((PB+13)) sessions_specs/mg3_efficiency.json ) & B1=$!
( run mg3_quality env MG3_CKPT_DIR=$MODELS/Matrix-Game-3.0 MG3_DEMO_MODE=quality MG3_DEMO_NUM_GPUS=2 \
    bash run_one.sh mg3_quality mg3 mg3 $GC,$GD $((PB+14)) sessions_specs/mg3_quality.json ) & B2=$!
wait $B1 $B2
run lingbot_large_whole env LINGBOT_WORLD_CKPT_DIR=$MODELS/lingbot-world-base-cam LINGBOT_DEMO_MODEL_SIZE=large LINGBOT_DEMO_WARMUP=0 LINGBOT_DEMO_NUM_GPUS=4 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  bash run_one.sh lingbot_large_whole lingbot lingbot $GA,$GB,$GC,$GD $((PB+15)) sessions_specs/lingbot_large_whole.json
echo "QUEUE[$S] ALL DONE ($(date +%H:%M:%S))"
