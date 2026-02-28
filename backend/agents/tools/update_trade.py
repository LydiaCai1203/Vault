"""Tool: update_trade - update an existing trade (e.g. close position)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db import TradeORM, dumps

from .common import get_db, parse_time
from .schema import ToolParam, make_remote_tool


def handle_update_trade(user_id: str, **kwargs: Any) -> dict:
    db = get_db()
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
            trade.exit_time = parse_time(kwargs["exit_time"])
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


UPDATE_TRADE = make_remote_tool(
    name="update_trade",
    description="更新已有的交易记录（如平仓、补充信息）。传入 trade_id 和要更新的字段。",
    parameters=[
        ToolParam("trade_id", "string", "要更新的交易记录 ID"),
        ToolParam("status", "string", "状态: OPEN 或 CLOSED", required=False),
        ToolParam("exit_price", "number", "平仓价格", required=False),
        ToolParam("exit_time", "string", "平仓时间 ISO 格式", required=False),
        ToolParam("pnl_cny", "number", "盈亏金额(人民币)", required=False),
        ToolParam("emotion_tags", "string", "逗号分隔的情绪标签", required=False),
        ToolParam("notes", "string", "备注", required=False),
    ],
)
