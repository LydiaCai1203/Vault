"""Technical Analyzer - for chart/indicator-based trading style.

When market_context K-line data is available (via Data Service enrichment),
performs real signal verification: MA crossovers, price vs MA position,
volume confirmation, etc. Falls back to keyword-based heuristics when
K-line data is unavailable.

Focuses on:
- Signal consistency: entries/exits based on preset signals vs. impulsive
- Signal verification: did the claimed technical signal actually exist?
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
        result["tagged_strategy"] = any(_is_strategy_tag(t) for t in tags)

        result["plan_deviation"] = trade.get("plan_deviation", None)
        result["has_plan_deviation"] = bool(trade.get("plan_deviation"))

        rule_flags = trade.get("rule_flags", [])
        result["signal_adherence"] = "PLAN_DEVIATION" not in rule_flags

        mkt = trade.get("market_context", {})
        if mkt.get("data_available"):
            klines = mkt.get("klines_during", [])
            klines_before = mkt.get("klines_before", [])
            verification = _verify_entry_signal(
                trade, klines_before + klines, entry_reason
            )
            result["signal_verification"] = verification
            result["signal_verified"] = verification.get("verified", False)

            exit_analysis = _analyze_exit_quality(trade, mkt)
            result["exit_analysis"] = exit_analysis
        else:
            result["signal_verification"] = {"available": False}
            result["signal_verified"] = None
            result["exit_analysis"] = {"available": False}

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

        verified_count = 0
        verifiable_count = 0
        for t in trades:
            mkt = t.get("market_context", {})
            if mkt.get("data_available"):
                verifiable_count += 1
                klines = mkt.get("klines_before", []) + mkt.get("klines_during", [])
                v = _verify_entry_signal(t, klines, t.get("entry_reason", ""))
                if v.get("verified"):
                    verified_count += 1

        signal_verification_rate = (
            verified_count / verifiable_count if verifiable_count > 0 else None
        )

        premature_exits = 0
        exit_analyzed = 0
        for t in trades:
            mkt = t.get("market_context", {})
            if mkt.get("data_available") and t.get("exit_price"):
                exit_analyzed += 1
                ea = _analyze_exit_quality(t, mkt)
                if ea.get("premature_exit"):
                    premature_exits += 1

        premature_exit_rate = (
            premature_exits / exit_analyzed if exit_analyzed > 0 else None
        )

        return {
            "signal_consistency": round(signal_consistency, 4),
            "indicator_stability": round(indicator_stability, 4),
            "strategy_distribution": tag_dist,
            "unique_strategies_used": unique_strategies,
            "plan_deviation_rate": round(deviation_rate, 4),
            "impulsive_entry_rate": round(impulsive_rate, 4),
            "signal_verification_rate": round(signal_verification_rate, 4) if signal_verification_rate is not None else None,
            "premature_exit_rate": round(premature_exit_rate, 4) if premature_exit_rate is not None else None,
            "method_score": round(self._batch_method_score(
                signal_consistency, indicator_stability, deviation_rate,
                impulsive_rate, signal_verification_rate,
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

        svr = batch.get("signal_verification_rate")
        if svr is not None:
            if svr >= 0.7:
                strengths.append(f"信号验证通过率{svr:.0%}，技术分析判断较准确")
            elif svr < 0.4:
                issues.append(f"信号验证通过率仅{svr:.0%}，声称的技术信号多数不成立，需加强图形识别能力")

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

        per = batch.get("premature_exit_rate")
        if per is not None and per > 0.3:
            issues.append(f"过早离场率{per:.0%}，出场后价格继续向有利方向运行，考虑优化止盈策略")

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
                "signal_verification_rate": batch.get("signal_verification_rate"),
                "premature_exit_rate": batch.get("premature_exit_rate"),
            },
        }

    def _single_method_score(self, analysis: dict) -> float:
        score = 3.0
        if analysis.get("has_signal_reference"):
            score += 0.6
        if analysis.get("tagged_strategy"):
            score += 0.3
        if analysis.get("signal_adherence"):
            score += 0.4
        if analysis.get("has_plan_deviation"):
            score -= 1.0
        if analysis.get("signal_verified") is True:
            score += 0.7
        elif analysis.get("signal_verified") is False:
            score -= 0.5
        return min(5.0, max(1.0, round(score, 1)))

    def _batch_method_score(
        self,
        signal_consistency: float,
        indicator_stability: float,
        deviation_rate: float,
        impulsive_rate: float,
        signal_verification_rate: float | None = None,
    ) -> float:
        score = (
            signal_consistency * 1.5
            + indicator_stability * 0.8
            + (1 - deviation_rate) * 1.0
            + (1 - impulsive_rate) * 0.7
        )
        if signal_verification_rate is not None:
            score += signal_verification_rate * 1.0
        else:
            score += 0.5
        return min(5.0, max(1.0, score))


# ---------------------------------------------------------------------------
# Signal verification using actual K-line data
# ---------------------------------------------------------------------------

def _verify_entry_signal(
    trade: dict,
    klines: list[dict],
    entry_reason: str,
) -> dict:
    """Verify whether the claimed entry signal existed in the K-line data."""
    if not klines or len(klines) < 5:
        return {"available": False, "verified": None}

    closes = [k["close"] for k in klines]
    entry_price = trade.get("entry_price", 0)
    checks: dict[str, Any] = {"available": True, "signals_checked": []}

    any_verified = False

    if any(kw in entry_reason for kw in ("均线", "MA", "金叉", "死叉")):
        ma5 = _sma(closes, 5)
        ma10 = _sma(closes, 10)
        ma20 = _sma(closes, 20)
        if ma5 is not None and ma10 is not None:
            golden_cross = ma5 > ma10 and (len(closes) >= 6 and _sma(closes[:-1], 5) <= _sma(closes[:-1], 10))  # type: ignore
            checks["ma_cross"] = {
                "ma5": round(ma5, 2), "ma10": round(ma10, 2),
                "ma20": round(ma20, 2) if ma20 else None,
                "golden_cross_present": golden_cross,
            }
            checks["signals_checked"].append("MA_cross")
            if golden_cross or (trade.get("direction") == "LONG" and ma5 > ma10):
                any_verified = True

    if any(kw in entry_reason for kw in ("突破", "支撑", "阻力")):
        recent_high = max(k["high"] for k in klines[-20:]) if len(klines) >= 20 else max(k["high"] for k in klines)
        recent_low = min(k["low"] for k in klines[-20:]) if len(klines) >= 20 else min(k["low"] for k in klines)
        checks["breakout"] = {
            "recent_high": round(recent_high, 2),
            "recent_low": round(recent_low, 2),
            "entry_near_high": entry_price >= recent_high * 0.98,
            "entry_near_low": entry_price <= recent_low * 1.02,
        }
        checks["signals_checked"].append("breakout")
        direction = trade.get("direction", "LONG")
        if direction == "LONG" and entry_price >= recent_high * 0.98:
            any_verified = True
        elif direction == "SHORT" and entry_price <= recent_low * 1.02:
            any_verified = True

    if any(kw in entry_reason for kw in ("放量", "缩量", "量能", "量价")):
        if klines and all("volume" in k for k in klines):
            volumes = [k["volume"] for k in klines]
            avg_vol = sum(volumes[:-1]) / len(volumes[:-1]) if len(volumes) > 1 else volumes[0]
            last_vol = volumes[-1]
            vol_ratio = last_vol / avg_vol if avg_vol > 0 else 1.0
            checks["volume"] = {
                "avg_volume": round(avg_vol, 0),
                "entry_day_volume": round(last_vol, 0),
                "volume_ratio": round(vol_ratio, 2),
                "is_high_volume": vol_ratio > 1.5,
            }
            checks["signals_checked"].append("volume")
            if "放量" in entry_reason and vol_ratio > 1.5:
                any_verified = True
            elif "缩量" in entry_reason and vol_ratio < 0.7:
                any_verified = True

    if not checks["signals_checked"]:
        if _has_signal_keywords(entry_reason):
            checks["signals_checked"].append("keyword_only")
            any_verified = True

    checks["verified"] = any_verified
    return checks


def _analyze_exit_quality(trade: dict, market_context: dict) -> dict:
    """Analyze whether the exit was premature by checking post-exit price action."""
    klines_after = market_context.get("klines_after_exit", [])
    if not klines_after or not trade.get("exit_price"):
        return {"available": False}

    exit_price = trade["exit_price"]
    direction = trade.get("direction", "LONG")
    post_prices = [k["close"] for k in klines_after]

    if direction == "LONG":
        max_post = max(post_prices) if post_prices else exit_price
        missed_gain_pct = (max_post - exit_price) / exit_price if exit_price > 0 else 0
        premature = missed_gain_pct > 0.03
    else:
        min_post = min(post_prices) if post_prices else exit_price
        missed_gain_pct = (exit_price - min_post) / exit_price if exit_price > 0 else 0
        premature = missed_gain_pct > 0.03

    return {
        "available": True,
        "premature_exit": premature,
        "missed_gain_pct": round(missed_gain_pct, 4),
        "post_exit_days_checked": len(klines_after),
    }


def _sma(values: list[float], period: int) -> float | None:
    """Simple moving average of the last `period` values."""
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


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
        "signal_verification_rate": None,
        "premature_exit_rate": None,
        "method_score": 3.0,
    }


_instance = TechnicalAnalyzer()
register(_instance)
