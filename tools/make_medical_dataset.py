# tools/make_medical_dataset.py

import json
from pathlib import Path

problems = [
    {
        "id": "med_001",
        "problem": (
            "A medication is ordered at 5 mg/kg for a patient who weighs 72 kg. "
            "The medication comes in vials of 40 mg/mL. "
            "How many milliliters should be administered to deliver the ordered dose?"
        ),
        # 5 * 72 = 360 mg; 360 / 40 = 9 mL
        "answer": "9",
    },
    {
        "id": "med_002",
        "problem": (
            "A drug needs to be infused at 8 micrograms per kilogram per minute for a 65 kg patient. "
            "The IV bag contains 400 mg of the drug in 250 mL of solution. "
            "What pump rate in mL/hr should be used, rounded to one decimal?"
        ),
        # Dose = 0.52 mg/min; per hour = 31.2 mg/hr; conc = 1.6 mg/mL; rate = 19.5 mL/hr
        "answer": "19.5",
    },
    {
        "id": "med_003",
        "problem": (
            "A one liter bag of IV fluids (1000 mL) is ordered to run over 8 hours. "
            "The IV set has a drop factor of 20 drops per mL. "
            "What drip rate in drops per minute (gtt/min) should be used, rounded to the nearest whole number?"
        ),
        # 125 mL/hr -> 2.083 mL/min -> 41.67 gtt/min -> 42
        "answer": "42",
    },
    {
        "id": "med_004",
        "problem": (
            "A patient weighs 80 kg and is 1.65 meters tall. "
            "What is the patient's body mass index (BMI), rounded to two decimals?"
        ),
        # 80 / 1.65^2 ≈ 29.38
        "answer": "29.38",
    },
    {
        "id": "med_005",
        "problem": (
            "A nurse prepares an IV infusion that contains 500 mg of a drug in 250 mL of solution. "
            "The infusion is set to run at 30 mL/hr. "
            "How many milligrams of drug does the patient receive per hour?"
        ),
        # 2 mg/mL * 30 = 60 mg/hr
        "answer": "60",
    },
    {
        "id": "med_006",
        "problem": (
            "A drug has a half life of 6 hours. A patient receives a single IV dose that "
            "results in 120 mg of the drug in the body immediately after administration. "
            "Assuming first order elimination and no further dosing, how many milligrams of drug "
            "remain in the body after 18 hours?"
        ),
        # 3 half-lives: 120 * (1/2)^3 = 15 mg
        "answer": "15",
    },
    {
        "id": "med_007",
        "problem": (
            "The recommended adult dose of a drug is 400 mg for a body surface area (BSA) "
            "of 1.8 m^2. A pediatric patient has a BSA of 0.9 m^2. "
            "Using simple BSA scaling, what dose in mg should the child receive?"
        ),
        # 400 * 0.9 / 1.8 = 200 mg
        "answer": "200",
    },
    {
        "id": "med_008",
        "problem": (
            "A pharmacist needs to prepare 80 mL of a 15 percent solution of a drug using a "
            "40 percent stock solution and diluent. "
            "How many milliliters of the 40 percent stock solution should be used?"
        ),
        # C1 V1 = C2 V2 -> V1 = 15 * 80 / 40 = 30 mL
        "answer": "30",
    },
    {
        "id": "med_009",
        "problem": (
            "An IV order is written for 750 mL of normal saline to be infused at 125 mL/hr. "
            "How many hours will it take for the infusion to complete?"
        ),
        # 750 / 125 = 6 hours
        "answer": "6",
    },
    {
        "id": "med_010",
        "problem": (
            "A child weighs 24 kg and is prescribed 30 mg/kg/day of a medication divided into "
            "three equal doses. "
            "How many milligrams should be given in each dose?"
        ),
        # Daily dose = 30 * 24 = 720 mg; per dose = 720 / 3 = 240 mg
        "answer": "240",
    },
    {
        "id": "med_011",
        "problem": (
            "A pharmacist needs to prepare 250 mL of a 10 percent solution of a drug from a "
            "25 percent stock solution. "
            "How many milliliters of the 25 percent stock solution are required?"
        ),
        # V1 = 10 * 250 / 25 = 100 mL
        "answer": "100",
    },
    {
        "id": "med_012",
        "problem": (
            "A medication has a half life of 8 hours. A single IV dose leaves 200 mg of the drug "
            "in the body immediately after administration. "
            "Assuming first order elimination, how many milligrams remain after 24 hours?"
        ),
        # 3 half-lives: 200 * (1/2)^3 = 25 mg
        "answer": "25",
    },
    {
        "id": "med_013",
        "problem": (
            "An order is written for 500 mL of IV fluid to infuse over 5 hours. "
            "The IV tubing has a drop factor of 15 drops per mL. "
            "What is the drip rate in drops per minute (gtt/min), rounded to the nearest whole number?"
        ),
        # 100 mL/hr = 1.6667 mL/min -> 25 gtt/min
        "answer": "25",
    },
    {
        "id": "med_014",
        "problem": (
            "A patient is instructed to take a base dose of 6 units of insulin plus 1 unit "
            "for every 10 grams of carbohydrate in a meal. "
            "If the meal contains 75 grams of carbohydrate, how many units of insulin should be given, "
            "rounded to the nearest whole unit?"
        ),
        # 6 + 75/10 = 13.5 -> 14 units
        "answer": "14",
    },
    {
        "id": "med_015",
        "problem": (
            "A dose of 750 mg of an antibiotic is ordered. The pharmacy supplies vials labeled "
            "250 mg in 5 mL. "
            "How many milliliters of the reconstituted solution are needed to provide the ordered dose?"
        ),
        # 250 mg in 5 mL -> 50 mg/mL; 750 / 50 = 15 mL
        "answer": "15",
    },
    {
        "id": "med_016",
        "problem": (
            "A continuous infusion is ordered at 1.2 mg/kg/hr for a 54 kg patient. "
            "The IV solution contains 100 mg of drug in 50 mL. "
            "What pump rate in mL/hr should be used, rounded to one decimal?"
        ),
        # Dose = 1.2 * 54 = 64.8 mg/hr; conc = 2 mg/mL; rate = 32.4 mL/hr
        "answer": "32.4",
    },
    {
        "id": "med_017",
        "problem": (
            "An IV infusion is running at 30 mL/hr. The solution contains 12 mg/mL of a drug. "
            "How many milligrams of drug does the patient receive over 10 hours?"
        ),
        # 30 * 12 * 10 = 3600 mg
        "answer": "3600",
    },
    {
        "id": "med_018",
        "problem": (
            "A medication is ordered at 7 mg/kg as a single dose for a patient who weighs 92 kg. "
            "The maximum single dose for this medication is 600 mg. "
            "What dose in mg should be administered?"
        ),
        # 7 * 92 = 644 mg, but max is 600 mg
        "answer": "600",
    },
    {
        "id": "med_019",
        "problem": (
            "A solution is prepared by dissolving 90 mg of a drug in 60 mL of fluid. "
            "What is the concentration of the solution expressed as a percent (w/v), "
            "rounded to two decimals?"
        ),
        # 90 mg = 0.09 g; 0.09 g / 60 mL * 100 ≈ 0.15%
        "answer": "0.15",
    },
    {
        "id": "med_020",
        "problem": (
            "A prescription is written for 45 tablets, with instructions to take 3 tablets per day. "
            "For how many days will the prescription last?"
        ),
        # 45 / 3 = 15 days
        "answer": "15",
    },
    {
        "id": "med_021",
        "problem": (
            "Using the Cockcroft Gault equation for a male, estimate creatinine clearance for "
            "a 60 year old man who weighs 80 kg and has a serum creatinine of 1.2 mg/dL. "
            "Use CrCl = (140 - age) × weight / (72 × serum creatinine). "
            "What is the creatinine clearance in mL/min, rounded to one decimal?"
        ),
        # CrCl = (140 - 60) * 80 / (72 * 1.2) ≈ 74.1
        "answer": "74.1",
    },
    {
        "id": "med_022",
        "problem": (
            "Using the Cockcroft Gault equation for a female, estimate creatinine clearance for "
            "a 70 year old woman who weighs 65 kg and has a serum creatinine of 1.0 mg/dL. "
            "Use CrCl = 0.85 × (140 - age) × weight / (72 × serum creatinine). "
            "What is the creatinine clearance in mL/min, rounded to one decimal?"
        ),
        # Base CrCl = (140 - 70) * 65 / (72 * 1.0) ≈ 63.19; female factor 0.85 -> ≈ 53.7
        "answer": "53.7",
    },
    {
        "id": "med_023",
        "problem": (
            "A patient's lab results show sodium 140 mmol/L, chloride 104 mmol/L, "
            "and bicarbonate (HCO3-) 20 mmol/L. "
            "What is this patient's anion gap in mmol/L?"
        ),
        # Anion gap = Na - Cl - HCO3 = 140 - 104 - 20 = 16
        "answer": "16",
    },
    {
        "id": "med_024",
        "problem": (
            "A patient with hyperglycemia has a measured serum sodium of 130 mmol/L and a "
            "serum glucose of 400 mg/dL. "
            "Use the correction formula: corrected Na = measured Na + 1.6 × "
            "((glucose - 100) / 100). "
            "What is the corrected sodium in mmol/L, rounded to one decimal?"
        ),
        # Corrected Na = 130 + 1.6 * (300 / 100) = 130 + 4.8 = 134.8
        "answer": "134.8",
    },
    {
        "id": "med_025",
        "problem": (
            "You want to calculate maintenance IV fluid using the 4 2 1 rule. "
            "For the first 10 kg of weight, give 4 mL/kg/hr. "
            "For the next 10 kg, give 2 mL/kg/hr. "
            "For any remaining kilograms above 20 kg, give 1 mL/kg/hr. "
            "What is the maintenance rate in mL/hr for a 23 kg child?"
        ),
        # 4*10 + 2*10 + 1*3 = 63 mL/hr
        "answer": "63",
    },
    {
        "id": "med_026",
        "problem": (
            "An insulin infusion is prepared by placing 50 units of insulin in 500 mL of saline. "
            "The infusion is running at 8 mL/hr for a patient. "
            "How many units of insulin does the patient receive in 12 hours, "
            "rounded to one decimal?"
        ),
        # Conc = 50 / 500 = 0.1 units/mL; hourly dose = 0.1 * 8 = 0.8 units/hr
        # 12 hours -> 9.6 units
        "answer": "9.6",
    },
    {
        "id": "med_027",
        "problem": (
            "A medication has a half life of 6 hours. A single IV dose leaves 200 mg "
            "of the drug in the body immediately after administration. "
            "Assuming first order elimination and no further dosing, after how many hours will "
            "only 25 mg of the drug remain in the body?"
        ),
        # 200 -> 100 -> 50 -> 25: three half-lives; 3 * 6 = 18 hours
        "answer": "18",
    },
    {
        "id": "med_028",
        "problem": (
            "A patient receives a 500 mg IV loading dose of a medication, followed by a "
            "continuous infusion of 60 mg/hr. "
            "Ignoring elimination, after how many hours will the patient have received "
            "a total of 1,000 mg of the drug, rounded to one decimal?"
        ),
        # Additional dose needed = 1000 - 500 = 500 mg; time = 500 / 60 ≈ 8.3 hours
        "answer": "8.3",
    },
    {
        "id": "med_029",
        "problem": (
            "A child who weighs 18 kg is prescribed 15 mg/kg of a liquid medication. "
            "The concentration of the liquid is 150 mg in 5 mL. "
            "How many milliliters should be given for one dose?"
        ),
        # Dose = 15 * 18 = 270 mg; 150 mg in 5 mL -> 30 mg/mL; 270 / 30 = 9 mL
        "answer": "9",
    },
    {
        "id": "med_030",
        "problem": (
            "A 1,500 mL bag of IV fluids is ordered to run over 12 hours. "
            "The tubing has a drop factor of 15 drops per mL. "
            "What is the drip rate in drops per minute (gtt/min), "
            "rounded to the nearest whole number?"
        ),
        # 1500 / 12 = 125 mL/hr; 125 / 60 ≈ 2.083 mL/min; 2.083 * 15 ≈ 31 gtt/min
        "answer": "31",
    },
    {
        "id": "med_031",
        "problem": (
            "A neonate weighing 4 kg is receiving D10W (10 percent dextrose, "
            "which is 100 mg/mL of glucose) at 18 mL/hr. "
            "What is the glucose infusion rate (GIR) in mg/kg/min, rounded to one decimal?"
        ),
        # GIR = (rate * conc) / (weight * 60) = 18 * 100 / (4 * 60) = 7.5 mg/kg/min
        "answer": "7.5",
    },
    {
        "id": "med_032",
        "problem": (
            "A provider orders potassium chloride (KCl) 25 mEq to be added to a 500 mL bag "
            "of normal saline. "
            "What is the final concentration of KCl in mEq/L, assuming the volume stays at 500 mL?"
        ),
        # 25 mEq in 0.5 L -> 50 mEq/L
        "answer": "50",
    },
    {
        "id": "med_033",
        "problem": (
            "A 70 kg adult needs an IV loading dose of a drug. "
            "The target plasma concentration is 10 mg/L and the volume of distribution (Vd) "
            "is 0.7 L/kg. The drug is given intravenously, so bioavailability is 1. "
            "What loading dose in mg should be given?"
        ),
        # LD = target * Vd * weight = 10 * 0.7 * 70 = 490 mg
        "answer": "490",
    },
    {
        "id": "med_034",
        "problem": (
            "A 60 kg adult needs an oral loading dose of a drug. "
            "The target plasma concentration is 8 mg/L, the volume of distribution (Vd) "
            "is 0.6 L/kg, and oral bioavailability is 0.5. "
            "What oral loading dose in mg should be given?"
        ),
        # LD = target * Vd * weight / F = 8 * 0.6 * 60 / 0.5 = 576 mg
        "answer": "576",
    },
    {
        "id": "med_035",
        "problem": (
            "A drug has a clearance of 5 L/hr. The target steady state plasma concentration "
            "is 4 mg/L. The drug is administered as a continuous IV infusion. "
            "What infusion rate in mg/hr will achieve the target concentration?"
        ),
        # Rate = Cl * Css = 5 * 4 = 20 mg/hr
        "answer": "20",
    },
    {
        "id": "med_036",
        "problem": (
            "A patient's blood glucose is measured as 180 mg/dL. "
            "The molecular weight of glucose is 180 g/mol. "
            "Convert this glucose value to mmol/L. "
            "What is the glucose concentration in mmol/L?"
        ),
        # 180 mg/dL = 1800 mg/L = 1.8 g/L; 1.8 / 180 = 0.01 mol/L = 10 mmol/L
        "answer": "10",
    },
    {
        "id": "med_037",
        "problem": (
            "A patient's lab results are: urinary sodium 40 mEq/L, plasma sodium 140 mEq/L, "
            "urinary creatinine 100 mg/dL, and plasma creatinine 1.0 mg/dL. "
            "Use the fractional excretion of sodium (FeNa) formula:\n"
            "FeNa percent = (Urine Na × Plasma Cr) / (Plasma Na × Urine Cr) × 100. "
            "What is the FeNa in percent, rounded to two decimals?"
        ),
        # FeNa = (40 * 1) / (140 * 100) * 100 ≈ 0.29%
        "answer": "0.29",
    },
    {
        "id": "med_038",
        "problem": (
            "A patient has a measured serum calcium of 7.8 mg/dL and a serum albumin of 2.5 g/dL. "
            "Use the corrected calcium formula: corrected Ca = measured Ca + 0.8 × (4.0 - albumin). "
            "What is the corrected calcium in mg/dL?"
        ),
        # Corrected Ca = 7.8 + 0.8 * (4 - 2.5) = 7.8 + 1.2 = 9.0
        "answer": "9.0",
    },
    {
        "id": "med_039",
        "problem": (
            "An IV vasopressor is ordered at 10 micrograms per kilogram per minute for a "
            "90 kg patient. The IV bag contains 200 mg of the drug in 250 mL of solution. "
            "The maximum allowable dose is 50 mg/hr. "
            "What pump rate in mL/hr should be used to stay at the maximum allowable dose, "
            "rounded to one decimal?"
        ),
        # At 10 mcg/kg/min: dose ≈ 54 mg/hr, above max; cap at 50 mg/hr
        # Conc = 200 / 250 = 0.8 mg/mL; rate = 50 / 0.8 = 62.5 mL/hr
        "answer": "62.5",
    },
    {
        "id": "med_040",
        "problem": (
            "A patient's blood pressure is 110/70 mmHg. "
            "Use the approximate formula for mean arterial pressure (MAP): "
            "MAP ≈ (SBP + 2 × DBP) / 3. "
            "What is the MAP in mmHg, rounded to one decimal?"
        ),
        # MAP = (110 + 2*70) / 3 = 250 / 3 ≈ 83.3
        "answer": "83.3",
    },
    {
        "id": "med_041",
        "problem": (
            "An adult chemotherapy regimen recommends 75 mg/m^2 of a drug. "
            "The patient's body surface area (BSA) is 1.9 m^2. "
            "What dose in mg should be given?"
        ),
        # Dose = 75 * 1.9 = 142.5 mg
        "answer": "142.5",
    },
    {
        "id": "med_042",
        "problem": (
            "A patient weighs 154 pounds. A medication is ordered at 5 micrograms per kilogram "
            "per minute. The IV bag contains 400 mg of drug in 250 mL. "
            "Convert the weight to kilograms using 1 kg = 2.2 lb, then calculate "
            "the pump rate in mL/hr needed to deliver the ordered dose, "
            "rounded to one decimal."
        ),
        # Weight = 154 / 2.2 = 70 kg
        # Dose = 5 mcg/kg/min * 70 = 350 mcg/min = 0.35 mg/min = 21 mg/hr
        # Conc = 400 / 250 = 1.6 mg/mL; rate = 21 / 1.6 ≈ 13.1 mL/hr
        "answer": "13.1",
    },
    {
        "id": "med_043",
        "problem": (
            "An IV antibiotic is prepared as 1,000 mg in 250 mL of solution. "
            "The infusion is set to run at 50 mL/hr for 24 hours. "
            "How many milligrams of antibiotic does the patient receive in 24 hours?"
        ),
        # Conc = 1000 / 250 = 4 mg/mL; 4 * 50 = 200 mg/hr; 200 * 24 = 4800 mg
        "answer": "4800",
    },
    {
        "id": "med_044",
        "problem": (
            "A patient weighs 180 pounds and is 5 feet 9 inches tall. "
            "Convert the weight to kilograms using 1 kg = 2.2 lb and the height to meters "
            "using 1 inch = 2.54 cm (5 feet 9 inches is 69 inches). "
            "What is the patient's body mass index (BMI), rounded to two decimals?"
        ),
        # Weight ≈ 81.82 kg; height ≈ 1.7526 m; BMI ≈ 26.64
        "answer": "26.64",
    },
    {
        "id": "med_045",
        "problem": (
            "A patient's blood pressure is 135/85 mmHg. "
            "Use the approximate formula for mean arterial pressure (MAP): "
            "MAP ≈ (SBP + 2 × DBP) / 3. "
            "What is the MAP in mmHg, rounded to two decimals?"
        ),
        # MAP = (135 + 2*85) / 3 = 305 / 3 ≈ 101.67
        "answer": "101.67",
    },
    {
        "id": "med_046",
        "problem": (
            "A dietitian estimates that a hospitalized patient requires 30 kcal/kg/day. "
            "If the patient weighs 70 kg, what is the total daily caloric requirement in kilocalories?"
        ),
        # 30 * 70 = 2100 kcal/day
        "answer": "2100",
    },
    {
        "id": "med_047",
        "problem": (
            "A microdrip IV tubing delivers 60 drops per mL. An order is written to infuse "
            "25 mL/hr of a medication. "
            "What is the drip rate in drops per minute (gtt/min)?"
        ),
        # 25 mL/hr = 25/60 mL/min; * 60 gtt/mL = 25 gtt/min
        "answer": "25",
    },
    {
        "id": "med_048",
        "problem": (
            "A patient's hemoglobin decreases from 14.0 g/dL to 9.8 g/dL. "
            "By what percentage did the hemoglobin decrease, "
            "rounded to one decimal place?"
        ),
        # Decrease = 14.0 - 9.8 = 4.2; percent = 4.2 / 14 * 100 ≈ 30.0%
        "answer": "30.0",
    },
    {
        "id": "med_049",
        "problem": (
            "A 1,000 mL bag of IV fluids is set to run at 75 mL/hr. "
            "Ignoring any residual volume, how many hours will it take for the bag to empty, "
            "rounded to one decimal?"
        ),
        # Time = 1000 / 75 ≈ 13.3 hours
        "answer": "13.3",
    },
    {
        "id": "med_050",
        "problem": (
            "A pediatric medication is normally dosed at 6 mg/kg/day. "
            "Due to renal impairment, the dose should be reduced by 25 percent. "
            "For a child who weighs 32 kg, what is the adjusted daily dose in mg?"
        ),
        # Normal dose = 6 * 32 = 192 mg; reduced by 25% -> 192 * 0.75 = 144 mg
        "answer": "144",
    },
]

out_path = Path("data/medical_quant.jsonl")
out_path.parent.mkdir(parents=True, exist_ok=True)

with out_path.open("w", encoding="utf-8") as f:
    for p in problems:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Wrote {len(problems)} medical problems to {out_path}")
