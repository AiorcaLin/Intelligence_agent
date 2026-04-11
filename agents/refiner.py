"""Refiner Agent — 内容改进与优化。"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from litellm import acompletion

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("REFINER_MODEL", "deepseek/deepseek-chat")


async def refine(state: dict[str, Any]) -> dict[str, Any]:
    """对未通过质量评估的条目进行 LLM 改写优化。"""
    rejected = state.get("refined_data", [])
    iteration = state.get("iteration_count", 0)
    cost_tracking = dict(state.get("cost_tracking", {}))

    if not rejected:
        return {"refined_data": [], "iteration_count": iteration + 1}

    items_text = "\n\n".join(
        f"【条目 {i+1}】\n"
        f"标题: {item.get('title', '无标题')}\n"
        f"内容: {item.get('content', '无内容')[:400]}\n"
        f"来源: {item.get('source_name', '未知')}\n"
        f"质量分数: {item.get('quality_score', 'N/A')}"
        for i, item in enumerate(rejected)
    )

    prompt = (
        "你是一位专业的情报编辑。以下条目未通过质量评估，请逐条改进：\n\n"
        "改进要求：\n"
        "1. 补充缺失的标题或内容\n"
        "2. 提升表达清晰度和专业性\n"
        "3. 去除冗余信息，保留核心要点\n"
        "4. 添加必要的上下文说明\n\n"
        f"待改进条目:\n{items_text}\n\n"
        "请以 JSON 数组格式输出改进后的条目，每条包含字段: title, content, source_name, source_url。\n"
        "直接输出 JSON，不要添加其他内容。"
    )

    model = os.getenv("REFINER_MODEL", DEFAULT_MODEL)

    try:
        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = response.choices[0].message.content.strip()

        usage = response.usage
        cost_tracking.setdefault("models", {})
        model_stats = cost_tracking["models"].setdefault(model, {"input_tokens": 0, "output_tokens": 0})
        model_stats["input_tokens"] += getattr(usage, "prompt_tokens", 0)
        model_stats["output_tokens"] += getattr(usage, "completion_tokens", 0)

        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0]

        refined_items = json.loads(content)
        if not isinstance(refined_items, list):
            refined_items = [refined_items]

        for original, refined in zip(rejected, refined_items):
            refined.setdefault("source_url", original.get("source_url", ""))
            refined.setdefault("source_name", original.get("source_name", ""))
            refined["fetched_at"] = original.get("fetched_at")
            refined["relevance_hint"] = original.get("relevance_hint", 0.5)

    except Exception as exc:
        logger.error("Refiner 改写失败: %s", exc)
        refined_items = rejected

    return {
        "refined_data": refined_items,
        "iteration_count": iteration + 1,
        "cost_tracking": cost_tracking,
    }
