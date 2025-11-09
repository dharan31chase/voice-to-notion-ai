#!/usr/bin/env python3
"""
Simple MCP Server - Proof of Concept
Tests basic file reading capability
"""

from mcp.server.fastmcp import FastMCP
import os

# Initialize MCP server
mcp = FastMCP(name="ai-assistant-poc")

@mcp.tool()
def read_file(path: str) -> str:
    """
    Read a file from the ai-assistant repo.

    Args:
        path: Relative path from repo root (e.g., 'README.md')

    Returns:
        File contents as string
    """
    repo_root = os.path.expanduser("~/Documents/1. Projects/ai-assistant")
    full_path = os.path.join(repo_root, path)

    if not os.path.exists(full_path):
        return f"Error: File not found at {full_path}"

    try:
        with open(full_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    mcp.run()
