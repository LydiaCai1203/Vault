"""Agent 相关请求/响应数据结构（chat、recorder、analyzer、reporter）。"""

from __future__ import annotations

from pydantic import BaseModel, Field


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
