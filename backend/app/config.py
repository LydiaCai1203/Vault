"""Application configuration from config file (no environment variables)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
_config: dict[str, Any] | None = None


def _load_config() -> dict[str, Any]:
    global _config
    if _config is not None:
        return _config
    if not _CONFIG_PATH.is_file():
        raise RuntimeError(f"Config file required: {_CONFIG_PATH}")
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        _config = json.load(f)
    return _config


def get_database_url() -> str:
    """PostgreSQL connection URL. Required for startup."""
    url = _load_config().get("database_url")
    if not url:
        raise RuntimeError("config.json must set database_url (PostgreSQL only)")
    return url


def get_redis_url() -> str | None:
    """Redis URL for agent queue; null if not used."""
    return _load_config().get("redis_url")


def get_agent_mode() -> str:
    """Agent run mode: inline | sandbox."""
    return _load_config().get("agent_mode", "inline")


def get_llm_config() -> dict[str, str]:
    """LLM model names per agent (orchestrator, recorder, analyzer_interpret, reporter)."""
    return _load_config().get("llm") or {}
