"""Analysis Engine - routes to Base + Style analyzer, merges results.

Pure code router (NOT an LLM Agent):
1. Always runs BaseAnalyzer (common metrics)
2. Routes to the appropriate StyleAnalyzer based on trading style
3. Merges results into a unified AnalysisResult
"""

from __future__ import annotations

from typing import Any

from . import base as base_analyzer
from .styles import get_style_analyzer


def analyze(
    trades: list[dict],
    style: str = "technical",
    risk_rules: dict | None = None,
    analysis_type: str = "batch",
    trade_id: str | None = None,
) -> dict:
    """Run Base + Style analysis on trades.

    Args:
        trades: list of trade dicts, optionally enriched with market_context
        style: trading style name for routing
        risk_rules: optional risk rules from Portfolio
        analysis_type: "single" for one trade, "batch" for period analysis
        trade_id: specific trade ID for single analysis
    """
    if analysis_type == "single" and trade_id:
        return _analyze_single(trades, trade_id, style)
    return _analyze_batch(trades, style, risk_rules)


def _analyze_batch(
    trades: list[dict],
    style: str,
    risk_rules: dict | None = None,
) -> dict:
    base_result = base_analyzer.analyze(trades, risk_rules)

    style_result: dict[str, Any] = {}
    style_analyzer = get_style_analyzer(style)
    if style_analyzer:
        try:
            style_result = style_analyzer.analyze_batch(trades, {})
        except Exception as e:
            style_result = {"error": str(e)}

    method_diagnosis: dict[str, Any] = {}
    if style_analyzer:
        try:
            method_diagnosis = style_analyzer.get_method_diagnosis(trades)
        except Exception as e:
            method_diagnosis = {"error": str(e)}

    return {
        "analysis_type": "batch",
        "trade_count": len(trades),
        "style": style,
        "base_metrics": base_result,
        "style_metrics": style_result,
        "method_diagnosis": method_diagnosis,
    }


def _analyze_single(
    trades: list[dict],
    trade_id: str,
    style: str,
) -> dict:
    trade = next((t for t in trades if t.get("id") == trade_id), None)
    if not trade:
        if trades:
            trade = trades[0]
        else:
            return {"error": "trade not found", "trade_id": trade_id}

    base_result = base_analyzer.analyze_single(trade)

    style_result: dict[str, Any] = {}
    style_analyzer = get_style_analyzer(style)
    if style_analyzer:
        try:
            style_result = style_analyzer.analyze_single(trade, {})
        except Exception as e:
            style_result = {"error": str(e)}

    return {
        "analysis_type": "single",
        "trade_id": trade_id,
        "style": style,
        "base_analysis": base_result,
        "style_analysis": style_result,
    }
