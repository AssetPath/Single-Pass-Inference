# app/orchestrator.py

from typing import Dict, List, Tuple
from app.vertex_client import call_flash, call_pro
import re
from typing import Dict, List, Tuple, Any


def extract_last_number(text: str) -> str | None:
    """Extract the last integer or decimal number from the text."""
    if not text:
        return None
    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    return matches[-1] if matches else None

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

#  DOMAIN-SPECIFIC QUANTITATIVE AGENTS

# General math (GSM8K / MATH)
QUANT_AGENTS = [
    {
        "name": "arith_solver",
        "suffix": (
            "You are a university mathematics lecturer who specializes in arithmetic, "
            "percentages, compounding, and basic quantitative reasoning. "
            "Work slowly and show every intermediate numeric step."
        ),
        "temperature": 0.1,
    },
    {
        "name": "algebra_solver",
        "suffix": (
            "You are a math professor who turns word problems into algebraic equations. "
            "Define variables, write equations, and solve them step by step."
        ),
        "temperature": 0.1,
    },
    {
        "name": "python_solver",
        "suffix": (
            "You are a quantitative analyst who thinks as if writing a short Python script. "
            "Introduce variables, express formulas explicitly, and compute the answer carefully."
        ),
        "temperature": 0.15,
    },
    {
        "name": "readcarefully_solver",
        "suffix": (
            "You are a careful teaching assistant. "
            "First restate the problem in your own words. "
            "List the known quantities and what is being asked before solving."
        ),
        "temperature": 0.1,
    },
    {
        "name": "heuristic_solver",
        "suffix": (
            "You are a senior problem-solving coach. "
            "Focus on sanity checks, magnitude estimates, and catching subtle misreads."
        ),
        "temperature": 0.2,
    },
]

# Finance / hedge fund math
FIN_AGENTS = [
    {
        "name": "hf_quant",
        "suffix": (
            "You are a hedge fund quantitative researcher. "
            "You specialize in compounding returns, leverage, beta hedging, and risk metrics."
        ),
        "temperature": 0.1,
    },
    {
        "name": "risk_manager",
        "suffix": (
            "You are a senior risk manager. "
            "Think in terms of volatility, Value at Risk (VaR), and exposure sizing."
        ),
        "temperature": 0.1,
    },
    {
        "name": "portfolio_manager",
        "suffix": (
            "You are a long/short equity portfolio manager. "
            "Reason using notions of gross exposure, net exposure, and betas."
        ),
        "temperature": 0.1,
    },
    {
        "name": "derivatives_trader",
        "suffix": (
            "You are an options and futures trader. "
            "You compute payoffs, PnL, and leverage clearly and precisely."
        ),
        "temperature": 0.15,
    },
    {
        "name": "accountant_fin",
        "suffix": (
            "You are a financial accountant. "
            "You check all percentage calculations and cash flows very carefully."
        ),
        "temperature": 0.1,
    },
]

# Medical quantitative calculations (dosing, rates, half-life)
MED_AGENTS = [
    {
        "name": "clin_pharm",
        "suffix": (
            "You are a clinical pharmacist. "
            "You specialize in mg/kg dosing, infusion rates, half-life, and solution concentrations."
        ),
        "temperature": 0.1,
    },
    {
        "name": "icu_nurse",
        "suffix": (
            "You are an ICU nurse. "
            "You set IV pump rates, drip rates, and perform unit conversions very carefully."
        ),
        "temperature": 0.1,
    },
    {
        "name": "med_resident",
        "suffix": (
            "You are a medical resident. "
            "You show each step for dose, volume, and time calculations."
        ),
        "temperature": 0.1,
    },
    {
        "name": "dose_checker",
        "suffix": (
            "You are a safety-focused dose checker. "
            "You verify that doses and rates are within plausible ranges and units."
        ),
        "temperature": 0.1,
    },
    {
        "name": "units_specialist",
        "suffix": (
            "You are a unit-conversion specialist. "
            "You pay extra attention to mg, mcg, mL, %, and time units."
        ),
        "temperature": 0.1,
    },
]

