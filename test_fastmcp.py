#!/usr/bin/env python3
import sys

# Redirect BEFORE any imports
sys.stdout = sys.stderr

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("test")

@mcp.tool()
def hello() -> str:
    """Test tool"""
    return "Hello"

if __name__ == "__main__":
    # Restore stdout for MCP
    import sys
    sys.stdout = sys.__stdout__
    mcp.run()
