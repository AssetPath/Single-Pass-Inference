from fastapi import FastAPI

app = FastAPI()

# app/app.py
from vertex_client import call_flash, call_pro

def main():
    user_prompt = "Explain what single-pass reflective inference is in 2 short sentences."
    print("=== Flash draft ===")
    draft = call_flash(user_prompt)
    print(draft)

    print("\n=== Pro judge ===")
    improved = call_pro(f"You are a careful reviewer. Improve this explanation:\n\n{draft}")
    print(improved)

if __name__ == "__main__":
    main()

