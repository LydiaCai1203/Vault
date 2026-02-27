"""Recorder Agent - natural language to structured trade record."""

from __future__ import annotations

import json
import os
import sys

from ..base import BaseAgent, AgentResult
from ..llm import LLMGateway, ModelConfig
from ..prompts.recorder import SYSTEM_PROMPT
from .tools import RECORDER_TOOLS


class RecorderAgent(BaseAgent):
    name = "recorder"
    system_prompt = SYSTEM_PROMPT
    tools = RECORDER_TOOLS
    max_steps = 10

    def __init__(self, gateway: LLMGateway | None = None):
        config = ModelConfig.from_env()
        self.llm_model = config.recorder
        super().__init__(gateway)

    def _format_task(self, payload: dict) -> str:
        user_input = payload.get("input", "")
        context = payload.get("context", {})
        parts = [f"用户输入：{user_input}"]
        if context:
            parts.append(f"上下文：{json.dumps(context, ensure_ascii=False)}")
        return "\n".join(parts)


def main() -> None:
    """Entry point for sandbox execution."""
    agent = RecorderAgent()
    agent.run_as_sandbox()


if __name__ == "__main__":
    main()
