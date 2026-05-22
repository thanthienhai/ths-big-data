from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .data import prepare_dataset
from .evaluate_models import evaluate_all
from .metrics import compute_metrics
from .report import write_summary
from .train_model import train_full_model
from .utils import (
    apply_overrides,
    check_runtime,
    collect_runtime_metadata,
    destroy_distributed,
    distributed_barrier,
    is_main_process,
    load_yaml,
    seed_everything,
    timestamp,
    wait_for_files,
    write_json,
    write_yaml,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run full fine-tuning and baseline evaluation.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-root")
    parser.add_argument("--baselines", help="Comma-separated optional baseline model IDs.")
    parser.add_argument("--smoke-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = apply_overrides(load_yaml(args.config), args)
    seed_everything(int(config.get("experiment", {}).get("seed", 42)))
    output_root = Path(config.get("experiment", {}).get("output_root", "train/outputs"))
    run_id = os.environ.get("RUN_ID") or timestamp()
    output_dir = output_root / f"{config.get('experiment', {}).get('name', 'run')}_{run_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    if is_main_process():
        write_yaml(config, output_dir / "resolved_config.yaml")
        write_json(collect_runtime_metadata(config, output_dir), output_dir / "run_metadata.json")
    distributed_barrier()

    errors = check_runtime(config)
    if errors:
        if is_main_process():
            write_json({"errors": errors}, output_dir / "runtime_errors.json")
            for error in errors:
                print(f"Runtime error: {error}", file=sys.stderr)
        return 2

    dataset_summary = {}
    eval_status = {}
    metrics = []
    try:
        if is_main_process():
            dataset_summary = prepare_dataset(config, output_dir)
        else:
            wait_for_files(
                [
                    output_dir / "dataset_summary.json",
                    output_dir / "data" / "train.jsonl",
                    output_dir / "data" / "validation.jsonl",
                    output_dir / "data" / "test.jsonl",
                ]
            )
        distributed_barrier()
        if config.get("evaluation", {}).get("rerun_only"):
            checkpoint_dir = Path(config.get("evaluation", {}).get("checkpoint_path", ""))
            if not checkpoint_dir.exists():
                raise RuntimeError("evaluation.rerun_only=true requires evaluation.checkpoint_path to exist.")
        else:
            checkpoint_dir = train_full_model(config, output_dir)
        distributed_barrier()
        if not is_main_process():
            destroy_distributed()
            return 0
        if not dataset_summary:
            dataset_summary_path = output_dir / "dataset_summary.json"
            if dataset_summary_path.exists():
                import json

                dataset_summary = json.loads(dataset_summary_path.read_text(encoding="utf-8"))
        eval_status = evaluate_all(config, output_dir, checkpoint_dir)
        metrics = compute_metrics(output_dir, config, eval_status)
        write_summary(output_dir, dataset_summary, eval_status, metrics, config)
    except Exception as exc:
        if is_main_process():
            write_json({"error": str(exc)}, output_dir / "failure.json")
            if dataset_summary:
                write_summary(output_dir, dataset_summary, eval_status, metrics, config)
        destroy_distributed()
        raise

    if is_main_process():
        print(f"Run complete: {output_dir}")
    destroy_distributed()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
