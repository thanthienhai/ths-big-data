from __future__ import annotations

import csv
import importlib.metadata
import json
import os
import platform
import random
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config must be a mapping: {path}")
    return data


def write_yaml(data: dict[str, Any], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def write_json(data: Any, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(rows: list[dict[str, Any]], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in rows for key in row})
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def deep_update(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_update(result[key], value)
        else:
            result[key] = value
    return result


def apply_overrides(config: dict[str, Any], args: Any) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    if getattr(args, "output_root", None):
        updates.setdefault("experiment", {})["output_root"] = args.output_root
    if getattr(args, "smoke_test", False):
        updates.setdefault("experiment", {})["smoke_test"] = True
        updates.setdefault("experiment", {})["require_cuda"] = False
    if getattr(args, "baselines", None):
        optional = []
        for item in args.baselines.split(","):
            item = item.strip()
            if item:
                name = item.replace("/", "_").replace("-", "_").lower()
                optional.append({"name": name, "model_id": item, "required": False})
        updates["baselines"] = {"required": config.get("baselines", {}).get("required", []), "optional": optional}
    return deep_update(config, updates)


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def local_rank() -> int:
    return int(os.environ.get("LOCAL_RANK", os.environ.get("RANK", "0")))


def is_main_process() -> bool:
    return local_rank() == 0


def distributed_barrier() -> None:
    try:
        import torch.distributed as dist

        if dist.is_available() and dist.is_initialized():
            dist.barrier()
    except Exception:
        pass


def wait_for_files(paths: list[Path], timeout_seconds: int = 1800) -> None:
    deadline = time.time() + timeout_seconds
    missing = [path for path in paths if not path.exists()]
    while missing and time.time() < deadline:
        time.sleep(2)
        missing = [path for path in paths if not path.exists()]
    if missing:
        raise TimeoutError(f"Timed out waiting for files: {[str(path) for path in missing]}")


def seed_everything(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except Exception:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def package_versions(names: list[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


def run_command(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def collect_runtime_metadata(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    cuda: dict[str, Any] = {"available": False}
    try:
        import torch

        cuda["available"] = bool(torch.cuda.is_available())
        if torch.cuda.is_available():
            cuda["device_count"] = torch.cuda.device_count()
            cuda["devices"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
            cuda["memory_gb"] = [round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 2) for i in range(torch.cuda.device_count())]
    except Exception as exc:
        cuda["error"] = str(exc)

    return {
        "created_at": timestamp(),
        "output_dir": str(output_dir),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cuda": cuda,
        "git_commit": run_command(["git", "rev-parse", "HEAD"]),
        "git_status_short": run_command(["git", "status", "--short"]),
        "packages": package_versions(["torch", "transformers", "datasets", "accelerate", "evaluate", "rouge-score", "bert-score", "scikit-learn"]),
        "model": config.get("model", {}),
        "dataset": config.get("dataset", {}),
    }


def check_runtime(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    min_gb = float(config.get("experiment", {}).get("min_free_disk_gb", 1))
    free_gb = shutil.disk_usage(Path.cwd()).free / (1024**3)
    if free_gb < min_gb:
        errors.append(f"Free disk is {free_gb:.1f}GB, below required {min_gb:.1f}GB.")

    require_cuda = bool(config.get("experiment", {}).get("require_cuda", False))
    if require_cuda:
        try:
            import torch

            if not torch.cuda.is_available():
                errors.append("CUDA is required for the default full fine-tuning run but no CUDA device is available.")
        except Exception as exc:
            errors.append(f"Could not inspect CUDA availability: {exc}")

    if config.get("model", {}).get("base_model_id", "").startswith(("Qwen/", "meta-llama/", "google/")) and not os.environ.get("HF_TOKEN"):
        # Not fatal for public models, but useful for gated baselines and rate limits.
        print("Warning: HF_TOKEN is not set. Public models may still work; gated models or high-rate downloads may fail.")
    return errors
