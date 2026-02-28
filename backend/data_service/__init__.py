"""Data Service - aggregates trade records with market context data.

Responsibilities:
- Fetch K-line (OHLCV) data for trade holding periods
- Fetch historical context data before entry
- Fetch post-exit data for hindsight analysis
- Fetch benchmark (index) returns for comparison
- Enrich trade dicts with market_context before passing to Analysis Engine
"""

from .service import enrich_trades, enrich_single_trade

__all__ = ["enrich_trades", "enrich_single_trade"]
