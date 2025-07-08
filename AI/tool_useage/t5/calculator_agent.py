# calculator_agent.py

import subprocess
import re
import ollama

def handle_tool_request(input_text):
    print("[DEBUG] calculator_agent: received input")

    prompt = (
        "Extract ONLY the valid Python math expression from the input below.\n"
        "Convert number words to digits. Return ONLY the expression inside <expression>...</expression> tags.\n"
        "Do not explain anything.\n\n"
        f"Input: {input_text}"
    )

    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    raw_llm_output = response['message']['content'].strip()

    print(f"[DEBUG] calculator_agent: raw LLM output:\n{raw_llm_output}")

    match = re.search(r"<expression>(.*?)</expression>", raw_llm_output, re.DOTALL)
    if not match:
        print("[DEBUG] calculator_agent: No <expression> tags found.")
        return "The result is ERROR: failed to parse expression."

    expression = match.group(1).strip()
    expression = re.sub(r'[^\d\+\-\*/\.\(\)\s]', '', expression)

    print(f"[DEBUG] calculator_agent: parsed '{expression}'")

    try:
        result = subprocess.run(
            ["python", "calculator.py", expression],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        print(f"[DEBUG] Tool output: {result}")
        if result.startswith("CALC_RESULT:"):
            value = result.split("CALC_RESULT:")[1].strip()
            return f"The result is {value}."
        else:
            return f"[DEBUG] calculator_agent: Unexpected output → {result}"
    except subprocess.CalledProcessError as e:
        return f"[DEBUG] calculator_agent ERROR: {e.stderr}"
