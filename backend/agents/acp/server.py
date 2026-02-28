"""ACP Server - exposes all Vault agents via Agent Communication Protocol.

Creates a single ACP server that registers all Vault agents as ACP-discoverable
endpoints. External systems can discover and invoke agents through the standard
ACP REST interface.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

from ..llm import LLMGateway
from .orchestrator_acp import register_orchestrator
from .recorder_acp import register_recorder
from .reporter_acp import register_reporter

logger = logging.getLogger(__name__)


def create_acp_server() -> Server:
    """Create and configure an ACP server with all Vault agents registered."""
    server = Server()
    gateway = LLMGateway()

    register_orchestrator(server, gateway)
    register_recorder(server, gateway)
    register_reporter(server, gateway)

    return server
