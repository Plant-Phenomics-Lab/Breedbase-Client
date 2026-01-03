import requests
from typing import Dict, Any
from pathlib import Path
import sys
from utils import logger
import logging
from authlib.integrations.base_client.errors import InvalidTokenError
from client.auth.sgn_auth import create_sgn_session
from client.auth.no_auth import create_base_session
from config.type import BrapiServerConfig


class BrapiClient:
  def __init__(self, config: BrapiServerConfig):
    self.username = config.username
    self.password = config.password
    self.base_url = config.base_url.rstrip('/')
    
    # Normalize auth type to lowercase for comparison
    self._auth_type = config.authtype.lower() if config.authtype else None
    
    if self._auth_type == "sgn":
      self.session = create_sgn_session(
        base_url=self.base_url,
        auto_login=True,
        username=self.username,
        password=self.password,
        store_token=False,
      )
    else:
      # Default to base session if no auth type or unknown type
      self.session = create_base_session()
    self.download_path = config.downloads_dir

  def _try_reauth(self) -> bool:
    """
    Attempt re-authentication once for SGN sessions.
    
    SGN servers don't support OAuth2 refresh tokens, so we must
    re-authenticate with username/password when the token expires.
    
    Returns:
        True if re-auth successful, False otherwise
    """
    if self._auth_type != "sgn":
      return False
    
    if not hasattr(self.session, 'login') or not self.username or not self.password:
      logging.info("Re-auth skipped: missing login method or credentials")
      return False
    
    try:
      logging.info("Token expired, attempting re-authentication...")
      self.session.login(self.username, self.password)
      logging.info("Re-authentication successful")
      return True
    except Exception as e:
      logging.error(f"Re-authentication failed: {e}")
      return False

  def _get(self, path: str, params=None) -> Dict[str, Any]:
    url = f'{self.base_url}/{path.lstrip("/")}'
    try:
      # Let other execptions bubble up to the tool wrapper
      resp = self.session.get(url, params=params, timeout=60)
      resp.raise_for_status()
      return resp.json()
    except InvalidTokenError:
      if self._try_reauth():
        resp = self.session.get(url, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()
      raise

  def _post(self, path: str, json=None, data=None, params=None) -> Dict[str, Any]:
    url = f'{self.base_url}/{path.lstrip("/")}'
    try:
      resp = self.session.post(url, json=json, data=data, params=params, timeout=60)
      resp.raise_for_status()
      return resp.json()
    except InvalidTokenError:
      if self._try_reauth():
        resp = self.session.post(url, json=json, data=data, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()
      raise

  def fetch_serverinfo(self) -> Dict[str, Any]:
    # Use direct session call to avoid logging issues during startup
    # If this fails, we just return empty dict and let capability builder handle defaults
    url = f'{self.base_url}/serverinfo'
    try:
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
