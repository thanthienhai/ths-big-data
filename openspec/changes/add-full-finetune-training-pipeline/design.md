## Context

The project now focuses on full fine-tuning Qwen3-4B for Vietnamese legal response generation. The paper already defines the research direction, but the repository lacks executable code that can produce reproducible evidence: model checkpoints, baseline comparisons, predictions, metrics, and logs.

The requested implementation must be usable by running one shell file. That entrypoint must handle environment preparation, dependency installation, dataset/model downloads, deterministic 10% dataset sampling, full fine-tuning, baseline evaluation, and final result aggregation. The current `train/` directory is empty, so the change can introduce a clean training package without migration from existing training code.

The main stakeholder is the researcher writing the paper. The output must support academic claims about whether full fine-tuning Qwen3-4B improves Vietnamese legal response quality compared with baseline models. The pipeline must therefore record enough metadata to distinguish hypothesis, method, and measured result.

## Goals / Non-Goals

**Goals:**
- Provide a single shell entrypoint that can run the complete experiment from setup to metrics.
- Train Qwen3-4B with full fine-tuning, not LoRA, QLoRA, adapters, retrieval augmentation, or reranking.
- Use exactly 10% of the referenced legal dataset by default, selected deterministically by seed.
- Create train/validation/test splits with leakage control based on source metadata when available.
- Evaluate the fine-tuned Qwen3-4B checkpoint and baseline models with the same test set, prompt template, decoding parameters, and metric code.
- Save all experiment artifacts needed for later paper writing: configs, logs, predictions, metrics, run metadata, and model checkpoint locations.
- Make resource constraints explicit so the script fails early with actionable messages when full fine-tuning is not feasible on the current machine.

**Non-Goals:**
- No RAG, vector database, document retrieval, reranking, or external document lookup.
- No LoRA, QLoRA, PEFT adapters, preference optimization, RLHF, DPO, or continued pre-training.
- No guarantee that a 4B full fine-tune fits on consumer hardware; the pipeline should expose requirements and fail clearly when resources are insufficient.
- No fabrication of benchmark scores. Result files may contain empty or failed baseline entries when a model cannot run under local constraints.
- No direct modification of paper DOCX files; this change only generates experimental evidence.

## Decisions

### Decision 1: Use a single orchestration shell script with Python subcommands

The implementation will add `train/run_full_finetune.sh` as the user-facing entrypoint. Internally it will call Python scripts or modules for setup, dataset preparation, training, baseline inference, evaluation, and report generation.

Rationale: a shell entrypoint matches the user's requirement: "chỉ cần chạy 1 file .sh là xong". Python remains responsible for ML logic where structured configs, dataset APIs, and metric calculations are easier to test.

Alternatives considered:
- A Python-only CLI: simpler on Windows, but does not satisfy the one `.sh` requirement.
- A notebook: convenient for experiments but weak for reproducibility and automation.

### Decision 2: Store configuration in YAML and write resolved config to outputs

The pipeline will include a default config such as `train/configs/full_finetune_10pct.yaml`. The shell script can accept environment variable overrides for model IDs, dataset ID, output directory, max steps, sample fraction, baseline list, and smoke-test mode. At runtime, the resolved config must be saved with the result artifacts.

Rationale: YAML keeps experiment settings visible for the paper and makes repeated runs comparable.

Alternatives considered:
- Hard-coded constants: easier initially but weak for research reproducibility.
- Many command-line flags only: flexible but error-prone for long experiment definitions.

### Decision 3: Default dataset sampling is deterministic 10%

Dataset preparation will load the referenced Vietnamese legal dataset, shuffle with a fixed seed, take 10% by default, and then create train/validation/test splits. If source document identifiers exist, splitting should group by source to reduce leakage. If source identifiers are unavailable, the script must record that limitation in run metadata.

Rationale: the user's current requirement is to train only 10% of the dataset, while still leaving a path to full-data experiments later.

