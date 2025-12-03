from typing import Optional, Callable
from pathlib import Path
from fastmcp import FastMCP, Context
from src.mcp_server.session.result_cache import ResultCache
import json


def register_result_cache_tools(server: FastMCP, get_session_cache: Callable):
  """Tools for working with saved results"""

  @server.resource('brapi://results/{session_id}')
  def list_saved_results(context: Context, session_id: str) -> str:
    """List all saved results"""
    result_cache, _ = get_session_cache(context, session_id)

    results = result_cache.list_results()

    summary = {
      'total_results': len(results),
      'results': [
        {
          'result_id': info['result_id'],
          'query': info['metadata'].get('query'),
          'row_count': info['row_count'],
          'columns': info['columns'],
          'size_mb': round(info['size_bytes'] / 1024 / 1024, 2),
          'created_at': info['created_at'],
        }
        for info in results.values()
      ],
    }

    return json.dumps(summary, indent=2)

  @server.resource('brapi://results/{session_id}/{result_id}')
  def get_result(context: Context, session_id: str, result_id: str) -> str:
    """
    Get a saved result as CSV text (for small results).

    For large results, use load_result() tool with limit instead.
    """
    result_cache, _ = get_session_cache(context, session_id)
    info = result_cache.get_result_info(result_id)

    if not info:
      return json.dumps({'error': f"Result '{result_id}' not found"})

    # Only return as resource if small (<1000 rows)
    if info['row_count'] > 1000:
      return json.dumps(
        {
          'error': 'Result too large to return as resource',
          'row_count': info['row_count'],
          'hint': f"Use load_result('{result_id}', limit=100) tool instead",
        }
      )

    # Read and return CSV
    with open(info['file_path'], 'r') as f:
      return f.read()

  @server.tool()
  def get_result_summary(context: Context, session_id: str, result_id: str) -> dict:
    """
    Get summary of a saved result WITHOUT loading data.

    Use this to understand what's in the result.

    Args:
        session_id: Session ID
        result_id: ID of saved result

    Returns:
        Metadata: columns, row count, size, etc.
    """
    result_cache, _ = get_session_cache(context, session_id)
    info = result_cache.get_result_info(result_id)

    if not info:
      return {
        'error': f"Result '{result_id}' not found",
        'available_results': list(result_cache.list_results().keys()),
      }

    return {
      'result_id': info['result_id'],
      'description': info['metadata'].get('query'),
      'row_count': info['row_count'],
      'column_count': info['column_count'],
      'columns': info['columns'],
      'size_mb': round(info['size_bytes'] / 1024 / 1024, 2),
      'created_at': info['created_at'],
    }

  @server.tool()
  def load_result(
    context: Context,
    session_id: str,
    result_id: str,
    limit: Optional[int] = None,
    columns: Optional[list[str]] = None,
    offset: int = 0,
  ) -> dict:
    """
    Load a saved result (or part of it) into context.

    **Use this sparingly** - only load what you need for analysis.

    Args:
        result_id: ID of saved result
        session_id: Session ID
        limit: Maximum rows to load (default: all)
        columns: Specific columns to load (default: all)
        offset: Skip first N rows (for pagination)

    Examples:
        # Load first 100 rows for sampling
        load_result('study123_obs', limit=100)

        # Load specific columns for analysis
        load_result('study123_obs', columns=['traitName', 'value'], limit=500)

        # Paginate through results
        load_result('study123_obs', limit=100, offset=0)   # First 100
        load_result('study123_obs', limit=100, offset=100) # Next 100

    Returns:
        Data and metadata
    """
    try:
      # Load with offset support
      result_cache, _ = get_session_cache(context, session_id)
      result_data = result_cache.load_result(result_id=result_id, limit=limit, columns=columns)

      # Apply offset if needed
      if offset > 0:
        data = result_data['data'][offset:]
        if limit:
          data = data[:limit]
        result_data['data'] = data
        result_data['metadata']['offset'] = offset

      return {'success': True, **result_data}
    except Exception as e:
      return {'success': False, 'error': str(e)}

  @server.tool()
  def get_download_instructions(result_id: str, session_id: Optional[str] = None, context: Context = None) -> dict:
    """
    Get instructions for downloading a result via HTTP.

    Returns URLs and examples for various download methods.

    Args:
        result_id: Result ID to download
        session_id: Optional session ID

    Returns:
        Download URLs and command examples
    """
    if not context:
      return {'error': 'No conversation context available'}

    try:
      result_cache, active_session_id = get_session_cache(context, session_id)
    except PermissionError as e:
      return {'error': str(e)}

    info = result_cache.get_result_info(result_id)
    if not info:
      return {'error': f"Result '{result_id}' not found"}

    base_url = 'http://localhost:8000'  # Get from config
    download_url = f'{base_url}/download/{active_session_id}/{result_id}'

    return {
      'result_id': result_id,
      'session_id': active_session_id,
      'file_info': {
        'format': info['format'],
        'size_mb': round(info['size_bytes'] / 1024 / 1024, 2),
        'row_count': info['row_count'],
        'columns': info['columns'],
      },
      'download': {
        'url': download_url,
      },
      # 'format_conversion': {
      #   'csv': f'{download_url}?format=csv',
      #   'json': f'{download_url}?format=json',
      #   'parquet': f'{download_url}?format=parquet',
      # },
    }

  @server.tool()
  def quick_download_link(result_id: str, session_id: Optional[str] = None, context: Context = None) -> dict:
    """
    Get a quick download link (just the URL).

    For simple "give me the download link" queries.
    """
    if not context:
      return {'error': 'No conversation context'}

    try:
      result_cache, active_session_id = get_session_cache(context, session_id)
    except PermissionError as e:
      return {'error': str(e)}

    info = result_cache.get_result_info(result_id)
    if not info:
      return {'error': f"Result '{result_id}' not found"}

    base_url = 'http://localhost:8000'
    download_url = f'{base_url}/download/{active_session_id}/{result_id}'

    return {
      'download_url': download_url,
    }
