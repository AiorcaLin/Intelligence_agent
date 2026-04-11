"""DeFiLlama DeFi 协议与收益数据工具。"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFILLAMA_BASE = "https://api.llama.fi"


async def fetch_defi_protocols(limit: int = 20) -> list[dict[str, Any]]:
    """获取 TVL 排名前 N 的 DeFi 协议。"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{DEFILLAMA_BASE}/protocols")
            resp.raise_for_status()

        protocols: list[dict] = resp.json()
        protocols.sort(key=lambda p: p.get("tvl", 0) or 0, reverse=True)

        results: list[dict[str, Any]] = []
        for proto in protocols[:limit]:
            results.append({
                "name": proto.get("name", ""),
                "symbol": proto.get("symbol", ""),
                "tvl": proto.get("tvl"),
                "chain": proto.get("chain", ""),
                "chains": proto.get("chains", []),
                "category": proto.get("category", ""),
                "change_1d": proto.get("change_1d"),
                "change_7d": proto.get("change_7d"),
                "url": proto.get("url", ""),
            })
        return results

    except Exception as exc:
        logger.error("DeFiLlama 协议查询失败: %s", exc)
        return []


async def fetch_defi_yields() -> list[dict[str, Any]]:
    """获取 DeFiLlama 收益池数据（按 TVL 排序，前 30 条）。"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get("https://yields.llama.fi/pools")
            resp.raise_for_status()

        data = resp.json().get("data", [])
        data.sort(key=lambda p: p.get("tvlUsd", 0) or 0, reverse=True)

        results: list[dict[str, Any]] = []
        for pool in data[:30]:
            results.append({
                "pool_id": pool.get("pool", ""),
                "project": pool.get("project", ""),
                "chain": pool.get("chain", ""),
                "symbol": pool.get("symbol", ""),
                "tvl_usd": pool.get("tvlUsd"),
                "apy": pool.get("apy"),
                "apy_base": pool.get("apyBase"),
                "apy_reward": pool.get("apyReward"),
            })
        return results

    except Exception as exc:
        logger.error("DeFiLlama 收益查询失败: %s", exc)
        return []
