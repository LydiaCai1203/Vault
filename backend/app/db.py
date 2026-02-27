from __future__ import annotations

import json
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import (
    create_engine,
    String,
    DateTime,
    Float,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class TradeORM(Base):
    __tablename__ = "trades"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    market: Mapped[str] = mapped_column(String)
    direction: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)

    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    entry_price: Mapped[float] = mapped_column(Float)

    exit_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    exit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    position_pct: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pnl_cny: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    emotion_tags_json: Mapped[str] = mapped_column(Text, default="[]")
    rule_flags_json: Mapped[str] = mapped_column(Text, default="[]")
    tags_json: Mapped[str] = mapped_column(Text, default="[]")

    entry_reason: Mapped[str] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ReviewORM(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    type: Mapped[str] = mapped_column(String)
    range_start: Mapped[date] = mapped_column()
    range_end: Mapped[date] = mapped_column()

    payload_json: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ChecklistORM(Base):
    __tablename__ = "checklist"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    text: Mapped[str] = mapped_column(Text)
    done: Mapped[bool] = mapped_column()


def make_engine(db_url: str):
    # PostgreSQL only
    if not db_url.startswith("postgresql"):
        raise ValueError("Only PostgreSQL DATABASE_URL is supported")
    return create_engine(db_url, future=True)


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def loads(s: str):
    return json.loads(s) if s else []


SessionLocal = sessionmaker(autocommit=False, autoflush=False)
