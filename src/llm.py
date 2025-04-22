"""LLM module for AI Agent.

This module handles interactions with language models,
with primary support for DeepSeek and fallback to OpenAI.
"""

from typing import Dict, List, Optional, Any, Union

from langchain_core.language_models import BaseLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek


from config import config

class LLMProvider:
    """Provider class for language model interactions."""

    def __init__(self):
        """Initialize the LLM provider with configuration."""
        self.llm = self._init_llm()

    def _init_llm(self) -> BaseLLM:
        """Initialize the appropriate language model based on config."""

        try:
            # Try importing the DeepSeek integration
            # If not available, this will raise ImportError

            print("config.llm.api_key:", config.llm.api_key)
            return ChatDeepSeek(
                model=config.llm.model_name,
                api_key=config.llm.api_key,
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens,
            )
        except ImportError:
            if config.debug:
                print("DeepSeek integration not found. Falling back to OpenAI.")



    def generate_ui_layout(self, prompt: str) -> Dict[str, Any]:
        """Generate UI layout based on the prompt.

        Args:
            prompt: Natural language description of the UI layout

        Returns:
            Dictionary containing the structured layout representation
        """
        layout_prompt = ChatPromptTemplate.from_template(
            """
            You are a UI/UX expert specializing in creating Figma-compatible designs.
            Convert the following natural language description into a structured JSON
            format that represents the described UI layout.

            Requirements:
            1. The layout should be hierarchical, with parent and child components
            2. Include appropriate styling information (colors, spacing, fonts)
            3. Use standard Figma component terminology where possible
            4. Format must be valid JSON that can be parsed programmatically

            DESCRIPTION:
            {prompt}

            OUTPUT FORMAT EXAMPLE:
            ```json
            {
              "name": "Dashboard Layout",
              "type": "FRAME",
              "width": 1440,
              "height": 900,
              "backgroundColor": "#FFFFFF",
              "children": [
                {
                  "name": "Sidebar",
                  "type": "RECTANGLE",
                  "x": 0,
                  "y": 0,
                  "width": 250,
                  "height": 900,
                  "backgroundColor": "#F5F5F5",
                  "children": [...]
                },
                {
                  "name": "Content Area",
                  "type": "FRAME",
                  "x": 250,
                  "y": 0,
                  "width": 1190,
                  "height": 900,
                  "backgroundColor": "#FFFFFF",
                  "children": [...]
                }
              ]
            }
            ```

            Respond with only the JSON, no explanations or other text.
            """
        )

        # Generate the UI layout using the LLM
        result = self.llm.invoke(
            layout_prompt.format(prompt=prompt)
        )

        # Extract the JSON content from the response
        import json
        import re

        content = result.content

        # Extract JSON content between ```json and ``` if present
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_match = re.search(json_pattern, content)

        if json_match:
            json_str = json_match.group(1)
        else:
            # If no code block markers, try to use the entire content
            json_str = content

        try:
            # Parse the JSON string into a Python dictionary
            layout_data = json.loads(json_str)
            return layout_data
        except json.JSONDecodeError as e:
            if config.debug:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw content: {content}")

            # Return a minimal error response
            return {"error": "Failed to parse layout", "message": str(e)}


# Create a global instance of the LLM provider
llm_provider = LLMProvider()
