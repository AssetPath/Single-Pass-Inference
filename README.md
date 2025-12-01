# Single-Pass-Inference
Final Project COMP 647

## Example Clinical Demo

### Input Dialogue
```text
Patient: I've had chest pain for about 3 hours. It started while I was resting.
Doctor: Where exactly is the pain and does it go anywhere?
Patient: It's in the center of my chest and goes into my left arm. I'm also a bit short of breath.
Doctor: Any sweating, nausea, or lightheadedness?
Patient: Yes, I'm sweating a lot and I feel nauseous.
Doctor: Do you have a history of heart disease, high blood pressure, or diabetes?
Patient: I have high blood pressure and high cholesterol.
```

### Demo Output
```text
===== CLINICAL AGENT SUMMARIES (5 agents) =====

--- primary_care ---
Section Header: genhx
Section Text: Patient presents with chest pain for approximately 3 hours, which started at rest. The pain is located in the center of the chest and radiates to the left arm. Associated symptoms include shortness of breath, significant sweating, and nausea. Patient has a history of high blood pressure and high cholesterol.

--- emergency ---
Section Header: genhx
Section Text: Patient presents with 3 hours of central chest pain radiating to the left arm, which started at rest. Associated symptoms include shortness of breath, significant sweating, and nausea. Patient has a history of hypertension and hypercholesterolemia.

--- specialist ---
Section Header: genhx
Section Text: The patient presents with acute onset chest pain, experienced for approximately 3 hours, which began while resting. The pain is localized to the center of the chest and radiates to the left arm. Associated symptoms include shortness of breath, significant sweating, and nausea. The patient has a history of hypertension and hypercholesterolemia.

--- pharmacist ---
Section Header: genhx
Section Text: Patient presents with 3 hours of central chest pain, radiating to the left arm, which started at rest. Associated symptoms include shortness of breath, diaphoresis, and nausea. Patient has a history of hypertension and hypercholesterolemia.

--- nurse ---
Section Header: genhx
Section Text: Patient reports 3 hours of central chest pain that started at rest, radiating to the left arm. Associated symptoms include shortness of breath, significant sweating, and nausea. Patient has a history of high blood pressure and high cholesterol.

===== CHIEF OF MEDICINE FINAL SUMMARY =====

Section Header: History of Present Illness
Section Text: The patient presents with acute onset of central chest pain that started at rest approximately 3 hours ago. The pain is located in the center of the chest
```