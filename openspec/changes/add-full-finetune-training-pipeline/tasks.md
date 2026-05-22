## 1. Project Structure and Entrypoint

- [x] 1.1 Create the `train/` package structure for configs, scripts/modules, requirements, and generated outputs.
- [x] 1.2 Add `train/run_full_finetune.sh` as the single user-facing entrypoint runnable from the repository root.
- [x] 1.3 Add shell logic to create/use a project-local virtual environment and install pinned Python dependencies.
- [x] 1.4 Add shell argument or environment-variable support for config path, output directory, smoke-test mode, and baseline selection.
- [x] 1.5 Add early runtime checks for Python availability, CUDA/GPU availability, disk space, Hugging Face authentication hints, and required command-line tools.

## 2. Configuration and Metadata

- [x] 2.1 Add a default YAML config for the 10% Qwen3-4B full fine-tuning experiment.
- [x] 2.2 Include config fields for dataset ID, sample fraction, seed, split ratios, schema mapping, model IDs, training hyperparameters, decoding parameters, metrics, and baseline list.
- [x] 2.3 Implement config loading and environment-variable overrides in Python.
- [x] 2.4 Write the resolved runtime config to each timestamped output directory before dataset preparation starts.
- [x] 2.5 Add run metadata capture for git status/commit when available, host info, CUDA info, package versions, model IDs, dataset ID, and output paths.

## 3. Dataset Preparation

- [x] 3.1 Implement dataset loading from the configured Hugging Face dataset.
- [x] 3.2 Implement configurable column mapping for question, legal context, answer, and source metadata.
- [x] 3.3 Implement deterministic 10% sampling using the configured seed.
- [x] 3.4 Implement train/validation/test splitting with source-level grouping when source identifiers are available.
- [x] 3.5 Record leakage-control limitations when grouped splitting is unavailable.
- [x] 3.6 Implement prompt formatting for instruction tuning using fixed `instruction`, `question`, `legal_context`, and `answer` fields.
- [x] 3.7 Save processed dataset splits and `dataset_summary.json` under the run output directory.

## 4. Full Fine-Tuning Implementation

- [x] 4.1 Implement Qwen3-4B model and tokenizer loading for trainable full fine-tuning.
- [x] 4.2 Implement tokenization that masks prompt tokens and computes loss only on answer tokens.
- [x] 4.3 Add assertions that PEFT, LoRA, QLoRA, adapters, and frozen-layer training are not active.
- [x] 4.4 Configure Hugging Face Trainer or Accelerate for full-parameter optimization with gradient checkpointing where supported.
- [x] 4.5 Implement training logs in JSONL format with loss, learning rate, epoch/step, throughput, and memory usage where available.
- [x] 4.6 Save checkpoint, tokenizer, training state, and checkpoint pointer metadata after successful training.
- [x] 4.7 Add failure handling that preserves partial logs and metadata when training fails.

## 5. Baseline and Fine-Tuned Evaluation

- [x] 5.1 Implement shared generation code for all evaluated models using the same prompt template and decoding parameters.
- [x] 5.2 Evaluate the original configured Qwen3-4B baseline on the fixed test split.
- [x] 5.3 Evaluate the fine-tuned Qwen3-4B checkpoint on the fixed test split.
- [x] 5.4 Implement optional baseline evaluation for configured models such as Qwen2.5, Gemma, Phi, Llama, Mistral, PhoGPT, VinaLLaMA, or SeaLLM.
- [x] 5.5 Record optional baseline load/evaluation failures without aborting the entire experiment.
- [x] 5.6 Save per-model prediction JSONL files with prompt, reference answer, generated answer, source metadata, latency, and failure status.

## 6. Metrics and Reporting

- [x] 6.1 Implement Exact Match and token-level F1 metrics for generated answers.
- [x] 6.2 Implement ROUGE-L scoring.
- [x] 6.3 Implement optional BERTScore scoring when dependencies and hardware allow it.
- [x] 6.4 Record latency, throughput, and GPU memory usage where available.
- [x] 6.5 Write aggregate `metrics.json` and `metrics.csv` comparing fine-tuned and baseline models.
- [x] 6.6 Generate `run_summary.md` with dataset summary, model list, training settings, metric table, baseline failures, and interpretation cautions.

## 7. Smoke Test and Validation

- [x] 7.1 Add smoke-test config or mode using a tiny dataset slice, tiny model or minimal train steps, and reduced generation limits.
- [x] 7.2 Ensure `bash train/run_full_finetune.sh SMOKE_TEST=1` or an equivalent documented invocation validates setup, dataset flow, training loop wiring, evaluation wiring, and output generation.
- [x] 7.3 Add lightweight tests or validation commands for config loading, dataset formatting, metric functions, and output file creation.
- [x] 7.4 Run the smoke test and verify it creates resolved config, dataset summary, prediction files, metrics files, and run summary.

## 8. Documentation and Reproducibility

- [x] 8.1 Add a README or usage section under `train/` explaining prerequisites, one-command execution, GPU expectations, output layout, and smoke-test usage.
- [x] 8.2 Document required Hugging Face authentication and gated-model behavior.
- [x] 8.3 Document that the default experiment uses 10% of the dataset and that scores must not be reported as full-dataset results.
- [x] 8.4 Document how to change baseline models and how to rerun evaluation without retraining when a checkpoint already exists.
- [x] 8.5 Verify the implementation satisfies every scenario in `specs/full-finetune-training-pipeline/spec.md`.
