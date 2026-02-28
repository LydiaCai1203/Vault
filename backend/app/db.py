"""数据库连接、Session、JSON 序列化工具。ORM 定义在 app.models。"""

from __future__ import annotations

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, ChecklistORM, ReviewORM, TradeORM

# 向后兼容：从 db 仍可 import ORM 与工具
__all__ = [
    "Base",
    "ChecklistORM",
    "ReviewORM",
    "TradeORM",
    "SessionLocal",
    "dumps",
    "loads",
    "make_engine",
]


def make_engine(db_url: str):
    if not db_url.startswith("postgresql"):
        raise ValueError("Only PostgreSQL DATABASE_URL is supported")
    return create_engine(db_url, future=True)


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def loads(s: str):
    return json.loads(s) if s else []


SessionLocal = sessionmaker(autocommit=False, autoflush=False)
