from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token
import json
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
    """

    def __init__(
        self,
        base_url: str,
        token_endpoint: str,
        token_file: str = ".brapi_token.json",
        store_token: bool = False,
        **kwargs,
    ):
        """
        Initialize OAuth2 session with optional token management.

        Args:
            base_url: Base URL of the BrAPI server
            token_endpoint: Path to token endpoint
            token_file: Path to JSON file for token persistence
            store_token: If True, tokens are persisted to disk
            **kwargs: Additional arguments passed to OAuth2Session
        """
        self.base_url = base_url.rstrip("/")
        self.token_url = f"{self.base_url}{token_endpoint}"
        self.store_token = store_token

        if self.store_token:
            self.temp_dir = os.path.join(os.getcwd(), ".brapi_temp")
            os.makedirs(self.temp_dir, exist_ok=True)
            self.token_file = os.path.join(self.temp_dir, token_file)
        else:
            self.temp_dir = None
            self.token_file = None

        token = self._load_token() if self.store_token else None

        super().__init__(
            token=token,
            token_endpoint=self.token_url,
            update_token=self._save_token if self.store_token else None,
            **kwargs,
        )

    def _save_token(self, token: Dict, refresh_token=None, access_token=None):
        """Save token to file (called automatically by authlib if store_token=True)."""
        if not self.store_token or not self.token_file:
            return

        if isinstance(token, OAuth2Token):
            token = dict(token)

        Path(self.token_file).write_text(json.dumps(token, indent=2))

    def _load_token(self) -> Optional[Dict]:
        """Load token from file if it exists and storing is enabled."""
        if not self.store_token or not self.token_file:
            return None

        try:
            token_data = json.loads(Path(self.token_file).read_text())
            return token_data
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def is_authenticated(self) -> bool:
        """Check if session has a valid, non-expired token."""
        if not self.token:
            return False
        return not self.token.is_expired()

    def ensure_authenticated(self, login_callback: Optional[Callable] = None):
        """Ensure session is authenticated, prompting for login if needed."""
        if not self.is_authenticated():
            if login_callback:
                login_callback()
            else:
                raise RuntimeError("Not authenticated. Please call login() method first.")
