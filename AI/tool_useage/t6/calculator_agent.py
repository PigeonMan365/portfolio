# calculator_agent.py

import subprocess
import re
import ollama

def handle_tool_request(input_text):
    print("[DEBUG] calculator_agent: received input")

    prompt = (
        "Extract the math expression from this input and wrap it inside <expression>...</expression> tags.\n"
        "Convert number words to digits. Return only the expression, do not compute or explain.\n"
        f"Input: {input_text}"
    )

    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    raw_llm_output = response['message']['content'].strip()
    print(f"[DEBUG] calculator_agent: raw LLM output:\n{raw_llm_output}")

    # Find all expressions in <expression>...</expression> tags
    candidates = re.findall(r"<expression>(.*?)</expression>", raw_llm_output, re.DOTALL)
    valid_expr = None

    for expr in candidates:
        expr = expr.strip()
        if is_valid_expression(expr):
            valid_expr = expr
            break

    if not valid_expr:
        print("[DEBUG] calculator_agent: No valid expression found in <expression> tags.")
        return "The result is ERROR: failed to parse expression."

    print(f"[DEBUG] calculator_agent: parsed '{valid_expr}'")

    try:
        result = subprocess.run(
            ["python", "calculator.py", valid_expr],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()

        print(f"[DEBUG] Tool output: {result}")

        if result.startswith("CALC_RESULT:"):
            value = result.split("CALC_RESULT:")[1].strip()
            return f"The result is {value}."
        else:
            return "The result is ERROR: Unexpected tool output."
    except subprocess.CalledProcessError as e:
        return f"The result is ERROR: {e.stderr}"

def is_valid_expression(expr):
    """Validate if the string looks like a proper arithmetic expression."""
    # Reject things like just a number (e.g., "2") or expressions with "=" in them
    if "=" in expr:
        return False
    # Accept only if it includes an operator and at least two numbers or expressions
    return bool(re.search(r"\d+\s*[\+\-\*/]\s*\d+", expr))
