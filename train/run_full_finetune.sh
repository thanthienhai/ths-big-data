#!/usr/bin/env bash
set -euo pipefail

for arg in "$@"; do
  if [[ "$arg" == *=* ]]; then
    export "$arg"
  fi
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

SMOKE_TEST="${SMOKE_TEST:-0}"
CONFIG_PATH="${CONFIG_PATH:-}"
OUTPUT_ROOT="${OUTPUT_ROOT:-}"
BASELINES="${BASELINES:-}"
SKIP_INSTALL="${SKIP_INSTALL:-0}"
PYTHON_BIN="${PYTHON_BIN:-python}"
VENV_DIR="${VENV_DIR:-$REPO_ROOT/.venv-full-finetune}"
# Hard configuration for the target training machine: 2x NVIDIA H200.
USE_ACCELERATE="1"
ACCELERATE_CONFIG="$REPO_ROOT/train/configs/accelerate_2xh200.yaml"
NUM_GPUS="2"
CUDA_VISIBLE_DEVICES="4,5"
export CUDA_VISIBLE_DEVICES
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
export RUN_ID

if [[ -z "$CONFIG_PATH" ]]; then
  if [[ "$SMOKE_TEST" == "1" || "$SMOKE_TEST" == "true" ]]; then
    CONFIG_PATH="$REPO_ROOT/train/configs/smoke_test.yaml"
  else
    CONFIG_PATH="$REPO_ROOT/train/configs/full_finetune_10pct.yaml"
  fi
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  for candidate in python3 python.exe py; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PYTHON_BIN="$candidate"
      break
    fi
  done
fi

PYTHON_CMD=("$PYTHON_BIN")
if [[ "$PYTHON_BIN" == "py" ]]; then
  PYTHON_CMD=(py -3)
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python runtime not found. Set PYTHON_BIN=/path/to/python and rerun." >&2
  exit 2
fi

if [[ "$SKIP_INSTALL" != "1" ]]; then
  if [[ ! -d "$VENV_DIR" ]]; then
    "${PYTHON_CMD[@]}" -m venv "$VENV_DIR"
  fi
  # shellcheck disable=SC1091
  source "$VENV_DIR/Scripts/activate" 2>/dev/null || source "$VENV_DIR/bin/activate"
  python -m pip install --upgrade pip
  python -m pip install -r "$REPO_ROOT/train/requirements.txt"
else
  echo "Skipping dependency installation because SKIP_INSTALL=1"
fi

EXTRA_ARGS=()
if [[ -n "$OUTPUT_ROOT" ]]; then
  EXTRA_ARGS+=(--output-root "$OUTPUT_ROOT")
fi
if [[ -n "$BASELINES" ]]; then
  EXTRA_ARGS+=(--baselines "$BASELINES")
fi
if [[ "$SMOKE_TEST" == "1" || "$SMOKE_TEST" == "true" ]]; then
  EXTRA_ARGS+=(--smoke-test)
fi

if [[ "$SMOKE_TEST" == "1" || "$SMOKE_TEST" == "true" ]]; then
  USE_ACCELERATE="0"
fi

if [[ "$USE_ACCELERATE" == "1" ]]; then
  "${PYTHON_CMD[@]}" -m accelerate.commands.launch \
    --config_file "$ACCELERATE_CONFIG" \
    --num_processes "$NUM_GPUS" \
    -m train.pipeline --config "$CONFIG_PATH" "${EXTRA_ARGS[@]}"
else
  "${PYTHON_CMD[@]}" -m train.pipeline --config "$CONFIG_PATH" "${EXTRA_ARGS[@]}"
fi
