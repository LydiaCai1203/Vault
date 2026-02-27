"""Technical Analyzer - for chart/indicator-based trading style.

Focuses on:
- Signal consistency: entries/exits based on preset signals vs. impulsive
- Indicator stability: consistent use of indicator combinations
- Timeframe consistency: decisions on the planned timeframe
- Method dimension: system signal adherence score
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from . import register


class TechnicalAnalyzer:
    style_name = "technical"

    def analyze_single(self, trade: dict, context: dict) -> dict:
        result: dict[str, Any] = {}

        entry_reason = trade.get("entry_reason", "")
        result["has_signal_reference"] = _has_signal_keywords(entry_reason)

        tags = trade.get("tags", [])
        result["tagged_strategy"] = any(
            _is_strategy_tag(t) for t in tags
        )

        result["plan_deviation"] = trade.get("plan_deviation", None)
        result["has_plan_deviation"] = bool(trade.get("plan_deviation"))

        rule_flags = trade.get("rule_flags", [])
        result["signal_adherence"] = "PLAN_DEVIATION" not in rule_flags

        result["method_score"] = self._single_method_score(result)

        return result

    def analyze_batch(self, trades: list[dict], period: dict) -> dict:
        if not trades:
            return _empty_batch()

        signal_refs = sum(
            1 for t in trades
            if _has_signal_keywords(t.get("entry_reason", ""))
        )
        signal_consistency = signal_refs / len(trades) if trades else 0.0

        strategy_tags: list[str] = []
        for t in trades:
            for tag in t.get("tags", []):
                if _is_strategy_tag(tag):
                    strategy_tags.append(tag)
        tag_dist = dict(Counter(strategy_tags))
        unique_strategies = len(tag_dist)

        indicator_stability = 1.0
        if unique_strategies > 3:
            indicator_stability = max(0.3, 1.0 - (unique_strategies - 3) * 0.15)

        plan_deviations = sum(
            1 for t in trades
            if t.get("plan_deviation") or "PLAN_DEVIATION" in t.get("rule_flags", [])
        )
        deviation_rate = plan_deviations / len(trades) if trades else 0.0

        impulsive_count = sum(
            1 for t in trades
            if "IMPULSIVE" in t.get("emotion_tags", [])
            or "FOMO" in t.get("emotion_tags", [])
        )
        impulsive_rate = impulsive_count / len(trades) if trades else 0.0

        return {
            "signal_consistency": round(signal_consistency, 4),
            "indicator_stability": round(indicator_stability, 4),
            "strategy_distribution": tag_dist,
            "unique_strategies_used": unique_strategies,
            "plan_deviation_rate": round(deviation_rate, 4),
            "impulsive_entry_rate": round(impulsive_rate, 4),
            "method_score": round(self._batch_method_score(
                signal_consistency, indicator_stability, deviation_rate, impulsive_rate
            ), 1),
        }

    def get_method_diagnosis(self, trades: list[dict]) -> dict:
        batch = self.analyze_batch(trades, {})

        issues: list[str] = []
        strengths: list[str] = []

        sc = batch["signal_consistency"]
        if sc >= 0.8:
            strengths.append(f"信号一致性良好({sc:.0%})，大部分交易基于预设信号")
        elif sc < 0.5:
            issues.append(f"信号一致性偏低({sc:.0%})，多笔交易缺乏明确的技术信号支撑")

        dr = batch["plan_deviation_rate"]
        if dr > 0.3:
            issues.append(f"计划偏离率过高({dr:.0%})，频繁偏离交易计划")
        elif dr <= 0.1:
            strengths.append(f"计划执行度高，偏离率仅{dr:.0%}")

        ir = batch["impulsive_entry_rate"]
        if ir > 0.2:
            issues.append(f"冲动/FOMO交易占比{ir:.0%}，需加强进场纪律")

        ist = batch["indicator_stability"]
        if ist < 0.6:
            issues.append("使用的指标/策略过于分散，建议聚焦1-2个核心策略")

        return {
            "dimension": "Method",
            "style": "technical",
            "score": batch["method_score"],
            "strengths": strengths,
            "issues": issues,
            "metrics": {
                "signal_consistency": batch["signal_consistency"],
                "indicator_stability": batch["indicator_stability"],
                "plan_deviation_rate": batch["plan_deviation_rate"],
                "impulsive_entry_rate": batch["impulsive_entry_rate"],
            },
        }

    def _single_method_score(self, analysis: dict) -> float:
        score = 3.0
        if analysis.get("has_signal_reference"):
            score += 0.8
        if analysis.get("tagged_strategy"):
            score += 0.4
        if analysis.get("signal_adherence"):
            score += 0.5
        if analysis.get("has_plan_deviation"):
            score -= 1.0
        return min(5.0, max(1.0, round(score, 1)))

    def _batch_method_score(
        self,
        signal_consistency: float,
        indicator_stability: float,
        deviation_rate: float,
        impulsive_rate: float,
    ) -> float:
        score = (
            signal_consistency * 2.0
            + indicator_stability * 1.0
            + (1 - deviation_rate) * 1.0
            + (1 - impulsive_rate) * 1.0
        )
        return min(5.0, max(1.0, score))


_SIGNAL_KEYWORDS = {
    "均线", "MA", "MACD", "KDJ", "RSI", "布林", "BOLL",
    "突破", "支撑", "阻力", "金叉", "死叉", "背离",
    "形态", "头肩", "双底", "双顶", "三角", "旗形",
    "量能", "放量", "缩量", "量价",
    "趋势线", "通道", "斐波那契",
}


def _has_signal_keywords(text: str) -> bool:
    return any(kw in text for kw in _SIGNAL_KEYWORDS)


def _is_strategy_tag(tag: str) -> bool:
    strategy_indicators = {
        "均线", "MACD", "突破", "回调", "趋势", "形态",
        "量价", "波段", "日线", "周线", "分时",
    }
    return any(s in tag for s in strategy_indicators)


def _empty_batch() -> dict:
    return {
        "signal_consistency": 0.0,
        "indicator_stability": 0.0,
        "strategy_distribution": {},
        "unique_strategies_used": 0,
        "plan_deviation_rate": 0.0,
        "impulsive_entry_rate": 0.0,
        "method_score": 3.0,
    }


_instance = TechnicalAnalyzer()
register(_instance)
