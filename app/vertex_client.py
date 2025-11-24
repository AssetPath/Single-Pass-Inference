import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

PROJECT_ID = "single-pass-inference-comp-647"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

flash_model = GenerativeModel("gemini-2.5-flash")
pro_model = GenerativeModel("gemini-2.5-pro")


def call_flash(prompt: str, temperature: float = 0.4, max_tokens: int = 512) -> str:
    cfg = GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    response = flash_model.generate_content(prompt, generation_config=cfg)
    # robust access to text
    try:
        return response.text
    except ValueError:
        # Fallback: try to inspect candidates manually
        if response.candidates:
            cand = response.candidates[0]
            if getattr(cand, "content", None) and getattr(cand.content, "parts", None):
                parts = cand.content.parts
                return "".join(getattr(p, "text", "") for p in parts)
        # last-resort fallback to avoid crashing pipeline
        return "[no visible text returned – likely hit max tokens on hidden thoughts]"


def call_pro(prompt: str, max_tokens: int = 1024) -> str:
    cfg = GenerationConfig(
        temperature=0.2,
        max_output_tokens=max_tokens,
    )
    response = pro_model.generate_content(prompt, generation_config=cfg)
    try:
        return response.text
    except ValueError:
        if response.candidates:
            cand = response.candidates[0]
            if getattr(cand, "content", None) and getattr(cand.content, "parts", None):
                parts = cand.content.parts
                return "".join(getattr(p, "text", "") for p in parts)
        return "[no visible text returned – likely hit max tokens on hidden thoughts]"
