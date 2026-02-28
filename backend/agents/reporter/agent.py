"""Report Agent - transforms AnalysisResult into readable Markdown reports."""

from __future__ import annotations

import json
import os
import sys

from ..base import BaseAgent, AgentResult
from ..llm import LLMGateway, ModelConfig
from ..prompts.reporter import SYSTEM_PROMPT
from .tools import REPORTER_TOOLS


class ReporterAgent(BaseAgent):
    name = "reporter"
    system_prompt = SYSTEM_PROMPT
    tools = REPORTER_TOOLS
    max_steps = 8

    def __init__(self, gateway: LLMGateway | None = None):
        config = ModelConfig.from_config()
        self.llm_model = config.reporter
        super().__init__(gateway)

    def _format_task(self, payload: dict) -> str:
        report_type = payload.get("report_type", "weekly")
        analysis_data = payload.get("analysis_data", {})
        if isinstance(analysis_data, str):
            try:
                analysis_data = json.loads(analysis_data)
            except json.JSONDecodeError:
                pass

        parts = [
            f"请生成一份{self._type_label(report_type)}复盘报告。",
            "",
            "## 分析数据",
            json.dumps(analysis_data, ensure_ascii=False, indent=2, default=str),
        ]

        if payload.get("date_from") and payload.get("date_to"):
            parts.insert(1, f"时间范围：{payload['date_from']} 至 {payload['date_to']}")

        return "\n".join(parts)

    def _parse_final_answer(self, content: str) -> AgentResult:
        """Reporter's final answer is typically markdown text, not JSON."""
        return AgentResult(success=True, result={"report_markdown": content})

    @staticmethod
    def _type_label(t: str) -> str:
        return {"single": "单笔", "weekly": "周度", "monthly": "月度"}.get(t, t)


def main() -> None:
    """Entry point for sandbox execution."""
    agent = ReporterAgent()
    agent.run_as_sandbox()


if __name__ == "__main__":
    main()
