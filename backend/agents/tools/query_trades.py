"""Tool: query_trades - direct trade query (Orchestrator, no sub-Agent)."""

from __future__ import annotations

from typing import Any

from .schema import make_remote_tool
from .search_trades import handle_search_trades, SEARCH_TRADES_PARAMS


def handle_query_trades(user_id: str, **kwargs: Any) -> dict:
    return handle_search_trades(user_id=user_id, **kwargs)


QUERY_TRADES = make_remote_tool(
    name="query_trades",
    description="直接查询交易记录（简单查询不需要经过 Agent）。",
    parameters=SEARCH_TRADES_PARAMS,
)
