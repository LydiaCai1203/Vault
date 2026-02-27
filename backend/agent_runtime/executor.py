"""SandboxExecutor - spawn agent containers with bidirectional JSONL streaming.

The Executor acts as the Tool Proxy: when an agent issues a remote tool_call,
the Executor intercepts it, executes the action (DB query, sub-agent spawn),
and injects the result back via stdin.
"""

from __future__ import annotations

import json
import logging
import subprocess
import uuid
from typing import Any, Callable

from .queue import AgentTask

logger = logging.getLogger(__name__)

AGENT_IMAGES = {
    "orchestrator": "vault-agent-orchestrator",
    "recorder": "vault-agent-recorder",
    "analyzer": "vault-agent-analyzer",
    "reporter": "vault-agent-reporter",
}


class ToolProxy:
    """Handles remote tool calls on behalf of sandboxed agents.

    Each handler receives (user_id, tool_name, arguments) and returns a dict.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register(self, tool_name: str, handler: Callable[..., Any]) -> None:
        self._handlers[tool_name] = handler

    def execute(self, user_id: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        handler = self._handlers.get(tool_name)
        if not handler:
            return {"error": f"no proxy handler for tool: {tool_name}"}
        try:
            return handler(user_id=user_id, **arguments)
        except Exception as e:
            logger.error("ToolProxy error for %s: %s", tool_name, e)
            return {"error": str(e)}


class SandboxExecutor:
    """Spawns agent containers via docker run with JSONL bidirectional I/O.

    Two modes:
    - Streaming (default): keeps stdin/stdout open, proxies tool calls in real-time
    - One-shot (fallback): sends payload via stdin, reads stdout once
    """

    def __init__(
        self,
        image_prefix: str = "vault-agent",
        tool_proxy: ToolProxy | None = None,
    ):
        self.image_prefix = image_prefix
        self.tool_proxy = tool_proxy or ToolProxy()

    def spawn(
        self,
        agent_type: str,
        user_id: str,
        payload: dict[str, Any],
        task_id: str | None = None,
        timeout_sec: int = 120,
    ) -> dict[str, Any]:
        """Run agent in sandbox with bidirectional JSONL streaming."""
        task_id = task_id or str(uuid.uuid4())
        image = AGENT_IMAGES.get(agent_type, f"{self.image_prefix}-{agent_type}")
        payload_json = json.dumps(payload, ensure_ascii=False)

        cmd = [
            "docker", "run", "--rm", "-i",
            "--read-only",
            "--network=none",
            "-e", f"USER_ID={user_id}",
            "-e", f"TASK_ID={task_id}",
            image,
        ]

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            return {"success": False, "error": "docker not found", "task_id": task_id}

        try:
            assert proc.stdin is not None
            assert proc.stdout is not None

            proc.stdin.write(payload_json.encode("utf-8"))
            proc.stdin.write(b"\n")
            proc.stdin.flush()

            return self._stream_loop(proc, user_id, task_id, timeout_sec)

        except subprocess.TimeoutExpired:
            proc.kill()
            return {"success": False, "error": "timeout", "task_id": task_id}
        except Exception as e:
            proc.kill()
            return {"success": False, "error": str(e), "task_id": task_id}

    def _stream_loop(
        self,
        proc: subprocess.Popen,
        user_id: str,
        task_id: str,
        timeout_sec: int,
    ) -> dict[str, Any]:
        """Read JSONL lines from agent stdout. Proxy tool calls, forward results."""
        import select
        import time

        assert proc.stdout is not None
        assert proc.stdin is not None

        start = time.monotonic()
        accumulated_output = ""

        while True:
            elapsed = time.monotonic() - start
            if elapsed > timeout_sec:
                proc.kill()
                return {"success": False, "error": "timeout", "task_id": task_id}

            line_bytes = proc.stdout.readline()
            if not line_bytes:
                break

            line = line_bytes.decode("utf-8").strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                accumulated_output += line + "\n"
                continue

            msg_type = msg.get("type")

            if msg_type == "tool_call":
                tool_name = msg.get("tool")
                arguments = msg.get("arguments", {})
                result = self.tool_proxy.execute(user_id, tool_name, arguments)
                result_line = json.dumps(result, ensure_ascii=False, default=str) + "\n"
                proc.stdin.write(result_line.encode("utf-8"))
                proc.stdin.flush()

            elif msg_type == "final":
                proc.wait(timeout=5)
                return {
                    "success": True,
                    "result": msg.get("result"),
                    "task_id": task_id,
                }

            elif msg_type == "error":
                proc.wait(timeout=5)
                return {
                    "success": False,
                    "error": msg.get("error", "unknown"),
                    "task_id": task_id,
                }

            else:
                if "success" in msg:
                    proc.wait(timeout=5)
                    return {**msg, "task_id": task_id}
                accumulated_output += line + "\n"

        proc.wait(timeout=10)
        if accumulated_output.strip():
            try:
                data = json.loads(accumulated_output.strip().split("\n")[-1])
                return {"success": True, "result": data, "task_id": task_id}
            except json.JSONDecodeError:
                pass

        stderr_out = ""
        if proc.stderr:
            stderr_out = proc.stderr.read().decode("utf-8", errors="replace")

        if proc.returncode != 0:
            return {
                "success": False,
                "error": stderr_out or f"exit code {proc.returncode}",
                "task_id": task_id,
            }

        return {"success": True, "result": {}, "task_id": task_id}

    def spawn_inline(
        self,
        agent_type: str,
        user_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Run agent in-process (no Docker) for development/testing."""
        from agents.recorder.agent import RecorderAgent
        from agents.orchestrator.agent import OrchestratorAgent
        from agents.reporter.agent import ReporterAgent

        agent_map = {
            "recorder": RecorderAgent,
            "orchestrator": OrchestratorAgent,
            "reporter": ReporterAgent,
        }

        agent_cls = agent_map.get(agent_type)
        if not agent_cls:
            return {"success": False, "error": f"unknown agent: {agent_type}"}

        agent = agent_cls()
        result = agent.run(payload)
        return {
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "need_user_input": result.need_user_input,
        }
