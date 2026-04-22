"""Configuration from environment variables for PSA MCP Server."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class PSAConfig:
    """Configuration for the PSA BrAPI MCP Server."""

    base_url: str
    auth_type: str
    username: Optional[str]
    password: Optional[str]
    data_dir: str

    @classmethod
    def from_env(cls) -> "PSAConfig":
        """
        Load configuration from environment variables.

        Environment variables:
            BRAPI_BASE_URL: Base URL for BrAPI server (required)
            BRAPI_AUTH_TYPE: Authentication type - "sgn" or "none" (default: "none")
            BRAPI_USERNAME: Username for authentication (required if auth_type="sgn")
            BRAPI_PASSWORD: Password for authentication (required if auth_type="sgn")
            BRAPI_DATA_DIR: Directory for downloaded data (default: "./data")

        Returns:
            PSAConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        base_url = os.environ.get("BRAPI_BASE_URL")
        if not base_url:
            raise ValueError("BRAPI_BASE_URL environment variable is required")

        auth_type = os.environ.get("BRAPI_AUTH_TYPE", "none").lower()
        username = os.environ.get("BRAPI_USERNAME")
        password = os.environ.get("BRAPI_PASSWORD")
        data_dir = os.environ.get("BRAPI_DATA_DIR", "./data")

        if auth_type == "sgn" and (not username or not password):
            raise ValueError(
                "BRAPI_USERNAME and BRAPI_PASSWORD are required when BRAPI_AUTH_TYPE=sgn"
            )

        return cls(
            base_url=base_url.rstrip("/"),
            auth_type=auth_type,
            username=username,
            password=password,
            data_dir=data_dir,
        )


# Singleton config instance - loaded on import
def get_config() -> PSAConfig:
    """Get the PSA configuration from environment variables."""
    return PSAConfig.from_env()
