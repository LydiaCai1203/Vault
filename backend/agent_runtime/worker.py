"""Worker: pull tasks from Redis, run in sandbox, optionally store results."""

from __future__ import annotations

import os
import time

from .executor import SandboxExecutor, ToolProxy
from .queue import dequeue, enqueue_result
from .tool_handlers import register_all

REDIS_URL = os.getenv("REDIS_URL")
QUEUE_NAME = "vault:agent:tasks"
RESULT_PREFIX = "vault:agent:result:"


def run_worker(poll_interval: float = 1.0) -> None:
    """Poll Redis for tasks, spawn sandbox, write result."""
    if not REDIS_URL:
        raise RuntimeError("REDIS_URL required for worker")

    tool_proxy = ToolProxy()
    register_all(tool_proxy)
    executor = SandboxExecutor(tool_proxy=tool_proxy)

    while True:
        task = dequeue(REDIS_URL, QUEUE_NAME)
        if not task:
            time.sleep(poll_interval)
            continue
        result = executor.spawn(
            task.agent_type,
            task.user_id,
            task.payload,
            task_id=task.task_id,
        )
        enqueue_result(REDIS_URL, RESULT_PREFIX + task.task_id, result)


if __name__ == "__main__":
    run_worker()
