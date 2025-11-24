# app/orchestrator.py
from typing import Dict, List, Tuple
from app.vertex_client import call_flash, call_pro

AGENTS = [
    {"name": "solver_1", "suffix": "Think step by step and be cautious.", "temperature": 0.4},
    {"name": "solver_2", "suffix": "Try an alternative approach if one comes to mind.", "temperature": 0.6},
    {"name": "solver_3", "suffix": "Double-check any arithmetic carefully.", "temperature": 0.3},
    {"name": "solver_4", "suffix": "Look for edge cases that might break naive solutions.", "temperature": 0.5},
    {"name": "solver_5", "suffix": "Be concise and focus on the final numeric answer.", "temperature": 0.4},
]


def run_single_pass_generalist(problem: str):
    agent_outputs = {}

    for cfg in AGENTS:
        full_prompt = (
            "You are a generalist reasoning assistant solving math word problems.\n"
            f"{cfg['suffix']}\n\n"
            f"Problem:\n{problem}"
        )
        answer = call_flash(full_prompt, temperature=cfg["temperature"], max_tokens=512)
        agent_outputs[cfg["name"]] = answer

    # 2) Build judge prompt
    judge_prompt_lines: List[str] = [
        "You are a careful generalist judge.",
        "You are given several candidate solutions from different solvers.",
        "Your tasks:",
        "1. Check which solution is most correct and consistent.",
        "2. If there are mistakes, correct them.",
        "3. Output a single final answer and a short explanation.",
        "",
        f"Original problem:\n{problem}\n",
        "Candidate solutions:\n",
    ]

    for name, text in agent_outputs.items():
        judge_prompt_lines.append(f"### {name}\n{text}\n")

    judge_prompt_lines.append(
        "Now choose the best reasoning (or combine them) and give a final answer.\n"
        "Structure your response as:\n"
        "Final answer: <short answer>\n"
        "Explanation: <2–4 sentences of reasoning>."
    )

    judge_prompt = "\n".join(judge_prompt_lines)
    final_answer = call_pro(judge_prompt)

    return agent_outputs, final_answer
