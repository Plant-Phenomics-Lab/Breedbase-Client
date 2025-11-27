from client.capabilities.capability_builder import ServerCapabilities


def check_endpoint_exists(capabilities: ServerCapabilities, service: str) -> bool:
  """Check if a service endpoint exists in capabilities"""
  service_clean = service.lstrip('/')

  for module in capabilities.modules.values():
    for endpoint in module.endpoints:
      if service_clean in endpoint:
        return True

  return False


def list_all_services(capabilities: ServerCapabilities) -> list[str]:
  """List all available service endpoints"""
  services = []
  for module in capabilities.modules.values():
    services.extend(module.endpoints.keys())
  return sorted(set(services))


def list_search_services(capabilities: ServerCapabilities) -> list[str]:
  """List all available search endpoints"""
  services = []
  for module in capabilities.modules.values():
    for endpoint in module.endpoints.keys():
      if endpoint.startswith('search/'):
        services.append(endpoint.replace('search/', ''))
  return sorted(set(services))


def check_images_supported(capabilities: ServerCapabilities) -> bool:
  """Check if images endpoint is supported"""
  for module in capabilities.modules.values():
    if 'images' in module.endpoints or 'search/images' in module.endpoints:
      return True
  return False
