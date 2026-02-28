"""Analyzer sandbox entry - receives trades via stdin, returns analysis JSON.

Not an LLM Agent. Pure code computation routed through the Analysis Engine.
"""

from __future__ import annotations

import json
import os
import sys

from analysis.engine import analyze


def main() -> None:
    user_id = os.environ.get("USER_ID", "")
    task_id = os.environ.get("TASK_ID", "")
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw else {}

    trades = payload.get("trades", [])
    style = payload.get("style", "technical")
    analysis_type = payload.get("analysis_type", "batch")
    trade_id = payload.get("trade_id")
    risk_rules = payload.get("risk_rules")

    result = analyze(
        trades,
        style=style,
        risk_rules=risk_rules,
        analysis_type=analysis_type,
        trade_id=trade_id,
    )
    result["user_id"] = user_id
    result["task_id"] = task_id
    print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
