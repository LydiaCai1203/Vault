"""LLM Gateway - unified LLM calling via litellm with per-agent model routing."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from app.config import get_llm_config


@dataclass
class ModelConfig:
    """Per-agent model assignment. Read from config.json under "llm"."""

    orchestrator: str = "anthropic/claude-3-5-haiku-20241022"
    recorder: str = "anthropic/claude-3-5-haiku-20241022"
    analyzer_interpret: str = "anthropic/claude-sonnet-4-20250514"
    reporter: str = "anthropic/claude-sonnet-4-20250514"

    @classmethod
    def from_config(cls) -> ModelConfig:
        raw = get_llm_config()
        return cls(
            orchestrator=raw.get("orchestrator", cls.orchestrator),
            recorder=raw.get("recorder", cls.recorder),
            analyzer_interpret=raw.get("analyzer_interpret", cls.analyzer_interpret),
            reporter=raw.get("reporter", cls.reporter),
        )

    def for_agent(self, agent_name: str) -> str:
        return getattr(self, agent_name, self.orchestrator)


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any = None

    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0

    def has_content(self) -> bool:
        return self.content is not None and len(self.content.strip()) > 0

    @classmethod
    def from_litellm(cls, response: Any) -> LLMResponse:
        choice = response.choices[0]
        msg = choice.message
        content = msg.content
        tool_calls: list[ToolCall] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                args = tc.function.arguments
                if isinstance(args, str):
                    args = json.loads(args)
                tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))
        return cls(content=content, tool_calls=tool_calls, raw=response)


class LLMGateway:
    """Thin wrapper over litellm.completion with tool support."""

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig.from_config()

    def call(
        self,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> LLMResponse:
        import litellm

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = litellm.completion(**kwargs)
        return LLMResponse.from_litellm(response)
