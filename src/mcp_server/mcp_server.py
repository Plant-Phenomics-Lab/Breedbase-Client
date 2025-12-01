# from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP

from config.type import BrapiServerConfig
from client.client import BrapiClient
from client.capabilities.capability_builder import CapabilityBuilder
from mcp_server.tools.generic.tools import register_discovery_tools, register_generic_tools
from mcp_server.tools.file_handling.images import register_image_tools

class BrapiMcpServer:
  def __init__(self, config: BrapiServerConfig):
    self.config = config

  def create_server(self) -> FastMCP:
    client = BrapiClient(self.config)
    server_name = self.config.name
    capabilities = CapabilityBuilder.from_server(
      client,
      server_name
    )
    
    server = FastMCP(server_name)
    
    register_discovery_tools(server, capabilities)
    register_generic_tools(server, client, capabilities)
    register_image_tools(server, client, capabilities, self.config)
    
    return server