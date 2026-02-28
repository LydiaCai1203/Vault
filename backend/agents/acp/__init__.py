"""ACP (Agent Communication Protocol) adapters for Vault agents.

Wraps internal agents with standard ACP interfaces for interoperability.
Each adapter exposes an agent via the acp-sdk Server, allowing external
systems to discover and interact with Vault agents using the ACP standard.

Usage:
    from agents.acp import create_acp_server
    server = create_acp_server()
    server.run(port=8100)
"""

from .server import create_acp_server

__all__ = ["create_acp_server"]
