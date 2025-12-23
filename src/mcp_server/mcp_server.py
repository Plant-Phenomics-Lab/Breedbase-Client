from fastmcp import FastMCP, Context
from typing import Optional

from config.type import BrapiServerConfig
from client.client import BrapiClient
from client.capabilities.capability_builder import CapabilityBuilder
from mcp_server.session.session_manager import SessionManager
from mcp_server.session.result_cache import ResultCache
from mcp_server.tools.generic.tools import (
  register_discovery_tools,
  register_generic_tools,
)
from mcp_server.tools.file_handling.images import register_image_tools
from mcp_server.tools.file_handling.result_cache import register_result_cache_tools


class BrapiMcpServer:
  def __init__(self, config: BrapiServerConfig):
    self.config = config
    self.session_manager = SessionManager(config.sessions_dir)

  def get_session_cache(
    self,
    context: Optional[Context] = None,
    session_id: Optional[str] = None,
  ) -> tuple[ResultCache, str]:
    """
    Get cache for session. Survives server restarts.
    """
    return self.session_manager.get_or_create_session(session_id, context)

  def create_server(self) -> FastMCP:
    client = BrapiClient(self.config)
    server_name = self.config.name
    capabilities = CapabilityBuilder.from_server(client, server_name)

    server = FastMCP(server_name)

    register_discovery_tools(server, capabilities)
    register_generic_tools(server, client, capabilities, self.get_session_cache)
    register_image_tools(server, client, capabilities, self.config)
    register_result_cache_tools(server, self.get_session_cache, self.config)

    return server
