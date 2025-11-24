# eval/metrics.py
import re
from typing import Optional


def normalize_text(text: str) -> str:
    """Lowercase and strip whitespace for loose string comparison."""
    return " ".join(text.strip().lower().split())


def extract_last_number(text: str) -> Optional[str]:
    """
    Extract the last integer or decimal from the text.
    Used for math QA like GSM8K.
    """
    if not text:
        return None
    # Allow negative numbers and decimals
    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    if not matches:
        return None
    return matches[-1]


def numeric_match(pred: str, gold: str) -> bool:
    """
    Compare prediction and gold by their last numeric value.
    If parse fails, fall back to normalized string exact match.
    """
    gold_num = extract_last_number(gold)
    pred_num = extract_last_number(pred)

    if gold_num is not None and pred_num is not None:
        return gold_num == pred_num

    # Fallback: normalized string match
    return normalize_text(pred) == normalize_text(gold)
