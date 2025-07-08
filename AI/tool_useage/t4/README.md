Test 4 – Dynamic Tool Selection via Registry

This iteration introduces a scalable architecture for tool awareness and selection using a centralized "tool_registry.json".

    To run use "Python core_agent.py"

    Architecture
      "core_agent.py": acts as the starting point, loads tool registry, selects tool using LLM
      "tool_registry.json": maps tool names → descriptions & entrypoints
      "tool_handler.py": runs the correct tool script
      "io_agent.py": receives user input, returns final response
      "calculator.py", "word_counter.py", "reverse_text.py": standalone CLI tools

      Behavior
        - Core prompts LLM: “Which tool should be used?”
        - Tool Handler executes only that tool
        - Output returned and formatted for the user


      What It Enables
        - Extensible plugin registry
        - Tool discovery via LLM


  Example

  What would you like to do? (Tools include Calculator, word counter and reverse text): what is ten minus two * 8 + 11
  [DEBUG] I/O Agent: Received input → what is ten minus two * 8 + 11
  [DEBUG] Core Agent: LLM selected tool → calculator
  [DEBUG] Tool Handler: Running tool 'calculator' with input: what is ten minus two * 8 + 11
  [DEBUG] Tool Handler: Parsed math expression: 10 - 2 * 8 + 11
  [DEBUG] Tool Handler: Tool output: CALC_RESULT: 5
  [DEBUG] I/O Agent: Final response to user:
  The result is 5.
