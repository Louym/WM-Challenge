#!/usr/bin/env bash
# usage: run_one.sh <run_name> <model_key> <conda_env> <gpu> <port> <sessions_json>
# Extra model-specific env vars are inherited from the caller's environment.
set -o pipefail

RUN_NAME="$1"; MODEL_KEY="$2"; CONDA_ENV="$3"; GPU="$4"; PORT="$5"; SESSIONS_JSON="$6"

OUT_DIR="/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo_sample29_outputs"
DEMO_DIR="/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/demo"
DATASET="/mnt/nfs/home/yumingl/workspace/PI/WM/baselines/SANA_WM_dev/playground/dataset/dataset"
CONDA_BIN="/mnt/nfs/home/yumingl/software/anaconda3/bin/conda"
BASE_PY="/mnt/nfs/home/yumingl/software/anaconda3/bin/python"

mkdir -p "$OUT_DIR/logs" "$OUT_DIR/videos"
SERVER_LOG="$OUT_DIR/logs/${RUN_NAME}.server.log"
DRIVER_LOG="$OUT_DIR/logs/${RUN_NAME}.driver.log"

export WM_DEMO_GPU="$GPU"
export WM_DEMO_PORT="$PORT"
export WM_DEMO_HOST="127.0.0.1"

eval "$("$CONDA_BIN" shell.bash hook)"
conda activate "$CONDA_ENV"

setsid bash "$DEMO_DIR/run_demo.sh" "$MODEL_KEY" > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!
echo "[run_one] $RUN_NAME: server pid $SERVER_PID (env=$CONDA_ENV gpu=$GPU port=$PORT)"

cleanup() {
  if kill -0 "$SERVER_PID" 2>/dev/null; then
    kill -- -"$SERVER_PID" 2>/dev/null || kill "$SERVER_PID" 2>/dev/null
    sleep 5
    kill -9 -- -"$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

"$BASE_PY" "$OUT_DIR/driver.py" \
  --base "http://127.0.0.1:$PORT" \
  --image "$DATASET/demo_29.png" \
  --prompt-file "$DATASET/demo_29.txt" \
  --sessions "$SESSIONS_JSON" \
  --sessions-dir "$DEMO_DIR/sessions" \
  --out-dir "$OUT_DIR/videos" \
  > "$DRIVER_LOG" 2>&1
RC=$?

echo "[run_one] $RUN_NAME: driver exit $RC"
exit $RC
