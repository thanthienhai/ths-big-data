from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .utils import read_jsonl, write_jsonl


def _mock_answer(row: dict[str, Any], model_name: str) -> str:
    if "finetuned" in model_name or "checkpoint" in model_name:
        return row["answer"]
    return row["answer"].split(".")[0] + "."


def _generate_real(model_id_or_path: str, rows: list[dict[str, Any]], config: dict[str, Any], is_adapter: bool = False) -> list[dict[str, Any]]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer_source = config["model"]["base_model_id"] if is_adapter else model_id_or_path
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_source, trust_remote_code=bool(config["model"].get("trust_remote_code", True)))
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    base_source = config["model"]["base_model_id"] if is_adapter else model_id_or_path
    model = AutoModelForCausalLM.from_pretrained(
        base_source,
        trust_remote_code=bool(config["model"].get("trust_remote_code", True)),
        torch_dtype="auto",
        device_map="auto",
    )
    if is_adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, model_id_or_path)
        model.eval()
    gen_cfg = config.get("generation", {})
    outputs = []
    for row in rows:
        start = time.time()
        inputs = tokenizer(row["prompt"], return_tensors="pt").to(model.device)
        with torch.no_grad():
            generated = model.generate(
                **inputs,
                max_new_tokens=int(gen_cfg.get("max_new_tokens", 256)),
                do_sample=bool(gen_cfg.get("do_sample", False)),
                temperature=float(gen_cfg.get("temperature", 0.0)) if gen_cfg.get("do_sample", False) else None,
                top_p=float(gen_cfg.get("top_p", 1.0)),
                pad_token_id=tokenizer.eos_token_id,
            )
        text = tokenizer.decode(generated[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True)
        outputs.append({**row, "generated_answer": text.strip(), "latency_seconds": time.time() - start, "failure": ""})
    return outputs


def _evaluate_one(name: str, model_id: str, rows: list[dict[str, Any]], config: dict[str, Any], is_adapter: bool = False) -> tuple[list[dict[str, Any]], str]:
    if config.get("experiment", {}).get("smoke_test") or model_id.startswith("smoke/"):
        outputs = []
        for row in rows:
            start = time.time()
            outputs.append({**row, "generated_answer": _mock_answer(row, name), "latency_seconds": time.time() - start, "failure": ""})
        return outputs, ""
    try:
        return _generate_real(model_id, rows, config, is_adapter=is_adapter), ""
    except Exception as exc:
        return [], str(exc)


def evaluate_all(config: dict[str, Any], output_dir: Path, checkpoint_dir: Path) -> dict[str, Any]:
    rows = read_jsonl(output_dir / "data" / "test.jsonl")
    max_eval = config.get("evaluation", {}).get("max_eval_samples")
    if max_eval:
        rows = rows[: int(max_eval)]
    pred_dir = output_dir / "eval_predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)

    models = []
    for item in config.get("baselines", {}).get("required", []):
        models.append(dict(item))
    for item in config.get("baselines", {}).get("optional", []):
        models.append(dict(item))
    models.append({"name": "qwen3_lora_finetuned", "model_id": str(checkpoint_dir), "required": True, "is_adapter": True})

    status: dict[str, Any] = {}
    for model in models:
        name = model["name"]
        outputs, failure = _evaluate_one(name, model["model_id"], rows, config, is_adapter=bool(model.get("is_adapter", False)))
        if failure:
            status[name] = {"status": "failed", "reason": failure, "required": bool(model.get("required", False))}
            if model.get("required"):
                raise RuntimeError(f"Required model evaluation failed for {name}: {failure}")
            write_jsonl([{"model": name, "failure": failure}], pred_dir / f"{name}.jsonl")
        else:
            status[name] = {"status": "ok", "predictions": len(outputs), "required": bool(model.get("required", False))}
            write_jsonl(outputs, pred_dir / f"{name}.jsonl")
    return status
