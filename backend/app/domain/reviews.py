"""复盘 (reviews) 相关请求/响应结构。"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ReviewType(str, Enum):
    SINGLE = "SINGLE"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class ReviewScores(BaseModel):
    mind: float = Field(ge=0, le=5)
    method: float = Field(ge=0, le=5)
    money: float = Field(ge=0, le=5)


class Heatmap(BaseModel):
    rows: List[str]
    cols: List[str]
    values: List[List[int]]


class ReviewOut(BaseModel):
    id: str
    type: ReviewType
    range_start: date
    range_end: date
    sample_count: int
    win_rate: float
    rr: float
    expectancy: float
    scores: ReviewScores
    mistakes: List[str]
    todo: List[str]
    heatmap: Heatmap


class GenerateReviewIn(BaseModel):
    type: ReviewType = ReviewType.WEEKLY
    range_start: date
    range_end: date