# Engineering quantitative problems (electrical, mechanical, chemical, petroleum)
ENG_AGENTS = [
    {
        "name": "mech_eng",
        "suffix": (
            "You are a mechanical engineer. "
            "You handle forces, work, power, and energy calculations with unit consistency."
        ),
        "temperature": 0.1,
    },
    {
        "name": "elec_eng",
        "suffix": (
            "You are an electrical engineer. "
            "You use Ohm's law, power equations, and basic circuit relations accurately."
        ),
        "temperature": 0.1,
    },
    {
        "name": "chem_eng",
        "suffix": (
            "You are a chemical engineer. "
            "You think in terms of mass balance, concentration, and simple thermodynamics."
        ),
        "temperature": 0.1,
    },
    {
        "name": "petro_eng",
        "suffix": (
            "You are a petroleum engineer. "
            "You reason about flow rates, pressures, and reservoir-style calculations."
        ),
        "temperature": 0.15,
    },
    {
        "name": "eng_sanity",
        "suffix": (
            "You are an engineering sanity-checker. "
            "You ensure units and orders of magnitude make physical sense."
        ),
        "temperature": 0.2,
    },
]

def run_single_pass_with_agents(
    problem: str,
    agents: List[Dict[str, str]],
    domain: str = "general",
) -> Tuple[
    Dict[str, str],              # agent_outputs
    str,                         # judge_text
    Dict[str, Dict[str, Any]],   # per-agent usage
    Dict[str, Any],              # judge usage
]:
    """
    Generic single-pass ensemble:
    - Runs a set of domain-specific agents in parallel (conceptually)
    - Uses a Pro judge to pick or compute the final numeric answer.
    - Returns agent outputs + token usage for analysis.
    """
    agent_outputs: Dict[str, str] = {}
    agent_usage: Dict[str, Dict[str, Any]] = {}

    # Domain description for judge + solvers
    if domain == "financial":
        domain_desc = (
            "You are solving quantitative finance and hedge fund style problems "
            "about returns, leverage, beta hedging, and risk."
        )
    elif domain == "medical":
        domain_desc = (
            "You are solving medical dosage and infusion rate problems. "
            "These involve mg/kg, mL/hr, half-life, and concentration."
        )
    elif domain == "engineering":
        domain_desc = (
            "You are solving engineering problems involving forces, power, circuits, "
            "flow rates, and other physical quantities."
        )
    else:
        domain_desc = "You are solving general quantitative math word problems."

    # 1. Run all solvers with a strict output format
    for cfg in agents:
        full_prompt = (
            f"{domain_desc}\n"
            f"{cfg['suffix']}\n\n"
            "Solve the problem carefully.\n"
            "You must follow this exact output format:\n\n"
            "Reasoning:\n"
            "<step by step reasoning here>\n\n"
            "Final Answer:\n"
            "<single numeric answer, no words besides the number>\n\n"
            "If the answer is not an integer, you may use a decimal or a simplified fraction.\n\n"
            f"Problem:\n{problem}\n"
        )

        answer, usage = call_flash(
            full_prompt,
            temperature=cfg["temperature"],
            max_tokens=512,
            return_usage=True,
        )
        name = cfg["name"]
        agent_outputs[name] = answer
        agent_usage[name] = usage  # <- store per-agent token usage

    # 2. Judge (Gemini Pro)
    judge_lines: List[str] = [
        "You are an expert quantitative evaluation assistant.\n",
        "You will be given a problem and several candidate solutions.\n",
        "Each solution has the format:\n"
        "Reasoning:\n"
        "<step by step reasoning>\n"
        "Final Answer:\n"
        "<number>\n\n",
        "Your task:\n"
        "1. Check whether each solver's reasoning and final numeric answer are mathematically correct.\n"
        "2. Compare the final numeric answers to see which solvers agree.\n"
        "3. Decide which solver is most likely correct.\n"
        "4. If all solvers look unreliable, carefully solve the problem yourself.\n\n",
        "Domain-specific hints:\n"
        "- For financial problems, check compounding vs simple percentages, leverage math, hedging logic, and units (dollars, percentages, years).\n"
        "- For medical problems, check unit conversions (mg, mcg, mL, %), rates (per hour, per minute), and plausible dose ranges.\n"
        "- For engineering problems, check physical units, conservation relations, and whether the magnitude of the answer is realistic.\n"
        "If these hints do not apply, just reason like a careful mathematician.\n\n",
        f"Original problem:\n{problem}\n\n",
        "Candidate solutions:\n",
    ]

    for name, text in agent_outputs.items():
        judge_lines.append(f"### {name}\n{text}\n")

    judge_lines.append(
        "Now decide on the best final numeric answer.\n"
        "If you trust one solver, you may select its final answer.\n"
        "If none are trustworthy, compute your own answer carefully.\n\n"
        "Return your output in exactly this format:\n\n"
        "FINAL_ANSWER: <single numeric answer>\n"
        "JUSTIFICATION: <short explanation of why this answer is most likely correct>\n"
    )

    judge_text, judge_usage = call_pro(
        "\n".join(judge_lines),
        max_tokens=1024,
        return_usage=True,
    )

    return agent_outputs, judge_text, agent_usage, judge_usage


