"""Backward-compatible redirect: analyzer logic moved to analysis/ module."""

from analysis.engine import analyze

__all__ = ["analyze"]
