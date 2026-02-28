"""ACP adapter for Orchestrator Agent."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

from ..llm import LLMGateway
from ..orchestrator.agent import OrchestratorAgent

logger = logging.getLogger(__name__)


def register_orchestrator(server: Server, gateway: LLMGateway) -> None:
    """Register the Orchestrator Agent with an ACP server."""

    @server.agent(
        name="vault-orchestrator",
        description=(
            "Vault 交易日志系统的协调者。理解用户关于交易记录和复盘的自然语言请求，"
            "路由到对应的专业 Agent（记录/分析/报告），汇总结果后回复用户。"
        ),
    )
    async def orchestrator_agent(
        input: list[Message], context: Context
    ) -> AsyncGenerator[RunYield, RunYieldResume]:
        user_text = _extract_text(input)
        conversation = _extract_conversation(input)

        agent = OrchestratorAgent(gateway=gateway)
        result = agent.run({
            "input": user_text,
            "conversation": conversation,
        })

        if result.need_user_input:
            yield Message(
                role="agent",
                parts=[MessagePart(content=json.dumps(
                    {"need_user_input": result.need_user_input},
                    ensure_ascii=False,
                ))],
            )
        elif result.success and result.result:
            text = result.result.get("text", json.dumps(result.result, ensure_ascii=False))
            yield Message(
                role="agent",
                parts=[MessagePart(content=text)],
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


def _extract_conversation(messages: list[Message]) -> list[dict]:
    conv = []
    for msg in messages[:-1]:
        role = msg.role or "user"
        text = ""
        for part in msg.parts:
            if part.content:
                text += str(part.content)
        if text:
            conv.append({"role": role, "content": text})
    return conv
