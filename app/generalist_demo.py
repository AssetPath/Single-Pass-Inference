# app/run_generalist_demo.py
from orchestrator import run_single_pass_generalist

def main():
    problem = "If Alice has 3 apples and buys 5 more, then eats 2, how many are left?"
    agents, final_answer = run_single_pass_generalist(problem)

    print("=== Agent outputs ===")
    for name, out in agents.items():
        print(f"\n--- {name} ---\n{out}")

    print("\n=== Judge final answer ===")
    print(final_answer)

if __name__ == "__main__":
    main()
