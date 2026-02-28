"""Tool: call_recorder - delegate to Recorder Agent."""

from __future__ import annotations

import json
from typing import Any

from agents.recorder.agent import RecorderAgent
from .schema import ToolParam, make_remote_tool


def handle_call_recorder(user_id: str, **kwargs: Any) -> dict:
    payload = {"input": kwargs.get("input", "")}
    if kwargs.get("context"):
        try:
            payload["context"] = json.loads(kwargs["context"])
        except (json.JSONDecodeError, TypeError):
            payload["context"] = {"raw": kwargs["context"]}

    agent = RecorderAgent()
    result = agent.run(payload)
    return {
        "success": result.success,
        "result": result.result,
        "error": result.error,
        "need_user_input": result.need_user_input,
    }


CALL_RECORDER = make_remote_tool(
    name="call_recorder",
    description="调用 Recorder Agent 完成交易记录任务（新建或平仓）。传入用户的原始描述。",
    parameters=[
        ToolParam("input", "string", "用户关于交易记录的原始描述"),
        ToolParam("context", "string", "额外上下文信息(JSON格式)", required=False),
    ],
)
