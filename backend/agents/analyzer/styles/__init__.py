"""Style analyzers: technical, value, trend, short_term.

Registry pattern - each style module registers itself.
"""

from __future__ import annotations

from typing import Any, Protocol


class StyleAnalyzerProtocol(Protocol):
    style_name: str

    def analyze_single(self, trade: dict, context: dict) -> dict: ...
    def analyze_batch(self, trades: list[dict], period: dict) -> dict: ...
    def get_method_diagnosis(self, trades: list[dict]) -> dict: ...


_REGISTRY: dict[str, StyleAnalyzerProtocol] = {}


def register(analyzer: StyleAnalyzerProtocol) -> None:
    _REGISTRY[analyzer.style_name] = analyzer


def get_style_analyzer(style: str) -> StyleAnalyzerProtocol | None:
    return _REGISTRY.get(style)


def list_styles() -> list[str]:
    return list(_REGISTRY.keys())


from . import technical  # noqa: E402 - trigger registration
