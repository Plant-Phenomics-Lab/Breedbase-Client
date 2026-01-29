"""
PSA (Parental Selection Agent) - Simplified BrAPI MCP Server

Entry point for the STDIO-mode MCP server with purpose-built tools
for plant breeding data discovery and retrieval.

Usage:
    BRAPI_BASE_URL=https://sweetpotatobase.org/brapi/v2 \
    BRAPI_AUTH_TYPE=sgn \
    BRAPI_USERNAME=user \
    BRAPI_PASSWORD=pass \
    uv run python -m psa.main
"""

import sys
import os

# Ensure src is in path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP

from psa.config import get_config
from psa.client import init_client, get_client
from psa.tools.discovery import register_discovery_tools
from psa.tools.studies import register_study_tools
from psa.tools.observations import register_observation_tools
from psa.tools.germplasm import register_germplasm_tools


def create_server() -> FastMCP:
    """Create and configure the PSA MCP server with all tools."""
    # Load configuration from environment
    config = get_config()

    # Initialize the global BrAPI client
    client = init_client(config)

    # Create the MCP server
    server = FastMCP("PSA BrAPI Server")

    # Register all tool groups
    register_discovery_tools(server, client)
    register_study_tools(server, client)
    register_observation_tools(server, client, config)
    register_germplasm_tools(server, client)

    return server


def main():
    """Run the PSA MCP server in STDIO mode."""
    try:
        server = create_server()
        server.run()
    except ValueError as e:
        sys.stderr.write(f"Configuration error: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Server error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
