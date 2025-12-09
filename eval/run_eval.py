# eval/run_eval.py
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Iterable, Optional

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))  # add repo root to sys.path

from app.orchestrator import run_single_pass_generalist
from app.vertex_client import call_flash
from eval.metrics import numeric_match, extract_last_number

from app.orchestrator import (
    run_clinical_single_pass_clinical,
    run_single_pass_generalist,
    run_single_pass_financial,
    run_single_pass_medical,
    run_single_pass_engineering,
)

# Helpers

def load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    """Stream JSONL file one example at a time."""
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def build_single_prompt(problem: str) -> str:
    """Prompt for single-model baseline on GSM8K / MATH."""
    return (
        "You are a generalist reasoning assistant solving math word problems.\n"
        "Think step by step and then give a final numeric answer.\n\n"
        f"Problem:\n{problem}\n\n"
        "Provide your reasoning, then clearly state the final answer."
    )


def to_numeric(text: str) -> Optional[str]:
    """Wrapper so we also log the parsed numeric form (if any)."""
    return extract_last_number(text)  # may return None

# Single-model baseline

def evaluate_single(
    data_path: Path,
    limit: int | None = None,
    output_path: Path | None = None,
) -> None:
    """
    Baseline: one Gemini Flash call per problem with a generic math prompt.
    Saves rich JSONL with parsed numeric answers.
    """
    results: list[Dict[str, Any]] = []
    total = 0
    correct = 0

    for i, item in enumerate(load_jsonl(data_path)):
        if limit is not None and i >= limit:
            break

        pid = item.get("id", f"example_{i}")
        problem = item["problem"]
        gold = item["answer"]

        prompt = build_single_prompt(problem)
        pred_raw = call_flash(prompt, temperature=0.4, max_tokens=512)

        is_correct = numeric_match(pred_raw, gold)
        total += 1
        correct += int(is_correct)

        record: Dict[str, Any] = {
            "id": pid,
            "problem": problem,
            "gold_answer_raw": gold,
            "gold_answer_num": to_numeric(gold),
            "mode": "single",
            "single": {
                "raw_output": pred_raw,
                "pred_answer_num": to_numeric(pred_raw),
                "correct": is_correct,
                # token usage will be filled once we plumb it through from vertex_client
                "tokens_prompt": None,
                "tokens_completion": None,
                "tokens_total": None,
            },
        }
        results.append(record)

        if (i + 1) % 5 == 0:
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
    """
    Single-pass reflective ensemble:
    - Routes to domain-specific solvers based on the dataset name.
    - Runs multiple agents + a Pro judge that selects/synthesizes a final answer.
    """
    results: list[Dict[str, Any]] = []
    total = 0
    correct = 0

    # -------------------------
    # Choose domain-specific ensemble
    # -------------------------
    name = data_path.name.lower()
    if "financial" in name:
        ensemble_fn = run_single_pass_financial
    elif "medical" in name:
        ensemble_fn = run_single_pass_medical
    elif "engineering" in name or "eng_" in name:
        ensemble_fn = run_single_pass_engineering
    else:
        ensemble_fn = run_single_pass_generalist

    # -------------------------
    # Helpers
    # -------------------------
    def extract_final_answer(judge_text: str) -> str:
        """
        Pull the numeric answer from the judge output.

        Expected format:
        FINAL_ANSWER: 6.03
        JUSTIFICATION: ...
        """
        for line in judge_text.splitlines():
            line = line.strip()
            if line.upper().startswith("FINAL_ANSWER"):
                # Handle 'FINAL_ANSWER: 6.03'
                if ":" in line:
                    return line.split(":", 1)[1].strip()
                # Fallback: 'FINAL_ANSWER 6.03'
                parts = line.split()
                if len(parts) >= 2:
                    return parts[-1].strip()

        num = extract_last_number(judge_text)
        return num if num is not None else judge_text.strip()

    def to_numeric(text: str | None) -> str | None:
        if text is None:
            return None
        return extract_last_number(str(text))

    # Main evaluation loop
    for i, item in enumerate(load_jsonl(data_path)):
        if limit is not None and i >= limit:
            break

        pid = item.get("id", f"example_{i}")
        problem = item.get("problem") or item.get("question")
        gold = str(item.get("answer")).strip()

        # Run the domain-appropriate ensemble
        agent_outputs, judge_text, agent_usage, judge_usage = ensemble_fn(problem)
        judge_answer = extract_final_answer(judge_text)

        # Compare judge final answer to gold
        is_correct = numeric_match(judge_answer, gold)
        total += 1
        correct += int(is_correct)

        # Build per-solver structure for logging
        solvers_struct = []
        for solver_name, raw_text in agent_outputs.items():
            usage = agent_usage.get(solver_name, {}) or {}
            inp = usage.get("input_tokens")
            out = usage.get("output_tokens")
            total = usage.get("total_tokens")
            if total is None and (inp is not None or out is not None):
                total = (inp or 0) + (out or 0)

            solvers_struct.append(
                {
                    "name": solver_name,
                    "raw_output": raw_text,
                    "pred_answer_num": to_numeric(raw_text),
                    "tokens_prompt": inp,
                    "tokens_completion": out,
                    "tokens_total": total,
                }
            )

        record: Dict[str, Any] = {
            "id": pid,
            "problem": problem,
            "gold_answer_raw": gold,
            "gold_answer_num": to_numeric(gold),
            "mode": "ensemble",
            "ensemble": {
                "judge_output_raw": judge_text,
                "judge_answer_raw": judge_answer,
                "judge_answer_num": to_numeric(judge_answer),
                "correct": is_correct,
                "solvers": solvers_struct,
                "tokens_total_prompt": judge_usage.get("input_tokens"),
                "tokens_total_completion": judge_usage.get("output_tokens"),
                "tokens_total": judge_usage.get("total_tokens"),
            },
        }
        results.append(record)

        if (i + 1) % 5 == 0:
            print(f"[ensemble] Processed {i+1} examples. Running accuracy: {correct/total:.3f}")

    acc = correct / total if total else 0.0
    print(f"\n[ensemble] Final accuracy: {acc:.3f} over {total} examples.")

    if output_path is not None:
        with output_path.open("w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[ensemble] Saved detailed results to {output_path}")

# CLI

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to JSONL eval file (e.g., GSM8K / MATH export).",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["single", "ensemble", "both"],
        default="both",
        help="Which evaluation mode to run.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of examples to evaluate.",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default="results",
        help="Directory to write JSONL outputs.",
    )

    args = parser.parse_args()
    data_path = Path(args.data)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.mode in ("single", "both"):
        single_out = outdir / "financial_results_single.jsonl"
        evaluate_single(data_path, limit=args.limit, output_path=single_out)

    if args.mode in ("ensemble", "both"):
        ensemble_out = outdir / "financial_results_ensemble.jsonl"
        evaluate_ensemble(data_path, limit=args.limit, output_path=ensemble_out)


if __name__ == "__main__":
    main()
