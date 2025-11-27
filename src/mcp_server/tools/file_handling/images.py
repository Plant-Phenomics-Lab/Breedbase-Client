from typing import Optional, Dict
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from client.client import BrapiClient
from client.capabilities.capability_builder import ServerCapabilities
from client.helpers import fetch_paginated, search_paginated, download_images_batch
from client.capabilities.helpers import check_images_supported
from config.type import BrapiServerConfig


def register_image_tools(
  server: FastMCP,
  client: BrapiClient,
  capabilities: ServerCapabilities,
  config: BrapiServerConfig,
):
  """Register image-related tools"""

  @server.tool()
  def get_image_search_parameters() -> dict:
    """
    Get valid search parameters for the images endpoint.

    Returns schema of all valid search parameters with their types.
    Use this before calling download_images() to see what filters are available.
    """
    for module in capabilities.modules.values():
      for endpoint in module.endpoints.keys():
        if 'search/images' in endpoint:
          return {
            'service': 'search/images',
            'valid_parameters': module.endpoints[endpoint].input_schema,
            'description': 'Use these parameters with download_images()',
          }

    return {'error': 'Image search not supported by this server'}

  @server.tool()
  def download_images(
    search_params: Optional[Dict] = None,
    max_images: int = 50,
  ) -> dict:
    """
    Download images from BrAPI to local directory.

    Use get_image_search_parameters() first to see valid search parameters.

    Args:
        search_params: Search parameters dict (optional)
        max_images: Maximum images to download

    Returns:
        Download summary with success/failure counts
    """
    # Check capabilities
    if not check_images_supported(capabilities):
      return {'success': False, 'error': 'Images endpoint not supported by this server'}

    try:
      ts = datetime.now().strftime("%Y%m%d_%H%M%S")
      output_path = config.downloads_dir / ts
      output_path.mkdir(parents=True, exist_ok=True)

      # # Fetch image metadata (using our clean utility)
      # if search_params:
      #   df, metadata = search_paginated(
      #     client=client,
      #     service='images',
      #     search_params=search_params,
      #     max_pages=max_images // 100 + 1,
      #     pagesize=min(100, max_images),
      #     as_dataframe=True,
      #   )
      # else:
      df, metadata = fetch_paginated(
        client=client,
        endpoint='images',
        params=search_params,
        max_pages=max_images // 100 + 1,
        pagesize=min(100, max_images),
        as_dataframe=True,
      )

      if len(df) == 0:
        return {
          'success': True,
          'message': 'No images found matching criteria',
          'images_downloaded': 0,
        }

      # Limit to max_images
      df = df.head(max_images)

      # Convert to list of dicts for utility
      image_records = df.to_dict(orient='records')


      # Download images (utility orchestrates, client does HTTP)
      downloaded, failed = download_images_batch(
        client=client, output_dir=output_path, image_records=image_records
      )

      # Save metadata CSV
      metadata_path = output_path / 'images_metadata.csv'
      df.to_csv(metadata_path, index=False)

      return {
        'success': True,
        'output_directory': str(output_path.absolute()),
        'images_downloaded': len(downloaded),
        'images_failed': len(failed),
        'total_found': len(df),
        'metadata_csv': str(metadata_path),
        'downloaded_images': downloaded,
        'failed_images': failed if failed else None,
      }

    except Exception as e:
      return {'success': False, 'error': str(e)}
