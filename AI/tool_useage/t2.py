# ma.py

import subprocess
import ollama
import re

# === Core Agent ===
def core_agent(llm_model):
    user_input = input("Enter your math question: ")
    print(f"[DEBUG] Core received: {user_input}")

    print("[DEBUG] Core sends task to Tool Handler...")
    tool_response = tool_handler(llm_model, user_input)

    result = extract_result(tool_response)
    print(f"[DEBUG] Core final message: The result of your request is: {result}")


# === Tool Handler Agent ===
def tool_handler(llm_model, message_from_core):
    prompt = (
        f"You are a tool-handling assistant.\n"
        f"Your job is to extract only a math expression from the input below.\n"
        f"Respond ONLY in this format: <expression>math_expression_here</expression>\n"
        f"Do NOT solve it. Do NOT explain. Only extract and format.\n"
        f"Convert number words to digits.\n\n"
        f"Input: {message_from_core}"
    )

    response = ollama.chat(model=llm_model, messages=[{"role": "user", "content": prompt}])
    llm_output = response['message']['content'].strip()

    print(f"[DEBUG] Tool Handler raw model output: {llm_output}")

    match = re.search(r"<expression>(.*?)</expression>", llm_output)
    if not match:
        return "[DEBUG] Tool Handler ERROR: No valid expression found."

    cleaned_expr = match.group(1).strip()
    print(f"[DEBUG] Tool Handler parsed: {cleaned_expr}")

    # Step 2: Run calculator.py
    try:
        print(f"[DEBUG] Tool Handler running calculator with: {cleaned_expr}")
        result_raw = subprocess.run(
            ["python", "calculator.py", cleaned_expr],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[DEBUG] Tool Handler ERROR: Calculator failed with: {e.stderr}"

    print(f"[DEBUG] Tool output: {result_raw}")

    if result_raw.startswith("CALC_RESULT:"):
        result = result_raw.split("CALC_RESULT:")[1].strip()
        tool_message = f"The result of {cleaned_expr} is {result}"
        print(f"[DEBUG] Tool Handler response: {tool_message}")
        return tool_message
    else:
        return "[DEBUG] Tool Handler ERROR: Invalid output from calculator."


# === Helpers ===
def extract_result(response_text):
    match = re.search(r"is\s+(-?\d+(\.\d+)?)\s*$", response_text)
    return match.group(1) if match else "an error occurred."


# === Main Entry ===
if __name__ == "__main__":
    model_name = "llama3"  # Replace with your local Ollama model name
    core_agent(model_name)
