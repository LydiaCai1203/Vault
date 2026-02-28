"""Tool proxy handlers - execute DB operations on behalf of sandboxed agents.

Each handler function receives user_id as first kwarg, then tool-specific args.
All DB queries are filtered by user_id for tenant isolation.
"""

from __future__ import annotations

import logging
import threading
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.db import TradeORM, SessionLocal, loads, dumps

logger = logging.getLogger(__name__)


def _get_db() -> Session:
    return SessionLocal()


def _get_record_hints(user_id: str, trade_id: str, symbol: str, position_pct: float) -> dict:
    """无摩擦提示：本周笔数、同标的持仓笔数、总仓位占比。仅事实陈述，不拦截。"""
    db = _get_db()
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


def _schedule_entry_snapshot(user_id: str, trade_id: str) -> None:
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
                trade = _trade_to_dict(t)
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


def handle_create_trade(user_id: str, **kwargs: Any) -> dict:
    db = _get_db()
    try:
        now = datetime.now(timezone.utc)
        trade_id = str(uuid.uuid4())

        emotion_tags = []
        if kwargs.get("emotion_tags"):
            emotion_tags = [t.strip() for t in kwargs["emotion_tags"].split(",")]

        tags = []
        if kwargs.get("tags"):
            tags = [t.strip() for t in kwargs["tags"].split(",")]

        symbol = kwargs.get("symbol", "")
        position_pct = float(kwargs.get("position_pct", 0))

        trade = TradeORM(
            id=trade_id,
            user_id=user_id,
            symbol=symbol,
            name=kwargs.get("name", symbol or ""),
            market=kwargs.get("market", "沪A"),
            direction=kwargs.get("direction", "LONG"),
            status="OPEN",
            entry_price=float(kwargs.get("entry_price", 0)),
            entry_time=_parse_time(kwargs.get("entry_time", now.isoformat())),
            position_pct=position_pct,
            stop_loss=float(kwargs["stop_loss"]) if kwargs.get("stop_loss") else None,
            pnl_cny=None,
            exit_price=None,
            exit_time=None,
            entry_reason=kwargs.get("entry_reason", ""),
            notes=kwargs.get("notes"),
            emotion_tags_json=dumps(emotion_tags),
            rule_flags_json=dumps([]),
            tags_json=dumps(tags),
            created_at=now,
            updated_at=now,
        )
        db.add(trade)
        db.commit()

        hints = _get_record_hints(user_id, trade_id, symbol, position_pct)
        _schedule_entry_snapshot(user_id, trade_id)

        return {"trade_id": trade_id, "status": "created", "hints": hints}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def handle_update_trade(user_id: str, **kwargs: Any) -> dict:
    db = _get_db()
    try:
        trade_id = kwargs.get("trade_id")
        if not trade_id:
            return {"error": "trade_id is required"}

        trade = (
            db.query(TradeORM)
            .filter(TradeORM.id == trade_id, TradeORM.user_id == user_id)
            .first()
        )
        if not trade:
            return {"error": f"trade {trade_id} not found"}

        now = datetime.now(timezone.utc)

        if kwargs.get("status"):
            trade.status = kwargs["status"]
        if kwargs.get("exit_price") is not None:
            trade.exit_price = float(kwargs["exit_price"])
        if kwargs.get("exit_time"):
            trade.exit_time = _parse_time(kwargs["exit_time"])
        if kwargs.get("pnl_cny") is not None:
            trade.pnl_cny = float(kwargs["pnl_cny"])
        if kwargs.get("emotion_tags"):
            tags = [t.strip() for t in kwargs["emotion_tags"].split(",")]
            trade.emotion_tags_json = dumps(tags)
        if kwargs.get("notes"):
            trade.notes = kwargs["notes"]

        trade.updated_at = now
        db.commit()
        return {"trade_id": trade_id, "status": "updated"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def handle_get_open_trades(user_id: str, **kwargs: Any) -> dict:
    db = _get_db()
    try:
        q = db.query(TradeORM).filter(
            TradeORM.user_id == user_id,
            TradeORM.status == "OPEN",
        )
        symbol = kwargs.get("symbol")
        if symbol:
            q = q.filter(TradeORM.symbol.ilike(f"%{symbol}%"))
        rows = q.order_by(TradeORM.entry_time.desc()).limit(20).all()
        return {"trades": [_trade_to_dict(r) for r in rows]}
    finally:
        db.close()


def handle_search_trades(user_id: str, **kwargs: Any) -> dict:
    db = _get_db()
    try:
        q = db.query(TradeORM).filter(TradeORM.user_id == user_id)

        if kwargs.get("symbol"):
            q = q.filter(TradeORM.symbol.ilike(f"%{kwargs['symbol']}%"))
        if kwargs.get("status"):
            q = q.filter(TradeORM.status == kwargs["status"])
        if kwargs.get("date_from"):
            q = q.filter(TradeORM.entry_time >= _parse_time(kwargs["date_from"]))
        if kwargs.get("date_to"):
            q = q.filter(TradeORM.entry_time <= _parse_time(kwargs["date_to"]))

        limit = int(kwargs.get("limit", 10))
        rows = q.order_by(TradeORM.entry_time.desc()).limit(limit).all()
        return {"trades": [_trade_to_dict(r) for r in rows]}
    finally:
        db.close()


def handle_get_trades_for_analysis(user_id: str, **kwargs: Any) -> dict:
    """Fetch trades for a date range, used by Orchestrator's call_analyzer."""
    db = _get_db()
    try:
        q = db.query(TradeORM).filter(TradeORM.user_id == user_id)
        if kwargs.get("date_from"):
            q = q.filter(TradeORM.entry_time >= _parse_time(kwargs["date_from"]))
        if kwargs.get("date_to"):
            q = q.filter(TradeORM.entry_time <= _parse_time(kwargs["date_to"]))
        rows = q.order_by(TradeORM.entry_time.asc()).all()
        return {"trades": [_trade_to_dict(r) for r in rows]}
    finally:
        db.close()


def handle_get_previous_report(user_id: str, **kwargs: Any) -> dict:
    """Fetch the most recent review/report for comparison."""
    from app.db import ReviewORM

    db = _get_db()
    try:
        report_type = kwargs.get("type", "WEEKLY")
        row = (
            db.query(ReviewORM)
            .filter(ReviewORM.user_id == user_id, ReviewORM.type == report_type)
            .order_by(ReviewORM.created_at.desc())
            .first()
        )
        if not row:
            return {"found": False}

        import json
        payload = json.loads(row.payload_json) if row.payload_json else {}
        return {
            "found": True,
            "id": row.id,
            "type": row.type,
            "range_start": str(row.range_start),
            "range_end": str(row.range_end),
            "payload": payload,
        }
    finally:
        db.close()


def _trade_to_dict(t: TradeORM) -> dict:
    out = {
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


def _parse_time(s: str) -> datetime:
    from dateutil.parser import parse as dt_parse
    try:
        return dt_parse(s)
    except Exception:
        return datetime.now(timezone.utc)


def handle_call_recorder(user_id: str, **kwargs: Any) -> dict:
    """Orchestrator tool: delegate to Recorder Agent (inline)."""
    from agents.recorder.agent import RecorderAgent

    payload = {"input": kwargs.get("input", "")}
    if kwargs.get("context"):
        import json
        try:
            payload["context"] = json.loads(kwargs["context"])
        except (json.JSONDecodeError, TypeError):
            payload["context"] = {"raw": kwargs["context"]}

    agent = RecorderAgent()
    result = agent.run(payload)
    return {
        "success": result.success,
        "result": result.result,
        "error": result.error,
        "need_user_input": result.need_user_input,
    }


def handle_call_analyzer(user_id: str, **kwargs: Any) -> dict:
    """Orchestrator tool: DataService enrichment -> Analysis Engine.

    Flow: fetch trades -> enrich with market data -> run analysis engine.
    """
    from analysis.engine import analyze
    from data_service.service import enrich_trades

    trades_data = handle_get_trades_for_analysis(
        user_id=user_id,
        date_from=kwargs.get("date_from", ""),
        date_to=kwargs.get("date_to", ""),
    )
    trades = trades_data.get("trades", [])

    enriched = enrich_trades(trades)

    result = analyze(
        enriched,
        style=kwargs.get("style", "technical"),
        analysis_type=kwargs.get("analysis_type", "batch"),
        trade_id=kwargs.get("trade_id"),
    )
    return result


def handle_call_reporter(user_id: str, **kwargs: Any) -> dict:
    """Orchestrator tool: delegate to Reporter Agent (inline)."""
    from agents.reporter.agent import ReporterAgent

    payload = {
        "report_type": kwargs.get("report_type", "weekly"),
        "analysis_data": kwargs.get("analysis_data", "{}"),
        "date_from": kwargs.get("date_from"),
        "date_to": kwargs.get("date_to"),
    }

    agent = ReporterAgent()
    result = agent.run(payload)
    return {
        "success": result.success,
        "result": result.result,
        "error": result.error,
    }


def handle_ask_user(user_id: str, **kwargs: Any) -> dict:
    """Orchestrator tool: signal that user input is needed."""
    return {
        "need_user_input": kwargs.get("question", ""),
    }


def handle_query_trades(user_id: str, **kwargs: Any) -> dict:
    """Orchestrator tool: direct trade query (simple, no Agent needed)."""
    return handle_search_trades(user_id=user_id, **kwargs)


def register_all(proxy) -> None:
    """Register all tool handlers with a ToolProxy instance."""
    proxy.register("create_trade", handle_create_trade)
    proxy.register("update_trade", handle_update_trade)
    proxy.register("get_open_trades", handle_get_open_trades)
    proxy.register("search_trades", handle_search_trades)
    proxy.register("get_trades_for_analysis", handle_get_trades_for_analysis)
    proxy.register("get_previous_report", handle_get_previous_report)
    proxy.register("call_recorder", handle_call_recorder)
    proxy.register("call_analyzer", handle_call_analyzer)
    proxy.register("call_reporter", handle_call_reporter)
    proxy.register("ask_user", handle_ask_user)
    proxy.register("query_trades", handle_query_trades)
