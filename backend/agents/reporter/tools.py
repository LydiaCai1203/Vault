"""Reporter Agent tools - fetch analysis data and previous reports."""

from __future__ import annotations

from ..tools.get_analysis_result import GET_ANALYSIS_RESULT
from ..tools.get_previous_report import GET_PREVIOUS_REPORT

REPORTER_TOOLS = [
    GET_PREVIOUS_REPORT,
    GET_ANALYSIS_RESULT,
]
