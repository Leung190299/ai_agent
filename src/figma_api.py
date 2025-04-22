"""Figma API integration module.

This module handles the integration with the Figma API,
allowing the agent to create and update designs in a Figma file.
"""

import json
from typing import Any, Dict, List, Optional

import requests

from config import config


class FigmaAPI:
    """Client for interacting with the Figma API."""

    def __init__(self):
        """Initialize the Figma API client with configuration."""
        self.access_token = config.figma.access_token
        self.file_key = config.figma.file_key
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            "X-Figma-Token": self.access_token,
            "Content-Type": "application/json"
        }

    def is_enabled(self) -> bool:
        """Check if the Figma integration is enabled."""
        return config.figma.enabled

    def get_file(self) -> Dict[str, Any]:
        """Get the current Figma file data."""
        if not self.is_enabled():
            return {"error": "Figma integration not enabled"}

        url = f"{self.base_url}/files/{self.file_key}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"Error accessing Figma file: {response.status_code}"
            if config.debug:
                print(error_msg)
                print(response.text)
            return {"error": error_msg}

    def create_frame(self, name: str, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new frame in the Figma file based on layout data.

        Args:
            name: Name of the frame to create
            layout_data: Structured layout data to convert into Figma components

        Returns:
            Response from the Figma API
        """
        if not self.is_enabled():
            return {"error": "Figma integration not enabled"}

        # Convert our layout data format to Figma's expected format
        figma_nodes = self._convert_layout_to_figma_nodes(layout_data)

        # Use the Figma plugin API endpoint for batch operations
        url = f"{self.base_url}/files/{self.file_key}/nodes"

        # We'll need to create the file structure first, then update properties
        # This is a simplified implementation and would need to be expanded
        # for a full-featured integration

        if config.debug:
            print(f"Would create Figma frame with data: {json.dumps(figma_nodes, indent=2)}")
            return {"status": "debug_mode", "nodes": figma_nodes}

        # In non-debug mode, we'd make the actual API call
        # This would require a more complex implementation working with the Figma Plugin API
        return {"error": "Full Figma integration requires a plugin implementation"}

    def _convert_layout_to_figma_nodes(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert our layout format to Figma's node structure.

        This is a simplified conversion that would need to be expanded
        for a full implementation.

        Args:
            layout_data: Our structured layout data

        Returns:
            Figma-compatible node structure
        """
        # This is a placeholder for the actual conversion logic
        # A full implementation would map our properties to Figma's API structure

        def convert_node(node):
            """Recursively convert a node and its children."""
            figma_node = {
                "name": node.get("name", "Unnamed"),
                "type": node.get("type", "FRAME"),
                "position": {
                    "x": node.get("x", 0),
                    "y": node.get("y", 0)
                },
                "size": {
                    "width": node.get("width", 100),
                    "height": node.get("height", 100)
                },
                "styles": {
                    "fills": [
                        {
                            "type": "SOLID",
                            "color": self._hex_to_rgb(node.get("backgroundColor", "#FFFFFF"))
                        }
                    ]
                }
            }

            if "children" in node and isinstance(node["children"], list):
                figma_node["children"] = [convert_node(child) for child in node["children"]]

            return figma_node

        return convert_node(layout_data)

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Dict[str, float]:
        """Convert hex color string to RGB dict with normalized values."""
        hex_color = hex_color.lstrip('#')
        return {
            "r": int(hex_color[0:2], 16) / 255.0,
            "g": int(hex_color[2:4], 16) / 255.0,
            "b": int(hex_color[4:6], 16) / 255.0
        }


# Create a global instance of the Figma API client
figma_api = FigmaAPI()
