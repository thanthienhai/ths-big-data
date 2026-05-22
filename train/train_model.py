from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .utils import read_jsonl, write_json, write_jsonl


class JsonlTrainerLogger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.rows: list[dict[str, Any]] = []

    def callback(self):
        try:
            from transformers import TrainerCallback
        except ImportError:
            return None

        outer = self

        class _Callback(TrainerCallback):
            def on_log(self, args, state, control, logs=None, **kwargs):
                if hasattr(state, "is_world_process_zero") and not state.is_world_process_zero:
                    return
                row = {"step": state.global_step, "epoch": state.epoch, **(logs or {})}
                outer.rows.append(row)
                write_jsonl(outer.rows, outer.log_path)

        return _Callback()


def _mock_train(config: dict[str, Any], output_dir: Path) -> Path:
    checkpoint = output_dir / "checkpoints" / config["model"].get("checkpoint_dir_name", "mock_checkpoint")
    checkpoint.mkdir(parents=True, exist_ok=True)
    (checkpoint / "MOCK_ADAPTER.txt").write_text("Smoke-test LoRA adapter; no model weights were trained.\n", encoding="utf-8")
    write_jsonl(
        [{"step": 1, "loss": 0.0, "learning_rate": config["training"].get("learning_rate"), "note": "smoke test mock training"}],
        output_dir / "train_log.jsonl",
    )
    write_json({"checkpoint_path": str(checkpoint), "mode": "mock_lora_finetune"}, output_dir / "checkpoint_metadata.json")
    return checkpoint


def _tokenize_records(tokenizer: Any, records: list[dict[str, Any]], max_length: int) -> dict[str, list[list[int]]]:
    input_ids = []
    attention_mask = []
    labels = []
    for row in records:
        prompt = row["prompt"]
        answer = row["answer"]
        prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
        full = tokenizer(prompt + answer, truncation=True, max_length=max_length, add_special_tokens=True)
        ids = full["input_ids"]
        mask = full["attention_mask"]
        label = list(ids)
        prompt_len = min(len(prompt_ids), len(label))
        label[:prompt_len] = [-100] * prompt_len
        input_ids.append(ids)
        attention_mask.append(mask)
        labels.append(label)
    return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}


def _apply_lora(model: Any, config: dict[str, Any]) -> Any:
    try:
        from peft import LoraConfig, get_peft_model
    except ImportError as exc:
        raise RuntimeError("LoRA training requires `peft`. Re-run without SKIP_INSTALL or install train/requirements.txt.") from exc

    lora = config["model"].get("lora", {})
    peft_config = LoraConfig(
        r=int(lora.get("r", 32)),
        lora_alpha=int(lora.get("alpha", 64)),
        lora_dropout=float(lora.get("dropout", 0.05)),
        bias=str(lora.get("bias", "none")),
        task_type=str(lora.get("task_type", "CAUSAL_LM")),
        target_modules=list(lora.get("target_modules", ["q_proj", "v_proj"])),
    )
    return get_peft_model(model, peft_config)


def _assert_lora_finetune(model: Any) -> None:
    peft_config = getattr(model, "peft_config", None)
    if not peft_config:
        raise RuntimeError("LoRA fine-tuning required, but model has no PEFT configuration.")
    params = list(model.named_parameters())
    trainable = [name for name, param in params if param.requires_grad]
    if not trainable:
        raise RuntimeError("No trainable LoRA parameters found.")
    non_lora_trainable = [name for name in trainable if "lora_" not in name.lower()]
    if non_lora_trainable:
        raise RuntimeError(f"LoRA fine-tuning should only train LoRA parameters; found trainable base params: {non_lora_trainable[:5]}")


def train_full_model(config: dict[str, Any], output_dir: Path) -> Path:
    if config.get("experiment", {}).get("smoke_test"):
        return _mock_train(config, output_dir)

    try:
        import torch
        from datasets import Dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForSeq2Seq, Trainer, TrainingArguments
    except ImportError as exc:
        raise RuntimeError("LoRA training requires torch, datasets, transformers, and peft.") from exc

    data_dir = output_dir / "data"
    train_rows = read_jsonl(data_dir / "train.jsonl")
    val_rows = read_jsonl(data_dir / "validation.jsonl")
    model_id = config["model"]["base_model_id"]
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=bool(config["model"].get("trust_remote_code", True)))
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = config["model"].get("dtype", "auto")
    torch_dtype = "auto" if dtype == "auto" else getattr(torch, dtype)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=bool(config["model"].get("trust_remote_code", True)),
        torch_dtype=torch_dtype,
    )
    if config["model"].get("gradient_checkpointing"):
        model.gradient_checkpointing_enable()
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()
    model = _apply_lora(model, config)
    _assert_lora_finetune(model)
    if hasattr(model, "print_trainable_parameters"):
        model.print_trainable_parameters()

    max_len = int(config["training"].get("max_seq_length", 2048))
    train_ds = Dataset.from_dict(_tokenize_records(tokenizer, train_rows, max_len))
    val_ds = Dataset.from_dict(_tokenize_records(tokenizer, val_rows, max_len)) if val_rows else None
    checkpoint_dir = output_dir / "checkpoints" / config["model"].get("checkpoint_dir_name", "qwen_lora_adapter")
    logger = JsonlTrainerLogger(output_dir / "train_log.jsonl")
    cb = logger.callback()

    args = TrainingArguments(
        output_dir=str(checkpoint_dir),
        num_train_epochs=float(config["training"].get("num_train_epochs", 1)),
        per_device_train_batch_size=int(config["training"].get("per_device_train_batch_size", 1)),
        per_device_eval_batch_size=int(config["training"].get("per_device_eval_batch_size", 1)),
        gradient_accumulation_steps=int(config["training"].get("gradient_accumulation_steps", 1)),
        learning_rate=float(config["training"].get("learning_rate", 5e-6)),
        weight_decay=float(config["training"].get("weight_decay", 0.0)),
        warmup_ratio=float(config["training"].get("warmup_ratio", 0.0)),
        logging_steps=int(config["training"].get("logging_steps", 5)),
        save_strategy=config["training"].get("save_strategy", "epoch"),
        eval_strategy=config["training"].get("eval_strategy", "epoch"),
        max_steps=int(config["training"].get("max_steps", -1)),
        fp16=bool(config["training"].get("fp16", False)),
        bf16=bool(config["training"].get("bf16", False)),
        report_to=[],
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model),
        callbacks=[cb] if cb else [],
    )
    start = time.time()
    try:
        trainer.train()
        trainer.save_model(str(checkpoint_dir))
        if trainer.is_world_process_zero():
            tokenizer.save_pretrained(str(checkpoint_dir))
    except Exception:
        if trainer.is_world_process_zero():
            write_json({"checkpoint_path": str(checkpoint_dir), "failed_after_seconds": time.time() - start}, output_dir / "checkpoint_metadata.json")
        raise
    if trainer.is_world_process_zero():
        write_json(
            {
                "checkpoint_path": str(checkpoint_dir),
                "train_seconds": time.time() - start,
                "mode": "lora_finetune",
                "base_model_id": model_id,
                "lora": config["model"].get("lora", {}),
            },
            output_dir / "checkpoint_metadata.json",
        )
    return checkpoint_dir
