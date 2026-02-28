"""Agent / Executor / Queue 相关常量（从 config 读取，Redis 键等）。"""

from __future__ import annotations

from app.config import get_agent_mode, get_redis_url

# 运行模式
AGENT_MODE_INLINE = "inline"
AGENT_MODE_SANDBOX = "sandbox"

REDIS_URL = get_redis_url()
AGENT_MODE = get_agent_mode()

# Redis 队列与结果键
QUEUE_NAME = "vault:agent:tasks"
RESULT_PREFIX = "vault:agent:result:"
