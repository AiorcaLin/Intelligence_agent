"""Tester Agent — 质量评估与过滤。"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from difflib import SequenceMatcher
from typing import Any

logger = logging.getLogger(__name__)

MAX_AGE_HOURS = 48
QUALITY_THRESHOLD = 6.0

_recent_hashes: dict[str, float] = {}


async def evaluate(state: dict[str, Any]) -> dict[str, Any]:
    """对原始/精炼数据执行多维质量评估。"""
    data = state.get("refined_data") or state.get("raw_data", [])

    filtered: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    scores: list[float] = []

    for item in data:
        score = _score_item(item, data)
        scores.append(score)

        if score >= QUALITY_THRESHOLD:
            item["quality_score"] = score
            filtered.append(item)
        else:
            item["quality_score"] = score
            rejected.append(item)

    logger.info(
        "Tester 评估完成: %d/%d 通过 (阈值=%.1f)",
        len(filtered), len(data), QUALITY_THRESHOLD,
    )

    return {
        "filtered_data": filtered,
        "refined_data": rejected,
        "quality_scores": scores,
    }


def _score_item(item: dict[str, Any], all_items: list[dict[str, Any]]) -> float:
    """综合评分：内容质量 + 去重 + 时效 + 合规。"""
    score = 10.0

    # --- 内容质量 ---
    title = item.get("title", "")
    content = item.get("content", "")

    if not title:
        score -= 3.0
    if not content or len(content) < 20:
        score -= 2.0
    elif len(content) < 50:
        score -= 1.0

    if not item.get("source_url"):
        score -= 1.0

    # --- 去重 ---
    text_hash = _content_hash(title, content)
    now = time.time()

    if text_hash in _recent_hashes:
        if now - _recent_hashes[text_hash] < MAX_AGE_HOURS * 3600:
            score -= 4.0
    _recent_hashes[text_hash] = now

    for other in all_items:
        if other is item:
            continue
        other_title = other.get("title", "")
        if title and other_title and _similarity(title, other_title) > 0.85:
            score -= 2.0
            break

    # --- 时效性 ---
    fetched_at = item.get("fetched_at")
    if fetched_at and isinstance(fetched_at, (int, float)):
        age_hours = (now - fetched_at) / 3600
        if age_hours > MAX_AGE_HOURS:
            score -= 2.0
        elif age_hours > MAX_AGE_HOURS / 2:
            score -= 1.0

    # --- 中文内容合规 ---
    compliance_penalty = _check_compliance(title + " " + content)
    score -= compliance_penalty

    return max(0.0, min(10.0, score))


def _content_hash(title: str, content: str) -> str:
    text = (title + content).strip().lower()
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


_BLOCKED_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"赌博|博彩|色情|暴力恐怖",
        r"翻墙|VPN.*(免费|推荐)",
        r"代孕|枪支|毒品",
    ]
]


def _check_compliance(text: str) -> float:
    """基础中文内容合规过滤，返回扣分值。"""
    penalty = 0.0
    for pattern in _BLOCKED_PATTERNS:
        if pattern.search(text):
            penalty += 5.0
            break
    return penalty
