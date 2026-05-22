from __future__ import annotations

import inspect
import sys


def _version(package: str) -> str:
    try:
        from importlib.metadata import version

        return version(package)
    except Exception:
        return "not-installed"


def main() -> int:
    required = ["torch", "transformers", "accelerate", "peft", "datasets"]
    versions = {name: _version(name) for name in required}
    print("Environment versions:", versions)

    missing = [name for name, value in versions.items() if value == "not-installed"]
    if missing:
        print(f"Missing packages: {missing}", file=sys.stderr)
        return 2

    try:
        from accelerate import Accelerator

        signature = inspect.signature(Accelerator.unwrap_model)
    except Exception as exc:
        print(f"Could not inspect accelerate.Accelerator.unwrap_model: {exc}", file=sys.stderr)
        return 2

    if "keep_torch_compile" not in signature.parameters:
        print(
            "Incompatible accelerate installed: Accelerator.unwrap_model lacks "
            "`keep_torch_compile`, but current transformers requires it. "
            "Fix: rm -rf .venv-full-finetune && bash train/run_full_finetune.sh",
            file=sys.stderr,
        )
        return 2

    print("Environment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
