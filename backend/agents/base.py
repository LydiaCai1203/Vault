"""BaseAgent - the core perceive-think-act-observe loop driven by LLM."""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from typing import Any

from .llm import LLMGateway, LLMResponse, ModelConfig
from .tools import Tool

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    success: bool
    result: dict[str, Any] | str | None = None
    error: str | None = None
    need_user_input: str | None = None


class BaseAgent:
    """Abstract base for all Vault agents. Subclasses set name, system_prompt, tools."""

    name: str = "base"
    system_prompt: str = ""
    tools: list[Tool] = []
    max_steps: int = 15
    llm_model: str = "anthropic/claude-3-5-haiku-20241022"

    def __init__(self, gateway: LLMGateway | None = None):
        self.gateway = gateway or LLMGateway()
        self._tool_map: dict[str, Tool] = {t.name: t for t in self.tools}

    def run(self, task_payload: dict[str, Any]) -> AgentResult:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._format_task(task_payload)},
        ]
        tool_schemas = [t.to_openai_schema() for t in self.tools] if self.tools else None

        for step in range(self.max_steps):
            logger.debug("Agent %s step %d", self.name, step)
            try:
                response = self.gateway.call(
                    model=self.llm_model,
                    messages=messages,
                    tools=tool_schemas,
                )
            except Exception as e:
                logger.error("LLM call failed: %s", e)
                return AgentResult(success=False, error=f"llm_error: {e}")

            if response.has_tool_calls():
                messages.append(self._assistant_msg(response))
                for tc in response.tool_calls:
                    tool_result = self._execute_tool(tc.name, tc.arguments)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(tool_result, ensure_ascii=False, default=str),
                    })
            elif response.has_content():
                return self._parse_final_answer(response.content)  # type: ignore[arg-type]
            else:
                return AgentResult(success=False, error="empty LLM response")

        return AgentResult(success=False, error="max_steps_reached")

    def _format_task(self, payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, default=str)

    def _assistant_msg(self, response: LLMResponse) -> dict[str, Any]:
        msg: dict[str, Any] = {"role": "assistant"}
        if response.content:
            msg["content"] = response.content
        if response.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments, ensure_ascii=False),
                    },
                }
                for tc in response.tool_calls
            ]
        return msg

    def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        tool = self._tool_map.get(name)
        if not tool:
            return {"error": f"unknown tool: {name}"}
        try:
            return tool.execute(**arguments)
        except Exception as e:
            logger.error("Tool %s failed: %s", name, e)
            return {"error": str(e)}

    def _parse_final_answer(self, content: str) -> AgentResult:
        """Try to parse JSON from content; fallback to raw text."""
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                if data.get("need_user_input"):
                    return AgentResult(
                        success=True,
                        need_user_input=data["need_user_input"],
                        result=data,
                    )
                return AgentResult(success=True, result=data)
            return AgentResult(success=True, result={"text": content})
        except json.JSONDecodeError:
            return AgentResult(success=True, result={"text": content})

    def run_as_sandbox(self) -> None:
        """Entry point when running inside a Docker sandbox."""
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        result = self.run(payload)
        output = {
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "need_user_input": result.need_user_input,
        }
        sys.stdout.write(json.dumps(output, ensure_ascii=False, default=str) + "\n")
        sys.stdout.flush()
