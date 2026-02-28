"""Recorder Agent tools - create/update/query trades via Executor proxy."""

from __future__ import annotations

from typing import Any

from ..tools import ToolParam, make_local_tool
from ..tools.create_trade import CREATE_TRADE
from ..tools.get_open_trades import GET_OPEN_TRADES
from ..tools.search_trades import SEARCH_TRADES
from ..tools.update_trade import UPDATE_TRADE


def _validate_trade(**kwargs: Any) -> dict:
    errors = []
    warnings = []

    required = ["symbol", "direction", "entry_price", "entry_time", "position_pct", "entry_reason"]
    for f in required:
        if f not in kwargs or kwargs[f] is None or kwargs[f] == "":
            errors.append(f"必填字段缺失: {f}")

    if "direction" in kwargs and kwargs["direction"] not in ("LONG", "SHORT"):
        errors.append("direction 必须是 LONG 或 SHORT")

    if "position_pct" in kwargs:
        try:
            pct = float(kwargs["position_pct"])
            if pct < 0 or pct > 1:
                errors.append("position_pct 必须在 0-1 之间")
        except (ValueError, TypeError):
            errors.append("position_pct 必须是数字")

    if "entry_price" in kwargs and "stop_loss" in kwargs:
        try:
            ep = float(kwargs["entry_price"])
            sl = float(kwargs["stop_loss"])
            direction = kwargs.get("direction", "LONG")
            if direction == "LONG" and sl > ep:
                warnings.append(f"做多但止损({sl})高于开仓价({ep})，请确认")
            elif direction == "SHORT" and sl < ep:
                warnings.append(f"做空但止损({sl})低于开仓价({ep})，请确认")
        except (ValueError, TypeError):
            pass

    optional_missing = []
    for f in ["emotion_tags", "stop_loss", "notes"]:
        if f not in kwargs or kwargs[f] is None or kwargs[f] == "":
            optional_missing.append(f)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "optional_missing": optional_missing,
    }


VALIDATE_TRADE = make_local_tool(
    name="validate_trade",
    description="校验交易数据的完整性和合理性。传入要校验的字段。",
    parameters=[
        ToolParam("symbol", "string", "品种", required=False),
        ToolParam("direction", "string", "方向", required=False),
        ToolParam("entry_price", "number", "开仓价", required=False),
        ToolParam("entry_time", "string", "开仓时间", required=False),
        ToolParam("position_pct", "number", "仓位占比", required=False),
        ToolParam("entry_reason", "string", "进场理由", required=False),
        ToolParam("stop_loss", "number", "止损", required=False),
        ToolParam("emotion_tags", "string", "情绪标签", required=False),
        ToolParam("notes", "string", "备注", required=False),
    ],
    fn=_validate_trade,
)

RECORDER_TOOLS = [
    CREATE_TRADE,
    UPDATE_TRADE,
    GET_OPEN_TRADES,
    SEARCH_TRADES,
    VALIDATE_TRADE,
]
