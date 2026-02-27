"""FastAPI dependencies: database session, utilities, auth."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from .db import SessionLocal

# MVP: use X-User-Id header; later replace with JWT
DEFAULT_USER_ID = "default"


def get_current_user(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> str:
    """Resolve user_id from request. MVP: X-User-Id header or default."""
    return x_user_id if x_user_id else DEFAULT_USER_ID


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def utcnow() -> datetime:
    """Current UTC timestamp."""
    return datetime.now(timezone.utc)
