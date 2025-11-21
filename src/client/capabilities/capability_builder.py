import pandas as pd

from .type import ServerCapabilities, ModuleCapability, EndpointCapability
from ..client import BrapiClient
from pathlib import Path

class CapabilityBuilder:
  @classmethod
  def from_server(cls, client: BrapiClient, server_name: str):
    serverinfo = client.fetch_serverinfo()
    result = serverinfo.get('result', {})
    calls = result.get('calls', []) or []
    
    metadata = pd.read_csv(Path(__file__).parent.parent / 'data' / 'metadata.csv')

    caps = ServerCapabilities(server_name=server_name)

    # Build modules dynamically as we discover them
    # modules: dict[str, ModuleCapability]
    modules = {}

    for call in calls:
      path = call.get('service')
      if not path:
        continue

      methods = set(call.get('methods') or [])
      data_types = call.get('dataTypes') or []

      # Prefer category from metadata
      row = metadata.loc[metadata['service'] == path]
      if not row.empty:
          category = row.iloc[0]['category']
      else:
          category = None

      if category:
        module = category.lower()
      else:
        continue

      # Ensure module exists
      if module and module not in modules:
        modules[module] = ModuleCapability(module)

      ep = EndpointCapability(
        path=path,
        methods=methods,
        data_types=data_types,
        module=module,
        description=row.iloc[0]['description'],
        input_schema=row.iloc[0]['dictionary_loc']
      )

      # register endpoint
      caps.endpoints[path] = ep

      if module:
        modules[module].endpoints[path] = ep

    # Assign modules to capability object
    caps.modules = modules
    return caps