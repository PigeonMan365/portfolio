# ai_agent.py

import subprocess
import ollama
import re

def get_math_expression(llm, user_input):
    prompt = (
        f"Convert the following question into a clean, valid Python math expression. "
        f"Use digits, replace words like 'four' with 4, and remove any non-math words:\n\n"
        f"\"{user_input}\"\n\n"
        f"ONLY return the raw math expression. No explanation, no result. Just the expression."
    )
    response = ollama.chat(model=llm, messages=[{"role": "user", "content": prompt}])
    return response['message']['content'].strip()

def clean_expression(expr):
    # Remove text after = or any unnecessary parts
    expr = expr.strip().splitlines()[0]
    expr = expr.split('=')[0].strip()

    # Remove non-math characters like letters
    expr = re.sub(r'[^\d\+\-\*/\.\(\)\s]', '', expr)

    return expr

def get_final_response(llm, expression, result):
    prompt = f"The result of {expression} is {result}. Respond to the user with this info."
    response = ollama.chat(model=llm, messages=[{"role": "user", "content": prompt}])
    return response['message']['content'].strip()

def main():
    llm = "llama3"  # Use whatever local model is running

    user_input = input("Enter your math question: ")
    print(f"[DEBUG] User input: {user_input}")

    raw_expr = get_math_expression(llm, user_input)
    print(f"[DEBUG] Raw parsed expression: {raw_expr}")

    cleaned_expr = clean_expression(raw_expr)
    print(f"[DEBUG] Cleaned expression: {cleaned_expr}")

    if not cleaned_expr:
        print("[DEBUG] Could not parse a valid math expression.")
        return

    print(f"[DEBUG] Running calculator with: {cleaned_expr}")
    try:
        result_raw = subprocess.run(
            ["python", "calculator.py", cleaned_expr],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[DEBUG] Calculator error: {e.stderr}")
        return

    print(f"[DEBUG] Tool returned: {result_raw}")

    if result_raw.startswith("CALC_RESULT:"):
        result = result_raw.split("CALC_RESULT:")[1].strip()
    else:
        print("[DEBUG] Invalid calculator output.")
        return

    final_response = get_final_response(llm, cleaned_expr, result)
    print(f"[DEBUG] Final AI response: {final_response}")

if __name__ == "__main__":
    main()
