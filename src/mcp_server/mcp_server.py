from mcp.server.fastmcp import FastMCP

from config.type import BrapiServerConfig
from client.client import BrapiClient
from client.capabilities.capability_builder import CapabilityBuilder

from mcp_server.tools.discovery import register_discovery_tools

class BrapiMcpServer:
  def __init__(self, config: BrapiServerConfig):
    self.config = config

  def create_server(self) -> FastMCP:
    client = BrapiClient(self.config)
    server_name = self.config.name
    caps = CapabilityBuilder.from_server(
      client,
      server_name
    )
    
    server = FastMCP(server_name)
    
    register_discovery_tools(server, capabilities=caps)
    return server