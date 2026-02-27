"""Agent layer: Orchestrator, Recorder, Analyzer, Reporter.

Architecture:
- BaseAgent: core perceive-think-act-observe loop (agents/base.py)
- Tool: function-calling interface for local/remote tools (agents/tools.py)
- LLMGateway: unified LLM calling via litellm (agents/llm.py)
- Orchestrator: intent routing + sub-agent coordination
- Recorder: NLU extraction + structured trade recording
- Analyzer Hub: pure-code routing to Base + Style analyzers
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
