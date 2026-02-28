"""Agent I/O protocol and shared types.

Sandbox convention:
- Input: env USER_ID, TASK_ID; JSON payload via stdin
- Output: JSON result to stdout
- JSONL bidirectional streaming for tool proxying

JSONL message types (Agent -> Executor):
  {"type": "tool_call", "tool": "...", "arguments": {...}}
  {"type": "final", "result": {...}}
  {"type": "error", "error": "..."}

JSONL message types (Executor -> Agent):
  {"tool": "...", "result": {...}}  (tool result injected)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MessageType(str, Enum):
    TASK = "task"
    RESPONSE = "response"
    ERROR = "error"
    NEED_USER_INPUT = "need_user_input"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    FINAL = "final"


@dataclass
class AgentMessage:
    """Structured message between API and agents."""

    type: MessageType
    task_id: str
    user_id: str
    agent_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None
    error: str | None = None


@dataclass
class AgentTask:
    """Task sent to sandbox executor."""

    task_id: str
    user_id: str
    agent_type: str
    payload: dict[str, Any]


@dataclass
class AgentResult:
    """Result from sandbox."""

    task_id: str
    success: bool
    result: dict[str, Any] | None = None
    error: str | None = None
    need_user_input: str | None = None
