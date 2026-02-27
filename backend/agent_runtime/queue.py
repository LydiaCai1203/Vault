"""Task queue types and Redis-based queue. Fallback to sync when Redis unavailable."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class AgentTask:
    task_id: str
    user_id: str
    agent_type: str
    payload: dict[str, Any]


def task_to_json(t: AgentTask) -> str:
    return json.dumps(asdict(t), ensure_ascii=False)


def task_from_json(s: str) -> AgentTask:
    d = json.loads(s)
    return AgentTask(
        task_id=d["task_id"],
        user_id=d["user_id"],
        agent_type=d["agent_type"],
        payload=d["payload"],
    )


def enqueue(redis_url: str, queue_name: str, task: AgentTask) -> str:
    """Push task to Redis list. Returns task_id."""
    import redis
    r = redis.from_url(redis_url)
    r.lpush(queue_name, task_to_json(task))
    return task.task_id


def dequeue(redis_url: str, queue_name: str, timeout_sec: int = 5) -> AgentTask | None:
    """Blocking pop from Redis. Returns None on timeout."""
    import redis
    r = redis.from_url(redis_url)
    raw = r.brpop(queue_name, timeout=timeout_sec)
    if not raw:
        return None
    _, data = raw
    return task_from_json(data)


def enqueue_result(redis_url: str, key: str, result: dict, ttl_sec: int = 3600) -> None:
    """Store result in Redis for polling. Key = RESULT_PREFIX + task_id."""
    import redis
    r = redis.from_url(redis_url)
    r.setex(key, ttl_sec, json.dumps(result, ensure_ascii=False))


def get_result(redis_url: str, key: str) -> dict | None:
    """Fetch result by task_id."""
    import redis
    r = redis.from_url(redis_url)
    raw = r.get(key)
    return json.loads(raw) if raw else None
