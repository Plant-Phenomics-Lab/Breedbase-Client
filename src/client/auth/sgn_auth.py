
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token
import requests
import time
import json
import getpass
from pathlib import Path
from typing import Optional, Dict, Callable
import os

from .base_oauth import BrAPIOAuth2Session
class SGNBrAPIOAuth2(BrAPIOAuth2Session):
  """
  OAuth2 session for SGN-based BrAPI servers (password grant flow).

  SGN (Sol Genomics Network) servers use a custom OAuth2 password grant
  implementation with a non-standard array-based request format:

  Request format:
      POST /brapi/v2/token
      Content-Type: application/json
      Body: [{
          "grant_type": "password",
          "username": "...",
          "password": "..."
      }]

  Response format:
      {
          "access_token": "...",
          "expires_in": 7200,
          "userDisplayName": "...",
          "metadata": {...}
      }

  Supported servers:
      - Sweetpotatobase.org
      - Cassavabase.org
      - Yambase.org
      - Musabase.org
      - And other SGN-based databases
  """

  def __init__(
    self,
    base_url: str,
    token_file: str = '.brapi_token.json',
    store_token: bool = False,
  ):
    """
    Initialize SGN BrAPI OAuth2 session.

    Args:
        base_url: Base URL (e.g., "https://sweetpotatobase.org")
        token_file: Path to token storage file (only used if store_token=True)
        store_token: If True, tokens are persisted to disk. If False (default), tokens kept in memory only
    """
    # SGN servers use /brapi/v2/token endpoint
    super().__init__(
      base_url=base_url,
      token_file=token_file,
      token_endpoint='/token',
      token_endpoint_auth_method=None,
      store_token=store_token,
    )
    self.login_time = None

  def login(
    self, username: Optional[str] = None, password: Optional[str] = None
  ) -> Dict:
    """
    Authenticate with username and password (OAuth2 password grant).

    This method implements SGN's custom array-based token request format.
    The token is kept in memory. If store_token=True, it's also saved to disk.

    Args:
        username: BrAPI username (prompted if None)
        password: BrAPI password (prompted if None, hidden input)

    Returns:
        Dictionary containing:
            - access_token: The bearer token
            - expires_at: Unix timestamp when token expires
            - userDisplayName: User's display name from server

    Raises:
        requests.HTTPError: If authentication fails
        ValueError: If credentials are invalid

    Example:
        >>> client = SGNBrAPIOAuth2("https://sweetpotatobase.org")
        >>> client.login("myusername", "mypassword")
        {'access_token': '...', 'expires_at': 1234567890, 'userDisplayName': 'John Doe'}
    """
    # Prompt for credentials if not provided
    if not username:
      username = input('Enter your BrAPI username: ')
    if not password:
      password = getpass.getpass('Enter your BrAPI password: ')

    # Validate credentials were provided
    if not username or not password:
      raise ValueError('Username and password must be provided')

    # Construct SGN's non-standard format
    # Note: This is NOT standard OAuth2, but required by SGN servers
    payload = {'grant_type': 'password', 'password': password, 'username': username}
  
    # Make authentication request
    response = requests.post(self.token_url, data=payload)

    # Raise exception if authentication failed
    response.raise_for_status()

    # Parse response
    data = response.json()

    # Extract token information
    access_token = data.get('access_token')
    expires_in = data.get('expires_in', 7200)  # Default 2 hours
    user_display_name = data.get('userDisplayName', username)

    if not access_token:
      raise ValueError('Server did not return an access token')

    # Convert to standard OAuth2 token format
    token = {
      'access_token': access_token,
      'token_type': 'Bearer',
      'expires_in': expires_in,
      'expires_at': int(time.time()) + expires_in,
      'userDisplayName': user_display_name,
    }

    # Save token in memory
    self.token = OAuth2Token(token)

    # Also save to disk if store_token=True
    if self.store_token:
      self._save_token(token)

    self.login_time = time.time()

    print(f'[OK] Login successful! Authenticated as: {user_display_name}')
    if not self.store_token:
      print(f'[INFO] Token stored in memory only (expires in {expires_in} seconds)')

    return token

  def logout(self):
    """
    Clear authentication token and optionally delete token file.

    Note: This is a local logout only. The server token remains valid
    until it expires naturally (no server-side revocation endpoint).
    """
    self.token = None

    # Only delete file if storing tokens to disk
    if self.store_token:
      try:
        Path(self.token_file).unlink()
        print(f'[OK] Token deleted from {self.token_file}')
      except FileNotFoundError:
        pass

    print('[OK] Logged out successfully')

  def _check_time(self):
    """
    Check before requests if token has expired.
    """
    if self.login_time and time.time() > self.login_time + self.token.get(
      'expires_in', 0
    ):
      print('[WARNING] Token has expired, logging in again.')
      self.logout()
      self.login()


# Convenience factory functions
def create_sgn_session(
  base_url: str = 'https://sweetpotatobase.org',
  token_file: str = '.brapi_token.json',
  auto_login: bool = False,
  username: Optional[str] = None,
  password: Optional[str] = None,
  store_token: bool = False,
) -> SGNBrAPIOAuth2:
  """
  Create an authenticated SGN BrAPI OAuth2 session.

  Args:
      base_url: Base URL of SGN server
      token_file: Path to token storage (only used if store_token=True)
      auto_login: If True, prompt for login if no valid token exists
      username: BrAPI username (optional, prompted if needed)
      password: BrAPI password (optional, prompted if needed)
      store_token: If True, tokens persisted to disk. If False (default), in-memory only

  Returns:
      Configured SGNBrAPIOAuth2 session

  Example:
      >>> # In-memory tokens (default, recommended for security)
      >>> session = create_sgn_session()
      >>> if not session.is_authenticated():
      ...     session.login()
      >>> response = session.get(f"{session.base_url}/brapi/v2/serverinfo")

      >>> # With disk persistence (for long-running processes)
      >>> session = create_sgn_session(store_token=True)
  """
  session = SGNBrAPIOAuth2(base_url, token_file, store_token=store_token)

  if auto_login and not session.is_authenticated():
    print('No valid token found.')
    session.login(username=username, password=password)

  return session
