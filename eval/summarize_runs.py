import json
from pathlib import Path
from typing import Dict, Any, Optional


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def summarize_run(name: str, ensemble_path: Path) -> Optional[Dict[str, Any]]:
    if not ensemble_path.exists():
        print(f"[warn] Missing ensemble file for {name}: {ensemble_path}")
        return None

    n = 0
    correct = 0
    total_tokens = 0

    for rec in load_jsonl(ensemble_path):
        n += 1
        ens = rec.get("ensemble", {})
        if ens.get("correct"):
            correct += 1

        tt = ens.get("tokens_total")
        if isinstance(tt, (int, float)):
            total_tokens += tt or 0

    if n == 0:
        print(f"[warn] No records in {ensemble_path}")
        return None

    acc = correct / n
    avg_tokens = total_tokens / n if n > 0 else 0.0
    tokens_per_correct = total_tokens / max(correct, 1)

    return {
        "name": name,
        "n": n,
        "accuracy": acc,
        "avg_tokens_per_problem": avg_tokens,
        "tokens_per_correct_answer": tokens_per_correct,
    }


def main():
    # Adjust paths/versions as needed
    runs = {
        "gsm8k": Path("results_gsm8k_v4/financial_results_ensemble.jsonl"),
        "math": Path("results_math_v1/financial_results_ensemble.jsonl"),
        "financial": Path("results_financial_v3/financial_results_ensemble.jsonl"),
        "medical": Path("results_medical_v3/financial_results_ensemble.jsonl"),
        "engineering": Path("results_engineering_v1/financial_results_ensemble.jsonl"),
    }

    summaries = []
    for name, path in runs.items():
        s = summarize_run(name, path)
        if s:
            summaries.append(s)

    print("\n===== ENSEMBLE SUMMARY (accuracy + token usage) =====\n")
    print(
        f"{'domain':<12} {'n':>5} {'acc':>8} {'avg_tokens':>14} {'tokens/correct':>18}"
    )
    print("-" * 60)
    for s in summaries:
        print(
            f"{s['name']:<12} "
            f"{s['n']:>5} "
            f"{s['accuracy']*100:>7.1f}% "
            f"{s['avg_tokens_per_problem']:>13.1f} "
            f"{s['tokens_per_correct_answer']:>17.1f}"
        )


if __name__ == "__main__":
    main()