Alternatives considered:
- First 10% of records: not robust because dataset order may encode source or difficulty bias.
- Random 10% without fixed seed: not reproducible.

### Decision 4: Implement true full fine-tuning with Hugging Face Trainer/Accelerate

Training will load Qwen3-4B in trainable precision, enable gradient checkpointing where supported, and update all model parameters. The training script must explicitly assert that PEFT/adapters are not active. It should support distributed execution through `accelerate` if configured, but the first implementation can run single-node.

Rationale: the paper scope is full fine-tuning. PEFT methods would change the research claim.

Alternatives considered:
- QLoRA/LoRA: more practical on limited VRAM, but outside the revised paper scope.
- Freezing lower layers: cheaper but no longer full fine-tuning.

### Decision 5: Baselines use the same prompt, decoding, and metrics

The evaluation pipeline will compare the fine-tuned Qwen3-4B checkpoint with baseline models such as Qwen3-4B original/instruct and optionally Qwen2.5, Gemma, Phi, Llama, Mistral, PhoGPT, VinaLLaMA, or SeaLLM when configured and accessible. All evaluated models must use the same test split, prompt template, max new tokens, temperature, top-p, and metric implementation.

Rationale: baseline comparisons are only meaningful when evaluation conditions are controlled.

Alternatives considered:
- Manual baseline outputs: faster but not reproducible.
- Different prompt per model: may improve individual model quality but weakens fair comparison.

### Decision 6: Generate machine-readable and paper-ready outputs

Each run will create a timestamped output directory containing:
- `resolved_config.yaml`
- `dataset_summary.json`
- `train_log.jsonl`
- `eval_predictions/<model>.jsonl`
- `metrics.json`
- `metrics.csv`
- `run_summary.md`
- checkpoint directory or a pointer to the checkpoint

Rationale: JSON/CSV supports later plotting and statistical analysis; Markdown supports quick paper integration.

## Risks / Trade-offs

- Full fine-tuning Qwen3-4B may exceed local GPU memory → The script must check CUDA availability and print estimated requirements; provide smoke-test mode for validating code paths without completing a full run.
- Some baseline models may require gated access or too much VRAM → Baseline failures must be recorded per model without aborting the whole experiment unless the required Qwen baseline fails.
- Dataset schema may differ from assumptions → Dataset preparation must inspect available columns and map them through a configurable schema section.
- Legal correctness cannot be fully captured by automatic metrics → The pipeline must save predictions for later human/legal review and include automatic metrics as supporting evidence, not final proof.
- Training on 10% of the dataset may understate final performance → Run metadata must record `sample_fraction=0.10`, and result summaries must avoid claims about full-data performance.
- Running dependency installation from a shell script can alter the environment → Use a project-local virtual environment by default and pin major dependency versions in a requirements file.

## Migration Plan

1. Add the training package under `train/` with a one-command shell entrypoint.
2. Add config, requirements, and Python scripts without changing existing paper files.
3. Validate the pipeline first in smoke-test mode with a tiny subset and short max steps.
4. Run the default 10% experiment on a GPU-capable environment.
5. If the pipeline fails due to hardware limits, keep generated logs and metadata for diagnosis; no repository rollback is needed because changes are additive.

Rollback is simple: remove the new `train/` scripts/configs and generated output directories. No persistent data migration is involved.

## Open Questions

- Which exact Hugging Face model ID should be the default starting point: `Qwen/Qwen3-4B-Base`, `Qwen/Qwen3-4B`, or `Qwen/Qwen3-4B-Instruct`?
- Which baseline models are locally feasible on the target GPU, and which require gated Hugging Face access?
- What is the exact schema of the referenced legal dataset in the local environment, especially the columns for question, context, answer, and source metadata?
- Should the first implementation include optional multi-GPU `accelerate` config, or only a single-GPU path plus clear documentation?
