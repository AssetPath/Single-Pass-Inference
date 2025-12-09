# eval/eval_clinical_agents_vs_gt_llm.py
import csv
from pathlib import Path
from app.vertex_client import call_pro

# Standardized section headers with descriptions
SECTION_HEADERS_WITH_DESCRIPTIONS = [
    "fam/sochx [FAMILY HISTORY/SOCIAL HISTORY]",
    "genhx [HISTORY OF PRESENT ILLNESS]",
    "pastmedicalhx [PAST MEDICAL HISTORY]",
    "cc [CHIEF COMPLAINT]",
    "pastsurgical [PAST SURGICAL HISTORY]",
    "allergy [ALLERGIES]",
    "ros [REVIEW OF SYSTEMS]",
    "medications [CURRENT MEDICATIONS]",
    "assessment [CLINICAL ASSESSMENT]",
    "exam [PHYSICAL EXAM FINDINGS]",
    "diagnosis [DIAGNOSIS]",
    "disposition [DISPOSITION]",
    "plan [CLINICAL PLAN]",
    "edcourse [EMERGENCY DEPARTMENT COURSE]",
    "immunizations [IMMUNIZATION HISTORY]",
    "imaging [IMAGING RESULTS]",
    "gynhx [GYNECOLOGIC HISTORY]",
    "procedures [PAST PROCEDURES]",
    "other_history [OTHER RELEVANT HISTORY]",
    "labs [LABORATORY RESULTS]",
]

HEADER_MAP = {}
for h in SECTION_HEADERS_WITH_DESCRIPTIONS:
    canonical = h.split(" ")[0].lower()
    alias = h[h.find("[") + 1 : h.find("]")].lower()
    HEADER_MAP[canonical] = canonical
    HEADER_MAP[alias] = canonical


def normalize_header(header: str) -> str:
    return HEADER_MAP.get(header.strip().lower(), header.strip().lower())


def llm_text_similarity_with_explanation(
    gt_text: str, pred_text: str
) -> tuple[float, str]:
    """
    Ask the LLM to score semantic similarity between GT and predicted text.
    Returns a tuple: (score 0–100, short explanation)
    """
    prompt = f"""
    You are a clinical evaluation assistant.
    Compare the following two clinical summaries of a patient.

    Ground Truth:
    {gt_text}

    Prediction:
    {pred_text}

    Task:
    - Provide a numeric similarity score from 0 to 100, where 100 means fully captures all essential information in the Ground Truth and 0 means completely irrelevant to the Ground Truth.
    - Also provide a short explanation (1–2 sentences) describing why the score is high or low, including any missing key information.
    - Respond ONLY in this exact format:
    Score: <number between 0 and 100>
    Explanation: <short explanation>
    """

    response = call_pro(prompt, max_tokens=1800)
    lines = response.strip().splitlines()
    score = 0.0
    explanation = ""
    for line in lines:
        if line.lower().startswith("score:"):
            try:
                score = float("".join(c for c in line if c.isdigit() or c == "."))
            except:
                score = 0.0
        elif line.lower().startswith("explanation:"):
            explanation = line.split(":", 1)[1].strip()
    return score, explanation


def main():
    results_csv = Path("eval/results/clinical/results_clinical.csv")
    gt_csv = Path("dataset/MTS-Dialog-TrainingSet_Dialogue_Removed.csv")
    out_csv = Path("eval/results/clinical/eval_clinical_agents_vs_gt_llm.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    gt_dict = {}
    with open(gt_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gt_dict[row["ID"]] = {
                "section_header": normalize_header(row["section_header"]),
                "section_text": row["section_text"].strip(),
            }

    eval_rows = []
    with open(results_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["ID"]
            gt = gt_dict.get(pid)
            if not gt:
                continue

            pred_header = normalize_header(row["Section Header"])
            gt_header = gt["section_header"]

            header_match = pred_header == gt_header

            text_score, explanation = llm_text_similarity_with_explanation(
                gt["section_text"], row["Section Text"].strip()
            )

            eval_rows.append(
                {
                    "ID": pid,
                    "Agent": row["Agent"],
                    "Header Match": header_match,
                    "Text Similarity": text_score,
                    "Explanation": explanation,
                }
            )

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ID",
                "Agent",
                "Header Match",
                "Text Similarity",
                "Explanation",
            ],
        )
        writer.writeheader()
        writer.writerows(eval_rows)

    agents = sorted(
        set(r["Agent"] for r in eval_rows if r["Agent"] != "chief_of_medicine")
    )
    agents.append("chief_of_medicine")

    print("\n" + "=" * 50)
    print("CLINICAL AGENT EVALUATION SUMMARY")
    print("=" * 50)
    for agent in agents:
        agent_rows = [r for r in eval_rows if r["Agent"] == agent]
        total = len(agent_rows)
        header_acc = sum(r["Header Match"] for r in agent_rows) / total if total else 0
        avg_text_sim = (
            sum(r["Text Similarity"] for r in agent_rows) / total if total else 0
        )
        print(
            f"{agent.upper():<25} | Header Accuracy: {header_acc*100:.2f}% | Average Text Similarity: {avg_text_sim:.2f} / 100"
        )
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
