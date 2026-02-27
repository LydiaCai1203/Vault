"""Tool base class and registry for Agent function-calling."""

from __future__ import annotations

import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolParam:
    name: str
    type: str
    description: str
    required: bool = True
    enum: list[str] | None = None


class Tool(ABC):
    """Base class for all Agent tools."""

    name: str
    description: str
    parameters: list[ToolParam]
    is_remote: bool = False

    def to_openai_schema(self) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []
        for p in self.parameters:
            prop: dict[str, Any] = {"type": p.type, "description": p.description}
            if p.enum:
                prop["enum"] = p.enum
            properties[p.name] = prop
            if p.required:
                required.append(p.name)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        ...


class LocalTool(Tool):
    """Tool that runs inside the sandbox (pure computation)."""

    is_remote = False


class RemoteTool(Tool):
    """Tool that requires Executor proxy (DB access, sub-agent calls)."""

    is_remote = True

    def execute(self, **kwargs: Any) -> Any:
        """Send tool call to Executor via JSONL stdout, read result from stdin."""
        request = {
            "type": "tool_call",
            "tool": self.name,
            "arguments": kwargs,
        }
        sys.stdout.write(json.dumps(request, ensure_ascii=False) + "\n")
        sys.stdout.flush()
        line = sys.stdin.readline().strip()
        if not line:
            return {"error": "no response from executor"}
        return json.loads(line)


def make_local_tool(
    name: str,
    description: str,
    parameters: list[ToolParam],
    fn: Callable[..., Any],
) -> LocalTool:
    """Helper to create a LocalTool from a plain function."""

    class _FnTool(LocalTool):
        def execute(self, **kwargs: Any) -> Any:
            return self._fn(**kwargs)

    tool = _FnTool()
    tool.name = name
    tool.description = description
    tool.parameters = parameters
    tool.is_remote = False
    tool._fn = fn  # type: ignore[attr-defined]
    return tool


def make_remote_tool(
    name: str,
    description: str,
    parameters: list[ToolParam],
) -> RemoteTool:
    """Helper to create a RemoteTool (execution proxied to Executor)."""

    tool = RemoteTool.__new__(RemoteTool)
    tool.name = name
    tool.description = description
    tool.parameters = parameters
    tool.is_remote = True
    return tool
