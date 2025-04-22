
Goal: Build an AI Agent that can generate Figma-compatible templates or UI layouts from natural language prompts.

Requirements:
0. Use uv manager for managing the agent's lifecycle and dependencies.
1. Use LangChain and LangGraph for building the agent's workflow.
2. Integrate DeepSeek LLM as the main reasoning/generation model.
3. The agent should understand prompts describing UI (e.g., "Create a dashboard layout with sidebar and chart area").
4. Output should be in a structured format (e.g., JSON, or Figma API-compatible format) that can be rendered into Figma.
5. Optional: Integrate Figma API to automatically create and update designs in a Figma file.

Steps:
- Initialize LangGraph with custom nodes for parsing, generating, and validating layout components.
- Use LangChain tools to process prompt and route sub-tasks (e.g., layout logic, component styling).
- Implement DeepSeek LLM as the core model for layout generation based on user input.
- Format the output for direct use with Figma plugin or API.

Start by defining the LangGraph structure and the agent interface.

Environment:
- Python 3.10+
- langchain
- langgraph
- openai or deepseek
- requests (for optional Figma API)

