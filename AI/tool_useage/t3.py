# three_ai_test.py

import subprocess
import re
import ollama

# === I/O AGENT ===
def io_agent(llm_model):
    user_input = input("Enter your math question: ")
    print("[DEBUG] I/O Agent: Received user input")
    print("[DEBUG] I/O Agent → Core: Forwarding message...")

    core_response = core_agent(llm_model, user_input)

    print("[DEBUG] I/O Agent: Final output to user:")
    print(core_response)


# === CORE AGENT ===
def core_agent(llm_model, message_from_io):
    print("[DEBUG] Core Agent: Received input")
    print("[DEBUG] Core Agent → Tool Handler: Sending task...")

    tool_response = tool_handler_agent(llm_model, message_from_io)

    print("[DEBUG] Core Agent: Received tool result")
    print("[DEBUG] Core Agent → I/O Agent: Sending formatted reply...")

    # Optional rephrasing for user friendliness
    final_message = f"The answer is {extract_result(tool_response)}."
    return final_message


# === TOOL HANDLER AGENT ===
def tool_handler_agent(llm_model, message_from_core):
    print("[DEBUG] Tool Handler: Received task")

    prompt = (
        "You are a tool handler AI. Your job is to extract a clean math expression from the user's question.\n"
        "Return ONLY the expression in this format: <expression>2 + 2</expression>\n"
        "Do NOT solve it. Do NOT explain. Convert number words to digits.\n\n"
        f"User input: {message_from_core}"
    )

    response = ollama.chat(model=llm_model, messages=[{"role": "user", "content": prompt}])
    llm_output = response['message']['content'].strip()

    match = re.search(r"<expression>(.*?)</expression>", llm_output)
    if not match:
        return "[DEBUG] Tool Handler ERROR: No valid expression found."

    expression = match.group(1).strip()
    print(f"[DEBUG] Tool Handler: Extracted expression: {expression}")
    print("[DEBUG] Tool Handler: Running calculator...")

    try:
        result_raw = subprocess.run(
            ["python", "calculator.py", expression],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[DEBUG] Tool Handler ERROR: Calculator failed: {e.stderr}"

    print(f"[DEBUG] Tool Handler: Tool output: {result_raw}")

    if result_raw.startswith("CALC_RESULT:"):
        result = result_raw.split("CALC_RESULT:")[1].strip()
        final_response = f"The result of {expression} is {result}"
        print("[DEBUG] Tool Handler → Core: Sending response...")
        return final_response
    else:
        return "[DEBUG] Tool Handler ERROR: Invalid calculator output."


# === HELPER ===
def extract_result(text):
    match = re.search(r"is\s+(-?\d+(\.\d+)?)\s*$", text)
    return match.group(1) if match else "an error occurred."


# === MAIN ===
if __name__ == "__main__":
    model_name = "llama3"  # Or your preferred local Ollama model
    io_agent(model_name)
