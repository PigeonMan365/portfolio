# core_agent.py

import json
from io_agent import get_user_input, generate_tool_plan, validate_plan, display_output
from tool_handler import execute_tool_chain

def load_tool_registry():
    with open("tool_registry.json", "r") as f:
        return json.load(f)

def core_agent():
    tool_registry = load_tool_registry()
    user_input = get_user_input()
    plan = generate_tool_plan(user_input, tool_registry)

    if not plan or not validate_plan(plan, tool_registry):
        display_output("Sorry, I couldn't generate a valid tool plan.")
        return

    final_output = execute_tool_chain(plan)
    display_output(final_output)

if __name__ == "__main__":
    core_agent()
