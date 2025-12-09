# eval/run_eval_clinical.py
import csv
import argparse
from pathlib import Path
from app.orchestrator import run_clinical_single_pass_clinical


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to CSV file with dialogues (columns: ID, dialogue)",
    )
    parser.add_argument(
        "--outcsv",
        type=str,
        default="eval/results/results_clinical.csv",
        help="Path to write final CSV results",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of examples to process",
    )
    args = parser.parse_args()

    data_path = Path(args.data)
    outcsv_path = Path(args.outcsv)
    outcsv_path.parent.mkdir(parents=True, exist_ok=True)

    results = []

    with open(data_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, quotechar='"')
        for idx, row in enumerate(reader):
            if args.limit is not None and idx >= args.limit:
                break

            pid = row["ID"]
            dialogue = row["dialogue"]

            agent_outputs, chief_summary = run_clinical_single_pass_clinical(dialogue)

            for agent in agent_outputs:
                results.append(
                    {
                        "ID": pid,
                        "Agent": agent["agent_name"],
                        "Section Header": agent["section_header"],
                        "Section Text": agent["section_text"],
                    }
                )

            results.append(
                {
                    "ID": pid,
                    "Agent": "chief_of_medicine",
                    "Section Header": chief_summary["section_header"],
                    "Section Text": chief_summary["section_text"],
                }
            )

            if (idx + 1) % 5 == 0:
                print(f"Processed {idx + 1} dialogues")

    fieldnames = ["ID", "Agent", "Section Header", "Section Text"]
    with open(outcsv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Finished! Results saved to {outcsv_path}")


if __name__ == "__main__":
    main()
