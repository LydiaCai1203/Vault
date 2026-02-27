"""Analyzer prompts - used only for style interpretation (optional LLM layer).

The Analyzer Hub and Base Analyzer are pure code. LLM is only used
for interpreting patterns in Style Analyzers when deeper diagnosis is needed.
"""

STYLE_INTERPRET_PROMPT = """\
你是一个交易行为分析师。基于以下统计指标，给出简洁的中文诊断。

要求：
1. 只描述数据反映的行为模式，不做市场预测
2. 每条诊断不超过 2 句话
3. 区分「做得好的」和「需要改进的」
4. 改进建议必须具体可执行

指标数据：
{metrics_json}
"""
