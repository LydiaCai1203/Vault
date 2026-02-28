"""Tool: ask_user - signal that user input is needed."""

from __future__ import annotations

from typing import Any

from .schema import ToolParam, make_remote_tool


def handle_ask_user(user_id: str, **kwargs: Any) -> dict:
    return {
        "need_user_input": kwargs.get("question", ""),
    }


ASK_USER = make_remote_tool(
    name="ask_user",
    description="向用户追问更多信息。当信息不完整无法继续时使用。",
    parameters=[
        ToolParam("question", "string", "要向用户提出的问题"),
    ],
)
