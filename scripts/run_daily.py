"""
每日情报生成手动触发脚本 - 用于测试完整的情报生成流水线。

用法：
  python -m scripts.run_daily --domain AI --density standard
  python -m scripts.run_daily --domain Crypto --density quick_scan
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_daily(domain: str, density: str) -> dict:
    """运行指定领域的完整情报生成流水线。

    Args:
        domain: 目标领域（AI / Crypto）。
        density: 密度级别（quick_scan / standard / research）。

    Returns:
        包含报告条目和成本明细的结果字典。
    """
    try:
        from agents.orchestrator import Orchestrator
    except ImportError as e:
        logger.error("Failed to import Orchestrator: %s", e)
        logger.error("Make sure agents/orchestrator.py exists.")
        sys.exit(1)

    config = {
        "domain": domain,
        "density_level": density,
        "template_config": None,
    }

    logger.info("Starting daily report generation: domain=%s, density=%s", domain, density)

    try:
        orchestrator = Orchestrator()
        result = await orchestrator.generate_report(config, user_id="system")

        items_count = len(result.get("report_items", []))
        cost = result.get("cost_breakdown", {})

        logger.info("Generated report with %d items", items_count)
        logger.info("Cost breakdown: %s", cost)

        return result

    except Exception as e:
        logger.error("Report generation failed: %s", e)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="手动触发每日情报生成")
    parser.add_argument(
        "--domain",
        default="AI",
        choices=["AI", "Crypto"],
        help="目标领域 (default: AI)",
    )
    parser.add_argument(
        "--density",
        default="standard",
        choices=["quick_scan", "standard", "research"],
        help="密度级别 (default: standard)",
    )
    args = parser.parse_args()

    asyncio.run(run_daily(args.domain, args.density))
