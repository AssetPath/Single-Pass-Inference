# app/orchestrator.py
import re
from typing import Dict, List, Tuple
from app.vertex_client import call_flash, call_pro


# ============================================================
#  GENERAL REASONING AGENTS (used for math)
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
#  CLINICAL PIPELINE (CLINICAL AGENTS + CHIEF OF MEDICINE)
# ============================================================


# --------- Clinical agents (for patient–doctor dialogue) ----------

CLINICAL_AGENTS = [
    {
        "name": "primary_care",
        "role": "You are a primary care physician focusing on overall patient health, chronic conditions, and longitudinal care.",
        "temperature": 0.4,
    },
    {
        "name": "emergency",
        "role": "You are an emergency physician focusing on acute symptoms, red flags, and urgent findings.",
        "temperature": 0.4,
    },
    {
        "name": "specialist",
        "role": "You are a specialist (e.g., cardiologist or neurologist) focusing on organ-specific concerns relevant to the patient’s presentation.",
        "temperature": 0.4,
    },
    {
        "name": "pharmacist",
        "role": "You are a clinical pharmacist focusing on medications, interactions, contraindications, and medication-related risks.",
        "temperature": 0.5,
    },
    {
        "name": "nurse",
        "role": "You are an experienced bedside nurse focusing on patient-reported symptoms, safety, and functional status.",
        "temperature": 0.5,
    },
]

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


def run_clinical_single_pass_clinical(
    dialogue: str,
) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
    """
    Run single-section clinical summarization:
    1) Each agent produces {agent_name, section_header, section_text} as strings
    2) Chief of Medicine merges the 5 agent outputs + dialogue into final summary
    """

    agent_outputs: List[Dict[str, str]] = []

    # ---- 1. Run the 5 generalist agents ----
    for cfg in CLINICAL_AGENTS:
        full_prompt = (
            "You are a clinical summarization assistant.\n"
            "You will summarize the following patient–doctor dialogue into a single structured section.\n"
            "Include ALL clinically relevant details from the dialogue, even if missing from the agents.\n\n"
            "Instructions:\n"
            f"- Allowed section headers (choose one exactly): {SECTION_HEADERS_WITH_DESCRIPTIONS}\n"
            "- Respond EXACTLY as:\n"
            "  Section Header: <header>\n"
            "  Section Text: <summary text>\n"
            "- Do NOT include code fences, JSON, markdown, extra commentary, or extra fields.\n"
            f"Perspective: {cfg['role']}\n"
            f"Dialogue:\n{dialogue}\n"
            "- Do NOT return 'unknown'. Always pick the closest matching allowed header.\n"
        )

        answer = call_flash(
            full_prompt, temperature=cfg["temperature"], max_tokens=512
        ).strip()

        # ---- Robust parsing ----
        header_match = re.search(r"Section Header\s*:\s*(.+)", answer, re.IGNORECASE)
        section_header = header_match.group(1).strip() if header_match else "unknown"

        # Grab everything after 'Section Text:' as the summary (multi-line)
        text_match = re.search(
            r"Section Text\s*:\s*(.+)", answer, re.IGNORECASE | re.DOTALL
        )
        section_text = text_match.group(1).strip() if text_match else ""

        agent_outputs.append(
            {
                "agent_name": cfg["name"],
                "section_header": section_header,
                "section_text": section_text,
            }
        )

    # ---- 2. Chief of Medicine ----
    agent_summaries_text = "\n".join(
        [
            f"{a['agent_name']}: {a['section_header']} - {a['section_text']}"
            for a in agent_outputs
        ]
    )

    chief_prompt = (
        "You are the Chief of Medicine at a large academic hospital.\n"
        "You are given the original patient–doctor dialogue and multiple agent summaries.\n"
        "Task:\n"
        "- Create a single, authoritative summary of the patient encounter.\n"
        "- Use the agent summaries only as guidance to understand what is potentially important; "
        "- Include ALL clinically relevant details from the dialogue, even if missing from the agents.\n"
        "- Choose the most appropriate section header from the allowed list exactly as provided.\n"
        "- Do NOT return 'unknown'. Always pick the closest matching allowed header.\n"
        "- Respond ONLY in this exact format:\n"
        "  Section Header: <header>\n"
        "  Section Text: <summary text>\n"
        "- Do NOT include code fences, JSON, markdown, or extra commentary.\n"
        f"Dialogue:\n{dialogue}\n"
        f"Agent summaries:\n{agent_summaries_text}\n"
    )

    final_answer = call_pro(chief_prompt, max_tokens=1800).strip()

    # Robust parsing
    header_match = re.search(r"Section Header\s*:\s*(.+)", final_answer, re.IGNORECASE)
    text_match = re.search(
        r"Section Text\s*:\s*(.+)", final_answer, re.IGNORECASE | re.DOTALL
    )

    final_summary = {
        "section_header": header_match.group(1).strip() if header_match else "unknown",
        "section_text": text_match.group(1).strip() if text_match else "",
    }

    return agent_outputs, final_summary
