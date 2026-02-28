"""Tool: get_open_trades - list open trades, optionally by symbol."""

from __future__ import annotations

from typing import Any

from app.db import TradeORM

from .common import get_db, trade_to_dict
from .schema import ToolParam, make_remote_tool


def handle_get_open_trades(user_id: str, **kwargs: Any) -> dict:
    db = get_db()
    try:
        q = db.query(TradeORM).filter(
            TradeORM.user_id == user_id,
            TradeORM.status == "OPEN",
        )
        symbol = kwargs.get("symbol")
        if symbol:
            q = q.filter(TradeORM.symbol.ilike(f"%{symbol}%"))
        rows = q.order_by(TradeORM.entry_time.desc()).limit(20).all()
        return {"trades": [trade_to_dict(r) for r in rows]}
    finally:
        db.close()


GET_OPEN_TRADES = make_remote_tool(
    name="get_open_trades",
    description="查询当前所有未平仓的持仓记录。可选按品种筛选。",
    parameters=[
        ToolParam("symbol", "string", "品种代码（可选，模糊匹配）", required=False),
    ],
)
