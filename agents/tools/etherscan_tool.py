"""Etherscan 链上交易数据工具。"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

ETHERSCAN_BASE = "https://api.etherscan.io/api"


async def fetch_latest_transactions(limit: int = 10) -> list[dict[str, Any]]:
    """获取以太坊最新区块的交易列表。"""
    api_key = os.getenv("ETHERSCAN_API_KEY", "")
    if not api_key:
        logger.warning("ETHERSCAN_API_KEY 未设置，跳过 Etherscan 数据采集")
        return []

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            block_resp = await client.get(ETHERSCAN_BASE, params={
                "module": "proxy",
                "action": "eth_blockNumber",
                "apikey": api_key,
            })
            block_resp.raise_for_status()
            latest_block = block_resp.json().get("result", "0x0")

            tx_resp = await client.get(ETHERSCAN_BASE, params={
                "module": "proxy",
                "action": "eth_getBlockByNumber",
                "tag": latest_block,
                "boolean": "true",
                "apikey": api_key,
            })
            tx_resp.raise_for_status()

        block_data = tx_resp.json().get("result", {})
        transactions = block_data.get("transactions", [])

        # 按 value 降序排列，取金额最大的交易
        transactions.sort(
            key=lambda tx: int(tx.get("value", "0x0"), 16), reverse=True
        )

        results: list[dict[str, Any]] = []
        for tx in transactions[:limit]:
            value_wei = int(tx.get("value", "0x0"), 16)
            value_eth = value_wei / 1e18
            results.append({
                "hash": tx.get("hash", ""),
                "from": tx.get("from", ""),
                "to": tx.get("to", ""),
                "value_eth": round(value_eth, 6),
                "gas_price_gwei": round(int(tx.get("gasPrice", "0x0"), 16) / 1e9, 2),
                "block_number": int(latest_block, 16),
            })

        return results

    except Exception as exc:
        logger.error("Etherscan 查询失败: %s", exc)
        return []
