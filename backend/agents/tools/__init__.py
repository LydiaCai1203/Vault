"""Agent tools: schema (for LLM) and handler implementations (for ToolProxy).

Schema (Tool, RemoteTool, make_remote_tool, etc.) is used by orchestrator/recorder/reporter
to define tools. Handlers are registered with ToolProxy via register_all(proxy).
"""

from __future__ import annotations

from .schema import (
    LocalTool,
    RemoteTool,
    Tool,
    ToolParam,
    make_local_tool,
    make_remote_tool,
)
from .create_trade import handle_create_trade
from .update_trade import handle_update_trade
from .get_open_trades import handle_get_open_trades
from .search_trades import handle_search_trades
from .get_trades_for_analysis import handle_get_trades_for_analysis
from .get_previous_report import handle_get_previous_report
from .call_recorder import handle_call_recorder
from .call_analyzer import handle_call_analyzer
from .call_reporter import handle_call_reporter
from .ask_user import handle_ask_user
from .query_trades import handle_query_trades

__all__ = [
    "Tool",
    "ToolParam",
    "LocalTool",
    "RemoteTool",
    "make_local_tool",
    "make_remote_tool",
    "register_all",
]


def register_all(proxy) -> None:
    """Register all tool handlers with a ToolProxy instance."""
    proxy.register("create_trade", handle_create_trade)
    proxy.register("update_trade", handle_update_trade)
    proxy.register("get_open_trades", handle_get_open_trades)
    proxy.register("search_trades", handle_search_trades)
    proxy.register("get_trades_for_analysis", handle_get_trades_for_analysis)
    proxy.register("get_previous_report", handle_get_previous_report)
    proxy.register("call_recorder", handle_call_recorder)
    proxy.register("call_analyzer", handle_call_analyzer)
    proxy.register("call_reporter", handle_call_reporter)
    proxy.register("ask_user", handle_ask_user)
    proxy.register("query_trades", handle_query_trades)
