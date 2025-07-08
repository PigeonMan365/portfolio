# io_agent.py

import ollama
import json
import re

def get_user_input():
    return input("What would you like to do? (Tools include Calculator, word counter and reverse text): ")

def generate_tool_plan(user_input, tool_registry):
    print(f"[DEBUG] I/O Agent: Received input → {user_input}")

    tool_list = "\n".join(
        [f"{name}: {info['description']}" for name, info in tool_registry.items()]
    )

    prompt = (
        "You are an intelligent task-planning AI with contextual reasoning abilities. Given a user message, return a list of tool calls.\n\n"
        "Choose ONLY from the following tools:\n"
        f"{tool_list}\n\n"
        "for String based tasks consider what part of the input each tool should be used on, such as a user specifying with quotations like: 'Example' "
        "Return a JSON array of steps. Each step MUST include:\n"
        "- tool: the tool name\n"
        "- input: the input the tool should operate on (from the original message)\n\n"
        "DO NOT chain tool outputs unless explicitly asked (e.g., 'use the result of...').\n"
        "DO NOT use $last_output unless it's clearly referred to by the user.\n"
        "Respond with ONLY valid JSON.\n\n"
        f"User input: {user_input}"
    )

    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    raw = response['message']['content'].strip()
    print(f"[DEBUG] I/O Agent: Raw plan response:\n{raw}")

    try:
        start = raw.index("[")
        end = raw.rindex("]") + 1
        plan_json = raw[start:end]
        plan = json.loads(plan_json)
        return plan
    except Exception as e:
        print(f"[DEBUG] I/O Agent: Failed to parse plan JSON → {e}")
        return []

def validate_plan(plan, tool_registry):
    for step in plan:
        tool = step.get("tool")
        if tool not in tool_registry:
            print(f"[DEBUG] I/O Agent: Unknown tool '{tool}' in plan.")
            return False
        if tool == "calculator":
            input_text = step.get("input", "")
            if not re.search(r"[\d\+\-\*/]", input_text):
                print(f"[DEBUG] I/O Agent: Calculator input '{input_text}' lacks math syntax.")
                return False
    return True

def display_output(response):
    print(f"[DEBUG] I/O Agent: Final response to user:\n{response}")
