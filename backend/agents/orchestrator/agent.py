"""Orchestrator Agent - intent routing and flow coordination."""

from __future__ import annotations

import json
import os
import sys

from ..base import BaseAgent, AgentResult
from ..llm import LLMGateway, ModelConfig
from ..prompts.orchestrator import SYSTEM_PROMPT
from .tools import ORCHESTRATOR_TOOLS


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    system_prompt = SYSTEM_PROMPT
    tools = ORCHESTRATOR_TOOLS
    max_steps = 15

    def __init__(self, gateway: LLMGateway | None = None):
        config = ModelConfig.from_env()
        self.llm_model = config.orchestrator
        super().__init__(gateway)

    def _format_task(self, payload: dict) -> str:
        user_input = payload.get("input", "")
        conversation = payload.get("conversation", [])
        parts = [f"用户消息：{user_input}"]
        if conversation:
            parts.insert(0, "对话历史：")
            for msg in conversation[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                parts.insert(-1, f"  {role}: {content}")
        return "\n".join(parts)


def main() -> None:
    """Entry point for sandbox execution."""
    agent = OrchestratorAgent()
    agent.run_as_sandbox()


if __name__ == "__main__":
    main()
