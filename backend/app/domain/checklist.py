"""待办清单 (checklist) 相关请求/响应结构。"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class ChecklistItem(BaseModel):
    id: str
    text: str
    done: bool = False


class ChecklistOut(BaseModel):
    items: List[ChecklistItem]
