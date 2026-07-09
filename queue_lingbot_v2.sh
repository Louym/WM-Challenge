#!/usr/bin/env bash
# LingBot-World-v2 (causal-fast): 3 samples x (clip-by-clip + whole-video), one GPU per sample, one server per sample.
# usage: queue_lingbot_v2.sh <gpuA> <gpuB> <gpuC>
cd /mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs
GA="$1"; GB="$2"; GC="$3"
[ -z "$GC" ] && { echo "usage: queue_lingbot_v2.sh <gpuA> <gpuB> <gpuC>"; exit 1; }

run() { echo "QUEUE[v2] starting $1 ($(date +%H:%M:%S))"; "${@:2}"; echo "QUEUE[v2] finished $1 rc=$? ($(date +%H:%M:%S))"; }

one_sample() {
  local sample=$1 gpu=$2 port=$3
  run "${sample}" env SAMPLE=$sample \
    WM_DEMO_ADAPTER=ext_adapters.lingbot_world_v2:LingBotWorldV2Adapter \
    PYTHONPATH=/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs \
    LINGBOT_WORLD_ROOT=/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/lingbot-world-v2 \
    LINGBOT_WORLD_CKPT_DIR=/mnt/nfs/home/yumingl/models/lingbot-world-v2-14b-causal-fast \
    LINGBOT_DEMO_MODEL_SIZE=small LINGBOT_DEMO_LOCAL_ATTN_SIZE=18 LINGBOT_DEMO_SINK_SIZE=6 LINGBOT_DEMO_WARMUP=0 \
    bash run_one.sh lingbot_v2_fast lingbot lingbot $gpu $port sessions_specs/lingbot_v2_fast.json
}

one_sample demo_29 $GA 8300 & P1=$!
one_sample demo_42 $GB 8310 & P2=$!
one_sample demo_79 $GC 8320 & P3=$!
wait $P1 $P2 $P3
echo "QUEUE[v2] ALL DONE ($(date +%H:%M:%S))"
