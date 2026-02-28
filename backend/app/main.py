"""Vault API - FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_database_url
from .db import Base, make_engine, SessionLocal
from .routers import agent, checklist, dashboard, health, reviews, trades

engine = make_engine(get_database_url())
Base.metadata.create_all(bind=engine)
SessionLocal.configure(bind=engine)

OPENAPI_TAGS = [
    {"name": "health", "description": "健康检查"},
    {"name": "agent", "description": "自然语言对话与 Agent（记一笔、复盘、报告）"},
    {"name": "trades", "description": "交易记录 CRUD"},
    {"name": "dashboard", "description": "仪表盘统计"},
    {"name": "reviews", "description": "复盘报告生成与查询"},
    {"name": "checklist", "description": "待办清单"},
]

app = FastAPI(
    title="Vault API",
    description="交易日志系统后端。所有需鉴权接口请携带 Header: **X-User-Id**（缺省为 default）。",
    version="0.1.0",
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(agent.router)
app.include_router(trades.router)
app.include_router(dashboard.router)
app.include_router(reviews.router)
app.include_router(checklist.router)
