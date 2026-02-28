"""Shared helpers for tool handlers (DB, trade serialization, time parsing)."""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.db import TradeORM, SessionLocal, loads, dumps

logger = logging.getLogger(__name__)


def get_db() -> Session:
    return SessionLocal()


def trade_to_dict(t: TradeORM) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": t.id,
        "symbol": t.symbol,
        "name": t.name,
        "market": t.market,
        "direction": t.direction,
        "status": t.status,
        "entry_time": t.entry_time.isoformat() if t.entry_time else None,
        "entry_price": t.entry_price,
        "exit_time": t.exit_time.isoformat() if t.exit_time else None,
        "exit_price": t.exit_price,
        "position_pct": t.position_pct,
        "stop_loss": t.stop_loss,
        "pnl_cny": t.pnl_cny,
        "entry_reason": t.entry_reason,
        "notes": t.notes,
        "emotion_tags": loads(t.emotion_tags_json),
        "rule_flags": loads(t.rule_flags_json),
        "tags": loads(t.tags_json),
    }
    if getattr(t, "entry_snapshot_json", None):
        out["entry_snapshot"] = loads(t.entry_snapshot_json)
    return out


def parse_time(s: str) -> datetime:
    from dateutil.parser import parse as dt_parse
    try:
        return dt_parse(s)
    except Exception:
        return datetime.now(timezone.utc)


def get_record_hints(user_id: str, trade_id: str, symbol: str, position_pct: float) -> dict[str, Any]:
    """无摩擦提示：本周笔数、同标的持仓笔数、总仓位占比。仅事实陈述，不拦截。"""
    db = get_db()
    try:
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        week_count = (
            db.query(TradeORM)
            .filter(TradeORM.user_id == user_id, TradeORM.entry_time >= week_start)
            .count()
        )

        open_trades = (
            db.query(TradeORM)
            .filter(TradeORM.user_id == user_id, TradeORM.status == "OPEN")
            .all()
        )
        same_symbol_open = sum(1 for t in open_trades if t.symbol and t.symbol.strip() == symbol.strip())
        total_position_pct = sum((t.position_pct or 0) for t in open_trades)

        return {
            "week_trade_count": week_count,
            "same_symbol_open_count": same_symbol_open,
            "total_open_position_pct": round(total_position_pct, 2),
        }
    except Exception as e:
        logger.debug("record hints failed: %s", e)
        return {}
    finally:
        db.close()


def schedule_entry_snapshot(user_id: str, trade_id: str) -> None:
    """后台线程：拉取该笔交易的入场日市场快照并写入 entry_snapshot_json。不阻塞保存。"""
    def _run() -> None:
        try:
            from app.db import SessionLocal, dumps
            from data_service.service import enrich_single_trade

            db = SessionLocal()
            try:
                t = db.query(TradeORM).filter(TradeORM.id == trade_id, TradeORM.user_id == user_id).first()
                if not t:
                    return
                trade = trade_to_dict(t)
                enrich_single_trade(trade)
                snapshot = trade.get("market_context")
                if not snapshot:
                    return
                t.entry_snapshot_json = dumps(snapshot)
                t.updated_at = datetime.now(timezone.utc)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.warning("entry snapshot failed for trade %s: %s", trade_id, e)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
