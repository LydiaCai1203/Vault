"""Tool: get_analysis_result - schema only (Reporter Agent). Handler TBD."""

from __future__ import annotations

from .schema import ToolParam, make_remote_tool

GET_ANALYSIS_RESULT = make_remote_tool(
    name="get_analysis_result",
    description="获取指定的分析结果数据。",
    parameters=[
        ToolParam("analysis_id", "string", "分析结果ID", required=False),
    ],
)
