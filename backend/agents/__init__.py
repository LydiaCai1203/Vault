"""Agent layer: LLM-powered Agents only (Orchestrator, Recorder, Reporter).

Analysis computation has been moved to the `analysis/` module.

Architecture:
- BaseAgent: core perceive-think-act-observe loop (agents/base.py)
- Tool: function-calling interface for local/remote tools (agents/tools.py)
- LLMGateway: unified LLM calling via litellm (agents/llm.py)
- Orchestrator: intent routing + sub-agent coordination
- Recorder: NLU extraction + structured trade recording
- Reporter: LLM-powered report generation from analysis data
"""

from .base import BaseAgent, AgentResult
from .llm import LLMGateway, ModelConfig
from .tools import Tool, LocalTool, RemoteTool

__all__ = [
    "BaseAgent",
    "AgentResult",
    "LLMGateway",
    "ModelConfig",
    "Tool",
    "LocalTool",
    "RemoteTool",
]