def run_single_pass_generalist(
    problem: str,
) -> Tuple[Dict[str, str], str, Dict[str, Dict[str, Any]], Dict[str, Any]]:
    return run_single_pass_with_agents(problem, QUANT_AGENTS, domain="general")


def run_single_pass_financial(
    problem: str,
) -> Tuple[Dict[str, str], str, Dict[str, Dict[str, Any]], Dict[str, Any]]:
    return run_single_pass_with_agents(problem, FIN_AGENTS, domain="financial")


def run_single_pass_medical(
    problem: str,
) -> Tuple[Dict[str, str], str, Dict[str, Dict[str, Any]], Dict[str, Any]]:
    return run_single_pass_with_agents(problem, MED_AGENTS, domain="medical")


def run_single_pass_engineering(
    problem: str,
) -> Tuple[Dict[str, str], str, Dict[str, Dict[str, Any]], Dict[str, Any]]:
    return run_single_pass_with_agents(problem, ENG_AGENTS, domain="engineering")



# ============================================================
#  CLINICAL PIPELINE 1 (GENERAL ANALYSTS + CHIEF OF MEDICINE)
# ============================================================


def run_clinical_single_pass_general(dialogue: str) -> Tuple[Dict[str, str], str]:
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
            f"Use the following perspective: {cfg['suffix']}\n"
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


# ============================================================
#  CLINICAL PIPELINE 2 (CLINICAL AGENTS + CHIEF OF MEDICINE)
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

    # ---- 1. Run 5 general analysts ----
    for cfg in CLINICAL_AGENTS:
        full_prompt = (
            "You are a clinical summarization assistant.\n"
            "You will summarize the following patient–doctor dialogue into a single structured section.\n\n"
            "Instructions:\n"
            f"- Allowed section headers (choose one): {SECTION_HEADERS_WITH_DESCRIPTIONS}\n"
            "- Respond EXACTLY as:\n"
            "  Section Header: <header>\n"
            "  Section Text: <summary text>\n"
            "- Do NOT include code fences, JSON, markdown, extra commentary, or extra fields.\n"
            f"Perspective: {cfg['role']}\n"
            f"Dialogue:\n{dialogue}\n"
        )

        answer = call_flash(full_prompt, temperature=cfg["temperature"], max_tokens=512)
        answer = answer.strip()

        # Parse simple output format
        lines = answer.splitlines()
        section_header = "unknown"
        section_text = ""
        for line in lines:
            if line.lower().startswith("section header:"):
                section_header = line.split(":", 1)[1].strip()
            elif line.lower().startswith("section text:"):
                section_text = line.split(":", 1)[1].strip()
            else:
                # Append continuation lines to section_text
                if section_text:
                    section_text += " " + line.strip()

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
        "- Merge the agent summaries into a single final summary.\n"
        "- Choose the most appropriate section header from the allowed list.\n"
        "- Respond ONLY in this exact format:\n"
        "  Section Header: <header>\n"
        "  Section Text: <summary text>\n"
        "- Do NOT include code fences, JSON, markdown, or extra commentary.\n"
        f"Dialogue:\n{dialogue}\n"
        f"Agent summaries:\n{agent_summaries_text}\n"
    )

    final_answer = call_pro(chief_prompt, max_tokens=1024)
    final_answer = final_answer.strip()

    # Parse final answer
    final_header = "unknown"
    final_text = ""
    lines = final_answer.splitlines()
    for line in lines:
        if line.lower().startswith("section header:"):
            final_header = line.split(":", 1)[1].strip()
        elif line.lower().startswith("section text:"):
            final_text = line.split(":", 1)[1].strip()
        else:
            if final_text:
                final_text += " " + line.strip()

    final_summary = {
        "section_header": final_header,
        "section_text": final_text,
    }

    return agent_outputs, final_summary
