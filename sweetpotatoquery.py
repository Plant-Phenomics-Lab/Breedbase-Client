#!/usr/bin/env python3
import sys
import io

# # Save original stdout for MCP protocol
# _original_stdout = sys.stdout

# # Redirect ALL prints to stderr during imports
# sys.stdout = sys.stderr

# Now import everything (prints won't corrupt MCP)
from mcp.server.fastmcp import FastMCP
from client_0_0 import BrAPIClient

# Initialize client (prints go to stderr)
sweetpotatobase = BrAPIClient(
    base_url="https://sweetpotatobase.org/brapi/v2",
    username="JerryHYu",
    password="$B1dX*JC$D!SeYpF"
)

# Restore stdout for MCP JSON protocol
# sys.stdout = _original_stdout

# Create MCP server
server = FastMCP("sweetpotatobasequery")

@server.tool()
def all_functions() -> str:
    """
    Use inherent funcitonality of the client to get a list of all possible endpoints
    """
    # Capture print output and return as string
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        sweetpotatobase.general_get(help=True)
        return captured.getvalue()
    finally:
        sys.stdout = old_stdout

@server.tool()
def specific_function(endpoint:str) -> str:
    """
    Get Data on a Specific Endpoint
    """
    return sweetpotatobase.general_get(help=endpoint)

if __name__ == "__main__":
    server.run()
