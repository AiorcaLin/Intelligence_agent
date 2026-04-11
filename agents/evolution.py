"""Evolution Agent — 模板/配方优化追踪。"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

EVOLUTION_DIR = Path(os.getenv("EVOLUTION_DIR", "data/evolution"))


async def evaluate_template(template_id: str, report_quality: float) -> dict[str, Any]:
    """追踪模板表现，为未来自动优化积累数据。"""
    record = {
        "template_id": template_id,
        "report_quality": report_quality,
        "timestamp": time.time(),
    }

    try:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        log_path = EVOLUTION_DIR / f"template_{template_id}.jsonl"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        history = _load_template_history(template_id)
        avg_quality = sum(r["report_quality"] for r in history) / len(history) if history else 0

        logger.info(
            "Evolution 记录: template=%s, quality=%.2f, avg=%.2f, runs=%d",
            template_id, report_quality, avg_quality, len(history),
        )

        return {
            "template_id": template_id,
            "current_quality": report_quality,
            "avg_quality": avg_quality,
            "total_runs": len(history),
            "trend": "improving" if report_quality > avg_quality else "declining",
        }

    except Exception as exc:
        logger.warning("Evolution 记录失败: %s", exc)
        return {"template_id": template_id, "error": str(exc)}


def _load_template_history(template_id: str) -> list[dict[str, Any]]:
    log_path = EVOLUTION_DIR / f"template_{template_id}.jsonl"
    if not log_path.exists():
        return []

    records: list[dict[str, Any]] = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records
