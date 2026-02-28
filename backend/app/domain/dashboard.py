"""仪表盘 (dashboard) 相关响应结构。"""

from __future__ import annotations

from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field


class EquityPoint(BaseModel):
    t: datetime
    equity: float


class DashboardSummaryOut(BaseModel):
    range_start: date
    range_end: date
    total_trades: int
    closed_trades: int
    win_rate: float
    exec_score: float = Field(ge=1, le=5)
    rule_violations: int
    stop_not_followed: int
    weekly_return_pct: float
    max_drawdown_pct: float
    equity_curve: List[EquityPoint]
