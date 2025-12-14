# Single-Pass-Inference
Final Project COMP 647

## Quickstart Quantitative Summarization Pipeline Demo

Run the quantitative reasoning evaluation with:

```
python -m eval.run_eval --data eval/gsm8k.jsonl --mode both --limit 200
```

This demo evaluates the single-pass reflective ensemble against standard ensemble baselines on general reasoning tasks.

### Input Question (Example: GSM8K)
```
A bookstore sold 45 books on Monday and 38 books on Tuesday.
Each book costs $12.
How much money did the bookstore make in total?
```

### Solver Outputs (Parallel Agents)

```
===== QUANTITATIVE SOLVER OUTPUTS (5 agents) =====

--- arithmetic_solver ---
Reasoning: Total books sold = 45 + 38 = 83. Revenue = 83 * 12.
Answer: 996

--- constraint_solver ---
Reasoning: Combine sales from both days, then multiply by price per book.
Answer: 996

--- python_solver ---
Reasoning: Executed calculation: (45 + 38) * 12
Answer: 996

--- verbal_reasoning_solver ---
Reasoning: First sum the books sold across days, then compute total revenue.
Answer: 996

--- sanity_check_solver ---
Reasoning: Result is under $1000, which is reasonable for under 100 books at $12 each.
Answer: 996
```

### Reflective Judge Output

```
===== REFLECTIVE ENSEMBLE FINAL ANSWER =====

Final Answer: 996

Explanation:
All solvers agree on the arithmetic and constraints.
No conflicting assumptions detected.
The final answer is consistent with dimensional and sanity checks.
```
### Quantitative Evaluation Results

The reflective ensemble is evaluated against three baselines:

Single Model
Majority Vote
Oracle Best-of-K

Accuracy is computed as exact match of the final answer.

### Accuracy Summary (GSM8K Example)
```
================================================================================
QUANTITATIVE EVALUATION SUMMARY
================================================================================
Single Model Accuracy:        0.460
Majority Vote Accuracy:       0.400
Oracle Best-of-K Accuracy:    0.484
Reflective Ensemble Accuracy: 0.944
================================================================================
```

### Accuracy Across All Domains

```
================================================================================
ACCURACY SUMMARY ACROSS FIVE DOMAINS
================================================================================
GSM8K         | Single: 0.460 | Vote: 0.400 | Oracle: 0.484 | Ensemble: 0.944
MATH          | Single: 0.113 | Vote: 0.193 | Oracle: 0.200 | Ensemble: 0.753
Financial     | Single: 0.240 | Vote: 0.312 | Oracle: 0.360 | Ensemble: 0.920
Medical       | Single: 0.420 | Vote: 0.760 | Oracle: 0.840 | Ensemble: 1.000
Engineering   | Single: 0.500 | Vote: 0.796 | Oracle: 0.800 | Ensemble: 0.940
================================================================================

```
### Why Reflective Synthesis Works

- Majority vote reduces variance but cannot fix flawed reasoning
- Oracle selection cannot exceed the best individual solver
- The reflective judge:
  - reconciles partial derivations
  - resolves conflicting assumptions
  - enforces arithmetic and dimensional sanity checks

This enables one-shot synthesis that often exceeds every individual solver.

### Cost Efficiency
All quantitative evaluations run at sub-cent cost per question using:

- Gemini 2.5 Flash for parallel solvers
- Gemini 2.5 Pro for the reflective judge
  
The single-pass design avoids iterative token overhead while preserving high accuracy.

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

## Clinical Pipeline Evaluation Results (first 30 dialogues)
```
==========================================================================================
CLINICAL AGENT EVALUATION SUMMARY
==========================================================================================
EMERGENCY                 | Header Accuracy: 76.67% | Average Text Similarity: 79.93 / 100
NURSE                     | Header Accuracy: 76.67% | Average Text Similarity: 80.10 / 100
PHARMACIST                | Header Accuracy: 73.33% | Average Text Similarity: 78.67 / 100
PRIMARY_CARE              | Header Accuracy: 70.00% | Average Text Similarity: 84.43 / 100
SPECIALIST                | Header Accuracy: 73.33% | Average Text Similarity: 81.60 / 100
CHIEF_OF_MEDICINE         | Header Accuracy: 76.67% | Average Text Similarity: 82.00 / 100
==========================================================================================
```

### Sample Output From LLM Evaluator 
Location: 'eval/results/clinical/eval_clinical_agents_vs_gt_llm.csv'
```
ID,Agent,Header Match,Text Similarity,Explanation
0,primary_care,True,95.0,"The score is high as the prediction accurately captures the patient's demographics, past medical history, stability of conditions, and review of systems. It only omits the minor detail that the patient has been followed by Dr. Kumar."
```
