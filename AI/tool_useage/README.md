Tool-Using AI System – Multi-Agent Reasoning Tests (1–6)

This project shows my experimentation and development of a tool-using ai system/agent, primarily fueled by Ollama by just using base models.
Each test builds on the previous to advance toward general-purpose task decomposition, tool selection, and execution of complex tasks using modular agents.


  Test Progression Summary

| Test | Advancement |
|------|-------------|
| **Test 1** | Basic AI-to-tool interface (calculator only) |
| **Test 2** | Multi-agent: Core AI delegates to Tool Handler |
| **Test 3** | Adds I/O Agent: I/O → core → tool |
| **Test 4** | Dynamic tool selection via registry |
| **Test 5** | Introduces individual Tool Agents per tool |
| **Test 6** | Full task planning: context-aware, multi-step chaining |

---

  Test Descriptions

  Test 1: Simple Tool Use (calculator)
    - Getting Ai to use a tool
    - Single AI system
    - AI extracts a math expression from user input
    - Uses subprocess to call "calculator.py"
    - AI Parses results for output

  Test 2: Core/ToolHandler Split
    - getting AI to communicate with another AI to use a tool
    - Dual AI system
    - Adds separation of logic
    - Core Agent asks Tool Handler to run tools
    - Simulates multi-agent delegation
    - getting AI to communicate with another AI to use a tool

  Test 3: segmented I/O Added
    - getting an ai to handle I/O and communicate with the system
    - Introduces input/output AI to simulate frontend
    - User interacts only with I/O agent
    - Clean separation: I/O → Core → ToolHandler → Tool

  Test 4: Tool Awareness & Dynamic Selection
    - getting the system to use the correct tool with more then one option
    - Adds "tool_registry.json" as a catalog of tools to chose from
    - Core Agent chooses the correct tool using LLM reasoning and sends that to Tool Handler
    - Tool Handler dynamically routes to correct script

  Test 5: Tool Agents Abstraction
    - adding AI to each tool
    - Each tool gets its own "*_agent.py" file
    - Tool Agents parse input, run subprocess, return results
    - Tool Handler delegates to agents instead of using raw tools itself

  Test 6: Chained Multi-Step Execution (using multiple tools in a single input prompt)
    - adding planning and ability to use multiple tools at once
    - I/O Agent generates a plan with multiple steps
    - Each step has its own tool and input
    - Core executes them sequentially, with optional "$last_output" substitution
    - System demonstrates contextual reasoning



    Requirements
      -Python 3.8+
      -ollama
