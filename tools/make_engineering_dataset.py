# tools/make_engineering_dataset.py

import json
from pathlib import Path

problems = [
    {
        "id": "eng_001",
        "problem": (
            "A constant force of 250 N is applied to move a crate 6 meters along a level floor. "
            "Ignoring friction, how much work in joules is done on the crate?"
        ),
        # W = F * d = 250 * 6 = 1500 J
        "answer": "1500",
    },
    {
        "id": "eng_002",
        "problem": (
            "An electric heater draws 8 A from a 230 V supply. "
            "Assuming a purely resistive load, how much power in watts does the heater consume?"
        ),
        # P = V * I = 230 * 8 = 1840 W
        "answer": "1840",
    },
    {
        "id": "eng_003",
        "problem": (
            "A resistor has a resistance of 20 ohms and carries a current of 3 A. "
            "What is the voltage across the resistor in volts?"
        ),
        # V = I * R = 3 * 20 = 60 V
        "answer": "60",
    },
    {
        "id": "eng_004",
        "problem": (
            "Water flows through a pipe at a volumetric flow rate of 0.015 m^3/s. "
            "How many liters per minute is this, rounded to the nearest whole number?"
        ),
        # 0.015 m^3/s = 15 L/s; per minute = 15 * 60 = 900 L/min
        "answer": "900",
    },
    {
        "id": "eng_005",
        "problem": (
            "A 2 kW motor operates at full power for 3.5 hours. "
            "How much energy in kilowatt-hours does it consume?"
        ),
        # E = P * t = 2 * 3.5 = 7 kWh
        "answer": "7",
    },
    {
        "id": "eng_006",
        "problem": (
            "A simply supported beam carries a uniformly distributed load of 4 kN/m over a span of 6 m. "
            "What is the total load on the beam in kilonewtons?"
        ),
        # Total load = w * L = 4 * 6 = 24 kN
        "answer": "24",
    },
    {
        "id": "eng_007",
        "problem": (
            "A car of mass 1200 kg is traveling at 25 m/s. "
            "What is its kinetic energy in kilojoules, rounded to one decimal?"
        ),
        # KE = 0.5 * 1200 * 25^2 = 375000 J = 375 kJ
        "answer": "375.0",
    },
    {
        "id": "eng_008",
        "problem": (
            "A chemical reactor operates at a production rate of 1800 kg of product per hour. "
            "How many kilograms are produced in 8 hours?"
        ),
        # 1800 * 8 = 14400 kg
        "answer": "14400",
    },
    {
        "id": "eng_009",
        "problem": (
            "A pump lifts water from a lower tank to a higher tank 12 m above. "
            "If the pump moves 0.02 m^3/s of water and the density of water is 1000 kg/m^3, "
            "what is the minimum hydraulic power in watts required (ignoring losses)?"
        ),
        # m_dot = 0.02 * 1000 = 20 kg/s; P = m_dot * g * h = 20 * 9.81 * 12 ≈ 2354 W
        "answer": "2354",
    },
    {
        "id": "eng_010",
        "problem": (
            "A cylindrical tank has a radius of 2 m and a height of 5 m. "
            "What is its volume in cubic meters, rounded to two decimals? Use pi ≈ 3.14."
        ),
        # V = π r^2 h ≈ 3.14 * 4 * 5 = 62.8 m^3
        "answer": "62.80",
    },
    {
        "id": "eng_011",
        "problem": (
            "A wire of resistance 8 ohms carries a current of 2.5 A for 4 hours. "
            "How much electrical energy in watt-hours is converted to heat in the wire?"
        ),
        # P = I^2 R = 2.5^2 * 8 = 50 W; E = 50 * 4 = 200 Wh
        "answer": "200",
    },
    {
        "id": "eng_012",
        "problem": (
            "A heat exchanger transfers 300 kW of heat continuously for 2.5 hours. "
            "How much total heat in megajoules is transferred? (1 kWh = 3.6 MJ)"
        ),
        # E = 300 kW * 2.5 h = 750 kWh; 750 * 3.6 = 2700 MJ
        "answer": "2700",
    },
    {
        "id": "eng_013",
        "problem": (
            "A gasoline engine has a brake power output of 80 kW and operates "
            "at a brake thermal efficiency of 30 percent. "
            "What is the rate of fuel energy input in kilowatts?"
        ),
        # Input = 80 / 0.30 ≈ 266.67 kW
        "answer": "266.67",
    },
    {
        "id": "eng_014",
        "problem": (
            "A 10 m^3 storage tank is filled with air at a pressure of 600 kPa. "
            "If the air is later used until the pressure drops to 200 kPa at the same temperature, "
            "what fraction of the original mass of air remains in the tank?"
        ),
        # m ∝ P at constant T,V; fraction = 200 / 600 = 1/3 ≈ 0.33
        "answer": "0.33",
    },
    {
        "id": "eng_015",
        "problem": (
            "Crude oil flows through a pipeline at 450 m^3/day. "
            "How many barrels per day is this, if 1 barrel = 0.159 m^3, "
            "rounded to the nearest whole barrel?"
        ),
        # barrels/day = 450 / 0.159 ≈ 2830.19 -> 2830
        "answer": "2830",
    },
    {
        "id": "eng_016",
        "problem": (
            "A gear train reduces the speed of a motor from 1800 rpm to 300 rpm. "
            "What is the overall speed reduction ratio?"
        ),
        # 1800 / 300 = 6 : 1
        "answer": "6",
    },
    {
        "id": "eng_017",
        "problem": (
            "A steel rod 2.5 m long elongates by 1.0 mm under a certain tensile load. "
            "What is the engineering strain, expressed as a dimensionless number, "
            "rounded to six decimal places?"
        ),
        # strain = ΔL / L = 0.001 / 2.5 = 0.0004
        "answer": "0.000400",
    },
    {
        "id": "eng_018",
        "problem": (
            "A refrigeration system removes heat from a cold space at a rate of 5 kW "
            "while consuming 2 kW of electrical power. "
            "What is its coefficient of performance (COP)?"
        ),
        # COP = Q_L / W = 5 / 2 = 2.5
        "answer": "2.5",
    },
    {
        "id": "eng_019",
        "problem": (
            "A distillation column produces 1200 kg/h of distillate "
            "and 800 kg/h of bottoms product. "
            "What is the total feed rate in kg/h?"
        ),
        # F = D + B = 1200 + 800 = 2000 kg/h
        "answer": "2000",
    },
    {
        "id": "eng_020",
        "problem": (
            "A solar panel array produces an average of 3.6 kW of electrical power "
            "for 6 hours per day. How much energy in kilowatt-hours is generated per day?"
        ),
        # E = 3.6 * 6 = 21.6 kWh
        "answer": "21.6",
    },
    # --- Additional engineering problems across disciplines ---
    {
        "id": "eng_021",
        "problem": (
            "Two resistors of 10 ohms and 15 ohms are connected in parallel, and this "
            "combination is connected in series with a 5 ohm resistor. "
            "What is the total resistance of the circuit in ohms?"
        ),
        # R_parallel = (10*15)/(10+15) = 150/25 = 6 ohms; R_total = 6 + 5 = 11
        "answer": "11",
    },
    {
        "id": "eng_022",
        "problem": (
            "A three phase, 400 V (line to line), 50 A load operates at a power factor of 0.8. "
            "What is the real power consumed by the load in watts, rounded to the nearest whole number? "
            "Use P = √3 × V × I × power factor."
        ),
        # P ≈ 1.732 * 400 * 50 * 0.8 ≈ 27712.81 W
        "answer": "27713",
    },
    {
        "id": "eng_023",
        "problem": (
            "A 15 kW electric motor runs at 1500 rpm. "
            "Assuming all power is converted to mechanical output, "
            "what is the output torque in newton meters, rounded to one decimal? "
            "Use T (N·m) ≈ 9550 × P(kW) / n(rpm)."
        ),
        # T ≈ 9550 * 15 / 1500 = 95.5 N·m
        "answer": "95.5",
    },
    {
        "id": "eng_024",
        "problem": (
            "A simply supported beam of span 4 m carries a single point load of 10 kN at midspan. "
            "What is the maximum bending moment in the beam in kN·m?"
        ),
        # M_max = P L / 4 = 10 * 4 / 4 = 10 kN·m
        "answer": "10",
    },
    {
        "id": "eng_025",
        "problem": (
            "Water flows through a circular pipe of internal diameter 0.05 m at a mean velocity "
            "of 2 m/s. The kinematic viscosity of water is 1.0×10^-6 m^2/s. "
            "What is the Reynolds number for the flow, rounded to the nearest whole number?"
        ),
        # Re = V D / ν = 2 * 0.05 / 1e-6 = 100000
        "answer": "100000",
    },
    {
        "id": "eng_026",
        "problem": (
            "In complete combustion of propane (C3H8), the stoichiometric reaction is "
            "C3H8 + 5 O2 → 3 CO2 + 4 H2O. "
            "If 44 kg of propane (1 kmol) are burned, how many kilograms of oxygen are required?"
        ),
        # 5 kmol O2 * 32 kg/kmol = 160 kg O2
        "answer": "160",
    },
    {
        "id": "eng_027",
        "problem": (
            "A stream of pure ethanol (molecular weight 46 kg/kmol) flows at 920 kg/h. "
            "What is the molar flow rate in kmol/h?"
        ),
        # n = 920 / 46 = 20 kmol/h
        "answer": "20",
    },
    {
        "id": "eng_028",
        "problem": (
            "An oil well has an initial production rate of 1000 barrels per day. "
            "Its rate declines exponentially with a decline constant of 0.2 per year. "
            "Assuming q = q0 × e^(−D t), what is the production rate in barrels per day "
            "after 3 years, rounded to two decimals?"
        ),
        # q ≈ 1000 * e^(−0.2*3) ≈ 548.81 bbl/day
        "answer": "548.81",
    },
    {
        "id": "eng_029",
        "problem": (
            "A petroleum reservoir contains 500,000 reservoir barrels of oil in place. "
            "The oil formation volume factor is 1.2 reservoir barrels per stock tank barrel. "
            "Assuming all oil can be produced, how many stock tank barrels would this equal, "
            "rounded to the nearest whole barrel?"
        ),
        # STB = 500,000 / 1.2 ≈ 416,666.67 -> 416,667
        "answer": "416667",
    },
    {
        "id": "eng_030",
        "problem": (
            "A reinforced concrete floor slab is 8 m long, 12 m wide, and 0.20 m thick. "
            "What is the volume of concrete required in cubic meters?"
        ),
        # V = 8 * 12 * 0.20 = 19.2 m^3
        "answer": "19.2",
    },
    {
        "id": "eng_031",
        "problem": (
            "A rigid tank of volume 0.10 m^3 contains air at a pressure of 500 kPa and "
            "temperature of 300 K. "
            "Assuming ideal gas behavior and using R = 0.287 kPa·m^3/(kg·K) for air, "
            "what is the mass of air in the tank in kilograms, rounded to two decimals?"
        ),
        # m = P V / (R T) = 500 * 0.1 / (0.287 * 300) ≈ 0.58 kg
        "answer": "0.58",
    },
    {
        "id": "eng_032",
        "problem": (
            "A 60 W light bulb is operated for 5 hours per day over 30 days. "
            "How much electrical energy in kilowatt-hours is consumed over the 30 days?"
        ),
        # P = 0.06 kW; E = 0.06 * 5 * 30 = 9 kWh
        "answer": "9",
    },
    {
        "id": "eng_033",
        "problem": (
            "A radioactive sample has an initial activity of 8000 Bq and a half life of 5 years. "
            "Assuming simple exponential decay, what will the activity be in Bq after 15 years?"
        ),
        # 15 years = 3 half-lives; A = 8000 / 2^3 = 1000 Bq
        "answer": "1000",
    },
    {
        "id": "eng_034",
        "problem": (
            "A radioactive isotope has a half life of 10 days. "
            "How many days will it take for the activity to decrease to one sixteenth "
            "of its original value?"
        ),
        # (1/16) = (1/2)^4 -> 4 half-lives; t = 4 * 10 = 40 days
        "answer": "40",
    },
    {
        "id": "eng_035",
        "problem": (
            "A diesel generator produces 500 kW of electrical power while consuming fuel at "
            "a rate that provides 1.6 MW of chemical energy. "
            "What is the overall efficiency of the generator in percent, "
            "rounded to two decimals?"
        ),
        # η = 500 / 1600 * 100 = 31.25%
        "answer": "31.25",
    },
    {
        "id": "eng_036",
        "problem": (
            "A heat exchanger must transfer 100 kW of heat from a hot fluid to a cold fluid. "
            "The overall heat transfer coefficient is 250 W/(m^2·K) and the log mean "
            "temperature difference is 40 K. "
            "What heat transfer area in square meters is required?"
        ),
        # Q = U A ΔT → A = 100,000 / (250 * 40) = 10 m^2
        "answer": "10",
    },
    {
        "id": "eng_037",
        "problem": (
            "Water flows in a pipe of diameter 0.30 m at a velocity of 2.0 m/s. "
            "The pipe then narrows to a diameter of 0.15 m. "
            "Assuming incompressible flow and neglecting losses, what is the velocity in the "
            "smaller pipe in m/s?"
        ),
        # Q = A1 V1; A ∝ D^2; V2 = V1 * (D1^2 / D2^2) = 2 * (0.30^2 / 0.15^2) = 8 m/s
        "answer": "8",
    },
    {
        "id": "eng_038",
        "problem": (
            "A single phase load consumes 3000 W at a power factor of 0.6 lagging. "
            "What is the apparent power of the load in kVA?"
        ),
        # S = P / pf = 3000 / 0.6 = 5000 VA = 5 kVA
        "answer": "5",
    },
    {
        "id": "eng_039",
        "problem": (
            "A circular steel rod of diameter 20 mm is subjected to a tensile force of 50 kN. "
            "What is the normal stress in the rod in megapascals (MPa), "
            "rounded to the nearest whole number?"
        ),
        # A = π (0.01)^2 ≈ 3.1416e-4 m^2; σ = 50,000 / A ≈ 1.59e8 Pa ≈ 159 MPa
        "answer": "159",
    },
    {
        "id": "eng_040",
        "problem": (
            "A Carnot heat engine operates between a high temperature reservoir at 500 K "
            "and a low temperature reservoir at 300 K. "
            "What is the maximum possible thermal efficiency in percent, "
            "rounded to one decimal?"
        ),
        # η = 1 − Tc/Th = 1 − 300/500 = 0.4 = 40.0%
        "answer": "40.0",
    },
    {
        "id": "eng_041",
        "problem": (
            "A crude oil has a specific gravity of 0.85 (relative to water at 60°F). "
            "The API gravity is given by API = (141.5 / SG) − 131.5. "
            "What is the API gravity, in degrees API, rounded to two decimals?"
        ),
        # API ≈ 141.5 / 0.85 − 131.5 ≈ 34.97
        "answer": "34.97",
    },
    {
        "id": "eng_042",
        "problem": (
            "A continuous stirred tank reactor (CSTR) has a liquid volume of 50 m^3 and "
            "a volumetric flow rate of 10 m^3/h. "
            "What is the residence time in hours?"
        ),
        # τ = V / Q = 50 / 10 = 5 h
        "answer": "5",
    },
    {
        "id": "eng_043",
        "problem": (
            "A rectangular spread footing is 2.0 m by 3.0 m in plan. "
            "The allowable soil bearing pressure is 150 kPa. "
            "What is the maximum allowable load that can be placed on the footing in kilonewtons?"
        ),
        # P = q_allow * A = 150 kPa * 6 m^2 = 900 kN
        "answer": "900",
    },
    {
        "id": "eng_044",
        "problem": (
            "A 5 g sample of a radioactive isotope has a half life of 5730 years. "
            "Assuming ideal half life behavior, how many grams of the isotope remain after "
            "11,460 years?"
        ),
        # 11,460 years = 2 half-lives; remaining mass = 5 / 4 = 1.25 g
        "answer": "1.25",
    },
    {
        "id": "eng_045",
        "problem": (
            "A pump delivers water at a flow rate of 0.03 m^3/s through a total head of 15 m. "
            "The overall pump efficiency is 70 percent. "
            "What is the required shaft power in kilowatts, rounded to two decimals? "
            "Use water density 1000 kg/m^3 and g = 9.81 m/s^2."
        ),
        # P_hydraulic = ρ g Q H = 1000*9.81*0.03*15 ≈ 4414.5 W
        # P_shaft = P_hydraulic / η ≈ 4414.5 / 0.7 ≈ 6.31 kW
        "answer": "6.31",
    },
    {
        "id": "eng_046",
        "problem": (
            "A 100 microfarad capacitor is charged to 200 V. "
            "How much energy is stored in the capacitor in joules? "
            "Use E = 0.5 × C × V^2."
        ),
        # C = 100e-6 F; E = 0.5 * 100e-6 * 200^2 = 2 J
        "answer": "2",
    },
    {
        "id": "eng_047",
        "problem": (
            "A solid flywheel has a mass moment of inertia of 2.0 kg·m^2. "
            "If a constant torque of 50 N·m is applied, "
            "what is the angular acceleration in rad/s^2?"
        ),
        # α = T / J = 50 / 2 = 25 rad/s^2
        "answer": "25",
    },
    {
        "id": "eng_048",
        "problem": (
            "The pressure at the surface of a large, open, fresh water reservoir is atmospheric. "
            "What is the gauge pressure in kilopascals at a depth of 5 m below the surface, "
            "rounded to one decimal? Use water density 1000 kg/m^3 and g = 9.81 m/s^2."
        ),
        # p = ρ g h = 1000 * 9.81 * 5 = 49,050 Pa = 49.05 kPa
        "answer": "49.1",
    },
    {
        "id": "eng_049",
        "problem": (
            "A mixing tank initially contains 200 kg of water. "
            "Then 50 kg of salt are added and fully dissolved. "
            "What is the mass percent of salt in the resulting solution, "
            "rounded to one decimal place?"
        ),
        # Total mass = 250 kg; salt fraction = 50 / 250 = 0.20 → 20.0%
        "answer": "20.0",
    },
    {
        "id": "eng_050",
        "problem": (
            "An industrial plant operates with an average electrical load of 350 kW continuously "
            "for 30 days. Electricity costs 0.10 dollars per kWh. "
            "What is the total electricity cost for the 30 days in dollars?"
        ),
        # E = 350 kW * 24 h/day * 30 days = 252,000 kWh; cost = 252,000 * 0.10 = 25,200
        "answer": "25200",
    },
]

out_path = Path("data/engineering_quant.jsonl")
out_path.parent.mkdir(parents=True, exist_ok=True)

with out_path.open("w", encoding="utf-8") as f:
    for p in problems:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Wrote {len(problems)} engineering problems to {out_path}")
