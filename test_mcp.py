from mcp.server.fastmcp import FastMCP

mcp = FastMCP("test")

@mcp.tool()
def hello() -> str:
    """Simple test tool"""
    return "Hello World"

if __name__ == "__main__":
    mcp.run()
