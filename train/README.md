# LoRA Fine-Tuning Pipeline

This directory contains the one-command experiment pipeline for LoRA fine-tuning Qwen3-4B on Vietnamese legal response generation.

## Quick Start

Run a smoke test first:

```bash
bash train/run_full_finetune.sh SMOKE_TEST=1
```

Run the default 10% LoRA fine-tuning experiment:

```bash
bash train/run_full_finetune.sh
```

The default run uses `train/configs/full_finetune_10pct.yaml`, samples 10% of the configured dataset with a fixed seed, trains LoRA adapters for Qwen3-4B, evaluates baselines, and writes outputs to `train/outputs/`.

## GPU Configuration

GPU selection is controlled by the shell entrypoint and the Accelerate config:

- Shell/runtime: `train/run_full_finetune.sh`
- Accelerate 2-GPU config: `train/configs/accelerate_2xh200.yaml`
- Training and LoRA settings: `train/configs/full_finetune_10pct.yaml`

For two H200 GPUs, run:

```bash
bash train/run_full_finetune.sh
```

The shell script hard-codes the target GPU runtime:

```text
CUDA_VISIBLE_DEVICES=0,1
NUM_GPUS=2
ACCELERATE_CONFIG=train/configs/accelerate_2xh200.yaml
mixed_precision=bf16
```

In `train/configs/full_finetune_10pct.yaml`, the default per-GPU batch is `per_device_train_batch_size: 4` and `gradient_accumulation_steps: 2`. With 2 GPUs, the effective batch size is:

```text
2 GPUs * batch 4 * grad accumulation 2 = 16 samples/update
```

If H200 memory allows, increase `per_device_train_batch_size` first. If training is unstable or out of memory, reduce it.

## Prerequisites

- Python 3.10 or newer.
- CUDA-capable GPU for the default LoRA fine-tuning run.
- Sufficient disk for model weights, dataset cache, checkpoints, and predictions.
- Hugging Face access for configured models. Set `HF_TOKEN` when using gated models or when download rate limits are a concern.

The script creates a local virtual environment at `.venv-full-finetune` and installs packages from `train/requirements.txt`. To use an existing environment:

```bash
bash train/run_full_finetune.sh SKIP_INSTALL=1
```

## Configuration

Useful overrides:

```bash
bash train/run_full_finetune.sh CONFIG_PATH=train/configs/smoke_test.yaml
bash train/run_full_finetune.sh OUTPUT_ROOT=train/outputs/custom
bash train/run_full_finetune.sh BASELINES=Qwen/Qwen2.5-3B-Instruct,microsoft/Phi-3.5-mini-instruct
```

The default experiment intentionally uses only 10% of the dataset. Scores from this run must be reported as 10%-data results, not full-dataset results.

## Outputs

Each run creates a timestamped directory with:

- `resolved_config.yaml`
- `run_metadata.json`
- `dataset_summary.json`
- `data/train.jsonl`, `data/validation.jsonl`, `data/test.jsonl`
- `train_log.jsonl`
- `checkpoint_metadata.json`
- `checkpoints/...` containing LoRA adapter weights
- `eval_predictions/*.jsonl`
- `metrics.json`
- `metrics.csv`
- `run_summary.md`

## Baselines

The required baseline is the original configured Qwen3-4B model. Optional baselines can include Qwen2.5, Gemma, Phi, Llama, Mistral, PhoGPT, VinaLLaMA, or SeaLLM. Optional baseline failures are recorded instead of aborting the whole experiment.

## Rerunning Evaluation

Set `evaluation.rerun_only: true` and `evaluation.checkpoint_path` in a config file to reuse an existing LoRA adapter checkpoint without retraining.

## Scope

This pipeline is for LoRA fine-tuning only. It does not implement full fine-tuning, QLoRA quantized training, RAG, vector search, reranking, or external document lookup.
