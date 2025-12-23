import requests
from typing import Dict, Any
from pathlib import Path
import sys
from client.auth.sgn_auth import create_sgn_session
from client.auth.no_auth import create_base_session
from config.type import BrapiServerConfig
from utils import logger


class BrapiClient:
  def __init__(self, config: BrapiServerConfig):
    self.base_url = config.base_url.rstrip('/')
    
    # Normalize auth type to lowercase for comparison
    auth_type = config.authtype.lower() if config.authtype else None
    
    if auth_type == "sgn":
      self.session = create_sgn_session(
        base_url=self.base_url,
        auto_login=True,
        username=config.username,
        password=config.password,
        store_token=False,
      )
    else:
      # Default to base session if no auth type or unknown type
      self.session = create_base_session()
    self.download_path = config.downloads_dir

  def _get(self, path: str, params=None) -> Dict[str, Any]:
    url = f'{self.base_url}/{path.lstrip("/")}'
    # Let exceptions bubble up to be handled by the tool wrapper
    resp = self.session.get(url, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()

  def fetch_serverinfo(self) -> Dict[str, Any]:
    # Use direct session call to avoid logging issues during startup
    # If this fails, we just return empty dict and let capability builder handle defaults
    try:
      url = f'{self.base_url}/serverinfo'
      resp = self.session.get(url, timeout=10)
      resp.raise_for_status()
      # sys.stderr.write(f"{resp.json()}")
      return resp.json()
    except Exception as e:
      sys.stderr.write(f"Error fetching serverinfo from {url}: {e}\n")
      return {}

  def download_file(self, url: str, output_path: Path) -> bool:
    """
    Download a file from URL to local path.
    Uses the same session for authentication.

    Args:
        url: Full URL to download from
        output_path: Local path to save file

    Returns:
        True if successful, False otherwise
    """
    # Let exceptions bubble up to be handled by the tool wrapper
    response = self.session.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
      for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

    return True
