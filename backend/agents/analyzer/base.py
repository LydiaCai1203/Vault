"""Backward-compatible redirect: base analysis moved to analysis.base."""

from analysis.base import analyze, analyze_single  # noqa: F401

__all__ = ["analyze", "analyze_single"]
