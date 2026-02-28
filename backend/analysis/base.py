"""Base Analyzer - common metrics shared across all trading styles.

Pure code computation, no LLM needed. Covers:
- Win rate, profit factor, expectancy
- Max single loss, max consecutive losses
- Position compliance (Money dimension)
- Stop-loss execution rate
- Emotion tag distribution (Mind dimension)
- Discipline violation frequency
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def analyze(trades: list[dict], risk_rules: dict | None = None) -> dict:
    """Compute base metrics for a list of trades.

    Args:
        trades: list of trade dicts with at least: pnl_cny, status, emotion_tags,
                rule_flags, position_pct, stop_loss, exit_price
        risk_rules: optional dict with max_single_risk_pct, max_position_pct, etc.
    """
    if not trades:
        return _empty_result()

    risk_rules = risk_rules or {}
    closed = [t for t in trades if t.get("status") == "CLOSED"]
    total = len(trades)
    closed_count = len(closed)

    wins = [t for t in closed if (t.get("pnl_cny") or 0) > 0]
    losses = [t for t in closed if (t.get("pnl_cny") or 0) < 0]
    breakeven = [t for t in closed if (t.get("pnl_cny") or 0) == 0]

    win_count = len(wins)
    loss_count = len(losses)
    win_rate = win_count / closed_count if closed_count > 0 else 0.0

    total_profit = sum(t.get("pnl_cny", 0) for t in wins)
    total_loss = abs(sum(t.get("pnl_cny", 0) for t in losses))
    avg_win = total_profit / win_count if win_count > 0 else 0.0
    avg_loss = total_loss / loss_count if loss_count > 0 else 0.0

    profit_factor = total_profit / total_loss if total_loss > 0 else float("inf") if total_profit > 0 else 0.0
    loss_rate = 1 - win_rate
    expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)

    pnl_values = [t.get("pnl_cny", 0) for t in closed]
    max_single_loss = min(pnl_values) if pnl_values else 0.0
    max_consecutive_losses = _max_consecutive(pnl_values, lambda x: x < 0)
    max_consecutive_wins = _max_consecutive(pnl_values, lambda x: x > 0)

    avg_rr = _avg_risk_reward(closed)

    money = _money_diagnosis(trades, risk_rules)
    mind = _mind_diagnosis(trades)

    return {
        "total_trades": total,
        "closed_trades": closed_count,
        "open_trades": total - closed_count,
        "win_count": win_count,
        "loss_count": loss_count,
        "breakeven_count": len(breakeven),
        "win_rate": round(win_rate, 4),
        "total_profit": round(total_profit, 2),
        "total_loss": round(total_loss, 2),
        "net_pnl": round(total_profit - total_loss, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "profit_factor": round(profit_factor, 4) if profit_factor != float("inf") else "inf",
        "expectancy": round(expectancy, 2),
        "max_single_loss": round(max_single_loss, 2),
        "max_consecutive_losses": max_consecutive_losses,
        "max_consecutive_wins": max_consecutive_wins,
        "avg_risk_reward": round(avg_rr, 4),
        "money_diagnosis": money,
        "mind_diagnosis": mind,
    }


def analyze_single(trade: dict, context: dict | None = None) -> dict:
    """Analyze a single trade in depth."""
    context = context or {}
    result: dict[str, Any] = {
        "trade_id": trade.get("id"),
        "symbol": trade.get("symbol"),
        "direction": trade.get("direction"),
        "pnl_cny": trade.get("pnl_cny"),
        "is_winner": (trade.get("pnl_cny") or 0) > 0,
    }

    if trade.get("stop_loss") and trade.get("entry_price"):
        entry = trade["entry_price"]
        sl = trade["stop_loss"]
        direction = trade.get("direction", "LONG")
        if direction == "LONG":
            risk = entry - sl
        else:
            risk = sl - entry
        result["planned_risk"] = round(risk, 2)

        if trade.get("exit_price"):
            ep = trade["exit_price"]
            if direction == "LONG":
                reward = ep - entry
            else:
                reward = entry - ep
            result["actual_reward"] = round(reward, 2)
            result["actual_rr"] = round(reward / risk, 2) if risk > 0 else None

    stop_followed = _check_stop_followed(trade)
    result["stop_loss_followed"] = stop_followed

    result["emotion_tags"] = trade.get("emotion_tags", [])
    result["rule_flags"] = trade.get("rule_flags", [])

    negative_emotions = {"ANXIOUS", "GREEDY", "FEARFUL", "IMPULSIVE", "REVENGE", "FOMO"}
    trade_emotions = set(trade.get("emotion_tags", []))
    result["emotional_trade"] = bool(trade_emotions & negative_emotions)

    return result


def _money_diagnosis(trades: list[dict], risk_rules: dict) -> dict:
    max_pos = risk_rules.get("max_position_pct", 0.3)
    compliant = sum(1 for t in trades if (t.get("position_pct") or 0) <= max_pos)
    position_compliance = compliant / len(trades) if trades else 0.0

    has_stop = [t for t in trades if t.get("stop_loss") is not None]
    stop_set_rate = len(has_stop) / len(trades) if trades else 0.0

    stop_followed = sum(1 for t in has_stop if _check_stop_followed(t))
    stop_exec_rate = stop_followed / len(has_stop) if has_stop else 0.0

    return {
        "position_compliance_rate": round(position_compliance, 4),
        "stop_loss_set_rate": round(stop_set_rate, 4),
        "stop_loss_execution_rate": round(stop_exec_rate, 4),
        "score": round(_score_money(position_compliance, stop_set_rate, stop_exec_rate), 1),
    }


def _mind_diagnosis(trades: list[dict]) -> dict:
    all_emotions: list[str] = []
    for t in trades:
        all_emotions.extend(t.get("emotion_tags", []))
    emotion_dist = dict(Counter(all_emotions))

    all_flags: list[str] = []
    for t in trades:
        all_flags.extend(t.get("rule_flags", []))
    violation_dist = dict(Counter(all_flags))
    violation_rate = len([t for t in trades if t.get("rule_flags")]) / len(trades) if trades else 0.0

    negative = {"ANXIOUS", "GREEDY", "FEARFUL", "IMPULSIVE", "REVENGE", "FOMO"}
    negative_count = sum(1 for e in all_emotions if e in negative)
    emotional_trade_rate = negative_count / len(all_emotions) if all_emotions else 0.0

    return {
        "emotion_distribution": emotion_dist,
        "violation_distribution": violation_dist,
        "violation_rate": round(violation_rate, 4),
        "emotional_trade_rate": round(emotional_trade_rate, 4),
        "score": round(_score_mind(violation_rate, emotional_trade_rate), 1),
    }


def _check_stop_followed(trade: dict) -> bool:
    if not trade.get("stop_loss") or not trade.get("exit_price"):
        return True
    sl = trade["stop_loss"]
    ep = trade["exit_price"]
    direction = trade.get("direction", "LONG")
    if direction == "LONG":
        return ep >= sl * 0.98  # 2% tolerance
    else:
        return ep <= sl * 1.02


def _avg_risk_reward(closed: list[dict]) -> float:
    ratios = []
    for t in closed:
        if t.get("stop_loss") and t.get("entry_price") and t.get("exit_price"):
            entry = t["entry_price"]
            sl = t["stop_loss"]
            ep = t["exit_price"]
            direction = t.get("direction", "LONG")
            if direction == "LONG":
                risk = entry - sl
                reward = ep - entry
            else:
                risk = sl - entry
                reward = entry - ep
            if risk > 0:
                ratios.append(reward / risk)
    return sum(ratios) / len(ratios) if ratios else 0.0


def _max_consecutive(values: list, predicate) -> int:
    max_count = 0
    current = 0
    for v in values:
        if predicate(v):
            current += 1
            max_count = max(max_count, current)
        else:
            current = 0
    return max_count


def _score_money(pos_compliance: float, stop_set: float, stop_exec: float) -> float:
    return min(5.0, max(1.0, (pos_compliance * 2 + stop_set * 1.5 + stop_exec * 1.5)))


def _score_mind(violation_rate: float, emotional_rate: float) -> float:
    base = 5.0
    base -= violation_rate * 3
    base -= emotional_rate * 2
    return min(5.0, max(1.0, base))


def _empty_result() -> dict:
    return {
        "total_trades": 0,
        "closed_trades": 0,
        "open_trades": 0,
        "win_count": 0,
        "loss_count": 0,
        "breakeven_count": 0,
        "win_rate": 0.0,
        "total_profit": 0.0,
        "total_loss": 0.0,
        "net_pnl": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "profit_factor": 0.0,
        "expectancy": 0.0,
        "max_single_loss": 0.0,
        "max_consecutive_losses": 0,
        "max_consecutive_wins": 0,
        "avg_risk_reward": 0.0,
        "money_diagnosis": {"position_compliance_rate": 0, "stop_loss_set_rate": 0, "stop_loss_execution_rate": 0, "score": 3.0},
        "mind_diagnosis": {"emotion_distribution": {}, "violation_distribution": {}, "violation_rate": 0, "emotional_trade_rate": 0, "score": 3.0},
    }
