"""交易 (trades) 相关请求/响应与枚举。"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ..db import TradeORM


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

    @classmethod
    def from_orm(cls, r: "TradeORM") -> TradeOut:
        from ..db import loads
        return cls(
            id=r.id,
            symbol=r.symbol,
            name=r.name,
            market=Market(r.market),
            direction=Direction(r.direction),
            status=TradeStatus(r.status),
            entry_time=r.entry_time,
            entry_price=r.entry_price,
            exit_time=r.exit_time,
            exit_price=r.exit_price,
            position_pct=r.position_pct,
            stop_loss=r.stop_loss,
            pnl_cny=r.pnl_cny,
            emotion_tags=[EmotionTag(x) if isinstance(x, str) else x for x in loads(r.emotion_tags_json)],
            rule_flags=[RuleFlag(x) if isinstance(x, str) else x for x in loads(r.rule_flags_json)],
            tags=loads(r.tags_json),
            entry_reason=r.entry_reason,
            notes=r.notes,
        )
