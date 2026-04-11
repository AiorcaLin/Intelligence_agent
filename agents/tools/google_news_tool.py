"""Google News RSS 新闻抓取工具。"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

from agents.tools.rss_tool import fetch_rss

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"


async def fetch_google_news(
    query: str = "artificial intelligence",
    lang: str = "zh-CN",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """通过 Google News RSS 搜索新闻。"""
    try:
        hl = lang
        gl = lang.split("-")[-1] if "-" in lang else "CN"
        url = f"{GOOGLE_NEWS_RSS}?q={quote(query)}&hl={hl}&gl={gl}&ceid={gl}:{hl}"

        items = await fetch_rss(url, limit=limit)

        for item in items:
            item["source"] = item.get("source") or "Google News"

        return items

    except Exception as exc:
        logger.error("Google News 查询失败 (%s): %s", query, exc)
        return []
