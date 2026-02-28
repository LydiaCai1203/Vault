"""Tool: search_trades - query trades with filters."""

from __future__ import annotations

from typing import Any

from app.db import TradeORM

from .common import get_db, parse_time, trade_to_dict
from .schema import ToolParam, make_remote_tool


def handle_search_trades(user_id: str, **kwargs: Any) -> dict:
    db = get_db()
    try:
        q = db.query(TradeORM).filter(TradeORM.user_id == user_id)

        if kwargs.get("symbol"):
            q = q.filter(TradeORM.symbol.ilike(f"%{kwargs['symbol']}%"))
        if kwargs.get("status"):
            q = q.filter(TradeORM.status == kwargs["status"])
        if kwargs.get("date_from"):
            q = q.filter(TradeORM.entry_time >= parse_time(kwargs["date_from"]))
        if kwargs.get("date_to"):
            q = q.filter(TradeORM.entry_time <= parse_time(kwargs["date_to"]))

        limit = int(kwargs.get("limit", 10))
        rows = q.order_by(TradeORM.entry_time.desc()).limit(limit).all()
        return {"trades": [trade_to_dict(r) for r in rows]}
    finally:
        db.close()


SEARCH_TRADES_PARAMS = [
    ToolParam("symbol", "string", "品种代码（模糊匹配）", required=False),
    ToolParam("date_from", "string", "起始日期 YYYY-MM-DD", required=False),
    ToolParam("date_to", "string", "截止日期 YYYY-MM-DD", required=False),
    ToolParam("status", "string", "状态: OPEN / CLOSED", required=False),
    ToolParam("limit", "number", "返回条数上限，默认10", required=False),
]

SEARCH_TRADES = make_remote_tool(
    name="search_trades",
    description="按条件搜索历史交易记录。",
    parameters=SEARCH_TRADES_PARAMS,
)
