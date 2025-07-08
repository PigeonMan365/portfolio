# tool_handler.py

import subprocess
import sys
import ollama
import re

def run_tool(tool_name, entrypoint, user_input):
    print(f"[DEBUG] Tool Handler: Running tool '{tool_name}' with input: {user_input}")

    # Special handling for calculator: parse math expression first
    if tool_name == "calculator":
        expression = extract_math_expression(user_input)
        if not expression:
            return "CALC_RESULT: ERROR: Unable to parse math expression"
        print(f"[DEBUG] Tool Handler: Parsed math expression: {expression}")
        arg = expression
    else:
        arg = user_input

    try:
        result = subprocess.run(
            ["python", entrypoint, arg],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        print(f"[DEBUG] Tool Handler: Tool output: {result}")
        return result
    except subprocess.CalledProcessError as e:
        return f"[DEBUG] Tool Handler ERROR: {e.stderr}"

def extract_math_expression(user_input):
    prompt = (
        "Extract ONLY the Python math expression from the following text. "
        "Convert number words to digits, and use valid math operators. "
        "Return ONLY the expression, e.g., 1 + 1 — no text, no explanation.\n\n"
        f"Text: {user_input}"
    )

    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    output = response['message']['content'].strip()

    # Sanitize (e.g., remove trailing '=' or explanations)
    output = output.split('=')[0].strip()
    output = re.sub(r'[^\d\+\-\*/\.\(\)\s]', '', output)
    return output if output else None
