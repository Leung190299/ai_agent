"""Configuration for the AI Agent.

This module contains configuration settings for the AI agent,
including model settings, API endpoints, and environment variables.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

class FigmaConfig(BaseModel):
    """Configuration for Figma API integration."""

    access_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("FIGMA_ACCESS_TOKEN"),
        description="Figma API access token"
    )
    file_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("FIGMA_FILE_KEY"),
        description="Figma file key to update"
    )
    enabled: bool = Field(
        default_factory=lambda: bool(os.getenv("FIGMA_ACCESS_TOKEN")),
        description="Whether Figma integration is enabled"
    )

class LLMConfig(BaseModel):
    """Configuration for the language model."""

    model_name: str = Field(
        default="deepseek",
        description="LLM model to use (deepseek or openai)"
    )
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"),
        description="API key for the LLM service"
    )
    temperature: float = Field(
        default=0.1,
        description="Temperature for model generation"
    )
    max_tokens: int = Field(
        default=1024,
        description="Maximum tokens for model generation"
    )

class AgentConfig(BaseModel):
    """Configuration for the AI Agent."""

    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG_MODE", "false").lower() == "true",
        description="Whether to enable debug mode"
    )
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent,
        description="Root directory of the project"
    )
    llm: LLMConfig = Field(
        default_factory=LLMConfig,
        description="LLM configuration"
    )
    figma: FigmaConfig = Field(
        default_factory=FigmaConfig,
        description="Figma configuration"
    )

# Create a global config instance
config = AgentConfig()
