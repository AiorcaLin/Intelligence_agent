"""arXiv 论文搜索工具。"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Any

import httpx

logger = logging.getLogger(__name__)

ARXIV_API = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}


async def fetch_arxiv(query: str, max_results: int = 20) -> list[dict[str, Any]]:
    """搜索 arXiv 论文，返回结构化结果列表。"""
    try:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(ARXIV_API, params=params)
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        results: list[dict[str, Any]] = []

        for entry in root.findall("atom:entry", NS):
            title_el = entry.find("atom:title", NS)
            summary_el = entry.find("atom:summary", NS)
            published_el = entry.find("atom:published", NS)
            link_el = entry.find("atom:id", NS)

            authors: list[str] = []
            for author_el in entry.findall("atom:author", NS):
                name_el = author_el.find("atom:name", NS)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())

            results.append({
                "title": (title_el.text or "").strip() if title_el is not None else "",
                "summary": (summary_el.text or "").strip() if summary_el is not None else "",
                "authors": authors,
                "url": (link_el.text or "").strip() if link_el is not None else "",
                "published_date": (published_el.text or "").strip() if published_el is not None else "",
            })

        return results

    except Exception as exc:
        logger.error("arXiv 查询失败 (%s): %s", query, exc)
        return []
