## Why

The current project has a research paper direction for full fine-tuning Qwen3-4B on Vietnamese legal text, but it does not yet have a reproducible training and evaluation program. This change is needed so the experiment can be run end-to-end from a single shell script, using only 10% of the referenced dataset initially, and produce comparable results against baseline models.

The immediate research need is to move from paper-level methodology to executable evidence: dataset loading, model weight download, dependency installation, full fine-tuning, baseline evaluation, metric reporting, and saved artifacts must be automated so results can be reproduced and later inserted into the paper.

## What Changes

- Add an end-to-end training and evaluation pipeline for full fine-tuning Qwen3-4B on Vietnamese legal data.
- Add a single shell entrypoint that installs dependencies, prepares the environment, downloads dataset/model weights, trains on 10% of the dataset, evaluates the fine-tuned model, evaluates baseline models, and writes results.
- Add dataset preparation logic that samples 10% of the referenced legal dataset with deterministic seeding and creates train/validation/test splits.
- Add full fine-tuning configuration for Qwen3-4B, distinct from LoRA/QLoRA or RAG-based approaches.
- Add baseline evaluation for the original Qwen3-4B model and selected comparable open-source models where feasible under local/GPU constraints.
- Add metric reporting for automatic and research-facing evaluation, including Exact Match/F1, ROUGE-L, BERTScore when available, latency, memory usage, and structured result summaries.
- Add experiment outputs suitable for paper writing, including JSON/CSV metrics, generated predictions, run metadata, and logs.
- Exclude RAG, vector search, retrieval pipelines, reranking, and external document lookup from this change.

## Capabilities

### New Capabilities
- `full-finetune-training-pipeline`: Covers one-command setup, dataset preparation, full fine-tuning Qwen3-4B on 10% of the legal dataset, baseline evaluation, metric computation, and reproducible experiment output generation.

### Modified Capabilities

## Impact

- Adds training/evaluation scripts, shell orchestration, configuration files, and experiment output conventions under the project workspace.
- Introduces Python ML dependencies such as `torch`, `transformers`, `datasets`, `accelerate`, `evaluate`, `rouge-score`, `bert-score`, `scikit-learn`, and optional experiment utilities.
- Requires GPU-capable execution for realistic full fine-tuning of Qwen3-4B; CPU execution may be limited to smoke tests or dataset preparation.
- Creates local artifact directories for downloaded models, processed datasets, checkpoints, logs, predictions, and metric reports.
- Does not change the paper DOCX files directly, but produces evidence that can later be incorporated into the paper.
