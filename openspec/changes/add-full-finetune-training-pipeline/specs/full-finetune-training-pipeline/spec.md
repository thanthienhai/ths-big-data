## ADDED Requirements

### Requirement: One-command experiment execution
The system SHALL provide a single shell entrypoint that runs the full experiment workflow from dependency setup through final result reporting.

#### Scenario: Run default experiment
- **WHEN** the user runs `bash train/run_full_finetune.sh` from the repository root
- **THEN** the system installs or verifies dependencies, prepares the dataset, downloads configured model weights, runs full fine-tuning, evaluates configured baselines, computes metrics, and writes a final run summary

#### Scenario: Fail early on missing required runtime
- **WHEN** the user runs the shell entrypoint in an environment without required Python, CUDA, disk, or authentication prerequisites
- **THEN** the system stops before training and prints an actionable error describing the missing prerequisite

### Requirement: Deterministic ten-percent dataset preparation
The system SHALL prepare exactly 10% of the configured Vietnamese legal dataset by default using deterministic sampling and reproducible split metadata.

#### Scenario: Prepare default sampled dataset
- **WHEN** dataset preparation runs with default configuration
- **THEN** the system loads the configured dataset, samples 10% using a fixed seed, creates train/validation/test splits, and writes `dataset_summary.json`

#### Scenario: Record leakage-control limitation
- **WHEN** the dataset does not expose a source document identifier for grouped splitting
- **THEN** the system still creates deterministic splits and records in metadata that source-level leakage control was unavailable

### Requirement: Full fine-tuning of Qwen3-4B
The system SHALL fine-tune Qwen3-4B by updating all trainable model parameters rather than using LoRA, QLoRA, PEFT adapters, frozen layers, or retrieval-based augmentation.

#### Scenario: Verify full fine-tuning mode
- **WHEN** training starts
- **THEN** the system verifies that PEFT/adapters are disabled and that all intended model parameters are trainable before the first optimizer step

#### Scenario: Save trained checkpoint
- **WHEN** training completes successfully
- **THEN** the system saves the model checkpoint, tokenizer, training state or logs, and checkpoint path in the run metadata

### Requirement: Controlled baseline evaluation
The system SHALL evaluate the fine-tuned model and configured baseline models under the same test split, prompt template, decoding settings, and metric implementation.

#### Scenario: Evaluate required Qwen baseline
- **WHEN** evaluation runs after training
- **THEN** the system evaluates the original configured Qwen3-4B baseline and the fine-tuned checkpoint on the same test examples

#### Scenario: Continue after optional baseline failure
- **WHEN** an optional baseline model cannot be loaded because of access, memory, or dependency constraints
- **THEN** the system records that baseline as failed with a reason and continues evaluating remaining models

### Requirement: Research-grade metric reporting
The system SHALL compute and persist automatic metrics and runtime metadata suitable for comparing the full fine-tuned model against baselines.

#### Scenario: Compute comparison metrics
- **WHEN** model predictions are generated for the test split
- **THEN** the system computes configured metrics including Exact Match or token F1, ROUGE-L, optional BERTScore, latency, and memory usage where available

#### Scenario: Persist result files
- **WHEN** evaluation completes
- **THEN** the system writes `metrics.json`, `metrics.csv`, per-model prediction files, and a human-readable `run_summary.md`

### Requirement: Reproducible experiment artifacts
The system SHALL create a timestamped output directory containing all configuration, logs, metadata, predictions, metrics, and checkpoint references needed to reproduce and audit the run.

#### Scenario: Save resolved configuration
- **WHEN** the experiment starts
- **THEN** the system writes the resolved configuration, seed, model IDs, dataset ID, sample fraction, split sizes, and decoding parameters to the output directory

#### Scenario: Preserve logs for failed runs
- **WHEN** the experiment fails after creating an output directory
- **THEN** the system preserves available logs and partial metadata so the failure can be diagnosed without rerunning earlier steps

### Requirement: Smoke-test mode
The system SHALL provide a smoke-test mode that validates setup, dataset flow, model loading stubs or tiny models, training loop wiring, evaluation wiring, and output generation without requiring a full Qwen3-4B training run.

#### Scenario: Run smoke test
- **WHEN** the user runs the shell entrypoint with smoke-test mode enabled
- **THEN** the system uses a tiny subset and short training configuration to verify the end-to-end code path and writes smoke-test metrics and logs
