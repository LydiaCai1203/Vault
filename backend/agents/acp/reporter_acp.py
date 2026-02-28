"""ACP adapter for Reporter Agent."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

from ..llm import LLMGateway
from ..reporter.agent import ReporterAgent

logger = logging.getLogger(__name__)


def register_reporter(server: Server, gateway: LLMGateway) -> None:
    """Register the Reporter Agent with an ACP server."""

    @server.agent(
        name="vault-reporter",
        description=(
            "Vault 报告生成者。将分析结果数据转化为用户可读的中文复盘报告，"
            "包含数据摘要、3M 维度诊断、具体改进建议。支持单笔/周度/月度报告。"
        ),
    )
    async def reporter_agent(
        input: list[Message], context: Context
    ) -> AsyncGenerator[RunYield, RunYieldResume]:
        payload = _extract_reporter_payload(input)

        agent = ReporterAgent(gateway=gateway)
        result = agent.run(payload)

        if result.success and result.result:
            markdown = result.result.get("report_markdown", "")
            if markdown:
                yield Message(
                    role="agent",
                    parts=[MessagePart(content=markdown)],
                )
            else:
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


def _extract_reporter_payload(messages: list[Message]) -> dict:
    """Extract reporter task payload from ACP messages.

    Expects the last message to contain JSON with report_type and analysis_data,
    or plain text requesting a report.
    """
    text = ""
    for msg in reversed(messages):
        for part in msg.parts:
            if part.content:
                text = str(part.content)
                break
        if text:
            break

    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {
            "report_type": "weekly",
            "analysis_data": {"raw_request": text},
        }
