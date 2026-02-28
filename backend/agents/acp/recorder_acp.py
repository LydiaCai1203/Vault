"""ACP adapter for Recorder Agent."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

from ..llm import LLMGateway
from ..recorder.agent import RecorderAgent

logger = logging.getLogger(__name__)


def register_recorder(server: Server, gateway: LLMGateway) -> None:
    """Register the Recorder Agent with an ACP server."""

    @server.agent(
        name="vault-recorder",
        description=(
            "Vault 交易记录助手。从自然语言描述中提取结构化交易数据，"
            "引导补全必填字段，校验数据合理性，保存交易记录。"
        ),
    )
    async def recorder_agent(
        input: list[Message], context: Context
    ) -> AsyncGenerator[RunYield, RunYieldResume]:
        user_text = _extract_text(input)

        agent = RecorderAgent(gateway=gateway)
        result = agent.run({"input": user_text})

        if result.need_user_input:
            yield Message(
                role="agent",
                parts=[MessagePart(content=json.dumps(
                    {"need_user_input": result.need_user_input},
                    ensure_ascii=False,
                ))],
            )
        elif result.success and result.result:
            yield Message(
                role="agent",
                parts=[MessagePart(content=json.dumps(
                    result.result, ensure_ascii=False, default=str,
                ))],
            )
        else:
            yield Message(
                role="agent",
                parts=[MessagePart(content=json.dumps(
                    {"error": result.error or "unknown error"},
                    ensure_ascii=False,
                ))],
            )


def _extract_text(messages: list[Message]) -> str:
    for msg in reversed(messages):
        for part in msg.parts:
            if part.content:
                return str(part.content)
    return ""
