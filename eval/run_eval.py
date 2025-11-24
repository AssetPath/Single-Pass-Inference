# eval/run_eval.py
import argparse
import json
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))  # add repo root to sys.path

from app.orchestrator import run_single_pass_generalist
from app.vertex_client import call_flash
from eval.metrics import numeric_match


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def build_single_prompt(problem: str) -> str:
    """Prompt for single-model baseline."""
    return (
        "You are a generalist reasoning assistant solving math word problems.\n"
        "Think step by step and then give a final numeric answer.\n\n"
        f"Problem:\n{problem}\n\n"
        "Provide your reasoning, then clearly state the final answer."
    )


def evaluate_single(
    data_path: Path,
    limit: int | None = None,
    output_path: Path | None = None,
) -> None:
    results = []
    total = 0
    correct = 0

    for i, item in enumerate(load_jsonl(data_path)):
        if limit is not None and i >= limit:
            break

        pid = item.get("id", f"example_{i}")
        problem = item["problem"]
        gold = item["answer"]

        prompt = build_single_prompt(problem)
        pred = call_flash(prompt, temperature=0.4, max_tokens=512)

        is_correct = numeric_match(pred, gold)

        total += 1
        correct += int(is_correct)

        results.append(
            {
                "id": pid,
                "problem": problem,
                "gold_answer": gold,
                "pred_answer": pred,
                "correct": is_correct,
                "mode": "single",
            }
        )

        if i % 5 == 0:
            print(f"[single] Processed {i+1} examples. Running accuracy: {correct/total:.3f}")

    acc = correct / total if total else 0.0
    print(f"\n[single] Final accuracy: {acc:.3f} over {total} examples.")

    if output_path is not None:
        with output_path.open("w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[single] Saved detailed results to {output_path}")


def evaluate_ensemble(
    data_path: Path,
    limit: int | None = None,
    output_path: Path | None = None,
) -> None:
    results = []
    total = 0
    correct = 0

    for i, item in enumerate(load_jsonl(data_path)):
        if limit is not None and i >= limit:
            break

        pid = item.get("id", f"example_{i}")
        problem = item["problem"]
        gold = item["answer"]

        agent_outputs, final_answer = run_single_pass_generalist(problem)
        is_correct = numeric_match(final_answer, gold)

        total += 1
        correct += int(is_correct)

        results.append(
            {
                "id": pid,
                "problem": problem,
                "gold_answer": gold,
                "final_answer": final_answer,
                "agent_outputs": agent_outputs,
                "correct": is_correct,
                "mode": "ensemble",
            }
        )

        if i % 5 == 0:
            print(f"[ensemble] Processed {i+1} examples. Running accuracy: {correct/total:.3f}")

    acc = correct / total if total else 0.0
    print(f"\n[ensemble] Final accuracy: {acc:.3f} over {total} examples.")

    if output_path is not None:
        with output_path.open("w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[ensemble] Saved detailed results to {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="Path to JSONL eval file")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["single", "ensemble", "both"],
        default="both",
        help="Which evaluation mode to run",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional max number of examples")
    parser.add_argument("--outdir", type=str, default="eval/results", help="Where to write result files")

    args = parser.parse_args()

    data_path = Path(args.data)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.mode in ("single", "both"):
        single_out = outdir / "results_single.jsonl"
        evaluate_single(data_path, limit=args.limit, output_path=single_out)

    if args.mode in ("ensemble", "both"):
        ensemble_out = outdir / "results_ensemble.jsonl"
        evaluate_ensemble(data_path, limit=args.limit, output_path=ensemble_out)


if __name__ == "__main__":
    main()
