from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import TradeORM, dumps, loads
from ..dependencies import get_current_user, get_db, utcnow
from ..schemas import TradeCreate, TradeOut, TradeUpdate

router = APIRouter(prefix="/api/trades", tags=["trades"])


def _orm_to_out(r: TradeORM) -> TradeOut:
    return TradeOut(
        id=r.id,
        symbol=r.symbol,
        name=r.name,
        market=r.market,
        direction=r.direction,
        status=r.status,
        entry_time=r.entry_time,
        entry_price=r.entry_price,
        exit_time=r.exit_time,
        exit_price=r.exit_price,
        position_pct=r.position_pct,
        stop_loss=r.stop_loss,
        pnl_cny=r.pnl_cny,
        emotion_tags=loads(r.emotion_tags_json),
        rule_flags=loads(r.rule_flags_json),
        tags=loads(r.tags_json),
        entry_reason=r.entry_reason,
        notes=r.notes,
    )


@router.get("", response_model=list[TradeOut])
def list_trades(
    status: str = "all",
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    q = db.query(TradeORM).filter(TradeORM.user_id == user_id)
    if status == "open":
        q = q.filter(TradeORM.status == "OPEN")
    elif status == "closed":
        q = q.filter(TradeORM.status == "CLOSED")
    rows = q.order_by(TradeORM.entry_time.desc()).all()
    return [_orm_to_out(r) for r in rows]


def _fetch_trade(trade_id: str, db: Session, user_id: str) -> TradeOut:
    r = db.query(TradeORM).filter(TradeORM.id == trade_id, TradeORM.user_id == user_id).first()
    if not r:
        raise HTTPException(404, "trade not found")
    return _orm_to_out(r)


@router.get("/{trade_id}", response_model=TradeOut)
def get_trade(
    trade_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return _fetch_trade(trade_id, db, user_id)


@router.post("", response_model=TradeOut)
def create_trade(
    payload: TradeCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    now = utcnow()
    tid = str(uuid4())
    r = TradeORM(
        id=tid,
        user_id=user_id,
        symbol=payload.symbol,
        name=payload.name,
        market=payload.market,
        direction=payload.direction,
        status=payload.status,
        entry_time=payload.entry_time,
        entry_price=payload.entry_price,
        exit_time=payload.exit_time,
        exit_price=payload.exit_price,
        position_pct=payload.position_pct,
        stop_loss=payload.stop_loss,
        pnl_cny=payload.pnl_cny,
        emotion_tags_json=dumps([e.value for e in payload.emotion_tags]),
        rule_flags_json=dumps([f.value for f in payload.rule_flags]),
        tags_json=dumps(payload.tags),
        entry_reason=payload.entry_reason,
        notes=payload.notes,
        created_at=now,
        updated_at=now,
    )
    db.add(r)
    db.commit()
    return _fetch_trade(tid, db, user_id)


@router.patch("/{trade_id}", response_model=TradeOut)
def update_trade(
    trade_id: str,
    payload: TradeUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    r = db.query(TradeORM).filter(TradeORM.id == trade_id, TradeORM.user_id == user_id).first()
    if not r:
        raise HTTPException(404, "trade not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        if k in {"emotion_tags", "rule_flags", "tags"} and v is not None:
            if k == "emotion_tags":
                r.emotion_tags_json = dumps([e.value if hasattr(e, "value") else e for e in v])
            elif k == "rule_flags":
                r.rule_flags_json = dumps([f.value if hasattr(f, "value") else f for f in v])
            else:
                r.tags_json = dumps(v)
        else:
            setattr(r, k, v)

    r.updated_at = utcnow()
    db.add(r)
    db.commit()
    return _fetch_trade(trade_id, db, user_id)

