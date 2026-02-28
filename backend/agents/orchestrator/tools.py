"""Orchestrator Agent tools - route to sub-agents and query data."""

from __future__ import annotations

from ..tools.ask_user import ASK_USER
from ..tools.call_analyzer import CALL_ANALYZER
from ..tools.call_recorder import CALL_RECORDER
from ..tools.call_reporter import CALL_REPORTER
from ..tools.query_trades import QUERY_TRADES

ORCHESTRATOR_TOOLS = [
    CALL_RECORDER,
    CALL_ANALYZER,
    CALL_REPORTER,
    QUERY_TRADES,
    ASK_USER,
]
