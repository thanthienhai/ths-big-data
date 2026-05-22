from __future__ import annotations

from pathlib import Path
from typing import Any


def write_summary(output_dir: Path, dataset_summary: dict[str, Any], eval_status: dict[str, Any], metrics: list[dict[str, Any]], config: dict[str, Any]) -> None:
    lines = [
        "# LoRA Fine-Tuning Run Summary",
        "",
        "## Dataset",
        f"- Dataset: `{dataset_summary.get('dataset_id')}`",
        f"- Sample fraction: `{dataset_summary.get('sample_fraction')}`",
        f"- Split sizes: `{dataset_summary.get('split_sizes')}`",
        f"- Leakage control: `{dataset_summary.get('leakage_control')}`",
        "",
        "## Training",
        f"- Base model: `{config.get('model', {}).get('base_model_id')}`",
        f"- Fine-tuning type: `lora`",
        f"- Smoke test: `{config.get('experiment', {}).get('smoke_test')}`",
        "",
        "## Evaluation Status",
    ]
    for name, status in eval_status.items():
        lines.append(f"- `{name}`: {status}")
    lines.extend(["", "## Metrics", ""])
    if metrics:
        headers = sorted({key for row in metrics for key in row})
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in metrics:
            lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    lines.extend(
        [
            "",
            "## Interpretation Cautions",
            "- The default run uses only 10% of the dataset; do not report it as a full-dataset result.",
            "- Automatic metrics support comparison but do not by themselves prove legal correctness.",
            "- Optional baseline failures are recorded and should be disclosed in the paper if used.",
        ]
    )
    (output_dir / "run_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
