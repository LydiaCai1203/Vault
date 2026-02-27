"""Application configuration from environment variables."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Get PostgreSQL connection URL. Required for startup."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required (PostgreSQL only)")
    return url
