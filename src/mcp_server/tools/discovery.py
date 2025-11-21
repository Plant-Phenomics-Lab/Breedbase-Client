
def register_discovery_tools(server, capabilities):
  @server.tool()
  def describe_server_capabilities():
    """
    Return a structured, LLM-friendly description of:
      - What endpoints exist
      - For each service: DbID support, Search support, description
    Derived entirely from ServerCapabilities.
    """
    return {
      'server': capabilities.server_name,
      'modules': {
        name: {
          'endpoints': list(m.endpoints.keys()),
        }
        for name, m in capabilities.modules.items()
      }
    }
