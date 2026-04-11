"""LangGraph 工作流定义 — GTRME 情报生成管线。"""

from __future__ import annotations

import logging
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from agents import generator, tester, refiner, memory

logger = logging.getLogger(__name__)

MAX_REFINE_ITERATIONS = 2
QUALITY_THRESHOLD = 6.0


class IntelState(TypedDict, total=False):
    subscription_config: dict
    user_id: str
    domain: str
    density_level: str              # quick_scan | standard | research
    template_config: dict
    raw_data: list[dict]
    filtered_data: list[dict]
    refined_data: list[dict]
    report_items: list[dict]
    action_items: list[dict]
    sources: list[dict]
    quality_scores: list[float]
    cost_tracking: dict
    error: str | None
    iteration_count: int


# ---------------------------------------------------------------------------
# Node wrappers — 每个节点接收完整 state，返回部分更新
# ---------------------------------------------------------------------------

async def _collect_node(state: IntelState) -> dict[str, Any]:
    try:
        return await generator.collect(state)
    except Exception as exc:
        logger.error("collect 节点异常: %s", exc)
        return {"raw_data": [], "error": str(exc)}


async def _test_node(state: IntelState) -> dict[str, Any]:
    try:
        return await tester.evaluate(state)
    except Exception as exc:
        logger.error("test 节点异常: %s", exc)
        return {"filtered_data": state.get("raw_data", []), "quality_scores": [], "error": str(exc)}


async def _refine_node(state: IntelState) -> dict[str, Any]:
    try:
        return await refiner.refine(state)
    except Exception as exc:
        logger.error("refine 节点异常: %s", exc)
        return {"iteration_count": state.get("iteration_count", 0) + 1, "error": str(exc)}


async def _summarize_node(state: IntelState) -> dict[str, Any]:
    try:
        return await generator.summarize(state)
    except Exception as exc:
        logger.error("summarize 节点异常: %s", exc)
        return {"report_items": [], "error": str(exc)}


async def _action_node(state: IntelState) -> dict[str, Any]:
    try:
        return await generator.add_action_items(state)
    except Exception as exc:
        logger.error("add_actions 节点异常: %s", exc)
        return {"action_items": [], "error": str(exc)}


async def _memory_node(state: IntelState) -> dict[str, Any]:
    try:
        return await memory.update(state)
    except Exception as exc:
        logger.warning("memory_update 节点异常: %s", exc)
        return {}


# ---------------------------------------------------------------------------
# 条件路由
# ---------------------------------------------------------------------------

def _should_refine(state: IntelState) -> str:
    """判断是否需要精炼：所有分数 >= 阈值则跳过，否则看迭代次数。"""
    scores = state.get("quality_scores", [])
    iteration = state.get("iteration_count", 0)

    if not scores or all(s >= QUALITY_THRESHOLD for s in scores):
        return "summarize"

    if iteration >= MAX_REFINE_ITERATIONS:
        logger.info("已达最大精炼次数 (%d)，跳过进入摘要", MAX_REFINE_ITERATIONS)
        return "summarize"

    return "refine"


# ---------------------------------------------------------------------------
# 构建 Graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    """构建并编译 GTRME 工作流图。"""
    workflow = StateGraph(IntelState)

    workflow.add_node("collect", _collect_node)
    workflow.add_node("test", _test_node)
    workflow.add_node("refine", _refine_node)
    workflow.add_node("summarize", _summarize_node)
    workflow.add_node("add_actions", _action_node)
    workflow.add_node("memory_update", _memory_node)

    workflow.set_entry_point("collect")
    workflow.add_edge("collect", "test")

    workflow.add_conditional_edges(
        "test",
        _should_refine,
        {"summarize": "summarize", "refine": "refine"},
    )

    workflow.add_edge("refine", "test")
    workflow.add_edge("summarize", "add_actions")
    workflow.add_edge("add_actions", "memory_update")
    workflow.add_edge("memory_update", END)

    return workflow


_compiled_graph = None


def get_compiled_graph():
    """获取已编译的工作流图（单例）。"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph().compile()
    return _compiled_graph


# ---------------------------------------------------------------------------
# 入口函数
# ---------------------------------------------------------------------------

async def run_intel_pipeline(
    subscription_config: dict[str, Any],
    user_id: str,
) -> IntelState:
    """执行完整的情报生成管线。

    Args:
        subscription_config: 包含 domain, density, template 等配置
        user_id: 用户标识

    Returns:
        完整的 IntelState，包含 report_items, action_items, sources 等
    """
    initial_state: IntelState = {
        "subscription_config": subscription_config,
        "user_id": user_id,
        "domain": subscription_config.get("domain", "ai"),
        "density_level": subscription_config.get("density", "standard"),
        "template_config": subscription_config.get("template_config", {}),
        "raw_data": [],
        "filtered_data": [],
        "refined_data": [],
        "report_items": [],
        "action_items": [],
        "sources": [],
        "quality_scores": [],
        "cost_tracking": {"models": {}},
        "error": None,
        "iteration_count": 0,
    }

    graph = get_compiled_graph()

    logger.info(
        "启动情报管线: user=%s, domain=%s, density=%s",
        user_id, initial_state["domain"], initial_state["density_level"],
    )

    final_state = await graph.ainvoke(initial_state)
    return final_state
