# app/orchestrator.py

from typing import Dict, List, Tuple
from app.vertex_client import call_flash, call_pro


# ============================================================
#  GENERAL REASONING AGENTS (used for both math + clinical)
# ============================================================

AGENTS = [
    {
        "name": "solver_1",
        "suffix": "Think step by step and be cautious.",
        "temperature": 0.4,
    },
    {
        "name": "solver_2",
        "suffix": "Try an alternative approach if one comes to mind.",
        "temperature": 0.6,
    },
    {
        "name": "solver_3",
        "suffix": "Double-check any arithmetic carefully.",
        "temperature": 0.3,
    },
    {
        "name": "solver_4",
        "suffix": "Look for edge cases or hidden assumptions.",
        "temperature": 0.5,
    },
    {
        "name": "solver_5",
        "suffix": "Be concise and aim directly for the answer.",
        "temperature": 0.4,
    },
]


# ============================================================
#  GENERALIST PIPELINE (GSM8K / MATH)
# ============================================================


def run_single_pass_generalist(problem: str) -> Tuple[Dict[str, str], str]:
    """
    Ensemble inference for GSM8K/MATH evaluation.
    Produces 5 generalist solver outputs + 1 judge (Gemini Pro).
    """
    agent_outputs: Dict[str, str] = {}

    # ---- 1. Run all generalist solvers ----
    for cfg in AGENTS:
        full_prompt = (
            "You are a generalist reasoning assistant solving math problems.\n"
            f"{cfg['suffix']}\n\n"
            f"Problem:\n{problem}\n\n"
            "Give your full reasoning and final answer."
        )
        answer = call_flash(full_prompt, temperature=cfg["temperature"], max_tokens=512)
        agent_outputs[cfg["name"]] = answer

    # ---- 2. Judge (Gemini Pro) ----
    judge_lines = [
        "You are a careful reasoning judge.",
        "You will evaluate several candidate solutions.\n",
        f"Original problem:\n{problem}\n\n",
        "Candidate solutions:\n",
    ]

    for name, text in agent_outputs.items():
        judge_lines.append(f"### {name}\n{text}\n")

    judge_lines.append(
        "Select the most correct solution (or synthesize them) and return:\n"
        "Final answer: <answer>\n"
        "Explanation: <2–4 sentence justification>"
    )

    final_answer = call_pro("\n".join(judge_lines), max_tokens=1024)

    return agent_outputs, final_answer


# ============================================================
#  CLINICAL PIPELINE (GENERAL ANALYSTS + CHIEF OF MEDICINE)
# ============================================================


# --------- Clinical agents (for patient–doctor dialogue) ----------

CLINICAL_AGENTS = [
    {
        "name": "ed_physician",
        "role": "You are an emergency physician focusing on triage, red flags, and immediate stabilization.",
        "temperature": 0.4,
    },
    {
        "name": "internal_medicine",
        "role": "You are an internal medicine attending focusing on holistic differential diagnosis.",
        "temperature": 0.4,
    },
    {
        "name": "cardiologist",
        "role": "You are a cardiologist focusing on cardiac risk, chest pain, and hemodynamics.",
        "temperature": 0.4,
    },
    {
        "name": "pharmacist",
        "role": "You are a clinical pharmacist focusing on medications, interactions, and contraindications.",
        "temperature": 0.5,
    },
    {
        "name": "nurse",
        "role": "You are an experienced bedside nurse focusing on symptoms, safety, and escalation criteria.",
        "temperature": 0.5,
    },
]


def run_clinical_single_pass(dialogue: str) -> Tuple[Dict[str, str], str]:
    """
    Ensemble inference for clinical dialogue.
    Uses SAME 5 general agents (not medical personas),
    then a 'Chief of Medicine' Pro judge for a clinical plan.
    """
    agent_outputs: Dict[str, str] = {}

    # ---- 1. Run 5 general analysts in a clinical reasoning wrapper ----
    for cfg in CLINICAL_AGENTS:
        full_prompt = (
            "You are a careful clinical reasoning assistant.\n"
            "You will be given a patient–clinician dialogue.\n"
            "Your job is to:\n"
            "- Extract key symptoms and risk factors\n"
            "- Identify any red-flag or emergency findings\n"
            "- Suggest next steps (tests, monitoring, escalation)\n\n"
            f"Use the following perspective: {cfg['role']}\n"
            "Do NOT include internal reasoning or chain-of-thought.\n\n"
            "Dialogue:\n"
            f"{dialogue}\n\n"
            "Respond with a structured note (VISIBLE TEXT ONLY):\n"
            "- Key findings\n"
            "- Main concerns\n"
            "- Recommended actions or diagnostic tests\n"
        )
        answer = call_flash(full_prompt, temperature=cfg["temperature"], max_tokens=512)
        agent_outputs[cfg["name"]] = answer

    # ---- 2. Chief of Medicine Judge ----
    judge_lines: List[str] = [
        "You are the Chief of Medicine at a large academic hospital.",
        "You will receive:",
        "1) The full patient dialogue",
        "2) Notes from 5 clinical analysts with different reasoning styles\n",
        "Your task: synthesize a SAFE and ACCURATE clinical assessment.\n",
        "Dialogue:",
        dialogue,
        "\nAnalyst notes:",
    ]

    for name, text in agent_outputs.items():
        judge_lines.append(f"\n### {name}\n{text}")

    judge_lines.append(
        "\nReturn ONLY the following structure (no extra commentary):\n\n"
        "ASSESSMENT:\n"
        "- <summary of symptoms, findings, red flags>\n\n"
        "IMPRESSION:\n"
        "- <likely diagnosis or differential>\n\n"
        "PLAN:\n"
        "- <next steps: tests, monitoring, escalation>\n"
        "- <include any MUST-NOT-MISS actions like ER transfer>\n"
    )

    final_answer = call_pro("\n".join(judge_lines), max_tokens=1024)

    return agent_outputs, final_answer
