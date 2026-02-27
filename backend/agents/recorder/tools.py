"""Recorder Agent tools - create/update/query trades via Executor proxy."""

from __future__ import annotations

import json
import re
from typing import Any

from ..tools import LocalTool, RemoteTool, ToolParam, make_local_tool, make_remote_tool


def _build_tools() -> list:
    tools = []

    tools.append(make_remote_tool(
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
    ))

    tools.append(make_remote_tool(
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
    ))

    tools.append(make_remote_tool(
        name="get_open_trades",
        description="查询当前所有未平仓的持仓记录。可选按品种筛选。",
        parameters=[
            ToolParam("symbol", "string", "品种代码（可选，模糊匹配）", required=False),
        ],
    ))

    tools.append(make_remote_tool(
        name="search_trades",
        description="按条件搜索历史交易记录。",
        parameters=[
            ToolParam("symbol", "string", "品种代码（模糊匹配）", required=False),
            ToolParam("date_from", "string", "起始日期 YYYY-MM-DD", required=False),
            ToolParam("date_to", "string", "截止日期 YYYY-MM-DD", required=False),
            ToolParam("status", "string", "状态: OPEN / CLOSED", required=False),
            ToolParam("limit", "number", "返回条数上限，默认10", required=False),
        ],
    ))

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

    tools.append(make_local_tool(
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
    ))

    return tools


RECORDER_TOOLS = _build_tools()
