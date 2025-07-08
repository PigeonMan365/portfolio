# word_counter_agent.py

import subprocess

def handle_tool_request(input_text):
    print("[DEBUG] word_counter_agent: received input")
    try:
        result = subprocess.run(
            ["python", "word_counter.py", input_text],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        print(f"[DEBUG] Tool output: {result}")
        if result.startswith("WORD_COUNT:"):
            value = result.split("WORD_COUNT:")[1].strip()
            return f"There are {value} words in your input."
        else:
            return f"[DEBUG] word_counter_agent: Unexpected output → {result}"
    except subprocess.CalledProcessError as e:
        return f"[DEBUG] word_counter_agent ERROR: {e.stderr}"
