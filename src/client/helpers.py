"""Clean data fetching utilities"""

import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re

from client.client import BrapiClient
from config.type import BrapiServerConfig


def fetch_paginated(
  client: BrapiClient,
  endpoint: str,
  params: Optional[Dict] = None,
  max_pages: Optional[int] = 100,
  pagesize: int = 100,
  as_dataframe: bool = True,
) -> Tuple[Any, Dict[str, Any]]:
  """
  Fetch paginated data from any BrAPI endpoint.

  Args:
      client: BrapiClient instance
      endpoint: Full endpoint path (e.g., 'studies', 'studies/123', 'variantsets/vs1/calls')
      params: Query parameters
      max_pages: Maximum pages to fetch (None = all)
      pagesize: Results per page
      as_dataframe: Return DataFrame if True, else list of dicts

  Returns:
      Tuple of (data, metadata)
  """
  all_data = []
  page = 0
  params = params or {}
  params['pageSize'] = pagesize

  total_count = 0

  while max_pages is None or page < max_pages:
    params['page'] = page

    response = client._get(endpoint, params=params)

    if not response or 'result' not in response:
      break

    # Extract data from response
    data = _extract_data(response['result'])

    if not data:
      break

    all_data.extend(data)

    # Check pagination
    metadata = response.get('metadata', {})
    pagination = metadata.get('pagination', {})

    total_count = pagination.get('totalCount', len(all_data))
    current_page = pagination.get('currentPage', page)
    total_pages = pagination.get('totalPages', 1)

    if max_pages is not None:
      total_pages = min(total_pages, max_pages)

    if current_page >= total_pages - 1:
      break

    page += 1

  metadata = {
    'totalCount': total_count,
    'returnedCount': len(all_data),
    'pagesFetched': page + 1,
    'timestamp': datetime.now().isoformat(),
  }

  if as_dataframe:
    df = pd.json_normalize(all_data) if all_data else pd.DataFrame()
    return df, metadata

  return all_data, metadata


def search_paginated(
  client: BrapiClient,
  service: str,
  search_params: Dict,
  max_pages: Optional[int] = 100,
  pagesize: int = 100,
  as_dataframe: bool = True,
) -> Tuple[Any, Dict[str, Any]]:
  """
  Execute BrAPI search (POST then GET results).

  Args:
      client: BrapiClient instance
      service: Service name (e.g., 'studies', 'germplasm')
      search_params: Search parameters
      max_pages: Maximum pages to fetch
      pagesize: Results per page
      as_dataframe: Return DataFrame if True

  Returns:
      Tuple of (data, metadata)
  """
  import requests

  # POST search request
  search_url = f'{client.base_url}/search/{service}'

  try:
    response = client.session.post(search_url, json=search_params, timeout=60)
    response.raise_for_status()
    search_response = response.json()
  except requests.exceptions.RequestException as e:
    empty_meta = {
      'totalCount': 0,
      'returnedCount': 0,
      'timestamp': datetime.now().isoformat(),
      'error': str(e),
    }
    return (pd.DataFrame() if as_dataframe else []), empty_meta

  # Get searchResultsDbId
  result = search_response.get('result', {})
  search_id = result.get('searchResultsDbId')

  if not search_id:
    # Data returned directly
    data = _extract_data(result)
    metadata = {
      'totalCount': len(data),
      'returnedCount': len(data),
      'timestamp': datetime.now().isoformat(),
    }
    if as_dataframe:
      df = pd.json_normalize(data) if data else pd.DataFrame()
      return df, metadata
    return data, metadata

  # GET search results with pagination
  results_endpoint = f'search/{service}/{search_id}'

  return fetch_paginated(
    client=client,
    endpoint=results_endpoint,
    params=None,
    max_pages=max_pages,
    pagesize=pagesize,
    as_dataframe=as_dataframe,
  )


def _extract_data(result_obj: Any) -> List[Dict]:
  """Extract data array from BrAPI result object"""
  if isinstance(result_obj, dict) and 'data' in result_obj:
    return result_obj.get('data', [])
  elif isinstance(result_obj, list):
    return result_obj
  elif isinstance(result_obj, dict):
    return [result_obj]
  else:
    return []


def download_images_batch(
  client: BrapiClient, output_dir: str, image_records: List[Dict],
) -> Tuple[List[Dict], List[Dict]]:
  """
  Download a batch of images to output directory.

  This function only orchestrates - actual HTTP is done by client.

  Args:
      client: BrapiClient instance (handles session/auth)
      config: BrapiConfig
      image_records: List of image metadata dicts with 'imageURL', 'imageName', etc.

  Returns:
      Tuple of (downloaded_list, failed_list)
  """

  downloaded = []
  failed = []

  for idx, record in enumerate(image_records):
    image_name = str(record.get('imageName', record.get('imageFileName', f'image_{idx}')))
    image_url = record.get('imageURL')
    image_id = record.get('imageDbId', f'unknown_{idx}')

    if not image_url:
      failed.append(
        {
          'image_id': image_id,
          'image_name': image_name,
          'reason': 'No image URL available',
        }
      )
      continue

    # Sanitize filename
    safe_name = sanitize_filename(filename=image_name,default_name=image_id)
    image_path = output_dir / safe_name

    # Client handles the actual download
    success = client.download_file(url=image_url, output_path=image_path)

    if success:
      downloaded.append(
        {
          'image_id': image_id,
          'image_name': image_name,
          'local_path': str(image_path),
          'url': image_url,
        }
      )
    else:
      failed.append(
        {
          'image_id': image_id,
          'image_name': image_name,
          'url': image_url,
          'reason': 'Download failed (see logs)',
        }
      )

  return downloaded, failed


def sanitize_filename(filename: str, default_name: str) -> str:
  """Sanitize filename to be filesystem-safe"""
  safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
  safe = safe.strip('. ')
  if not safe:
    safe = default_name
  return safe
