# Single-Pass-Inference
Final Project COMP 647

## Quickstart Clinical Summarization Pipeline Demo
Run the clinical pipeline demo with:
```
python -m app.clinical_demo   
```
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
Section Text: The patient presents with chest pain for 3 hours, which started at rest. The pain is located in the center of the chest and radiates to the left arm. Associated symptoms include shortness of breath, significant sweating, and nausea. The patient has a past medical history of high blood pressure and high cholesterol.

--- emergency ---
Section Header: genhx
Section Text: The patient presents with acute onset central chest pain for 3 hours, which started while resting and radiates to the left arm. Associated symptoms include shortness of breath, significant sweating, and nausea. The patient has a history of high blood pressure and high cholesterol.

--- specialist ---
Section Header: genhx
Section Text: The patient presents with chest pain for approximately 3 hours, which started while resting. The pain is located in the center of the chest and radiates into the left arm. Associated symptoms include shortness of breath, significant sweating, and nausea. The patient reports a history of high blood pressure and high cholesterol.

--- pharmacist ---
Section Header: genhx
Section Text: Patient presents with 3 hours of central chest pain radiating to the left arm, accompanied by shortness of breath, sweating, and nausea. Patient has a history of hypertension and hypercholesterolemia.

--- nurse ---
Section Header: genhx
Section Text: Patient presents with chest pain for 3 hours, which started at rest. The pain is located in the center of her chest and radiates to her left arm. She also reports shortness of breath, significant sweating, and nausea. Her past medical history includes high blood pressure and high cholesterol.

===== CHIEF OF MEDICINE FINAL SUMMARY =====

Section Header: genhx
Section Text: The patient presents with a 3-hour history of central chest pain that started at rest. The pain radiates to the left arm and is associated with shortness of breath, significant sweating, and nausea. The patient has a past medical history of high blood pressure and high cholesterol.
```

## Clinical Pipeline Evaluation Results (first 30 dialogs)
```
==================================================
CLINICAL AGENT EVALUATION SUMMARY
==================================================
EMERGENCY                 | Header Accuracy: 76.67% | Average Text Similarity: 79.93 / 100
NURSE                     | Header Accuracy: 76.67% | Average Text Similarity: 80.10 / 100
PHARMACIST                | Header Accuracy: 73.33% | Average Text Similarity: 78.67 / 100
PRIMARY_CARE              | Header Accuracy: 70.00% | Average Text Similarity: 84.43 / 100
SPECIALIST                | Header Accuracy: 73.33% | Average Text Similarity: 81.60 / 100
CHIEF_OF_MEDICINE         | Header Accuracy: 76.67% | Average Text Similarity: 82.00 / 100
==================================================
```