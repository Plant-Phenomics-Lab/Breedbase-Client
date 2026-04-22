"""Simplified BrAPI HTTP client for PSA MCP Server."""

import logging
from typing import Any, Dict, Optional

from authlib.integrations.base_client.errors import InvalidTokenError

from .auth.sgn_auth import create_sgn_session
from .auth.no_auth import create_base_session
from .config import PSAConfig

logger = logging.getLogger(__name__)


class BrAPIClient:
    """
    Simplified BrAPI HTTP client with automatic authentication handling.

    Supports SGN OAuth2 authentication or no authentication for public endpoints.
    Automatically re-authenticates on token expiry.
    """

    def __init__(self, config: PSAConfig):
        """
        Initialize the BrAPI client.

        Args:
            config: PSA configuration with base_url and auth settings
        """
        self.config = config
        self.base_url = config.base_url

        if config.auth_type == "sgn":
            self.session = create_sgn_session(
                base_url=self.base_url,
                username=config.username,
                password=config.password,
                auto_login=True,
                store_token=False,
            )
        else:
            self.session = create_base_session()

    def _try_reauth(self) -> bool:
        """Attempt re-authentication for SGN sessions."""
        if self.config.auth_type != "sgn":
            return False

        if not self.config.username or not self.config.password:
            return False

        try:
            logger.info("Token expired, attempting re-authentication...")
            self.session.login(self.config.username, self.config.password)
            logger.info("Re-authentication successful")
            return True
        except Exception as e:
            logger.error(f"Re-authentication failed: {e}")
            return False

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to a BrAPI endpoint.

        Args:
            path: API path (e.g., "/locations" or "locations")
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.HTTPError: On HTTP errors
            InvalidTokenError: If authentication fails and re-auth not possible
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            resp = self.session.get(url, params=params, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except InvalidTokenError:
            if self._try_reauth():
                resp = self.session.get(url, params=params, timeout=60)
                resp.raise_for_status()
                return resp.json()
            raise

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request to a BrAPI endpoint.

        Args:
            path: API path
            json: JSON body
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.HTTPError: On HTTP errors
            InvalidTokenError: If authentication fails and re-auth not possible
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            resp = self.session.post(url, json=json, params=params, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except InvalidTokenError:
            if self._try_reauth():
                resp = self.session.post(url, json=json, params=params, timeout=60)
                resp.raise_for_status()
                return resp.json()
            raise


# Global client instance (initialized in main.py)
_client: Optional[BrAPIClient] = None


def init_client(config: PSAConfig) -> BrAPIClient:
    """Initialize the global BrAPI client."""
    global _client
    _client = BrAPIClient(config)
    return _client


def get_client() -> BrAPIClient:
    """Get the global BrAPI client instance."""
    if _client is None:
        raise RuntimeError("BrAPI client not initialized. Call init_client() first.")
    return _client
