# eval/analyze_results.py

import json
from pathlib import Path
from statistics import mean
from typing import Dict, List, Any


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    data = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def compute_accuracy(records: List[Dict[str, Any]]) -> float:
    correct = 0
    total = 0

    for r in records:
        mode = r["mode"]

        if mode == "single":
            if r["single"]["correct"]:
                correct += 1
        elif mode == "ensemble":
            if r["ensemble"]["correct"]:
                correct += 1

        total += 1

    return correct / total if total else 0.0


def classify_difficulty(problem: str) -> str:
    """Approximate difficulty based on problem length."""
    words = len(problem.split())
    if words < 40:
        return "easy"
    elif words < 80:
        return "medium"
    else:
        return "hard"


def difficulty_breakdown(records: List[Dict[str, Any]]) -> Dict[str, float]:
    buckets = {"easy": [], "medium": [], "hard": []}

    for r in records:
        mode = r["mode"]
        problem = r["problem"]

        diff = classify_difficulty(problem)

        if mode == "single":
            correct = r["single"]["correct"]
        else:
            correct = r["ensemble"]["correct"]

        buckets[diff].append(int(correct))

    return {
        k: (sum(v) / len(v) if v else 0.0)
        for k, v in buckets.items()
    }


def run_analysis(single_path: Path, ensemble_path: Path) -> None:
    single_records = load_jsonl(single_path)
    ensemble_records = load_jsonl(ensemble_path)

    print("\n===== BASELINES =====")
    print(f"Majority vote accuracy: {majority_vote(ensemble_records):.3f}")
    print(f"Oracle best-of-K accuracy: {oracle_best_of_k(ensemble_records):.3f}")

    print("\n===== PER-SOLVER ACCURACY (Ensemble records) =====")
    solver_acc = per_solver_accuracy(ensemble_records)
    for name, a in solver_acc.items():
        print(f"{name}: {a:.3f}")

    print("\n===== ACCURACY =====")
    print(f"Single-model accuracy:   {compute_accuracy(single_records):.3f}")
    print(f"Ensemble accuracy:       {compute_accuracy(ensemble_records):.3f}")

    print("\n===== DIFFICULTY BREAKDOWN (Single) =====")
    print(difficulty_breakdown(single_records))

    print("\n===== DIFFICULTY BREAKDOWN (Ensemble) =====")
    print(difficulty_breakdown(ensemble_records))

def extract_solver_answers(record):
    if "ensemble" not in record:
        return []

    answers = []
    for solver in record["ensemble"]["solvers"]:
        num = solver.get("pred_answer_num")
        answers.append(num)
    return answers


def majority_vote(records):
    correct = 0
    total = 0

    for r in records:
        if r["mode"] != "ensemble":
            continue

        gold = r["gold_answer_num"]
        answers = extract_solver_answers(r)

        # Remove None predictions
        answers = [a for a in answers if a is not None]

        if not answers:
            continue

        # Count frequency
        freq = {}
        for a in answers:
            freq[a] = freq.get(a, 0) + 1

        # Majority answer
        majority = max(freq, key=freq.get)

        if majority == gold:
            correct += 1

        total += 1

    return correct / total if total else 0.0


def oracle_best_of_k(records):
    correct = 0
    total = 0

    for r in records:
        if r["mode"] != "ensemble":
            continue

        gold = r["gold_answer_num"]
        answers = extract_solver_answers(r)

        if gold in answers:
            correct += 1

        total += 1

    return correct / total if total else 0.0


def per_solver_accuracy(records):
    """
    Compute accuracy for each solver in the ensemble.
    Assumes ensemble records with:
      r["ensemble"]["solvers"] -> list of { "name", "pred_answer_num", ... }
    """
    stats = {}  # name -> {"correct": int, "total": int}

    for r in records:
        if r["mode"] != "ensemble":
            continue

        gold = r.get("gold_answer_num")
        if gold is None:
            continue

        for solver in r["ensemble"]["solvers"]:
            name = solver["name"]
            pred = solver.get("pred_answer_num")

            if name not in stats:
                stats[name] = {"correct": 0, "total": 0}

            if pred is not None:
                stats[name]["total"] += 1
                if pred == gold:
                    stats[name]["correct"] += 1

    # Convert to accuracy
    acc = {}
    for name, s in stats.items():
        total = s["total"]
        acc[name] = s["correct"] / total if total else 0.0

    return acc



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--single", type=str, required=True)
    parser.add_argument("--ensemble", type=str, required=True)

    args = parser.parse_args()

    run_analysis(Path(args.single), Path(args.ensemble))
