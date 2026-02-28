from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import TradeORM, ReviewORM, ChecklistORM, dumps, loads
from ..dependencies import get_current_user, get_db, utcnow
from ..domain.reviews import (
    GenerateReviewIn,
    Heatmap,
    ReviewOut,
    ReviewScores,
)

CN_TZ = ZoneInfo("Asia/Shanghai")
router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewOut])
def list_reviews(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    rows = (
        db.query(ReviewORM)
        .filter(ReviewORM.user_id == user_id)
        .order_by(ReviewORM.created_at.desc())
        .all()
    )
    out = []
    for r in rows:
        payload = loads(r.payload_json) if r.payload_json else None
        if not payload:
            continue
        out.append(ReviewOut(**payload))
    return out


@router.get("/{review_id}", response_model=ReviewOut)
def get_review(
    review_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    r = db.query(ReviewORM).filter(ReviewORM.id == review_id, ReviewORM.user_id == user_id).first()
    if not r:
        raise HTTPException(404, "review not found")
    payload = loads(r.payload_json)
    return ReviewOut(**payload)


@router.post("/generate", response_model=ReviewOut)
def generate_review(
    inp: GenerateReviewIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Generate a review from trades in range.

    Notes:
    - This is NOT market advice; it's behavior/discipline analytics.
    - The scoring is heuristic and can be swapped to your Analyzer later.
    """
    rid = str(uuid4())

    start_dt = datetime.combine(inp.range_start, datetime.min.time(), tzinfo=CN_TZ).astimezone(timezone.utc)
    end_dt = datetime.combine(inp.range_end, datetime.max.time(), tzinfo=CN_TZ).astimezone(timezone.utc)

    trades = (
        db.query(TradeORM)
        .filter(TradeORM.user_id == user_id)
        .filter(TradeORM.entry_time >= start_dt)
        .filter(TradeORM.entry_time <= end_dt)
        .order_by(TradeORM.entry_time.asc())
        .all()
    )

    closed = [t for t in trades if t.status == "CLOSED" and t.pnl_cny is not None]
    sample_count = len(closed)

    wins = [t for t in closed if (t.pnl_cny or 0) > 0]
    losses = [t for t in closed if (t.pnl_cny or 0) < 0]

    win_rate = (len(wins) / sample_count) if sample_count else 0.0

    avg_win = (sum(float(t.pnl_cny) for t in wins) / len(wins)) if wins else 0.0
    avg_loss_abs = (abs(sum(float(t.pnl_cny) for t in losses) / len(losses))) if losses else 0.0
    rr = (avg_win / avg_loss_abs) if avg_loss_abs else 0.0

    expectancy = win_rate * avg_win - (1.0 - win_rate) * avg_loss_abs

    stop_not_followed = 0
    overtrade = 0
    fomo = 0
    anxious = 0
    plan_dev = 0

    hm_rows = ["09:30-10:00", "10:00-11:30", "13:00-14:00", "14:00-15:00"]
    hm_cols = ["冲动入场", "追涨", "未按止损", "报复性交易", "情绪化加仓"]
    hm = [[0 for _ in hm_cols] for __ in hm_rows]

    def bucket(dt_utc: datetime) -> int:
        dt = dt_utc.astimezone(CN_TZ)
        h, m = dt.hour, dt.minute
        if (h == 9 and m >= 30) or (h == 10 and m < 0):
            return 0
        if (h == 10) or (h == 11 and m <= 30) or (h == 9 and m < 30):
            return 1
        if h == 13:
            return 2
        return 3

    for t in trades:
        flags = set(loads(t.rule_flags_json))
        emo = set(loads(t.emotion_tags_json))
        tags = set(loads(t.tags_json))

        if "STOP_NOT_FOLLOWED" in flags:
            stop_not_followed += 1
        if "OVERTRADING" in flags:
            overtrade += 1
        if "PLAN_DEVIATION" in flags:
            plan_dev += 1
        if "FOMO" in emo:
            fomo += 1
        if "ANXIOUS" in emo:
            anxious += 1

        b = bucket(t.entry_time)
        if "IMPULSIVE" in emo:
            hm[b][0] += 1
        if "追涨" in tags:
            hm[b][1] += 1
        if "STOP_NOT_FOLLOWED" in flags:
            hm[b][2] += 1
        if "REVENGE" in emo:
            hm[b][3] += 1
        if "加仓" in tags:
            hm[b][4] += 1

    hm_intensity = [[min(4, v) for v in row] for row in hm]

    mind_score = max(0.0, 5.0 - (fomo * 0.6 + anxious * 0.3))
    money_score = max(0.0, 5.0 - (stop_not_followed * 0.9))
    method_score = max(0.0, 5.0 - (plan_dev * 0.6 + overtrade * 0.4))

    mind_score = float(max(0.0, min(5.0, mind_score)))
    method_score = float(max(0.0, min(5.0, method_score)))
    money_score = float(max(0.0, min(5.0, money_score)))

    mistakes = []
    if fomo:
        mistakes.append("FOMO 增加（更易冲动入场）")
    if stop_not_followed:
        mistakes.append(f"本期 {stop_not_followed} 次未按止损执行")
    if plan_dev:
        mistakes.append("计划与执行偏差增加")
    if not mistakes:
        mistakes = ["整体纪律较稳定，继续保持"]

    todo = [
        "开仓前强制填写止损",
        "盘中情绪标签必选",
    ]
    if stop_not_followed:
        todo.insert(0, "止损触发即执行（禁止拖延）")
    if fomo:
        todo.append("不追涨：等待回踩确认后再入")

    payload = ReviewOut(
        id=rid,
        type=inp.type,
        range_start=inp.range_start,
        range_end=inp.range_end,
        sample_count=sample_count,
        win_rate=win_rate,
        rr=rr,
        expectancy=expectancy,
        scores=ReviewScores(mind=round(mind_score, 1), method=round(method_score, 1), money=round(money_score, 1)),
        mistakes=mistakes,
        todo=todo,
        heatmap=Heatmap(rows=hm_rows, cols=hm_cols, values=hm_intensity),
    ).model_dump()

    row = ReviewORM(
        id=rid,
        user_id=user_id,
        type=inp.type,
        range_start=inp.range_start,
        range_end=inp.range_end,
        payload_json=dumps(payload),
        created_at=utcnow(),
    )
    db.add(row)

    db.query(ChecklistORM).filter(ChecklistORM.user_id == user_id).delete()
    for i, text in enumerate(payload["todo"]):
        db.add(ChecklistORM(id=f"c{i+1}", user_id=user_id, text=text, done=False))

    db.commit()
    return ReviewOut(**payload)
