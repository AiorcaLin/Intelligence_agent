"""Orchestrator — 情报生成编排器。

负责模型路由、成本追踪、质量控制，并对外提供统一入口。
"""

from __future__ import annotations

import logging
import os
import random
import time
from typing import Any

from agents.graph import run_intel_pipeline, IntelState
from agents.evolution import evaluate_template

logger = logging.getLogger(__name__)

# 模型路由配置：80% DeepSeek，20% Claude（用于复杂分析）
MODEL_ROUTING = {
    "deepseek": {
        "model": "deepseek/deepseek-chat",
        "weight": 0.80,
        "cost_per_1k_input": 0.0014,
        "cost_per_1k_output": 0.0028,
    },
    "claude": {
        "model": "anthropic/claude-3-5-sonnet-20241022",
        "weight": 0.20,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
    },
}


def select_model(task_complexity: str = "normal") -> str:
    """根据任务复杂度和权重概率选择模型。"""
    if task_complexity == "complex":
        return MODEL_ROUTING["claude"]["model"]

    roll = random.random()
    if roll < MODEL_ROUTING["deepseek"]["weight"]:
        return MODEL_ROUTING["deepseek"]["model"]
    return MODEL_ROUTING["claude"]["model"]


def _calculate_cost(cost_tracking: dict[str, Any]) -> dict[str, Any]:
    """根据 token 用量计算实际费用。"""
    models = cost_tracking.get("models", {})
    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    breakdown: dict[str, Any] = {}

    for model_name, usage in models.items():
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        routing_info = None
        for _, info in MODEL_ROUTING.items():
            if info["model"] == model_name:
                routing_info = info
                break

        if routing_info:
            cost = (
                input_tokens / 1000 * routing_info["cost_per_1k_input"]
                + output_tokens / 1000 * routing_info["cost_per_1k_output"]
            )
        else:
            cost = (input_tokens + output_tokens) / 1000 * 0.002

        total_cost += cost
        breakdown[model_name] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
        }

    return {
        "total_cost_usd": round(total_cost, 6),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "breakdown": breakdown,
    }


async def generate_report(
    subscription_config: dict[str, Any],
    user_id: str,
) -> dict[str, Any]:
    """生成情报报告的统一入口。

    Args:
        subscription_config: 订阅配置，含 domain / density / template_config
        user_id: 用户 ID

    Returns:
        {report_items, action_items, sources, cost_breakdown, tokens_consumed}
    """
    start_time = time.time()

    model = select_model(
        task_complexity=subscription_config.get("complexity", "normal")
    )
    os.environ["DEFAULT_LLM_MODEL"] = model
    os.environ["SUMMARIZE_MODEL"] = model
    os.environ["ACTION_MODEL"] = model

    density = subscription_config.get("density", "standard")
    if density == "research":
        os.environ["SUMMARIZE_MODEL"] = MODEL_ROUTING["claude"]["model"]

    logger.info(
        "Orchestrator 启动: user=%s, domain=%s, model=%s",
        user_id, subscription_config.get("domain", "ai"), model,
    )

    try:
        final_state: IntelState = await run_intel_pipeline(subscription_config, user_id)
    except Exception as exc:
        logger.error("管线执行失败: %s", exc)
        return {
            "report_items": [],
            "action_items": [],
            "sources": [],
            "cost_breakdown": {},
            "tokens_consumed": 0,
            "error": str(exc),
        }

    cost_tracking = final_state.get("cost_tracking", {})
    cost_breakdown = _calculate_cost(cost_tracking)

    # Evolution 追踪
    template_id = subscription_config.get("template_id", "default")
    quality_scores = final_state.get("quality_scores", [])
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    await evaluate_template(template_id, avg_quality)

    elapsed = time.time() - start_time
    logger.info(
        "Orchestrator 完成: %.1fs, items=%d, cost=$%.4f",
        elapsed, len(final_state.get("report_items", [])), cost_breakdown["total_cost_usd"],
    )

    return {
        "report_items": final_state.get("report_items", []),
        "action_items": final_state.get("action_items", []),
        "sources": final_state.get("sources", []),
        "cost_breakdown": cost_breakdown,
        "tokens_consumed": cost_breakdown["total_input_tokens"] + cost_breakdown["total_output_tokens"],
        "quality_avg": avg_quality,
        "generation_time_seconds": round(elapsed, 2),
    }
