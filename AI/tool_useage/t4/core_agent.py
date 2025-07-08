# core_agent.py

import json
import ollama
from io_agent import get_user_input, display_output
from tool_handler import run_tool

def load_tool_registry():
    with open("tool_registry.json", "r") as f:
        return json.load(f)

def choose_tool(llm_model, user_input, tool_registry):
    tool_list = "\n".join(
        [f"{name}: {info['description']}" for name, info in tool_registry.items()]
    )
    prompt = (
        f"You are an AI that selects the correct tool from a registry.\n"
        f"Available tools:\n{tool_list}\n\n"
        f"Which tool is best suited for the user input below?\n"
        f"Respond ONLY with the tool name.\n\n"
        f"User input: {user_input}"
    )
    response = ollama.chat(model=llm_model, messages=[{"role": "user", "content": prompt}])
    tool_name = response['message']['content'].strip().lower()
    print(f"[DEBUG] Core Agent: LLM selected tool → {tool_name}")
    return tool_name

def core_agent():
    model = "llama3"  # or another local Ollama model
    user_input = get_user_input()
    tool_registry = load_tool_registry()

    tool_name = choose_tool(model, user_input, tool_registry)

    if tool_name not in tool_registry:
        print("[DEBUG] Core Agent: Invalid tool name returned.")
        display_output("Sorry, I couldn't determine which tool to use.")
        return

    entrypoint = tool_registry[tool_name]['entrypoint']
    result = run_tool(tool_name, entrypoint, user_input)
    response = format_response(tool_name, result)
    display_output(response)

def format_response(tool_name, tool_output):
    if tool_name == "calculator" and tool_output.startswith("CALC_RESULT:"):
        value = tool_output.split("CALC_RESULT:")[1].strip()
        return f"The result is {value}."
    elif tool_name == "word_counter" and tool_output.startswith("WORD_COUNT:"):
        value = tool_output.split("WORD_COUNT:")[1].strip()
        return f"There are {value} words in your input."
    elif tool_name == "reverse_text" and tool_output.startswith("REVERSED:"):
        value = tool_output.split("REVERSED:")[1].strip()
        return f"Reversed text: {value}"
    else:
        return f"[DEBUG] Core Agent: Could not understand tool output: {tool_output}"

if __name__ == "__main__":
    core_agent()
