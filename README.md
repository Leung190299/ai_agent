# AI Agent for Figma-Compatible UI Generation

This project implements an AI agent that can generate Figma-compatible templates or UI layouts from natural language prompts.

## Features

- Convert natural language descriptions into structured UI layouts
- Generate Figma-compatible JSON output
- Optional direct Figma integration via API
- REST API server for web integration
- Command-line interface for direct usage

## Architecture

The agent uses LangChain and LangGraph for workflow orchestration with the following components:

1. **LLM Integration**: Uses DeepSeek (with OpenAI fallback) for natural language understanding and generation
2. **LangGraph Agent**: Implements a multi-step workflow for requirement parsing, layout generation, and refinement
3. **Figma Formatter**: Ensures generated layouts follow Figma's structure requirements
4. **API Server**: Exposes functionality as a web service using FastAPI

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai_agent

# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following variables:

```
# API keys for LLM services
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here (fallback)

# Optional Figma API credentials
FIGMA_ACCESS_TOKEN=your_figma_access_token_here
FIGMA_FILE_KEY=your_figma_file_key_here

# Agent configuration
DEBUG_MODE=true
```

## Usage

### Command Line Interface

Generate a UI layout from a prompt:

```bash
python -m src.main "Create a dashboard layout with sidebar, header, and chart area"
```

Save the output to a file:

```bash
python -m src.main "Create a login form with email and password fields" --output layout.json
```

### API Server

Start the API server:

```bash
python -m src.api
```

Then make a POST request to the `/generate` endpoint:

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a product details page with image gallery and reviews section"}'
```

## Project Structure

```
ai_agent/
├── src/
│   ├── __init__.py        # Package initialization
│   ├── agent.py           # LangGraph agent implementation
│   ├── api.py             # FastAPI server
│   ├── config.py          # Configuration management
│   ├── figma_api.py       # Figma API integration
│   ├── formatter.py       # Figma-compatible output formatter
│   ├── llm.py             # LLM provider integration
│   └── main.py            # Command-line interface
├── tests/                 # Test directory
├── data/                  # Sample data and resources
├── .env                   # Environment variables
└── requirements.txt       # Project dependencies
```

## License

[MIT License](LICENSE)
