from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from .metrics import exact_match, rouge_l, token_f1
from .prompting import build_prompt
from .utils import load_yaml


def main() -> int:
    cfg = load_yaml(Path("train/configs/smoke_test.yaml"))
    prompt = build_prompt(cfg["dataset"]["instruction"], "Câu hỏi?", "Điều 1. Nội dung.")
    assert "### Instruction" in prompt and "### Answer" in prompt
    assert exact_match("A B", "a b") == 1.0
    assert token_f1("a b", "a c") > 0
    assert rouge_l("a b c", "a c") > 0
    with TemporaryDirectory() as tmp:
        path = Path(tmp)
        assert path.exists()
    print("Validation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

