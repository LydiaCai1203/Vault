"""Tool: call_reporter - delegate to Reporter Agent."""

from __future__ import annotations

from typing import Any

from agents.reporter.agent import ReporterAgent

from .schema import ToolParam, make_remote_tool


def handle_call_reporter(user_id: str, **kwargs: Any) -> dict:
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


CALL_REPORTER = make_remote_tool(
    name="call_reporter",
    description="调用 Reporter Agent 根据分析结果生成复盘报告。",
    parameters=[
        ToolParam("report_type", "string", "报告类型: single/weekly/monthly"),
        ToolParam("analysis_data", "string", "分析结果(JSON格式)"),
        ToolParam("date_from", "string", "起始日期", required=False),
        ToolParam("date_to", "string", "截止日期", required=False),
    ],
)
