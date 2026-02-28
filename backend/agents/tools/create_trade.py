"""Tool: create_trade - create a new open trade."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.db import TradeORM, dumps

from .common import get_db, get_record_hints, parse_time, schedule_entry_snapshot
from .schema import ToolParam, make_remote_tool


def handle_create_trade(user_id: str, **kwargs: Any) -> dict:
    db = get_db()
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
            entry_time=parse_time(kwargs.get("entry_time", now.isoformat())),
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

        hints = get_record_hints(user_id, trade_id, symbol, position_pct)
        schedule_entry_snapshot(user_id, trade_id)

        return {"trade_id": trade_id, "status": "created", "hints": hints}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


CREATE_TRADE = make_remote_tool(
    name="create_trade",
    description="创建一条新的交易记录。所有字段按 Trade Schema 传入。",
    parameters=[
        ToolParam("symbol", "string", "交易品种代码或名称"),
        ToolParam("name", "string", "品种中文名", required=False),
        ToolParam("direction", "string", "方向: LONG 或 SHORT"),
        ToolParam("entry_price", "number", "开仓价格"),
        ToolParam("entry_time", "string", "开仓时间 ISO 格式"),
        ToolParam("position_pct", "number", "仓位占比 0-1"),
        ToolParam("entry_reason", "string", "进场理由"),
        ToolParam("market", "string", "市场", required=False),
        ToolParam("stop_loss", "number", "止损价位", required=False),
        ToolParam("emotion_tags", "string", "逗号分隔的情绪标签", required=False),
        ToolParam("tags", "string", "逗号分隔的自定义标签", required=False),
        ToolParam("notes", "string", "备注", required=False),
    ],
)
