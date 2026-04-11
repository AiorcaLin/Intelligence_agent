"""Generator Agent — 数据采集与摘要生成。"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any

from litellm import acompletion

from agents.tools.arxiv_tool import fetch_arxiv
from agents.tools.github_tool import fetch_github_trending
from agents.tools.hackernews_tool import fetch_hackernews
from agents.tools.coingecko_tool import fetch_coingecko_trending, fetch_coingecko_market
from agents.tools.defi_llama_tool import fetch_defi_protocols, fetch_defi_yields
from agents.tools.etherscan_tool import fetch_latest_transactions
from agents.tools.rss_tool import fetch_rss
from agents.tools.google_news_tool import fetch_google_news

logger = logging.getLogger(__name__)

DOMAIN_SOURCE_MAP: dict[str, list[dict[str, Any]]] = {
    "ai": [
        {"fn": fetch_arxiv, "kwargs": {"query": "artificial intelligence"}, "weight": 1.0},
        {"fn": fetch_github_trending, "kwargs": {"language": "python"}, "weight": 0.8},
        {"fn": fetch_hackernews, "kwargs": {"limit": 30}, "weight": 0.7},
        {"fn": fetch_google_news, "kwargs": {"query": "AI 人工智能"}, "weight": 0.9},
    ],
    "crypto": [
        {"fn": fetch_coingecko_trending, "kwargs": {}, "weight": 1.0},
        {"fn": fetch_coingecko_market, "kwargs": {"limit": 20}, "weight": 0.9},
        {"fn": fetch_defi_protocols, "kwargs": {"limit": 20}, "weight": 0.8},
        {"fn": fetch_defi_yields, "kwargs": {}, "weight": 0.7},
        {"fn": fetch_latest_transactions, "kwargs": {"limit": 10}, "weight": 0.6},
    ],
    "tech": [
        {"fn": fetch_hackernews, "kwargs": {"limit": 30}, "weight": 1.0},
        {"fn": fetch_github_trending, "kwargs": {"language": ""}, "weight": 0.9},
        {"fn": fetch_google_news, "kwargs": {"query": "technology"}, "weight": 0.8},
        {"fn": fetch_arxiv, "kwargs": {"query": "computer science"}, "weight": 0.6},
    ],
}

DENSITY_CONFIG = {
    "quick_scan": {"target_items": 10, "style": "标题 + 一句话摘要"},
    "standard": {"target_items": 6, "style": "详细分析 + 来源引用"},
    "research": {"target_items": 3, "style": "深度分析 + 历史背景 + 多角度解读"},
}

DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "deepseek/deepseek-chat")


async def collect(state: dict[str, Any]) -> dict[str, Any]:
    """并行调用数据源，采集原始数据。"""
    domain = state.get("domain", "ai")
    template_config = state.get("template_config", {})

    sources = DOMAIN_SOURCE_MAP.get(domain, DOMAIN_SOURCE_MAP["ai"])

    custom_rss = template_config.get("extra_rss_feeds", [])
    for rss_url in custom_rss:
        sources.append({"fn": fetch_rss, "kwargs": {"url": rss_url}, "weight": 0.5})

    tasks = [src["fn"](**src["kwargs"]) for src in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    raw_data: list[dict[str, Any]] = []
    source_refs: list[dict[str, Any]] = []

    for src_cfg, result in zip(sources, results):
        if isinstance(result, Exception):
            logger.warning("数据源 %s 调用失败: %s", src_cfg["fn"].__name__, result)
            continue
        if not isinstance(result, list):
            continue

        source_name = src_cfg["fn"].__name__
        weight = src_cfg.get("weight", 1.0)
        source_refs.append({"source_name": source_name, "item_count": len(result)})

        for item in result:
            raw_data.append({
                "title": item.get("title") or item.get("name", ""),
                "content": item.get("summary") or item.get("description", ""),
                "source_name": source_name,
                "source_url": item.get("url", ""),
                "fetched_at": time.time(),
                "relevance_hint": weight,
                **{k: v for k, v in item.items() if k not in ("title", "summary", "description", "url")},
            })

    raw_data.sort(key=lambda x: x.get("relevance_hint", 0), reverse=True)

    return {"raw_data": raw_data, "sources": source_refs}


async def summarize(state: dict[str, Any]) -> dict[str, Any]:
    """基于密度级别生成结构化摘要。"""
    density = state.get("density_level", "standard")
    filtered = state.get("filtered_data", [])
    cost_tracking = dict(state.get("cost_tracking", {}))

    cfg = DENSITY_CONFIG.get(density, DENSITY_CONFIG["standard"])
    target = cfg["target_items"]
    style = cfg["style"]

    items_text = "\n\n".join(
        f"【{i+1}】{item.get('title', '无标题')}\n来源: {item.get('source_name', '未知')}\n"
        f"链接: {item.get('source_url', '')}\n内容: {item.get('content', '')[:500]}"
        for i, item in enumerate(filtered[:target * 2])
    )

    prompt = (
        f"你是一位专业的情报分析师。请根据以下原始情报条目，生成 {target} 条结构化情报摘要。\n\n"
        f"输出风格: {style}\n\n"
        f"原始情报:\n{items_text}\n\n"
        f"请以 JSON 数组格式输出，每条包含字段: title, summary, source_name, source_url, importance (1-10)。\n"
        f"直接输出 JSON，不要添加其他内容。"
    )

    model = os.getenv("SUMMARIZE_MODEL", DEFAULT_MODEL)

    try:
        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()

        usage = response.usage
        cost_tracking.setdefault("models", {})
        model_stats = cost_tracking["models"].setdefault(model, {"input_tokens": 0, "output_tokens": 0})
        model_stats["input_tokens"] += getattr(usage, "prompt_tokens", 0)
        model_stats["output_tokens"] += getattr(usage, "completion_tokens", 0)

        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0]

        report_items = json.loads(content)
        if not isinstance(report_items, list):
            report_items = [report_items]

    except Exception as exc:
        logger.error("摘要生成失败: %s", exc)
        report_items = [
            {
                "title": item.get("title", ""),
                "summary": (item.get("content", "") or "")[:200],
                "source_name": item.get("source_name", ""),
                "source_url": item.get("source_url", ""),
                "importance": 5,
            }
            for item in filtered[:target]
        ]

    return {"report_items": report_items, "cost_tracking": cost_tracking}


async def add_action_items(state: dict[str, Any]) -> dict[str, Any]:
    """为每条报告条目生成可操作建议。"""
    report_items = state.get("report_items", [])
    cost_tracking = dict(state.get("cost_tracking", {}))

    items_text = "\n".join(
        f"[{i+1}] {item.get('title', '')}: {item.get('summary', '')[:200]}"
        for i, item in enumerate(report_items)
    )

    prompt = (
        "你是一位专业的情报分析顾问。请根据以下情报条目，为每条生成 1-3 条可操作建议。\n\n"
        f"情报条目:\n{items_text}\n\n"
        "每条建议包含字段:\n"
        '- type: "read"（附带URL阅读原文）、"watch"（关注某人/项目）或 "action"（具体操作步骤）\n'
        "- description: 建议描述\n"
        "- url: 相关链接（仅 read 类型必填）\n"
        "- related_item_index: 关联的情报条目序号（从1开始）\n\n"
        "以 JSON 数组输出，不要添加其他内容。"
    )

    model = os.getenv("ACTION_MODEL", DEFAULT_MODEL)

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

        action_items = json.loads(content)
        if not isinstance(action_items, list):
            action_items = [action_items]

    except Exception as exc:
        logger.error("行动建议生成失败: %s", exc)
        action_items = [
            {
                "type": "read",
                "description": f"阅读原文: {item.get('title', '')}",
                "url": item.get("source_url", ""),
                "related_item_index": i + 1,
            }
            for i, item in enumerate(report_items)
        ]

    return {"action_items": action_items, "cost_tracking": cost_tracking}
