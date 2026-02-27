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

app = FastAPI(title="Vault API", version="0.1.0")

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
