"""CoinGecko 加密货币市场数据工具。"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

CG_BASE = "https://api.coingecko.com/api/v3"


async def fetch_coingecko_trending() -> list[dict[str, Any]]:
    """获取 CoinGecko 热门币种。"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{CG_BASE}/search/trending")
            resp.raise_for_status()

        data = resp.json()
        results: list[dict[str, Any]] = []
        for coin_wrapper in data.get("coins", []):
            coin = coin_wrapper.get("item", {})
            results.append({
                "id": coin.get("id", ""),
                "name": coin.get("name", ""),
                "symbol": coin.get("symbol", ""),
                "market_cap_rank": coin.get("market_cap_rank"),
                "thumb": coin.get("thumb", ""),
                "score": coin.get("score", 0),
            })
        return results

    except Exception as exc:
        logger.error("CoinGecko Trending 查询失败: %s", exc)
        return []


async def fetch_coingecko_market(limit: int = 20) -> list[dict[str, Any]]:
    """获取 CoinGecko 市值排名前 N 的币种市场数据。"""
    try:
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h,7d",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{CG_BASE}/coins/markets", params=params)
            resp.raise_for_status()

        raw: list[dict] = resp.json()
        results: list[dict[str, Any]] = []
        for coin in raw:
            results.append({
                "id": coin.get("id", ""),
                "name": coin.get("name", ""),
                "symbol": coin.get("symbol", ""),
                "current_price": coin.get("current_price"),
                "market_cap": coin.get("market_cap"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "total_volume": coin.get("total_volume"),
                "price_change_24h": coin.get("price_change_percentage_24h"),
                "price_change_7d": coin.get("price_change_percentage_7d_in_currency"),
            })
        return results

    except Exception as exc:
        logger.error("CoinGecko Market 查询失败: %s", exc)
        return []
