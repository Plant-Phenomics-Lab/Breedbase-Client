import requests
from typing import Dict, Any
from pathlib import Path

from client.auth.sgn_auth import create_sgn_session
from config.type import BrapiServerConfig
from utils import logger


class BrapiClient:
  def __init__(self, config: BrapiServerConfig):
    self.base_url = config.base_url.rstrip('/')
    self.session = create_sgn_session(
      base_url=self.base_url,
      auto_login=True,
      username=config.username,
      password=config.password,
      store_token=True,
    )
    self.download_path = config.downloads_dir

  def _get(self, path: str, params=None) -> Dict[str, Any]:
    url = f'{self.base_url}/{path.lstrip("/")}'
    try:
      resp = self.session.get(url, params=params, timeout=60)
      resp.raise_for_status()
      return resp.json()
    except requests.exceptions.HTTPError as e:
      logger.log(f'HTTP Error {e.response.status_code}: {e.response.reason}')
      logger.log(f'URL: {e.response.url}')
      logger.log(f'Response: {e.response.text}')
      return {}
    except requests.exceptions.RequestException as e:
      logger.log(f'Error making request to {url}: {e}')
      return {}

  def fetch_serverinfo(self) -> Dict[str, Any]:
    return self._get('serverinfo')

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
    try:
      response = self.session.get(url, stream=True, timeout=60)
      response.raise_for_status()

      with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
          f.write(chunk)

      return True

    except requests.exceptions.RequestException as e:
      logger.log(f'Error downloading file from {url}: {e}')
      return False
