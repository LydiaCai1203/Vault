"""Agent invocation - supports both sandbox (Docker) and inline (dev) execution.

Two modes:
- Sandbox: spawns Docker containers per request (production)
- Inline: runs agents in-process (development, VAULT_AGENT_MODE=inline)
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import TradeORM, loads
from ..dependencies import get_current_user, get_db
from agent_runtime.executor import SandboxExecutor, ToolProxy
from agent_runtime.queue import AgentTask, enqueue, get_result
from agent_runtime.tool_handlers import register_all

CN_TZ = ZoneInfo("Asia/Shanghai")
router = APIRouter(prefix="/api/agent", tags=["agent"])

tool_proxy = ToolProxy()
register_all(tool_proxy)
executor = SandboxExecutor(tool_proxy=tool_proxy)

REDIS_URL = os.getenv("REDIS_URL")
QUEUE_NAME = "vault:agent:tasks"
RESULT_PREFIX = "vault:agent:result:"
AGENT_MODE = os.getenv("VAULT_AGENT_MODE", "inline")


class ChatPayload(BaseModel):
    """主入口：自然语言对话，由 Orchestrator 路由到记一笔/复盘/查询等。"""
    input: str = Field(..., description="用户输入的自然语言")
    conversation: list[dict] | None = Field(None, description="历史消息 [{role, content}]，可选")


class RecorderPayload(BaseModel):
    """直接调用记录 Agent（解析自然语言为结构化交易并保存）。"""
    input: str = Field(..., description="用户关于交易的描述，如「今天买了比亚迪 230 元 2 成仓」")


class AnalyzerPayload(BaseModel):
    """按日期范围拉取交易并做分析（含市场数据丰富化）。"""
    range_start: str = Field(..., description="起始日期 YYYY-MM-DD")
    range_end: str = Field(..., description="截止日期 YYYY-MM-DD")
    style: str = Field("technical", description="风格: technical | value | trend | short_term")
    analysis_type: str = Field("batch", description="batch=区间分析, single=单笔需配合 trade_id")
    trade_id: str | None = Field(None, description="单笔分析时的交易 ID")


class ReporterPayload(BaseModel):
    """根据分析结果生成复盘报告。"""
    report_type: str = Field("weekly", description="报告类型: weekly | monthly | single")
    analysis_data: dict | str = Field(default_factory=dict, description="分析结果 JSON，可由 analyzer/run 返回")
    date_from: str | None = Field(None, description="区间起始日期")
    date_to: str | None = Field(None, description="区间截止日期")


@router.post("/chat")
def chat(
    payload: ChatPayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Main entry point: send user message to Orchestrator Agent."""
    task_payload = {
        "input": payload.input,
        "conversation": payload.conversation or [],
    }
    return _run_agent("orchestrator", user_id, task_payload)


@router.post("/recorder/run")
def run_recorder(
    payload: RecorderPayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    async_mode: bool = Query(False, alias="async"),
):
    """Run Recorder agent directly."""
    task_payload = {"input": payload.input}
    task_id = str(uuid.uuid4())
    if async_mode and REDIS_URL:
        task = AgentTask(task_id=task_id, user_id=user_id, agent_type="recorder", payload=task_payload)
        enqueue(REDIS_URL, QUEUE_NAME, task)
        return {"task_id": task_id, "status": "queued"}
    return _run_agent("recorder", user_id, task_payload)


@router.post("/analyzer/run")
def run_analyzer(
    payload: AnalyzerPayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    async_mode: bool = Query(False, alias="async"),
):
    """Run Analyzer in sandbox. Executor proxies: fetch trades and inject into payload."""
    from datetime import date

    try:
        range_start = date.fromisoformat(payload.range_start)
        range_end = date.fromisoformat(payload.range_end)
    except ValueError as e:
        raise HTTPException(400, f"Invalid date: {e}") from e

    start_dt = datetime.combine(range_start, datetime.min.time(), tzinfo=CN_TZ).astimezone(timezone.utc)
    end_dt = datetime.combine(range_end, datetime.max.time(), tzinfo=CN_TZ).astimezone(timezone.utc)

    rows = (
        db.query(TradeORM)
        .filter(TradeORM.user_id == user_id)
        .filter(TradeORM.entry_time >= start_dt)
        .filter(TradeORM.entry_time <= end_dt)
        .order_by(TradeORM.entry_time.asc())
        .all()
    )

    trades = [_serialize_trade(r) for r in rows]

    task_payload = {
        "trades": trades,
        "style": payload.style,
        "analysis_type": payload.analysis_type,
        "trade_id": payload.trade_id,
    }

    if AGENT_MODE == "inline":
        from analysis.engine import analyze
        from data_service.service import enrich_trades
        enriched = enrich_trades(trades)
        result = analyze(
            enriched,
            style=payload.style,
            analysis_type=payload.analysis_type,
            trade_id=payload.trade_id,
        )
        return {"success": True, "result": result}

    task_id = str(uuid.uuid4())
    if async_mode and REDIS_URL:
        task = AgentTask(task_id=task_id, user_id=user_id, agent_type="analyzer", payload=task_payload)
        enqueue(REDIS_URL, QUEUE_NAME, task)
        return {"task_id": task_id, "status": "queued"}
    result = executor.spawn("analyzer", user_id, task_payload, task_id=task_id)
    return result


@router.post("/reporter/run")
def run_reporter(
    payload: ReporterPayload,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Run Reporter agent directly."""
    task_payload = {
        "report_type": payload.report_type,
        "analysis_data": payload.analysis_data,
        "date_from": payload.date_from,
        "date_to": payload.date_to,
    }
    return _run_agent("reporter", user_id, task_payload)


@router.get("/tasks/{task_id}")
def get_agent_result(
    task_id: str,
    user_id: str = Depends(get_current_user),
):
    """Poll for async task result."""
    if not REDIS_URL:
        raise HTTPException(503, "Async results not available")
    data = get_result(REDIS_URL, RESULT_PREFIX + task_id)
    if not data:
        raise HTTPException(404, "Task not found or expired")
    return data


def _run_agent(agent_type: str, user_id: str, payload: dict) -> dict:
    """Run an agent either inline or in Docker sandbox based on config."""
    if AGENT_MODE == "inline":
        return executor.spawn_inline(agent_type, user_id, payload)
    task_id = str(uuid.uuid4())
    return executor.spawn(agent_type, user_id, payload, task_id=task_id)


def _serialize_trade(r: TradeORM) -> dict:
    return {
        "id": r.id,
        "symbol": r.symbol,
        "name": r.name,
        "market": r.market,
        "direction": r.direction,
        "status": r.status,
        "entry_time": r.entry_time.isoformat() if r.entry_time else None,
        "entry_price": r.entry_price,
        "exit_time": r.exit_time.isoformat() if r.exit_time else None,
        "exit_price": r.exit_price,
        "position_pct": r.position_pct,
        "stop_loss": r.stop_loss,
        "pnl_cny": r.pnl_cny,
        "entry_reason": r.entry_reason,
        "notes": r.notes,
        "emotion_tags": loads(r.emotion_tags_json),
        "rule_flags": loads(r.rule_flags_json),
        "tags": loads(r.tags_json),
    }
