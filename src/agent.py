"""LangGraph-based AI Agent for UI layout generation.

This module implements the main agent workflow using LangGraph
for generating Figma-compatible UI layouts from natural language.
"""

import json
from typing import Any, Dict, List, TypedDict, Annotated

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from config import config
from llm import llm_provider
from figma_api import figma_api


# Define the state schema for our agent
class AgentState(TypedDict):
    """State schema for the UI generation agent."""

    # Input state
    prompt: str

    # Processing state
    parsed_requirements: Dict[str, Any]
    layout_structure: Dict[str, Any]

    # Output state
    final_layout: Dict[str, Any]
    figma_response: Dict[str, Any]

    # Metadata and control
    errors: List[str]
    messages: List[Any]
    status: str


# Define the nodes in our graph

def parse_requirements(state: AgentState) -> AgentState:
    """Parse the user prompt to extract requirements for the UI layout."""
    prompt = state["prompt"]
    print(f"Parsing requirements from prompt: {prompt}")

    # Use the LLM to extract structured requirements from the prompt
    requirement_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an expert UI/UX designer. Extract structured requirements from the user's prompt."),
        HumanMessage(content=f"""
            Extract the key UI requirements from this description. Focus on:
            1. Layout type (dashboard, form, landing page, etc.)
            2. Key components needed
            3. Style preferences (colors, themes)
            4. Responsive design requirements
            5. Any specific functionality mentioned

            USER PROMPT: {prompt}

            Format your response as JSON with appropriate keys and values.
        """)
    ])

    try:
        result = llm_provider.llm.invoke(requirement_prompt)
        content = result.content

        # Extract JSON from the response
        import re
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_match = re.search(json_pattern, content)

        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = content

        requirements = json.loads(json_str)

        return {
            **state,
            "parsed_requirements": requirements,
            "messages": state["messages"] + [{"role": "system", "content": "Requirements extracted successfully."}],
            "status": "requirements_parsed"
        }
    except Exception as e:
        error_msg = f"Error parsing requirements: {str(e)}"
        return {
            **state,
            "errors": state["errors"] + [error_msg],
            "messages": state["messages"] + [{"role": "system", "content": error_msg}],
            "status": "error"
        }


def generate_layout(state: AgentState) -> AgentState:
    """Generate the UI layout based on parsed requirements."""
    prompt = state["prompt"]
    requirements = state["parsed_requirements"]

    # We'll use our LLM provider to generate the layout
    try:
        # Convert requirements back to text to include in the prompt
        req_text = "\n".join([f"- {k}: {v}" for k, v in requirements.items()])

        # Construct a richer prompt using the extracted requirements
        enriched_prompt = f"""
            {prompt}

            Based on these requirements:
            {req_text}

            Create a detailed UI layout that satisfies all requirements.
        """

        # Generate the layout using our LLM provider
        layout_data = llm_provider.generate_ui_layout(enriched_prompt)

        return {
            **state,
            "layout_structure": layout_data,
            "messages": state["messages"] + [{"role": "system", "content": "UI layout structure generated."}],
            "status": "layout_generated"
        }
    except Exception as e:
        error_msg = f"Error generating layout: {str(e)}"
        return {
            **state,
            "errors": state["errors"] + [error_msg],
            "messages": state["messages"] + [{"role": "system", "content": error_msg}],
            "status": "error"
        }


