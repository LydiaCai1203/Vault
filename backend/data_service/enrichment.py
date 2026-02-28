"""Trade enrichment - augments trade records with market context data.

Takes raw trade dicts from the DB and enriches them with:
- K-line data during the holding period
- Historical K-lines before entry (for context)
- K-lines after exit (for hindsight analysis)
- Benchmark return during the period
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

from .market_data import KLine, MarketDataProvider, get_provider

logger = logging.getLogger(__name__)

CONTEXT_DAYS_BEFORE = 30
CONTEXT_DAYS_AFTER = 5
DEFAULT_BENCHMARK = "sh000001"


def enrich_trade(
    trade: dict,
    provider: MarketDataProvider | None = None,
) -> dict:
    """Enrich a single trade dict with market context data.

    Adds a 'market_context' key containing K-line data and benchmark info.
    If market data is unavailable, returns the trade unchanged with an empty context.
    """
    provider = provider or get_provider()
    symbol = trade.get("symbol", "")
    entry_time = trade.get("entry_time", "")
    exit_time = trade.get("exit_time", "")

    if not symbol or not entry_time:
        trade["market_context"] = _empty_context()
        return trade

    entry_date = _to_date_str(entry_time)
    exit_date = _to_date_str(exit_time) if exit_time else entry_date

    before_date = _offset_date(entry_date, -CONTEXT_DAYS_BEFORE)
    after_date = _offset_date(exit_date, CONTEXT_DAYS_AFTER) if exit_time else entry_date

    klines_before = provider.get_klines(symbol, before_date, _offset_date(entry_date, -1))
    klines_during = provider.get_klines(symbol, entry_date, exit_date)
    klines_after = []
    if exit_time:
        klines_after = provider.get_klines(symbol, _offset_date(exit_date, 1), after_date)

    benchmark_klines = provider.get_index_klines(DEFAULT_BENCHMARK, entry_date, exit_date)
    benchmark_return = _compute_return(benchmark_klines)

    trade["market_context"] = {
        "klines_before": [_kline_to_dict(k) for k in klines_before],
        "klines_during": [_kline_to_dict(k) for k in klines_during],
        "klines_after_exit": [_kline_to_dict(k) for k in klines_after],
        "benchmark_return": benchmark_return,
        "data_available": bool(klines_during),
    }

    return trade


def enrich_trades(
    trades: list[dict],
    provider: MarketDataProvider | None = None,
) -> list[dict]:
    """Enrich a list of trades with market context data."""
    provider = provider or get_provider()
    return [enrich_trade(t, provider) for t in trades]


def _to_date_str(time_str: str) -> str:
    """Extract YYYY-MM-DD from an ISO datetime string."""
    if not time_str:
        return ""
    return time_str[:10]


def _offset_date(date_str: str, days: int) -> str:
    """Offset a date string by N days."""
    try:
        d = date.fromisoformat(date_str)
        return (d + timedelta(days=days)).isoformat()
    except (ValueError, TypeError):
        return date_str


def _compute_return(klines: list[KLine]) -> float | None:
    """Compute simple return from first to last K-line close."""
    if len(klines) < 2:
        return None
    first_close = klines[0].close
    last_close = klines[-1].close
    if first_close <= 0:
        return None
    return round((last_close - first_close) / first_close, 6)


def _kline_to_dict(k: KLine) -> dict:
    return {
        "date": k.date,
        "open": k.open,
        "high": k.high,
        "low": k.low,
        "close": k.close,
        "volume": k.volume,
    }


def _empty_context() -> dict:
    return {
        "klines_before": [],
        "klines_during": [],
        "klines_after_exit": [],
        "benchmark_return": None,
        "data_available": False,
    }
