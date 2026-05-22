# Full Fine-Tuning Pipeline

This directory contains the one-command experiment pipeline for full fine-tuning Qwen3-4B on Vietnamese legal response generation.

## Quick Start

Run a smoke test first:

```bash
bash train/run_full_finetune.sh SMOKE_TEST=1
```

Run the default 10% full fine-tuning experiment:

```bash
bash train/run_full_finetune.sh
```

The default run uses `train/configs/full_finetune_10pct.yaml`, samples 10% of the configured dataset with a fixed seed, trains Qwen3-4B with full-parameter optimization, evaluates baselines, and writes outputs to `train/outputs/`.

## Prerequisites

- Python 3.10 or newer.
- CUDA-capable GPU for the default full fine-tuning run.
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
- `eval_predictions/*.jsonl`
- `metrics.json`
- `metrics.csv`
- `run_summary.md`

## Baselines

The required baseline is the original configured Qwen3-4B model. Optional baselines can include Qwen2.5, Gemma, Phi, Llama, Mistral, PhoGPT, VinaLLaMA, or SeaLLM. Optional baseline failures are recorded instead of aborting the whole experiment.

## Rerunning Evaluation

Set `evaluation.rerun_only: true` and `evaluation.checkpoint_path` in a config file to reuse an existing checkpoint without retraining.

## Scope

This pipeline is for full fine-tuning only. It does not implement LoRA, QLoRA, PEFT adapters, RAG, vector search, reranking, or external document lookup.
