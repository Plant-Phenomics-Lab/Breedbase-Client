"""Generic BrAPI tools using general_get utility"""

from typing import Optional, Dict
from mcp.server.fastmcp import FastMCP
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
  def describe_server_capabilities():
    """
    Return a structured JSON of server capabilities
    """
    return {
      'server': capabilities.server_name,
      'modules': {
        name: {
          'endpoints': list(m.endpoints.keys()),
        }
        for name, m in capabilities.modules.items()
      },
    }


def register_generic_tools(
  server: FastMCP, client: BrapiClient, capabilities: ServerCapabilities
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

    Examples:
        brapi_get('studies')
        brapi_get('studies', db_id='study123')
        brapi_get('variantsets', db_id='vs1', sub='calls')

    Returns:
        Data and metadata
    """
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

      return {
        'data': df.to_dict(orient='records'),
        'metadata': {
          'endpoint': endpoint,
          'service': service,
          'db_id': db_id,
          'sub_resource': sub,
          'total_count': metadata.get('totalCount', len(df)),
          'returned_count': len(df),
          'columns': list(df.columns),
          'truncated': metadata.get('totalCount', 0) > max_results,
        },
      }
    except Exception as e:
      return {'error': str(e), 'service': service, 'endpoint': endpoint}

  @server.tool()
  def brapi_search(service: str, search_params: Dict, max_results: int = 100) -> dict:
    """
    **GENERIC FALLBACK** - Use specific search tools first if available!

    Search using POST /search/{service} endpoint.

    Args:
        service: Service name to search (e.g., 'studies', 'germplasm')
        search_params: Search parameters as dictionary
        max_results: Maximum results to return (max 500)

    Examples:
        brapi_search('locations', {'countryNames': ['Mozambique']})
        brapi_search('studies', {'studyTypes': ['Advanced Yield Trial'],'locationDbIds': ['80']})

    Returns:
        Search results and metadata
    """
    # Check if search is supported
    search_service = f'search/{service}'
    if not check_endpoint_exists(capabilities, search_service):
      return {
        'error': f"Search not supported for '{service}' on this server",
        'hint': 'Use describe_server_capabilities() to see available search endpoints',
        'available_search_services': list_search_services(capabilities),
      }

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

      return {
        'data': df.to_dict(orient='records'),
        'metadata': {
          'service': service,
          'search_params': search_params,
          'total_count': metadata.get('totalCount', len(df)),
          'returned_count': len(df),
          'columns': list(df.columns),
          'truncated': metadata.get('totalCount', 0) > max_results,
        },
      }
    except Exception as e:
      return {'error': str(e), 'service': service}

  # TODO :: Experimental Tool
  @server.tool()
  def brapi_aggregate(
    service: str,
    aggregation: str,
    group_by: Optional[str] = None,
    params: Optional[Dict] = None,
  ) -> dict:
    """
    Server-side aggregation for large datasets.
    Avoids loading huge datasets into LLM context.

    Args:
        service: Service name (e.g., 'studies', 'observations')
        aggregation: Type - 'count', 'unique', 'distribution', 'stats'
        group_by: Column to group by (for 'unique' and 'distribution')
        params: Filter parameters (uses GET endpoint)

    Examples:
        brapi_aggregate('studies', 'count')
        brapi_aggregate('observations', 'distribution', group_by='observationVariableDbId')

    Returns:
        Compact aggregation results
    """
    # Check capabilities
    if not check_endpoint_exists(capabilities, service):
      return {
        'error': f"Service '{service}' not supported",
        'available_services': list_all_services(capabilities),
      }

    try:
      # Fetch ALL data server-side
      df, metadata = fetch_paginated(
        client=client,
        endpoint=service,
        params=params,
        max_pages=None,  # Fetch all for aggregation
        pagesize=100,
        as_dataframe=True,
      )

      result = {
        'service': service,
        'aggregation': aggregation,
        'total_records': len(df),
      }

      if aggregation == 'count':
        result['counts'] = {
          'total': len(df),
          'unique_per_column': {
            col: int(df[col].nunique()) for col in df.columns if len(df) > 0
          },
        }

      elif aggregation == 'unique':
        if not group_by:
          return {'error': "group_by required for 'unique' aggregation"}
        if group_by not in df.columns:
          return {
            'error': f"Column '{group_by}' not found",
            'available_columns': list(df.columns),
          }

        unique_vals = df[group_by].unique().tolist()[:100]
        result['column'] = group_by
        result['unique_values'] = unique_vals
        result['total_unique'] = int(df[group_by].nunique())
        result['truncated_to_100'] = df[group_by].nunique() > 100

      elif aggregation == 'distribution':
        if not group_by:
          return {'error': "group_by required for 'distribution' aggregation"}
        if group_by not in df.columns:
          return {
            'error': f"Column '{group_by}' not found",
            'available_columns': list(df.columns),
          }

        dist = df[group_by].value_counts().head(50)
        result['column'] = group_by
        result['distribution'] = {str(k): int(v) for k, v in dist.to_dict().items()}
        result['showing_top_50'] = len(dist) >= 50

      elif aggregation == 'stats':
        stats = df.describe(include='all').to_dict()
        result['statistics'] = stats

      else:
        return {
          'error': f'Unknown aggregation: {aggregation}',
          'valid_types': ['count', 'unique', 'distribution', 'stats'],
        }

      return result

    except Exception as e:
      return {'error': str(e), 'service': service}
