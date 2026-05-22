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
    from .data import _normalize_rows

    test_cfg = dict(cfg)
    test_cfg["dataset"] = dict(cfg["dataset"])
    test_cfg["dataset"]["schema"] = {
        "question": ["question"],
        "context": ["context_list"],
        "answer": ["answer"],
        "source": ["qid"],
    }
    rows, meta = _normalize_rows(
        [{"question": "Q?", "context_list": ["Điều 1. Nội dung trả lời."], "qid": 1}],
        test_cfg,
    )
    assert rows and rows[0]["answer"] == "Điều 1. Nội dung trả lời."
    assert meta["weak_labels_from_context"] == 1
    with TemporaryDirectory() as tmp:
        path = Path(tmp)
        assert path.exists()
    print("Validation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
