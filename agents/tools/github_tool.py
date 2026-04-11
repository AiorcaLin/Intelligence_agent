"""GitHub Trending 数据抓取工具。"""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GITHUB_TRENDING_URL = "https://github.com/trending"


async def fetch_github_trending(
    language: str = "python", since: str = "daily"
) -> list[dict[str, Any]]:
    """抓取 GitHub Trending 页面，解析热门仓库列表。"""
    try:
        url = f"{GITHUB_TRENDING_URL}/{language}" if language else GITHUB_TRENDING_URL
        params = {"since": since}

        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(
                url,
                params=params,
                headers={"User-Agent": "IntelAgent/0.1"},
            )
            resp.raise_for_status()

        return _parse_trending_html(resp.text)

    except Exception as exc:
        logger.error("GitHub Trending 抓取失败: %s", exc)
        return []


def _parse_trending_html(html: str) -> list[dict[str, Any]]:
    """从 Trending 页面 HTML 中提取仓库信息（轻量正则方式）。"""
    results: list[dict[str, Any]] = []

    repo_blocks = re.findall(
        r'<article class="Box-row">(.*?)</article>', html, re.DOTALL
    )

    for block in repo_blocks:
        name_match = re.search(r'href="/([^"]+)"', block)
        if not name_match:
            continue
        repo_path = name_match.group(1).strip().strip("/")

        desc_match = re.search(r'<p class="[^"]*">(.*?)</p>', block, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        description = re.sub(r"<[^>]+>", "", description).strip()

        stars_match = re.search(
            r'href="/[^"]+/stargazers"[^>]*>\s*([\d,]+)', block, re.DOTALL
        )
        stars = int(stars_match.group(1).replace(",", "")) if stars_match else 0

        lang_match = re.search(
            r'<span itemprop="programmingLanguage">(.*?)</span>', block
        )
        lang = lang_match.group(1).strip() if lang_match else ""

        today_match = re.search(r'([\d,]+)\s+stars\s+today', block)
        stars_today = int(today_match.group(1).replace(",", "")) if today_match else 0

        results.append({
            "name": repo_path,
            "description": description,
            "url": f"https://github.com/{repo_path}",
            "stars": stars,
            "language": lang,
            "stars_today": stars_today,
        })

    return results
