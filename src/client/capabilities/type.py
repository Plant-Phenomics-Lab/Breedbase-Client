# brapi_mcp/client/capabilities.py
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


@dataclass
class EndpointCapability:
  path: str
  methods: Set[str]
  data_types: List[str]
  module: Optional[str] = None
  description: Optional[str] = None
  input_schema: Dict = None

@dataclass
class ModuleCapability:
  name: str
  endpoints: Dict[str, EndpointCapability] = field(default_factory=dict)


@dataclass
class ServerCapabilities:
  server_name: str
  modules: Dict[str, ModuleCapability] = field(default_factory=dict)
  endpoints: Dict[str, EndpointCapability] = field(default_factory=dict)

  def supports_module(self, module: str) -> bool:
    m = self.modules.get(module)
    return bool(m and m.implemented)

  def has_endpoint(self, endpoint: str) -> bool:
    ep = self.endpoints.get(endpoint)
    return bool(ep and ep.enabled)
