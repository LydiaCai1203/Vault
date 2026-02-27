from __future__ import annotations

from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import TradeORM, loads
from ..dependencies import get_current_user, get_db
from ..schemas import DashboardSummaryOut, EquityPoint

CN_TZ = ZoneInfo("Asia/Shanghai")
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryOut)
def dashboard_summary(
    range_start: date,
    range_end: date,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    start_dt = datetime.combine(range_start, datetime.min.time(), tzinfo=CN_TZ).astimezone(timezone.utc)
    end_dt = datetime.combine(range_end, datetime.max.time(), tzinfo=CN_TZ).astimezone(timezone.utc)

    rows = (
        db.query(TradeORM)
        .filter(TradeORM.user_id == user_id)
        .filter(TradeORM.entry_time >= start_dt)
        .filter(TradeORM.entry_time <= end_dt)
        .order_by(TradeORM.entry_time.asc())
        .all()
    )

    total = len(rows)
    closed = [r for r in rows if r.status == "CLOSED" and r.pnl_cny is not None]
    closed_n = len(closed)
    wins = [r for r in closed if (r.pnl_cny or 0) > 0]
    win_rate = (len(wins) / closed_n) if closed_n else 0.0

    stop_not_followed = 0
    violations = 0
    for r in rows:
        flags = set(loads(r.rule_flags_json))
        if flags:
            violations += len(flags)
        if "STOP_NOT_FOLLOWED" in flags:
            stop_not_followed += 1

    violations_per_trade = (violations / total) if total else 0.0
    exec_score = max(1.0, min(5.0, 5.0 - violations_per_trade * 1.4))

    equity = 100000.0
    peak = equity
    max_dd = 0.0
    curve: list[EquityPoint] = []
    for r in rows:
        if r.status == "CLOSED" and r.pnl_cny is not None:
            equity += float(r.pnl_cny)
        peak = max(peak, equity)
        dd = (equity - peak) / peak if peak else 0.0
        max_dd = min(max_dd, dd)
        curve.append(EquityPoint(t=r.entry_time, equity=equity))

    weekly_return_pct = (equity - 100000.0) / 100000.0 * 100.0
    max_drawdown_pct = max_dd * 100.0

    return DashboardSummaryOut(
        range_start=range_start,
        range_end=range_end,
        total_trades=total,
        closed_trades=closed_n,
        win_rate=win_rate,
        exec_score=round(exec_score, 2),
        rule_violations=violations,
        stop_not_followed=stop_not_followed,
        weekly_return_pct=round(weekly_return_pct, 2),
        max_drawdown_pct=round(max_drawdown_pct, 2),
        equity_curve=curve,
    )
