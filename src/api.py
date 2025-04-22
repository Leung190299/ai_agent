"""API server for the AI Agent.

This module implements a FastAPI server to expose the AI agent's
functionality through a REST API.
"""

import json
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.agent import generate_ui_from_prompt
from src.config import config


# Define request and response models
class UIRequest(BaseModel):
    """Model for UI generation request."""
    prompt: str
    options: Optional[Dict[str, Any]] = None

class UIResponse(BaseModel):
    """Model for UI generation response."""
    status: str
    layout: Dict[str, Any]
    errors: list
    figma_url: Optional[str] = None

# Create the FastAPI app
app = FastAPI(
    title="AI UI Generator",
    description="Generate Figma-compatible UI layouts from natural language prompts",
    version="0.1.0",
)

@app.post("/generate", response_model=UIResponse)
async def generate_ui(request: UIRequest) -> Dict[str, Any]:
    """Generate a UI layout from a natural language prompt.

    Args:
        request: The UI generation request

    Returns:
        Generated UI layout and related information
    """
    try:
        # Generate UI layout
        result = generate_ui_from_prompt(request.prompt)

        # Extract Figma URL if available
        figma_url = None
        if (
            result.get("figma_response")
            and isinstance(result["figma_response"], dict)
            and result["figma_response"].get("url")
        ):
            figma_url = result["figma_response"]["url"]

        return {
            "status": result.get("status", "unknown"),
            "layout": result.get("layout", {}),
            "errors": result.get("errors", []),
            "figma_url": figma_url,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating UI layout: {str(e)}"
        )

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


def start_server():
    """Start the API server."""
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=config.debug
    )


if __name__ == "__main__":
    start_server()
