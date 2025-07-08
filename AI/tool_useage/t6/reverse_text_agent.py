# reverse_text_agent.py

import subprocess

def handle_tool_request(input_text):
    print("[DEBUG] reverse_text_agent: received input")
    try:
        result = subprocess.run(
            ["python", "reverse_text.py", input_text],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        print(f"[DEBUG] Tool output: {result}")
        if result.startswith("REVERSED:"):
            value = result.split("REVERSED:")[1].strip()
            return f"Reversed text: {value}"
        else:
            return f"[DEBUG] reverse_text_agent: Unexpected output → {result}"
    except subprocess.CalledProcessError as e:
        return f"[DEBUG] reverse_text_agent ERROR: {e.stderr}"
