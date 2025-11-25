# eval/math_export.py
import json
import re
from pathlib import Path

from datasets import load_dataset

# Subsets in EleutherAI/hendrycks_math (from the HF card)
SUBSETS = [
    "algebra",
    "counting_and_probability",
    "geometry",
    "intermediate_algebra",
    "number_theory",
    "prealgebra",
    "precalculus",
]


def extract_math_answer(solution: str) -> str:
    """
    Extract the final answer from MATH solutions.

    Priority:
      1) Content inside \\boxed{...}
      2) Token after '='
      3) Last integer or simple fraction
      4) Raw stripped solution
    """
    # 1) Look for \boxed{...}
    boxed = re.findall(r"\\boxed\{([^}]*)\}", solution)
    if boxed:
        return boxed[-1].strip()

    # 2) Look for '= <token>'
    eq = re.findall(r"=\s*([^\s]+)", solution)
    if eq:
        return eq[-1].strip()

    # 3) Fallback: last integer or simple fraction
    matches = re.findall(r"-?\d+(?:/\d+)?", solution)
    if matches:
        return matches[-1]

    # 4) Final fallback
    return solution.strip()


def export_math_jsonl(out_path: str = "eval/math.jsonl", split: str = "test") -> None:
    """
    Export Hendrycks MATH (EleutherAI/hendrycks_math) to a single JSONL file:

      {"id": ..., "problem": ..., "answer": ...}

    We concatenate all topic subsets into one file.
    """
    print("Loading MATH dataset from EleutherAI/hendrycks_math...")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for subset in SUBSETS:
            print(f"  -> subset: {subset}, split: {split}")
            ds = load_dataset("EleutherAI/hendrycks_math", subset, split=split)

            for i, item in enumerate(ds):
                problem = item["problem"]
                solution = item["solution"]
                gold = extract_math_answer(solution)

                rec = {
                    "id": f"{subset}_{split}_{i}",
                    "problem": problem,
                    "answer": gold,
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1

    print(f"Saved {count} examples to {out_path}")


if __name__ == "__main__":
    export_math_jsonl()
