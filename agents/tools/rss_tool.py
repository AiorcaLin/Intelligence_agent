"""通用 RSS 订阅源解析工具。"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)


async def fetch_rss(url: str, limit: int = 20) -> list[dict[str, Any]]:
    """抓取并解析 RSS 订阅源，返回标准化条目列表。"""
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "IntelAgent/0.1"})
            resp.raise_for_status()

        root = ET.fromstring(resp.text)

        ns = {}
        if root.tag.startswith("{"):
            ns_uri = root.tag.split("}")[0].lstrip("{")
            ns["atom"] = ns_uri

        items: list[dict[str, Any]] = []

        # RSS 2.0 格式
        for item in root.iter("item"):
            entry = _parse_rss_item(item)
            items.append(entry)
            if len(items) >= limit:
                break

        # Atom 格式
        if not items:
            tag_prefix = f"{{{ns.get('atom', '')}}}" if ns else ""
            for entry_el in root.iter(f"{tag_prefix}entry"):
                entry = _parse_atom_entry(entry_el, tag_prefix)
                items.append(entry)
                if len(items) >= limit:
                    break

        return items

    except Exception as exc:
        logger.error("RSS 抓取失败 (%s): %s", url, exc)
        return []


def _parse_rss_item(item: ET.Element) -> dict[str, Any]:
    title = _text(item, "title")
    description = _text(item, "description")
    link = _text(item, "link")
    pub_date = _text(item, "pubDate")
    source = _text(item, "source") or _attr(item, "source", "url") or ""
    return {
        "title": title,
        "summary": description,
        "url": link,
        "published_date": pub_date,
        "source": source,
    }


def _parse_atom_entry(entry: ET.Element, prefix: str) -> dict[str, Any]:
    title = _text(entry, f"{prefix}title")
    summary = _text(entry, f"{prefix}summary") or _text(entry, f"{prefix}content")
    link_el = entry.find(f"{prefix}link")
    link = link_el.get("href", "") if link_el is not None else ""
    updated = _text(entry, f"{prefix}updated") or _text(entry, f"{prefix}published")
    return {
        "title": title,
        "summary": summary,
        "url": link,
        "published_date": updated,
        "source": "",
    }


def _text(parent: ET.Element, tag: str) -> str:
    el = parent.find(tag)
    return (el.text or "").strip() if el is not None else ""


def _attr(parent: ET.Element, tag: str, attr: str) -> str:
    el = parent.find(tag)
    return el.get(attr, "") if el is not None else ""
