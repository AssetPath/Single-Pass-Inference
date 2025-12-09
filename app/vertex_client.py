import time
from typing import Dict, Optional, Tuple, Union

import vertexai
from google.api_core.exceptions import ServiceUnavailable
from vertexai.generative_models import GenerativeModel, GenerationConfig

PROJECT_ID = "single-pass-inference-comp-647"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

flash_model = GenerativeModel("gemini-2.5-flash")
pro_model = GenerativeModel("gemini-2.5-pro")


def _safe_text(response) -> str:
    """
    Robustly extract text from a Gemini response.
    """
    try:
        return response.text
    except Exception:
        try:
            if getattr(response, "candidates", None):
                cand = response.candidates[0]
                if getattr(cand, "content", None) and getattr(cand.content, "parts", None):
                    parts = cand.content.parts
                    return "".join(getattr(p, "text", "") for p in parts)
        except Exception:
            pass
        return "[no visible text returned – likely hit max tokens on hidden thoughts]"


def _extract_usage(meta) -> Dict[str, Optional[int]]:
    """
    Normalize usage metadata into a simple dict:

      {
        "input_tokens": int | None,
        "output_tokens": int | None,
        "total_tokens": int | None
      }
    """
    if meta is None:
        return {
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
        }

    # meta can be an object or a dict depending on SDK version
    def _get(field: str):
        if hasattr(meta, field):
            return getattr(meta, field)
        if isinstance(meta, dict):
            return meta.get(field)
        return None

    inp = _get("prompt_token_count")
    out = _get("candidates_token_count")
    total = _get("total_token_count")

    if total is None and (inp is not None or out is not None):
        total = (inp or 0) + (out or 0)

    return {
        "input_tokens": inp,
        "output_tokens": out,
        "total_tokens": total,
    }


def call_flash(
    prompt: str,
    temperature: float = 0.4,
    max_tokens: int = 512,
    return_usage: bool = False,
    max_retries: int = 3,
) -> Union[str, Tuple[str, Dict[str, Optional[int]]]]:
    """
    Call Gemini 2.5 Flash.

    - By default returns just the text (backwards compatible).
    - If return_usage=True, returns (text, usage_dict).
    """
    cfg = GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    for attempt in range(max_retries):
        try:
            response = flash_model.generate_content(prompt, generation_config=cfg)
            text = _safe_text(response)
            if return_usage:
                usage = _extract_usage(getattr(response, "usage_metadata", None))
                return text, usage
            return text
        except ServiceUnavailable:
            if attempt == max_retries - 1:
                raise
            # simple linear backoff
            time.sleep(2 * (attempt + 1))


def call_pro(
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.2,
    return_usage: bool = False,
    max_retries: int = 3,
) -> Union[str, Tuple[str, Dict[str, Optional[int]]]]:
    """
    Call Gemini 2.5 Pro (used as judge).

    - By default returns just the text.
    - If return_usage=True, returns (text, usage_dict).
    """
    cfg = GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    for attempt in range(max_retries):
        try:
            response = pro_model.generate_content(prompt, generation_config=cfg)
            text = _safe_text(response)
            if return_usage:
                usage = _extract_usage(getattr(response, "usage_metadata", None))
                return text, usage
            return text
        except ServiceUnavailable:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
