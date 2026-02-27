"""Orchestrator Agent tools - route to sub-agents and query data."""

from __future__ import annotations

from ..tools import RemoteTool, ToolParam, make_remote_tool


def _build_tools() -> list:
    tools = []

    tools.append(make_remote_tool(
        name="call_recorder",
        description="调用 Recorder Agent 完成交易记录任务（新建或平仓）。传入用户的原始描述。",
        parameters=[
            ToolParam("input", "string", "用户关于交易记录的原始描述"),
            ToolParam("context", "string", "额外上下文信息(JSON格式)", required=False),
        ],
    ))

    tools.append(make_remote_tool(
        name="call_analyzer",
        description="调用 Analyzer Hub 执行交易分析。传入日期范围和分析类型。",
        parameters=[
            ToolParam("analysis_type", "string", "分析类型: single/weekly/monthly"),
            ToolParam("date_from", "string", "起始日期 YYYY-MM-DD"),
            ToolParam("date_to", "string", "截止日期 YYYY-MM-DD"),
            ToolParam("trade_id", "string", "单笔分析时的交易ID", required=False),
            ToolParam("style", "string", "交易风格: technical/value/trend/short_term", required=False),
        ],
    ))

    tools.append(make_remote_tool(
        name="call_reporter",
        description="调用 Reporter Agent 根据分析结果生成复盘报告。",
        parameters=[
            ToolParam("report_type", "string", "报告类型: single/weekly/monthly"),
            ToolParam("analysis_data", "string", "分析结果(JSON格式)"),
            ToolParam("date_from", "string", "起始日期", required=False),
            ToolParam("date_to", "string", "截止日期", required=False),
        ],
    ))

    tools.append(make_remote_tool(
        name="query_trades",
        description="直接查询交易记录（简单查询不需要经过 Agent）。",
        parameters=[
            ToolParam("symbol", "string", "品种代码(模糊匹配)", required=False),
            ToolParam("date_from", "string", "起始日期", required=False),
            ToolParam("date_to", "string", "截止日期", required=False),
            ToolParam("status", "string", "状态: OPEN/CLOSED", required=False),
            ToolParam("limit", "number", "返回条数上限", required=False),
        ],
    ))

    tools.append(make_remote_tool(
        name="ask_user",
        description="向用户追问更多信息。当信息不完整无法继续时使用。",
        parameters=[
            ToolParam("question", "string", "要向用户提出的问题"),
        ],
    ))

    return tools


ORCHESTRATOR_TOOLS = _build_tools()
