"""Hacker News 热门故事抓取工具。"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

HN_BASE = "https://hacker-news.firebaseio.com/v0"


async def fetch_hackernews(limit: int = 30) -> list[dict[str, Any]]:
    """获取 HN 热门故事列表。"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{HN_BASE}/topstories.json")
            resp.raise_for_status()
            story_ids: list[int] = resp.json()[:limit]

            tasks = [_fetch_story(client, sid) for sid in story_ids]
            stories = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[dict[str, Any]] = []
        for story in stories:
            if isinstance(story, dict):
                results.append(story)
        return results

    except Exception as exc:
        logger.error("HackerNews 抓取失败: %s", exc)
        return []


async def _fetch_story(client: httpx.AsyncClient, story_id: int) -> dict[str, Any]:
    resp = await client.get(f"{HN_BASE}/item/{story_id}.json")
    resp.raise_for_status()
    data = resp.json()
    return {
        "title": data.get("title", ""),
        "url": data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
        "score": data.get("score", 0),
        "author": data.get("by", ""),
        "comments_count": data.get("descendants", 0),
        "time": data.get("time", 0),
    }
