# app/clinical_demo.py

from app.orchestrator import run_clinical_single_pass_clinical


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

    # Run the single-pass clinical ensemble (with clinical agents)
    agent_outputs, final_summary = run_clinical_single_pass_clinical(dialogue)

    print("\n===== CLINICAL AGENT SUMMARIES (5 agents) =====")
    for agent_dict in agent_outputs:
        print(f"\n--- {agent_dict['agent_name']} ---")
        print(f"Section Header: {agent_dict['section_header']}")
        print(f"Section Text: {agent_dict['section_text']}")

    print("\n===== CHIEF OF MEDICINE FINAL SUMMARY =====")
    print(f"\nSection Header: {final_summary['section_header']}")
    print(f"Section Text: {final_summary['section_text']}")


if __name__ == "__main__":
    main()
