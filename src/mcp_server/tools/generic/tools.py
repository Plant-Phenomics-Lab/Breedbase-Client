"""Generic BrAPI tools using general_get utility"""

from typing import Optional, Dict, Callable
import hashlib
import json
from fastmcp import FastMCP, Context
from client.client import BrapiClient
from client.capabilities.capability_builder import ServerCapabilities
from client.capabilities.helpers import (
  check_endpoint_exists,
  list_all_services,
  list_search_services,
)
from client.helpers import fetch_paginated, search_paginated


def register_discovery_tools(server, capabilities):
  @server.tool()
  def describe_server_capabilities(context: Context):
    """
    Return a structured JSON of server capabilities
    """
    return {
      'server': capabilities.server_name,
      'session_id': context.session_id,
      'modules': {
        name: {
          'endpoints': list(m.endpoints.keys()),
        }
        for name, m in capabilities.modules.items()
      },
    }


def register_generic_tools(
  server: FastMCP, client: BrapiClient, capabilities: ServerCapabilities, get_session_cache: Callable
):
  """
  Register generic tools based on server capabilities.
  Only creates tools for endpoints the server actually supports.
  Implemented: brapi_get, brapi_search, brapi_aggregate
  """

  @server.tool()
  def brapi_get(
    service: str,
    db_id: Optional[str] = None,
    sub: Optional[str] = None,
    params: Optional[Dict] = None,
    max_results: int = 100,
    session_id: Optional[str] = None, 
    context: Context = None,
  ) -> dict:
    """
    **GENERIC FALLBACK** - Use specific tools first if available!

    Fetch data from any BrAPI GET endpoint.

    Args:
        service: Service name (e.g., 'studies', 'germplasm', 'observations')
        db_id: Specific resource ID (optional)
        sub: Sub-resource (e.g., 'calls', 'variants', 'callsets')
        params: Query parameters for filtering
        max_results: Maximum results to return (max 500)
        session_id: Send session ID

    Examples:
        brapi_get('studies')
        brapi_get('studies', db_id='study123')
        brapi_get('variantsets', db_id='vs1', sub='calls')

    Returns:
        Metadata about the query and result_id for accessing data
    """
    # TODO :: Return complete data in any case?
    return_data = False
    # Check capabilities
    if not check_endpoint_exists(capabilities, service):
      return {
        'error': f"Service '{service}' not supported by this server",
        'hint': 'Use describe_server_capabilities() to see available services',
        # TODO :: Test if listing services is helpful/unnecessary
        'available_services': list_all_services(capabilities),
      }

    # Build endpoint
    endpoint_parts = [service]
    if db_id:
      endpoint_parts.append(db_id)
    if sub:
      if sub not in ['calls', 'callsets', 'variants']:
        return {'error': f"Invalid sub-resource '{sub}'"}
      if not db_id:
        return {'error': f"sub-resource '{sub}' requires db_id"}
      endpoint_parts.append(sub)

    endpoint = '/'.join(endpoint_parts)

    # Fetch data
    try:
      max_results = min(max_results, 500)
      max_pages = max_results // 100 + 1

      df, metadata = fetch_paginated(
        client=client,
        endpoint=endpoint,
        params=params,
        max_pages=max_pages,
        pagesize=min(100, max_results),
        as_dataframe=True,
      )

      # Limit and clean
      df = df.head(max_results)
      df = df.dropna(axis=1, how='all')

      result_cache, active_session_id = get_session_cache(context, session_id)

      query_hash = hashlib.md5(
          json.dumps({
              "service": service,
              "db_id": db_id,
              "sub": sub,
              "params": params
          }, sort_keys=True).encode()
      ).hexdigest()[:8]
      result_id = f"{service}_{query_hash}"

      result_cache.save_result(
          result_id=result_id,
          session_id=active_session_id,
          data=df,
          metadata={
              "query": {
                  "service": service,
                  "db_id": db_id,
                  "sub": sub,
                  "params": params
              },
              "endpoint": endpoint
          },
          format='csv'
      )

      response = {
          "result_id": result_id,
          "session_id": active_session_id,
          "query": {
              "service": service,
              "endpoint": endpoint,
              "db_id": db_id,
              "params": params
          },
          "summary": {
              "total_count": metadata.get('totalCount', len(df)),
              "returned_count": len(df),
              "columns": list(df.columns),
              "column_count": len(df.columns),
              "truncated": metadata.get('totalCount', 0) > max_results
          },
          "access": {
              "resource": f"brapi://results/{active_session_id}/{result_id}",
              "tools": {
                  "get_summary": f"get_result_summary('{active_session_id}','{result_id}')",
                  "load_result": f"load_result('{active_session_id}','{result_id}', limit=100)",
              }
          },
          "hint": f"Data saved to server. Use resource brapi://results/{active_session_id}/{result_id} or load_result('{active_session_id}','{result_id}') to access."
      }
      
      # Optionally include data (for small results)
      if return_data:
          response["data"] = df.to_dict(orient='records')
          response["warning"] = "Data included in response - use return_data=False for large datasets"
      
      return response
    except Exception as e:
      return {'error': str(e), 'service': service, 'endpoint': endpoint}

  @server.tool()
  def brapi_search(service: str, 
                   search_params: Dict, 
                   max_results: int = 100, 
                   session_id: Optional[str] = None, 
                   context: Context = None) -> dict:

    """
    **GENERIC FALLBACK** - Use specific search tools first if available!

    Search using POST /search/{service} endpoint.

    Args:
        service: Service name to search (e.g., 'studies', 'germplasm')
        search_params: Search parameters as dictionary
        max_results: Maximum results to return (max 500)
        session_id: Send session ID

    Examples:
        brapi_search('locations', {'countryNames': ['Mozambique']})
        brapi_search('studies', {'studyTypes': ['Advanced Yield Trial'],'locationDbIds': ['80']})

    Returns:
        Metadata about the search and result_id for accessing data
    """
    # Check if search is supported
    # TODO :: Return complete data in any case?
    return_data = False

    search_service = f'search/{service}'
    if not check_endpoint_exists(capabilities, search_service):
      return {
        'error': f"Search not supported for '{service}' on this server",
        'hint': 'Use describe_server_capabilities() to see available search endpoints',
        'available_search_services': list_search_services(capabilities),
      }

    result_cache, active_session_id = get_session_cache(context, session_id)
    # Execute search
    try:
      max_results = min(max_results, 500)
      max_pages = max_results // 100 + 1

      df, metadata = search_paginated(
        client=client,
        service=service,
        search_params=search_params,
        max_pages=max_pages,
        pagesize=min(100, max_results),
        as_dataframe=True,
      )

      # Limit and clean
      df = df.head(max_results)
      df = df.dropna(axis=1, how='all')

      query_hash = hashlib.md5(
                json.dumps({
                    "service": service,
                    "search_params": search_params
                }, sort_keys=True).encode()
            ).hexdigest()[:8]
      
      result_id = f"search_{service}_{query_hash}"

      result_cache.save_result(
          session_id= active_session_id,
          result_id=result_id,
          data=df,
          metadata={
              "query": {
                  "service": service,
                  "search_params": search_params,
                  "search": True
              }
          },
          format='csv'
      )

      response = {
          "result_id": result_id,
          'session_id': active_session_id,
          "query": {
              "service": service,
              "search_params": search_params
          },
          "summary": {
              "total_matches": metadata.get('totalCount', len(df)),
              "returned_count": len(df),
              "columns": list(df.columns),
              "column_count": len(df.columns),
              "truncated": metadata.get('totalCount', 0) > max_results
          },
          "access": {
              "resource": f"brapi://results/{active_session_id}/{result_id}",
              "tools": {
                  "get_summary": f"get_result_summary('{active_session_id}','{result_id}')",
                  "load_sample": f"load_result('{active_session_id}','{result_id}', limit=100)",
                  "load_columns": f"load_result('{active_session_id}','{result_id}', columns=['col1', 'col2'])"
              }
          },
          "hint": f"Data saved to server. Access via resource or load_result('{result_id}')"
      }
      if return_data:
        response["data"] = df.to_dict(orient='records')
        response["warning"] = "Data included - use return_data=False for large datasets"
      
      return response
    except Exception as e:
      return {'error': str(e), 'service': service}