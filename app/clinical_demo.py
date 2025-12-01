# app/clinical_demo.py

from app.orchestrator import run_clinical_single_pass


def main():
    # Example patient–doctor dialogue
    dialogue = """
    Patient: I've had chest pain for about 3 hours. It started while I was resting.
    Doctor: Where exactly is the pain and does it go anywhere?
    Patient: It's in the center of my chest and goes into my left arm. I'm also a bit short of breath.
    Doctor: Any sweating, nausea, or lightheadedness?
    Patient: Yes, I'm sweating a lot and I feel nauseous.
    Doctor: Do you have a history of heart disease, high blood pressure, or diabetes?
    Patient: I have high blood pressure and high cholesterol.
    """

    # Run the single-pass clinical ensemble
    agents, final = run_clinical_single_pass(dialogue)

    print("===== CLINICAL ANALYST OUTPUTS (5 general agents) =====")
    for name, text in agents.items():
        print(f"\n--- {name} ---\n{text.strip()}")

    print("\n\n===== CHIEF OF MEDICINE (JUDGE) OUTPUT =====")
    print(final.strip())


if __name__ == "__main__":
    main()
