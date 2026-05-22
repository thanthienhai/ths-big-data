from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .utils import read_jsonl, write_csv, write_json


def _norm(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def exact_match(pred: str, ref: str) -> float:
    return 1.0 if _norm(pred) == _norm(ref) else 0.0


def token_f1(pred: str, ref: str) -> float:
    p_tokens = _norm(pred).split()
    r_tokens = _norm(ref).split()
    if not p_tokens or not r_tokens:
        return 0.0
    common = 0
    used = [False] * len(r_tokens)
    for tok in p_tokens:
        for i, ref_tok in enumerate(r_tokens):
            if not used[i] and tok == ref_tok:
                used[i] = True
                common += 1
                break
    if common == 0:
        return 0.0
    precision = common / len(p_tokens)
    recall = common / len(r_tokens)
    return 2 * precision * recall / (precision + recall)


def _lcs_len(a: list[str], b: list[str]) -> int:
    dp = [0] * (len(b) + 1)
    for x in a:
        prev = 0
        for j, y in enumerate(b, start=1):
            cur = dp[j]
            if x == y:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = cur
    return dp[-1]


def rouge_l(pred: str, ref: str) -> float:
    p_tokens = _norm(pred).split()
    r_tokens = _norm(ref).split()
    if not p_tokens or not r_tokens:
        return 0.0
    lcs = _lcs_len(p_tokens, r_tokens)
    precision = lcs / len(p_tokens)
    recall = lcs / len(r_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _optional_bertscore(preds: list[str], refs: list[str]) -> float | None:
    try:
        from bert_score import score

        _, _, f1 = score(preds, refs, lang="vi", verbose=False)
        return float(f1.mean().item())
    except Exception:
        return None


def compute_metrics(output_dir: Path, config: dict[str, Any], eval_status: dict[str, Any]) -> list[dict[str, Any]]:
    pred_dir = output_dir / "eval_predictions"
    rows = []
    for path in sorted(pred_dir.glob("*.jsonl")):
        model_name = path.stem
        preds = read_jsonl(path)
        if not preds or preds[0].get("failure"):
            rows.append({"model": model_name, "status": "failed", "reason": preds[0].get("failure") if preds else "no predictions"})
            continue
        pred_texts = [row.get("generated_answer", "") for row in preds]
        refs = [row.get("answer", "") for row in preds]
        latencies = [float(row.get("latency_seconds", 0.0)) for row in preds]
        metric_row: dict[str, Any] = {
            "model": model_name,
            "status": eval_status.get(model_name, {}).get("status", "ok"),
            "num_predictions": len(preds),
            "exact_match": sum(exact_match(p, r) for p, r in zip(pred_texts, refs)) / len(preds),
            "token_f1": sum(token_f1(p, r) for p, r in zip(pred_texts, refs)) / len(preds),
            "rouge_l": sum(rouge_l(p, r) for p, r in zip(pred_texts, refs)) / len(preds),
            "latency_seconds_avg": sum(latencies) / len(latencies) if latencies else 0.0,
        }
        if "bert_score" in config.get("evaluation", {}).get("metrics", []):
            bs = _optional_bertscore(pred_texts, refs)
            if bs is not None:
                metric_row["bert_score_f1"] = bs
            else:
                metric_row["bert_score_f1"] = "unavailable"
        rows.append(metric_row)
    write_json({"models": rows}, output_dir / "metrics.json")
    write_csv(rows, output_dir / "metrics.csv")
    return rows

