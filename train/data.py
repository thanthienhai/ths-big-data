from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Any

from .prompting import build_prompt
from .utils import write_json, write_jsonl


def _synthetic_rows() -> list[dict[str, Any]]:
    rows = []
    for i in range(20):
        article = 10 + i
        rows.append(
            {
                "question": f"Điều kiện pháp lý mẫu số {i} là gì?",
                "legal_context": f"Điều {article}. Chủ thể phải đáp ứng điều kiện A, B và C theo quy định mẫu.",
                "answer": f"Theo Điều {article}, chủ thể phải đáp ứng điều kiện A, B và C.",
                "source": f"synthetic-law-{i // 2}",
            }
        )
    return rows


def _load_hf_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        from datasets import DatasetDict, load_dataset
    except ImportError as exc:
        raise RuntimeError("The `datasets` package is required for non-smoke dataset loading.") from exc

    ds_cfg = config["dataset"]
    dataset = load_dataset(ds_cfg["id"], ds_cfg.get("name"))
    split = ds_cfg.get("split", "train")
    if isinstance(dataset, DatasetDict):
        data = dataset[split]
    else:
        data = dataset
    max_records = ds_cfg.get("max_records")
    if max_records:
        data = data.select(range(min(int(max_records), len(data))))
    return [dict(row) for row in data]


def _first_present(row: dict[str, Any], candidates: list[str]) -> Any:
    for key in candidates:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def _stringify_context(context: Any) -> str:
    if isinstance(context, list):
        chunks = []
        for item in context:
            if isinstance(item, dict):
                chunks.append(str(item.get("text") or item.get("content") or item))
            else:
                chunks.append(str(item))
        return "\n".join(chunks)
    if isinstance(context, dict):
        return str(context.get("text") or context.get("content") or context)
    return str(context or "")


def _derive_answer(answer: Any, context_text: str, allow_weak_labels: bool) -> tuple[str | None, bool]:
    if answer not in (None, ""):
        return str(answer), False
    if allow_weak_labels and context_text.strip():
        first_context = context_text.strip().splitlines()[0].strip()
        return first_context, True
    return None, False


def _normalize_rows(rows: list[dict[str, Any]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    schema = config["dataset"].get("schema", {})
    instruction = config["dataset"].get("instruction", "Trả lời câu hỏi dựa trên ngữ cảnh.")
    allow_weak_labels = bool(config["dataset"].get("allow_weak_labels_from_context", True))
    normalized = []
    dropped = 0
    weak_labels = 0
    for idx, row in enumerate(rows):
        question = _first_present(row, schema.get("question", ["question"]))
        context = _first_present(row, schema.get("context", ["context"]))
        answer = _first_present(row, schema.get("answer", ["answer"]))
        source = _first_present(row, schema.get("source", ["source"]))
        context_text = _stringify_context(context)
        answer_text, used_weak_label = _derive_answer(answer, context_text, allow_weak_labels)
        if not question or not answer_text:
            dropped += 1
            continue
        if used_weak_label:
            weak_labels += 1
        prompt = build_prompt(instruction, str(question), context_text)
        normalized.append(
            {
                "id": str(row.get("id", idx)),
                "instruction": instruction,
                "question": str(question),
                "legal_context": context_text,
                "answer": answer_text,
                "source_metadata": {"source": str(source) if source is not None else ""},
                "source_group": str(source) if source is not None else "",
                "prompt": prompt,
                "text": prompt + answer_text,
            }
        )
    return normalized, {"dropped_records": dropped, "weak_labels_from_context": weak_labels}


def _sample_rows(rows: list[dict[str, Any]], fraction: float, seed: int) -> list[dict[str, Any]]:
    if not rows:
        return rows
    sample_size = max(1, math.floor(len(rows) * fraction))
    rng = random.Random(seed)
    shuffled = list(rows)
    rng.shuffle(shuffled)
    return shuffled[:sample_size]


def _split_rows(rows: list[dict[str, Any]], ratios: dict[str, float], seed: int) -> tuple[dict[str, list[dict[str, Any]]], bool]:
    if not rows:
        return {"train": [], "validation": [], "test": []}, False
    has_groups = all(row.get("source_group") for row in rows)
    rng = random.Random(seed)
    train_ratio = float(ratios.get("train", 0.8))
    val_ratio = float(ratios.get("validation", 0.1))

    if has_groups and len({row["source_group"] for row in rows}) >= 3:
        groups: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            groups.setdefault(str(row["source_group"]), []).append(row)
        keys = list(groups)
        rng.shuffle(keys)
        train_cut = max(1, int(len(keys) * train_ratio))
        val_cut = max(train_cut + 1, int(len(keys) * (train_ratio + val_ratio))) if len(keys) > 2 else train_cut
        split_keys = {
            "train": keys[:train_cut],
            "validation": keys[train_cut:val_cut],
            "test": keys[val_cut:],
        }
        splits = {name: [row for key in selected for row in groups[key]] for name, selected in split_keys.items()}
    else:
        has_groups = False
        shuffled = list(rows)
        rng.shuffle(shuffled)
        train_cut = max(1, int(len(shuffled) * train_ratio))
        val_cut = max(train_cut + 1, int(len(shuffled) * (train_ratio + val_ratio))) if len(shuffled) > 2 else train_cut
        splits = {
            "train": shuffled[:train_cut],
            "validation": shuffled[train_cut:val_cut],
            "test": shuffled[val_cut:],
        }
    if not splits["test"] and len(rows) > 1:
        splits["test"].append(splits["train"].pop())
    if not splits["validation"] and len(splits["train"]) > 1:
        splits["validation"].append(splits["train"].pop())
    return splits, has_groups


def prepare_dataset(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    seed = int(config.get("experiment", {}).get("seed", 42))
    if config.get("experiment", {}).get("smoke_test"):
        raw_rows = _synthetic_rows()
    else:
        raw_rows = _load_hf_rows(config)
    normalized, normalization_meta = _normalize_rows(raw_rows, config)
    sampled = _sample_rows(normalized, float(config["dataset"].get("sample_fraction", 0.10)), seed)
    splits, grouped = _split_rows(sampled, config["dataset"].get("split_ratios", {}), seed)
    if not splits["train"]:
        available_columns = sorted({key for row in raw_rows[:20] for key in row.keys()})
        debug_summary = {
            "dataset_id": config["dataset"].get("id"),
            "sample_fraction": config["dataset"].get("sample_fraction"),
            "seed": seed,
            "raw_records": len(raw_rows),
            "normalized_records": len(normalized),
            "sampled_records": len(sampled),
            "available_columns_sample": available_columns,
            **normalization_meta,
        }
        write_json(debug_summary, output_dir / "dataset_summary.json")
        raise RuntimeError(
            "Prepared train split is empty. Check dataset schema mapping or enable dataset.allow_weak_labels_from_context."
        )

    data_dir = output_dir / "data"
    for split_name, split_rows in splits.items():
        write_jsonl(split_rows, data_dir / f"{split_name}.jsonl")
    summary = {
        "dataset_id": config["dataset"].get("id"),
        "sample_fraction": config["dataset"].get("sample_fraction"),
        "seed": seed,
        "raw_records": len(raw_rows),
        "normalized_records": len(normalized),
        "sampled_records": len(sampled),
        "split_sizes": {name: len(value) for name, value in splits.items()},
        "source_grouped_split": grouped,
        "leakage_control": "source_group" if grouped else "random_split_only_no_source_group",
        **normalization_meta,
    }
    write_json(summary, output_dir / "dataset_summary.json")
    return summary
