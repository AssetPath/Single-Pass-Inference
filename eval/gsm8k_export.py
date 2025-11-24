# eval/gsm8k_export.py
import json
from pathlib import Path

from datasets import load_dataset


def export_gsm8k_jsonl(
    split: str = "test",
    out_path: Path = Path("eval/gsm8k.jsonl"),
) -> None:
    """
    Export GSM8K to a simple JSONL format:
    {
      "id": ...,
      "problem": ...,
      "answer": ...   # final numeric answer as string
    }
    """
    print(f"Loading GSM8K split: {split}")
    dataset = load_dataset("gsm8k", "main")[split]

    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for i, item in enumerate(dataset):
            problem = item["question"]
            # GSM8K answers are usually "reasoning #### final_answer"
            raw_answer = item["answer"]
            if "####" in raw_answer:
                gold = raw_answer.split("####")[-1].strip()
            else:
                gold = raw_answer.strip()

            rec = {
                "id": f"gsm8k_{i}",
                "problem": problem,
                "answer": gold,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} examples to {out_path}")


if __name__ == "__main__":
    export_gsm8k_jsonl()
