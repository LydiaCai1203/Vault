from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class Market(str, Enum):
    SH_A = "沪A"
    SZ_A = "深A"
    STAR = "科创"
    CHINEXT = "创业板"


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TradeStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class EmotionTag(str, Enum):
    CALM = "CALM"
    ANXIOUS = "ANXIOUS"
    GREEDY = "GREEDY"
    FEARFUL = "FEARFUL"
    IMPULSIVE = "IMPULSIVE"
    EXCITED = "EXCITED"
    REVENGE = "REVENGE"
    FOMO = "FOMO"


class RuleFlag(str, Enum):
    STOP_NOT_FOLLOWED = "STOP_NOT_FOLLOWED"
    POSITION_TOO_LARGE = "POSITION_TOO_LARGE"
    OVERTRADING = "OVERTRADING"
    PLAN_DEVIATION = "PLAN_DEVIATION"


class TradeBase(BaseModel):
    symbol: str
    name: str
    market: Market
    direction: Direction
    status: TradeStatus = TradeStatus.OPEN

    entry_time: datetime
    entry_price: float

    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None

    position_pct: float = Field(ge=0, le=1)
    stop_loss: Optional[float] = None

    pnl_cny: Optional[float] = None

    emotion_tags: List[EmotionTag] = Field(default_factory=list)
    rule_flags: List[RuleFlag] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    entry_reason: str
    notes: Optional[str] = None


class TradeCreate(TradeBase):
    pass


class TradeUpdate(BaseModel):
    status: Optional[TradeStatus] = None
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl_cny: Optional[float] = None
    emotion_tags: Optional[List[EmotionTag]] = None
    rule_flags: Optional[List[RuleFlag]] = None
    tags: Optional[List[str]] = None
    entry_reason: Optional[str] = None
    notes: Optional[str] = None


class TradeOut(TradeBase):
    id: str


class ReviewType(str, Enum):
    SINGLE = "SINGLE"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class ReviewScores(BaseModel):
    mind: float = Field(ge=0, le=5)
    method: float = Field(ge=0, le=5)
    money: float = Field(ge=0, le=5)


class Heatmap(BaseModel):
    rows: List[str]
    cols: List[str]
    values: List[List[int]]


class ReviewOut(BaseModel):
    id: str
    type: ReviewType
    range_start: date
    range_end: date
    sample_count: int
    win_rate: float
    rr: float
    expectancy: float
    scores: ReviewScores
    mistakes: List[str]
    todo: List[str]
    heatmap: Heatmap


class GenerateReviewIn(BaseModel):
    type: ReviewType = ReviewType.WEEKLY
    range_start: date
    range_end: date


class ChecklistItem(BaseModel):
    id: str
    text: str
    done: bool = False


class ChecklistOut(BaseModel):
    items: List[ChecklistItem]


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
