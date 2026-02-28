"""Data Service - high-level API for fetching and enriching trade data.

Combines DB queries (via agents.tools handlers) with market data enrichment.
Used by the Orchestrator tool handlers to prepare data for the Analysis Engine.
"""

from __future__ import annotations

import logging
from typing import Any

from .enrichment import enrich_trade as _enrich_one, enrich_trades as _enrich_many
from .market_data import get_provider

logger = logging.getLogger(__name__)


def enrich_trades(trades: list[dict]) -> list[dict]:
    """Enrich a list of trade dicts with market context data.

    Safe to call even if akshare is not installed - returns trades unchanged
    with empty market_context in that case.
    """
    provider = get_provider()
    return _enrich_many(trades, provider)


def enrich_single_trade(trade: dict) -> dict:
    """Enrich a single trade dict with market context data."""
    provider = get_provider()
    return _enrich_one(trade, provider)
