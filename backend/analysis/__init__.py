"""Analysis Engine - pure code computation, not an LLM Agent.

Architecture:
- engine.py: Router that dispatches to Base + Style analyzers, merges results
- base.py: Common metrics shared across all trading styles (win rate, 3M scores, etc.)
- styles/: Pluggable style-specific analyzers (technical, value, trend, short_term)
"""

from .engine import analyze

__all__ = ["analyze"]
