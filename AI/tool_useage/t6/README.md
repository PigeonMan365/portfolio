Test 6 – Tool Chaining & Context-Aware Planning

This iteration adds multi-step task execution, where a plan is generated and each step is another tool.

      Architecture
        "core_agent.py": acts as the starting point, loads tool registry, selects tool using LLM
        "tool_registry.json": maps tool names → descriptions & entrypoints for each tool agent
        "tool_handler.py": runs the correct tool agent
        "io_agent.py": receives user input, returns final response
        "calculator.py", "word_counter.py", "reverse_text.py": standalone CLI tools
        "calculator_agent.py", "word_counter_agent.py", "reverse_text_agent.py": tool agents

        Changes
          - no changes in architecture
          - introduction of planning and multi tool use logic

        What it Enables
          - more complex tasks that require more then basic tool use.


  Example

  What would you like to do? (Tools include Calculator, word counter and reverse text): count these words "monday, apple, chair, Texas", reverse this text "dlrow olleh" and give me the result of 99/1 time 10 plus 9
  [DEBUG] I/O Agent: Received input → count these words "monday, apple, chair, Texas", reverse this text "dlrow olleh" and give me the result of 99/1 time 10 plus 9
  [DEBUG] I/O Agent: Raw plan response:
  Here is the list of tool calls in a JSON array:

  ```
  [
    {
      "tool": "word_counter",
      "input": "\"monday, apple, chair, Texas\""
    },
    {
      "tool": "reverse_text",
      "input": "\"dlrow olleh\""
    },
    {
      "tool": "calculator",
      "input": "99/1 * 10 + 9"
    }
  ]
  ```

  Note that I've parsed the input to identify the relevant parts for each tool. The word counter is given the sentence with quoted words, the reverse text tool is given the reversed text, and the calculator is given the arithmetic expression as input.
  [DEBUG] word_counter_agent: received input
  [DEBUG] Tool output: WORD_COUNT: 4
  [DEBUG] reverse_text_agent: received input
  [DEBUG] Tool output: REVERSED: "hello world"
  [DEBUG] calculator_agent: received input
  [DEBUG] calculator_agent: raw LLM output:
  <expression>99/1 * 10 + 9</expression>
  [DEBUG] calculator_agent: parsed '99/1 * 10 + 9'
  [DEBUG] Tool output: CALC_RESULT: 999.0
  [DEBUG] Tool Handler → word_counter_agent
  [DEBUG] word_counter_agent: received input → "monday, apple, chair, Texas"
  [DEBUG] Tool output: There are 4 words in your input.
  [DEBUG] Tool Handler → reverse_text_agent
  [DEBUG] reverse_text_agent: received input → "dlrow olleh"
  [DEBUG] Tool output: Reversed text: "hello world"
  [DEBUG] Tool Handler → calculator_agent
  [DEBUG] calculator_agent: received input → 99/1 * 10 + 9
  [DEBUG] Tool output: The result is 999.0.
  [DEBUG] Final response: The result is 999.0.
  [DEBUG] I/O Agent: Final response to user:
  There are 4 words in your input.
  Reversed text: "hello world"
  The result is 999.0.
