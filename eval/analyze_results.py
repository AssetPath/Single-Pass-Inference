# eval/analyze_results.py
import argparse
import json
from pathlib import Path


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def summarize_pair(single_path: Path, ensemble_path: Path, label: str):
    single_records = {r["id"]: r for r in load_jsonl(single_path)}
    ensemble_records = {r["id"]: r for r in load_jsonl(ensemble_path)}

    ids = sorted(set(single_records.keys()) & set(ensemble_records.keys()))

    total = len(ids)
    if total == 0:
        print(f"[{label}] No overlapping examples found.")
        return

    single_correct = 0
    ensemble_correct = 0
    both_correct = 0
    both_wrong = 0
    single_only = 0  # single correct, ensemble wrong
    ensemble_only = 0  # ensemble correct, single wrong

    for _id in ids:
        s = bool(single_records[_id]["correct"])
        e = bool(ensemble_records[_id]["correct"])

        if s:
            single_correct += 1
        if e:
            ensemble_correct += 1

        if s and e:
            both_correct += 1
        elif s and not e:
            single_only += 1
        elif not s and e:
            ensemble_only += 1
        else:
            both_wrong += 1

    acc_single = single_correct / total
    acc_ensemble = ensemble_correct / total

    print(f"\n=== {label} ===")
    print(f"Total examples: {total}")
    print(f"Single accuracy:   {acc_single:.3f} ({single_correct}/{total})")
    print(f"Ensemble accuracy: {acc_ensemble:.3f} ({ensemble_correct}/{total})")
    print(f"ΔAcc (ensemble - single): {acc_ensemble - acc_single:+.3f}")
    print()
    print("Outcome breakdown (out of overlapping examples):")
    print(f"  Both correct:                 {both_correct}")
    print(f"  Both wrong:                   {both_wrong}")
    print(f"  Single only correct (losses): {single_only}")
    print(f"  Ensemble only correct (wins): {ensemble_only}")
    print()
    if total > 0:
        print(f"  Win rate  (ensemble rescues single): {ensemble_only / total:.3f}")
        print(f"  Loss rate (ensemble harms single):   {single_only / total:.3f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gsm8k_dir", type=str, default="eval/results/gsm8k")
    parser.add_argument("--math_dir", type=str, default="eval/results/math")
    args = parser.parse_args()

    gsm8k_dir = Path(args.gsm8k_dir)
    math_dir = Path(args.math_dir)

    summarize_pair(
        gsm8k_dir / "results_single.jsonl",
        gsm8k_dir / "results_ensemble.jsonl",
        label="GSM8K",
    )

    summarize_pair(
        math_dir / "results_single.jsonl",
        math_dir / "results_ensemble.jsonl",
        label="MATH",
    )


if __name__ == "__main__":
    main()
