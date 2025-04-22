"""Main application module for the AI Agent.

This module provides the main entry point and API for the AI agent.
"""

import json
from typing import Any, Dict, Optional

from src.agent import generate_ui_from_prompt
from src.config import config


def generate_ui_layout(prompt: str, output_json: bool = False) -> Dict[str, Any]:
    """Generate a UI layout from a natural language prompt.

    Args:
        prompt: Natural language description of the UI layout
        output_json: Whether to output the result as JSON string

    Returns:
        Dictionary or JSON string with generated layout
    """
    # Use our agent to generate the UI layout
    result = generate_ui_from_prompt(prompt)

    if output_json:
        return json.dumps(result, indent=2)

    return result


def main():
    """Command-line entry point for the application."""
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate UI layouts from natural language prompts")
    parser.add_argument("prompt", nargs="?", help="Natural language prompt describing the UI layout")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    parser.add_argument("--output", "-o", help="Output file path to save the result")

    args = parser.parse_args()

    # If no prompt is provided, enter interactive mode
    if not args.prompt:
        print("Enter a prompt describing the UI layout you want to generate.")
        print("Type 'quit' or 'exit' to exit.")

        while True:
            prompt = input("\nPrompt> ")

            if prompt.lower() in ["quit", "exit"]:
                break

            if not prompt.strip():
                continue

            # Generate UI layout
            try:
                result = generate_ui_layout(prompt, args.json)

                if args.output:
                    with open(args.output, "w") as f:
                        if args.json:
                            f.write(result)
                        else:
                            f.write(json.dumps(result, indent=2))
                    print(f"Result saved to {args.output}")
                else:
                    if args.json:
                        print(result)
                    else:
                        print("\nGENERATED LAYOUT:")
                        print(json.dumps(result["layout"], indent=2))

                        if result.get("errors"):
                            print("\nERRORS:")
                            for error in result["errors"]:
                                print(f"- {error}")
            except Exception as e:
                print(f"Error: {str(e)}")
    else:
        # Process a single prompt
        try:
            result = generate_ui_layout(args.prompt, args.json)

            if args.output:
                with open(args.output, "w") as f:
                    if args.json:
                        f.write(result)
                    else:
                        f.write(json.dumps(result, indent=2))
                print(f"Result saved to {args.output}")
            else:
                if args.json:
                    print(result)
                else:
                    print("\nGENERATED LAYOUT:")
                    print(json.dumps(result["layout"], indent=2))

                    if result.get("errors"):
                        print("\nERRORS:")
                        for error in result["errors"]:
                            print(f"- {error}")
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