def refine_layout(state: AgentState) -> AgentState:
    """Refine the generated layout to ensure Figma compatibility."""
    layout_data = state["layout_structure"]

    # Use the LLM to check and refine the layout for Figma compatibility
    refine_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an expert Figma designer. Check and refine the layout to ensure Figma compatibility."),
        HumanMessage(content=f"""
            Check this UI layout structure for Figma compatibility:

            ```json
            {json.dumps(layout_data, indent=2)}
            ```

            Make sure it:
            1. Uses correct Figma component types (FRAME, TEXT, RECTANGLE, etc.)
            2. Has all required properties for each component type
            3. Has valid color values, positions, and dimensions
            4. Maintains proper parent-child relationships

            Return the refined JSON structure only. If no changes are needed, return the original.
        """)
    ])

    try:
        result = llm_provider.llm.invoke(refine_prompt)
        content = result.content

        # Extract JSON from the response
        import re
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_match = re.search(json_pattern, content)

        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = content

        refined_layout = json.loads(json_str)

        return {
            **state,
            "final_layout": refined_layout,
            "messages": state["messages"] + [{"role": "system", "content": "UI layout refined for Figma compatibility."}],
            "status": "layout_refined"
        }
    except Exception as e:
        error_msg = f"Error refining layout: {str(e)}"
        return {
            **state,
            "errors": state["errors"] + [error_msg],
            "messages": state["messages"] + [{"role": "system", "content": error_msg}],
            "final_layout": layout_data,  # Use the unrefined layout
            "status": "partial_success"
        }


def export_to_figma(state: AgentState) -> AgentState:
    """Export the final layout to Figma if integration is enabled."""
    layout_data = state["final_layout"]

    # Skip if Figma integration is not enabled
    if not figma_api.is_enabled():
        return {
            **state,
            "figma_response": {"status": "skipped", "message": "Figma integration not enabled"},
            "messages": state["messages"] + [{"role": "system", "content": "Figma export skipped (integration not enabled)."}],
            "status": "completed"
        }

    # Export to Figma
    try:
        layout_name = layout_data.get("name", "Generated UI Layout")
        figma_response = figma_api.create_frame(layout_name, layout_data)

        return {
            **state,
            "figma_response": figma_response,
            "messages": state["messages"] + [{"role": "system", "content": "Layout exported to Figma successfully."}],
            "status": "completed"
        }
    except Exception as e:
        error_msg = f"Error exporting to Figma: {str(e)}"
        return {
            **state,
            "errors": state["errors"] + [error_msg],
            "figma_response": {"status": "error", "message": str(e)},
            "messages": state["messages"] + [{"role": "system", "content": error_msg}],
            "status": "completed_with_errors"
        }


def should_export_to_figma(state: AgentState) -> str:
    """Decide whether to export to Figma or end the workflow."""
    # Export to Figma only if we have a valid layout and no critical errors
    if (
        "final_layout" in state
        and state["final_layout"]
        and state["status"] not in ["error"]
    ):
        return "export_to_figma"
    else:
        return "end"


# Build the agent graph
def build_agent() :
    """Build the LangGraph workflow for the UI generation agent."""
    # Create a new graph
    workflow = StateGraph(AgentState)

    # Add nodes to the graph
    workflow.add_node("parse_requirements", parse_requirements)
    workflow.add_node("generate_layout", generate_layout)
    workflow.add_node("refine_layout", refine_layout)
    workflow.add_node("export_to_figma", export_to_figma)

    # Connect the nodes
    workflow.add_edge("parse_requirements", "generate_layout")
    workflow.add_edge("generate_layout", "refine_layout")
    workflow.add_conditional_edges(
        "refine_layout",
        should_export_to_figma,
        {
            "export_to_figma": "export_to_figma",
            "end": END,
        }
    )
    workflow.add_edge("export_to_figma", END)

    # Set the entry point
    workflow.set_entry_point("parse_requirements")

    # Compile the graph
    return workflow.compile()


# Create the agent with a memory saver for checkpointing
memory = MemorySaver()
ui_agent = build_agent()


def generate_ui_from_prompt(prompt: str) -> Dict[str, Any]:
    """Generate a UI layout from a natural language prompt.

    Args:
        prompt: Natural language description of the desired UI layout

    Returns:
        Dictionary containing the generated layout and process information
    """
    # Initialize the agent state
    initial_state: AgentState = {
        "prompt": prompt,
        "parsed_requirements": {},
        "layout_structure": {},
        "final_layout": {},
        "figma_response": {},
        "errors": [],
        "messages": [],
        "status": "started"
    }


    # Run the agent
    result = ui_agent.invoke(initial_state)

    # Return a simplified response
    return {
        "status": result["status"],
        "layout": result["final_layout"],
        "figma_response": result["figma_response"],
        "errors": result["errors"],
        "messages": result["messages"],
    }
