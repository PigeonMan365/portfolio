# tool_handler.py

import importlib

def handle_tool_task(tool_name, user_input):
    try:
        print(f"[DEBUG] Tool Handler → {tool_name}_agent.py")
        tool_module = importlib.import_module(f"{tool_name}_agent")
        result = tool_module.handle_tool_request(user_input)
        return result
    except ModuleNotFoundError:
        return f"[DEBUG] Tool Handler: Tool Agent '{tool_name}_agent.py' not found."
    except AttributeError:
        return f"[DEBUG] Tool Handler: 'handle_tool_request()' not defined in {tool_name}_agent."
    except Exception as e:
        return f"[DEBUG] Tool Handler: Unexpected error: {e}"
