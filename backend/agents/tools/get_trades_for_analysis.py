"""Tool: get_trades_for_analysis - fetch trades in date range for analysis."""

from __future__ import annotations

from typing import Any

from app.db import TradeORM

from .common import get_db, parse_time, trade_to_dict


def handle_get_trades_for_analysis(user_id: str, **kwargs: Any) -> dict:
    """Fetch trades for a date range, used by Orchestrator's call_analyzer."""
    db = get_db()
    try:
        q = db.query(TradeORM).filter(TradeORM.user_id == user_id)
        if kwargs.get("date_from"):
            q = q.filter(TradeORM.entry_time >= parse_time(kwargs["date_from"]))
        if kwargs.get("date_to"):
            q = q.filter(TradeORM.entry_time <= parse_time(kwargs["date_to"]))
        rows = q.order_by(TradeORM.entry_time.asc()).all()
        return {"trades": [trade_to_dict(r) for r in rows]}
    finally:
        db.close()
