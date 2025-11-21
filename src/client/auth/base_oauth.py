from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token
import requests
import time
import json
import getpass
from pathlib import Path
from typing import Optional, Dict, Callable
import os

"""
OAuth2 Authentication Module for BrAPI Clients

This module provides OAuth2-based authentication for various BrAPI implementations,
handling token generation, storage, expiry checking, and automatic header injection.

Currently supported:
    - SGN-based BrAPI servers (Sweetpotatobase, Cassavabase, Yambase, etc.)

Future support planned:
    - GIGWA authentication
    - Standard OAuth2 authorization code flow
    - OAuth2 implicit flow

"""
class BrAPIOAuth2Session(OAuth2Session):
  """
  Base OAuth2 session for BrAPI authentication.

  This class extends authlib's OAuth2Session to provide:
  - Automatic token storage and loading (optional)
  - Token expiry checking
  - Automatic Authorization header injection
  - Token refresh callbacks

  Attributes:
      base_url (str): Base URL of the BrAPI server
      token_url (str): Full URL to the token endpoint
      token_file (str): Path to file where token is persisted (if enabled)
      token (OAuth2Token): Current authentication token
      store_token (bool): Whether to persist tokens to disk
  """

  def __init__(
    self,
    base_url: str,
    token_endpoint: str,
    token_file: str = '.brapi_token.json',
    store_token: bool = False,
    **kwargs,
  ):
    """
    Initialize OAuth2 session with optional token management.

    Args:
        base_url: Base URL of the BrAPI server (e.g., "https://sweetpotatobase.org/brapi/v2")
        token_endpoint: Path to token endpoint (e.g., "/brapi/v2/token")
        token_file: Path to JSON file for token persistence (only used if store_token=True)
        store_token: If True, tokens are persisted to disk. If False (default), tokens kept in memory only
        **kwargs: Additional arguments passed to OAuth2Session
    """
    self.base_url = base_url.rstrip('/')
    self.token_url = f'{self.base_url}{token_endpoint}'
    self.store_token = store_token

    # Only create temp directory if storing tokens to disk
    if self.store_token:
      self.temp_dir = os.path.join(os.getcwd(), '.brapi_temp')
      os.makedirs(self.temp_dir, exist_ok=True)
      self.token_file = os.path.join(self.temp_dir, token_file)
    else:
      self.temp_dir = None
      self.token_file = None

    # Load existing token only if storing is enabled
    token = self._load_token() if self.store_token else None

    # Initialize parent OAuth2Session with conditional token management
    super().__init__(
      token=token,
      token_endpoint=self.token_url,
      update_token=self._save_token if self.store_token else None,
      **kwargs,
    )

  def _save_token(self, token: Dict, refresh_token=None, access_token=None):
    """
    Save token to file (called automatically by authlib if store_token=True).

    This method is registered as a callback and will be invoked whenever
    the token changes (e.g., after login or refresh).

    Args:
        token: Token dictionary to save
        refresh_token: Optional refresh token (unused, for compatibility)
        access_token: Optional access token (unused, for compatibility)
    """
    # Skip if storing tokens is disabled
    if not self.store_token or not self.token_file:
      return

    # Convert OAuth2Token to dict if needed
    if isinstance(token, OAuth2Token):
      token = dict(token)

    # Write to file with pretty formatting
    Path(self.token_file).write_text(json.dumps(token, indent=2))
    print(f'[OK] Token saved to {self.token_file}')

  def _load_token(self) -> Optional[Dict]:
    """
    Load token from file if it exists and storing is enabled.

    Returns:
        Token dictionary if file exists and store_token=True, None otherwise
    """
    # Skip if storing tokens is disabled
    if not self.store_token or not self.token_file:
      return None

    try:
      token_data = json.loads(Path(self.token_file).read_text())
      print(f'[OK] Loaded existing token from {self.token_file}')
      return token_data
    except FileNotFoundError:
      print(f'[INFO] No existing token found at {self.token_file}')
      return None
    except json.JSONDecodeError as e:
      print(f'[WARNING] Could not parse token file: {e}')
      return None

  def is_authenticated(self) -> bool:
    """
    Check if session has a valid, non-expired token.

    Returns:
        True if authenticated with valid token, False otherwise
    """
    if not self.token:
      return False
    return not self.token.is_expired()

  def ensure_authenticated(self, login_callback: Optional[Callable] = None):
    """
    Ensure session is authenticated, prompting for login if needed.

    Args:
        login_callback: Optional function to call for login if token is expired.
                      Should accept no arguments and perform authentication.

    Raises:
        RuntimeError: If not authenticated and no login callback provided
    """
    if not self.is_authenticated():
      if login_callback:
        print('[WARNING] Token expired or missing, re-authenticating...')
        login_callback()
      else:
        raise RuntimeError('Not authenticated. Please call login() method first.')

