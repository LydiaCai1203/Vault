"""Tool: call_analyzer - fetch trades, enrich, run analysis engine."""

from __future__ import annotations

from typing import Any

from analysis.engine import analyze
from data_service.service import enrich_trades

from .get_trades_for_analysis import handle_get_trades_for_analysis
from .schema import ToolParam, make_remote_tool


def handle_call_analyzer(user_id: str, **kwargs: Any) -> dict:
    trades_data = handle_get_trades_for_analysis(
        user_id=user_id,
        date_from=kwargs.get("date_from", ""),
        date_to=kwargs.get("date_to", ""),
    )
    trades = trades_data.get("trades", [])

    enriched = enrich_trades(trades)

    return analyze(
        enriched,
        style=kwargs.get("style", "technical"),
        analysis_type=kwargs.get("analysis_type", "batch"),
        trade_id=kwargs.get("trade_id"),
    )

CALL_ANALYZER = make_remote_tool(
    name="call_analyzer",
    description="调用 Analyzer Hub 执行交易分析。传入日期范围和分析类型。",
    parameters=[
        ToolParam("analysis_type", "string", "分析类型: single/weekly/monthly"),
        ToolParam("date_from", "string", "起始日期 YYYY-MM-DD"),
        ToolParam("date_to", "string", "截止日期 YYYY-MM-DD"),
        ToolParam("trade_id", "string", "单笔分析时的交易ID", required=False),
        ToolParam("style", "string", "交易风格: technical/value/trend/short_term", required=False),
    ],
)
