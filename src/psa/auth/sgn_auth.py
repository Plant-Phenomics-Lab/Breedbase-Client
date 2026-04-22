from authlib.oauth2.rfc6749 import OAuth2Token
import requests
import time
from pathlib import Path
from typing import Optional, Dict

from .base_oauth import BrAPIOAuth2Session


class SGNBrAPIOAuth2(BrAPIOAuth2Session):
    """
    OAuth2 session for SGN-based BrAPI servers (password grant flow).

    SGN (Sol Genomics Network) servers use a custom OAuth2 password grant
    implementation. Supported servers include Sweetpotatobase, Cassavabase,
    Yambase, Musabase, and other SGN-based databases.
    """

    def __init__(
        self,
        base_url: str,
        token_file: str = ".brapi_token.json",
        store_token: bool = False,
    ):
        """
        Initialize SGN BrAPI OAuth2 session.

        Args:
            base_url: Base URL (e.g., "https://sweetpotatobase.org/brapi/v2")
            token_file: Path to token storage file
            store_token: If True, tokens are persisted to disk
        """
        super().__init__(
            base_url=base_url,
            token_file=token_file,
            token_endpoint="/token",
            token_endpoint_auth_method=None,
            store_token=store_token,
        )
        self.login_time = None

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """
        Authenticate with username and password (OAuth2 password grant).

        Args:
            username: BrAPI username
            password: BrAPI password

        Returns:
            Token dictionary with access_token, expires_at, userDisplayName

        Raises:
            requests.HTTPError: If authentication fails
            ValueError: If credentials are invalid
        """
        if not username or not password:
            raise ValueError("Username and password must be provided")

        payload = {"grant_type": "password", "password": password, "username": username}
        response = requests.post(self.token_url, data=payload)
        response.raise_for_status()

        data = response.json()
        access_token = data.get("access_token")
        expires_in = data.get("expires_in", 7200)
        user_display_name = data.get("userDisplayName", username)

        if not access_token:
            raise ValueError("Server did not return an access token")

        token = {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "expires_at": int(time.time()) + expires_in,
            "userDisplayName": user_display_name,
        }

        self.token = OAuth2Token(token)

        if self.store_token:
            self._save_token(token)

        self.login_time = time.time()
        return token

    def logout(self):
        """Clear authentication token."""
        self.token = None
        if self.store_token and self.token_file:
            try:
                Path(self.token_file).unlink()
            except FileNotFoundError:
                pass


def create_sgn_session(
    base_url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    auto_login: bool = False,
    store_token: bool = False,
) -> SGNBrAPIOAuth2:
    """
    Create an SGN BrAPI OAuth2 session.

    Args:
        base_url: Base URL of SGN server
        username: BrAPI username
        password: BrAPI password
        auto_login: If True, login immediately
        store_token: If True, tokens persisted to disk

    Returns:
        Configured SGNBrAPIOAuth2 session
    """
    session = SGNBrAPIOAuth2(base_url, store_token=store_token)

    if auto_login and username and password:
        session.login(username=username, password=password)

    return session
