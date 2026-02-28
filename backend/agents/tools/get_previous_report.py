"""Tool: get_previous_report - fetch most recent review for comparison."""

from __future__ import annotations

import json
from typing import Any

from app.db import ReviewORM

from .common import get_db
from .schema import ToolParam, make_remote_tool


def handle_get_previous_report(user_id: str, **kwargs: Any) -> dict:
    db = get_db()
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


GET_PREVIOUS_REPORT = make_remote_tool(
    name="get_previous_report",
    description="获取上期复盘报告，用于与本期对比。",
    parameters=[
        ToolParam("type", "string", "报告类型: WEEKLY/MONTHLY/SINGLE"),
    ],
)
