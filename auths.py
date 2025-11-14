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

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token
import requests
import time
import json
import getpass
from pathlib import Path
from typing import Optional, Dict, Callable
import os


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
        **kwargs
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
        self.token_url = f"{self.base_url}{token_endpoint}"
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
            **kwargs
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
        print(f"[OK] Token saved to {self.token_file}")

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
            print(f"[OK] Loaded existing token from {self.token_file}")
            return token_data
        except FileNotFoundError:
            print(f"[INFO] No existing token found at {self.token_file}")
            return None
        except json.JSONDecodeError as e:
            print(f"[WARNING] Could not parse token file: {e}")
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
                print("[WARNING] Token expired or missing, re-authenticating...")
                login_callback()
            else:
                raise RuntimeError(
                    "Not authenticated. Please call login() method first."
                )


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

    def __init__(self, base_url: str, token_file: str = '.brapi_token.json', store_token: bool = False):
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
            token_endpoint="/brapi/v2/token",
            token_endpoint_auth_method=None,
            store_token=store_token
        )
        self.login_time = None

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
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
            username = input("Enter your BrAPI username: ")
        if not password:
            password = getpass.getpass("Enter your BrAPI password: ")

        # Validate credentials were provided
        if not username or not password:
            raise ValueError("Username and password must be provided")

        # Construct SGN's non-standard format
        # Note: This is NOT standard OAuth2, but required by SGN servers
        payload = {
            "grant_type": "password",
            "password": password,
            "username": username
        }

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
            raise ValueError("Server did not return an access token")

        # Convert to standard OAuth2 token format
        token = {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': expires_in,
            'expires_at': int(time.time()) + expires_in,
            'userDisplayName': user_display_name
        }

        # Save token in memory
        self.token = OAuth2Token(token)
        
        # Also save to disk if store_token=True
        if self.store_token:
            self._save_token(token)
        
        self.login_time = time.time()

        print(f"[OK] Login successful! Authenticated as: {user_display_name}")
        if not self.store_token:
            print(f"[INFO] Token stored in memory only (expires in {expires_in} seconds)")

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
                print(f"[OK] Token deleted from {self.token_file}")
            except FileNotFoundError:
                pass

        print("[OK] Logged out successfully")

    def _check_time(self):
        """
        Check before requests if token has expired. 
        """
        if self.login_time and time.time() > self.login_time + self.token.get('expires_in', 0):
            print("[WARNING] Token has expired, logging in again.")
            self.logout()
            self.login()


# Convenience factory functions

def create_sgn_session(
    base_url: str = "https://sweetpotatobase.org",
    token_file: str = '.brapi_token.json',
    auto_login: bool = False,
    username: Optional[str] = None,
    password: Optional[str] = None,
    store_token: bool = False
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
        print("No valid token found. Please login:")
        session.login(username=username, password=password)

    return session

if __name__ == "__main__":
    """
    Example usage and testing
    """
    print("BrAPI OAuth2 Authentication Module")
    print("=" * 50)

    # Create session with in-memory tokens (default)
    client = create_sgn_session(
        base_url="https://sweetpotatobase.org",
        auto_login=False,
        store_token=False  # Explicitly in-memory only
    )

    # Check if already authenticated
    if client.is_authenticated():
        print("\n[INFO] Testing authenticated request...")
        try:
            response = client.get(f"{client.base_url}/brapi/v2/serverinfo")
            server_info = response.json()
            print(f"[OK] Connected to: {server_info.get('result', {}).get('serverName', 'Unknown')}")
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
    else:
        print("No valid token found. To test, run:")
        print("  from auths import create_sgn_session")
        print("  client = create_sgn_session()")
        print("  client.login()  # Will prompt for credentials")
