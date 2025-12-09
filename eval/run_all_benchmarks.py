import subprocess
from pathlib import Path
from datetime import datetime


# Adjust paths if your dataset files differ
DATASETS = [
    {
        "name": "gsm8k",
        "data_path": "eval/gsm8k.jsonl",
        "limit": 250,
        "outdir": "results_gsm8k_v4",
    },
    {
        "name": "math",
        "data_path": "eval/math.jsonl",  # change if your MATH path is different
        "limit": 150,
        "outdir": "results_math_v1",
    },
    {
        "name": "financial",
        "data_path": "data/financial_quant.jsonl",
        "limit": None,  # use full dataset
        "outdir": "results_financial_v4",
    },
    {
        "name": "medical",
        "data_path": "data/medical_quant.jsonl",
        "limit": None,  # use full dataset
        "outdir": "results_medical_v4",
    },
    {
        "name": "engineering",
        "data_path": "data/engineering_quant.jsonl",
        "limit": None,  # use full dataset
        "outdir": "results_engineering_v2",
    },
]


def run_cmd(cmd: list[str]) -> None:
    """Run a shell command and stream output."""
    print("\n====================================================")
    print("RUNNING:", " ".join(cmd))
    print("====================================================\n")
    subprocess.run(cmd, check=True)


def main() -> None:
    print("\n############################################")
    print("#  SINGLE-PASS INFERENCE: FULL BENCHMARKS  #")
    print("############################################")
    print("Started at:", datetime.now().isoformat())
    print()

    root = Path(".")

    for cfg in DATASETS:
        name = cfg["name"]
        data_path = root / cfg["data_path"]
        outdir = cfg["outdir"]
        limit = cfg["limit"]

        if not data_path.exists():
            print(f"[WARN] Skipping {name}: data file not found at {data_path}")
            continue

        # -----------------------------
        # 1. Run eval.run_eval
        # -----------------------------
        cmd_eval = [
            "python",
            "-m",
            "eval.run_eval",
            "--data",
            str(data_path),
            "--mode",
            "both",
            "--outdir",
            outdir,
        ]
        if limit is not None:
            cmd_eval.extend(["--limit", str(limit)])

        print(f"\n>>>> [{name.upper()}] Running evaluation...")
        run_cmd(cmd_eval)

        # -----------------------------
        # 2. Run eval.analyze_results
        # -----------------------------
        single_path = f"{outdir}/results_single.jsonl"
        ensemble_path = f"{outdir}/results_ensemble.jsonl"

        if not Path(single_path).exists() or not Path(ensemble_path).exists():
            print(f"[WARN] Skipping analysis for {name}: results files not found.")
            continue

        cmd_analyze = [
            "python",
            "-m",
            "eval.analyze_results",
            "--single",
            single_path,
            "--ensemble",
            ensemble_path,
        ]

        print(f"\n>>>> [{name.upper()}] Analyzing results...")
        run_cmd(cmd_analyze)

    print("\n############################################")
    print("#  ALL BENCHMARKS COMPLETED                #")
    print("############################################")
    print("Finished at:", datetime.now().isoformat())


if __name__ == "__main__":
    main()
