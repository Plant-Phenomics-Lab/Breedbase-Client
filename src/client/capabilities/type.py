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
  input_schema: Dict | None = None

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
      return bool(m and m.endpoints)
  
  def has_endpoint(self, endpoint: str) -> bool:
      ep = self.endpoints.get(endpoint)
      return bool(ep)

  def to_llm_format(self) -> Dict:
      """
      Simple format for LLM, list of base services by module + whether they support search, DBID or submodules.
      """
      consolidated = self.consolidate_modules()
      llm_formatted_modules = {}

      for module_name, module in consolidated["modules"].items():
          services_list = []
          
          for service_dict in module["services"]:
              services_list.append({
                  "name": service_dict["name"],
                  "supports_search": service_dict["supports_search"],
                  "supports_id": service_dict["supports_id"],
                  "sub_resources": service_dict["sub_resources"]
              })
          
          llm_formatted_modules[module_name] = services_list

      return {
          "server": self.server_name,
          "modules": llm_formatted_modules,
           "usage": {
              "note": "Use brapi_get() and brapi_search() tools with any service name",
              "examples": {
                  "list": "brapi_get('studies')",
                  "get_by_id": "brapi_get('studies', db_id='study123')",
                  "search": "brapi_search('studies', search_params={'studyName': 'Trial2024'})"
              }
           }
      }

  def _get_base_service(self, path: str) -> Optional[str]:
      """Extract base service name from path"""
      parts = path.strip('/').split('/')
      
      # Skip search result endpoints (they're internal)
      if 'search' in parts and '{searchResultsDbId}' in path:
          return None
      
      # For search endpoints, return the service being searched
      if parts[0] == 'search' and len(parts) > 1:
          return parts[1]
      
      # For regular endpoints, return the base
      return parts[0] if parts else None
  
  def consolidate_modules(self) -> Dict:
    """
    Convert capabilities to LLM-friendly consolidated format.
    Removes redundant /{id} endpoints and shows patterns clearly.
    """
    consolidated_modules = {}
    
    for module_name, module in self.modules.items():
        services = self._consolidate_module_endpoints(module)
        if services:
            consolidated_modules[module_name] = {
                "services": services
            }
    
    return {
        "server": self.server_name,
        "modules": consolidated_modules,
        "usage_guide": {
            "pattern": "All endpoints follow the same pattern",
            "examples": {
                "list": "brapi_get('service_name') - List all resources",
                "specific": "brapi_get('service_name', db_id='id') - Get specific resource",
                "search": "brapi_search('service_name', search_params={...}) - Search with filters",
                "sub_resource": "brapi_get('service_name', db_id='id', sub='calls') - Get sub-resource"
            },
            "note": "Check each service's 'supports_id', 'supports_search', and 'sub_resources' to see what's available"
        }
    }

  def _consolidate_module_endpoints(self, module: ModuleCapability) -> List[Dict]:
    """
    Consolidate module endpoints by removing redundant /{id} variants.
    Groups endpoints by base service.
    """
    # Group endpoints by base service
    services: Dict[str, Dict] = {}
    
    for path, endpoint in module.endpoints.items():
        base_service, has_id, sub_resource, is_search = self._parse_endpoint_path(path)
        
        # Initialize service if not exists
        if base_service not in services:
            services[base_service] = {
                "name": base_service,
                "methods": set(),
                "supports_id": False,
                "supports_search": False,
                "sub_resources": set(),
                "input_schema": None
            }
        
        # Accumulate info
        services[base_service]["methods"].update(endpoint.methods)
        
        if has_id:
            services[base_service]["supports_id"] = True
        
        if is_search:
            services[base_service]["supports_search"] = True
            # Save search schema
            if endpoint.input_schema:
                services[base_service]["input_schema"] = endpoint.input_schema
        
        if sub_resource:
            services[base_service]["sub_resources"].add(sub_resource)
    
    # Convert to list with usage examples
    result = []
    for service_name, info in services.items():
        service_dict = {
            "name": service_name,
            "methods": sorted(list(info["methods"])),
            "supports_id": info["supports_id"],
            "supports_search": info["supports_search"],
            "sub_resources": sorted(list(info["sub_resources"])) if info["sub_resources"] else None,
            "usage": self._generate_usage_examples(service_name, info)
        }
        
        # Add search schema if available
        if info["supports_search"] and info["input_schema"]:
            service_dict["search_parameters"] = info["input_schema"]
        
        result.append(service_dict)
    
    return sorted(result, key=lambda x: x["name"])

  def _parse_endpoint_path(self, path: str) -> tuple[str, bool, Optional[str], bool]:
    """
    Parse endpoint path into components.
    
    Returns:
        (base_service, has_id, sub_resource, is_search)
    
    Examples:
        'locations' -> ('locations', False, None, False)
        'locations/{locationDbId}' -> ('locations', True, None, False)
        'variantsets/{variantSetDbId}/calls' -> ('variantsets', True, 'calls', False)
        'search/locations/{searchResultsDbId}' -> ('locations', False, None, True)
    """
    parts = path.strip('/').split('/')
    
    # Handle search endpoints
    if parts[0] == 'search':
        base_service = parts[1] if len(parts) > 1 else 'unknown'
        # Ignore {searchResultsDbId} - it's just the GET results endpoint
        return (base_service, False, None, True)
    
    # Regular endpoints
    base_service = parts[0]
    has_id = len(parts) > 1 and '{' in parts[1]
    
    # Sub-resource (e.g., variantsets/{id}/calls)
    sub_resource = None
    if len(parts) > 2 and '{' not in parts[2]:
        sub_resource = parts[2]
    
    return (base_service, has_id, sub_resource, False)

  def _generate_usage_examples(self, service: str, info: Dict) -> Dict:
    """Generate usage examples for a service"""
    usage = {}
    
    # List all
    usage["list_all"] = f"brapi_get('{service}')"
    
    # Get specific
    if info["supports_id"]:
        usage["get_specific"] = f"brapi_get('{service}', db_id='id123')"
    
    # Search
    if info["supports_search"]:
        usage["search"] = f"brapi_search('{service}', search_params={{...}})"
        usage["get_search_params"] = f"get_search_parameters('{service}')"
    
    # Sub-resources
    if info["sub_resources"]:
        for sub in sorted(info["sub_resources"]):
            usage[f"get_{sub}"] = f"brapi_get('{service}', db_id='id123', sub='{sub}')"
    
    return usage

  def get_service_info(self, service: str) -> Optional[Dict]:
    """
    Get consolidated info for a specific service.
    Useful for the get_service_usage() tool.
    """
    llm_format = self.consolidate_modules()
    
    # Search across all modules
    for module_name, module_data in llm_format["modules"].items():
        for service_info in module_data["services"]:
            if service_info["name"] == service:
                return {
                    **service_info,
                    "module": module_name
                }
    
    return None
