Test 5 – Tool Agents Architecture

This iteration introduces an individual agent per tool. the idea is that each agent will be better at using each tool individually then a generalized AI.

      Architecture
        "core_agent.py": acts as the starting point, loads tool registry, selects tool using LLM
        "tool_registry.json": maps tool names → descriptions & entrypoints for each tool agent
        "tool_handler.py": runs the correct tool agent
        "io_agent.py": receives user input, returns final response
        "calculator.py", "word_counter.py", "reverse_text.py": standalone CLI tools
        "calculator_agent.py", "word_counter_agent.py", "reverse_text_agent.py": tool agents


      Changes
        - "tool_handler.py" no longer calls tools directly, instead calls the agent for each tool
        - Each agent handles:
          - Prompting LLM (if needed)
          - Formatting input
          - Executing the real tool via subprocess
          - Parsing tool output

        What It Enables
          - intelligent tool use

  Example

  What would you like to do? (Tools include Calculator, word counter and reverse text): count the words in this sentence
  [DEBUG] I/O Agent: Received input → count the words in this sentence
  [DEBUG] Core Agent: LLM selected tool → word_counter
  [DEBUG] Tool Handler → word_counter_agent.py
  [DEBUG] word_counter_agent: received input
  [DEBUG] Tool output: WORD_COUNT: 6
  [DEBUG] I/O Agent: Final response to user:
  There are 6 words in your input.
