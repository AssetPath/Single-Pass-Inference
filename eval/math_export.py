# eval/math_export.py
import json
from pathlib import Path
from datasets import load_dataset
import re


def extract_math_answer(solution: str) -> str:
    """
    Extract the final answer from MATH solutions.
    MATH answers often include \boxed{expression} or = expression.

    Examples:
      "\\boxed{42}" → "42"
      "\\boxed{\\frac{2}{3}}" → "2/3"
      "Ans = 17" → "17"
    """
    # 1. Look for \boxed{...}
    boxed = re.findall(r"\\boxed\{([^}]*)\}", solution)
    if boxed:
        ans = boxed[-1].strip()
        return ans

    # 2. Look for common patterns like '= <num>'
    eq = re.findall(r"=\s*([^\s]+)", solution)
    if eq:
        return eq[-1].strip()

    # 3. Last fallback: extract last number fraction or integer
    matches = re.findall(r"-?\d+(?:/\d+)?", solution)
    if matches:
        return matches[-1]

    # 4. If all fails, return raw
    return solution.strip()


def export_math_jsonl(out_path="eval/math.jsonl", split="test"):
    print("Loading MATH dataset...")
    data = load_dataset("competition_math")[split]

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for i, item in enumerate(data):
            problem = item["problem"]
            solution = item["solution"]
            gold = extract_math_answer(solution)

            rec = {
                "id": f"math_{i}",
                "problem": problem,
                "answer": gold
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1

    print(f"Saved {count} examples to {out_path}")


if __name__ == "__main__":
    export_math_jsonl()
