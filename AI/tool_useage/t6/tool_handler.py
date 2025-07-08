# tool_handler.py

import importlib

def execute_tool_chain(plan):
    current_input = None
    logs = []
    outputs = []

    for i, step in enumerate(plan):
        tool_name = step["tool"]
        input_text = step.get("input", current_input)

        # Sanitize substitution
        if input_text and "$last_output" in input_text:
            if current_input is not None:
                input_text = input_text.replace("$last_output", current_input)
            else:
                input_text = input_text.replace("$last_output", "")

        # Reject unsupported tokens
        if any(tok in input_text for tok in ["$0", "$step", "$first_output"]):
            return f"[DEBUG] Tool Handler: Unsupported reference in input → {input_text}"

        logs.append(f"[DEBUG] Tool Handler → {tool_name}_agent")

        try:
            tool_module = importlib.import_module(f"{tool_name}_agent")
            logs.append(f"[DEBUG] {tool_name}_agent: received input → {input_text}")
            result = tool_module.handle_tool_request(input_text)
        except ModuleNotFoundError:
            return f"[DEBUG] Tool Handler: Tool Agent '{tool_name}_agent.py' not found."
        except AttributeError:
            return f"[DEBUG] Tool Handler: 'handle_tool_request()' not defined in {tool_name}_agent."
        except Exception as e:
            return f"[DEBUG] Tool Handler: Unexpected error: {e}"

        logs.append(f"[DEBUG] Tool output: {result}")
        outputs.append(result)
        current_input = extract_output_value(result)

    logs.append(f"[DEBUG] Final response: {outputs[-1]}")
    print("\n".join(logs))
    return "\n".join(outputs)

def extract_output_value(output):
    if "CALC_RESULT:" in output:
        return output.split("CALC_RESULT:")[1].strip()
    elif "WORD_COUNT:" in output:
        return output.split("WORD_COUNT:")[1].strip()
    elif "REVERSED:" in output:
        return output.split("REVERSED:")[1].strip()
    else:
        # Fallback: try to extract a trailing number or raw text
        return output.strip()
