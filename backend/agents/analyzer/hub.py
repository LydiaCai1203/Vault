"""Backward-compatible redirect: analysis logic moved to analysis.engine."""

from analysis.engine import analyze, _analyze_batch, _analyze_single  # noqa: F401

__all__ = ["analyze"]
