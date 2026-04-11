"""Memory Agent — 用户偏好学习与记忆。"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MEMORY_DIR = Path(os.getenv("MEMORY_DIR", "data/memory"))


async def update(state: dict[str, Any]) -> dict[str, Any]:
    """记录本次生成的质量指标与成功模式。"""
    user_id = state.get("user_id", "anonymous")
    domain = state.get("domain", "unknown")
    quality_scores = state.get("quality_scores", [])
    report_items = state.get("report_items", [])
    cost_tracking = state.get("cost_tracking", {})

    record = {
        "timestamp": time.time(),
        "user_id": user_id,
        "domain": domain,
        "items_generated": len(report_items),
        "avg_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
        "max_quality": max(quality_scores) if quality_scores else 0,
        "min_quality": min(quality_scores) if quality_scores else 0,
        "cost_summary": cost_tracking,
    }

    try:
        user_dir = MEMORY_DIR / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        log_path = user_dir / "generation_log.jsonl"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info("Memory 记录已保存: user=%s, domain=%s", user_id, domain)

    except Exception as exc:
        logger.warning("Memory 记录保存失败: %s", exc)

    return {}


async def get_user_preferences(user_id: str) -> dict[str, Any]:
    """获取用户偏好数据（MVP 阶段返回默认值）。"""
    prefs_path = MEMORY_DIR / user_id / "preferences.json"

    if prefs_path.exists():
        try:
            with open(prefs_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.warning("读取用户偏好失败 (%s): %s", user_id, exc)

    return {
        "preferred_density": "standard",
        "preferred_domains": ["ai", "tech"],
        "language": "zh-CN",
        "min_quality_threshold": 6.0,
    }
