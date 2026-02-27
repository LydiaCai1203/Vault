"""Reporter Agent tools - fetch analysis data and previous reports."""

from __future__ import annotations

from ..tools import RemoteTool, ToolParam, make_remote_tool


def _build_tools() -> list:
    tools = []

    tools.append(make_remote_tool(
        name="get_previous_report",
        description="获取上期复盘报告，用于与本期对比。",
        parameters=[
            ToolParam("type", "string", "报告类型: WEEKLY/MONTHLY/SINGLE"),
        ],
    ))

    tools.append(make_remote_tool(
        name="get_analysis_result",
        description="获取指定的分析结果数据。",
        parameters=[
            ToolParam("analysis_id", "string", "分析结果ID", required=False),
        ],
    ))

    return tools


REPORTER_TOOLS = _build_tools()
