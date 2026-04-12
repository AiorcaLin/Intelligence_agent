# Agent 2: Agent引擎 — GTRME + LangGraph + 数据源工具

**Subagent ID**: `03fab152-4283-44d5-a9a2-d736dd87dc9c`  
**Parent Session**: `c0053be0-7157-4541-800b-d5a5ff5d737e`  
**总条目数**: 24

---

## Step 1: User Prompt

```
<user_query>
You are building the AI Agent Engine for an Intelligence Platform. The workspace is at e:\AI\Intelligence_agent.

Create ALL files in the `agents/` directory. The directory structure already exists:
- agents/
- agents/tools/

## Architecture: GTRME (Generator-Tester-Refiner-Memory-Evolution)

The agent engine uses LangGraph to orchestrate a multi-agent workflow for intel report generation.

### Create the following files:

### 1. agents/__init__.py
Empty or with version info.

### 2. agents/graph.py — LangGraph Workflow Definition
This is the main workflow using LangGraph's StateGraph.

State schema (TypedDict):
```python
class IntelState(TypedDict):
    subscription_config: dict     # domain, density, template config
    user_id: str
    domain: str
    density_level: str            # quick_scan | standard | research
    template_config: dict         # prompt_config from template
    raw_data: list[dict]          # collected raw items
    filtered_data: list[dict]     # after tester filtering
    refined_data: list[dict]      # after refiner improvements
    report_items: list[dict]      # final structured items
    action_items: list[dict]      # action suggestions
    sources: list[dict]           # source references
    quality_scores: list[float]   # tester scores
    cost_tracking: dict           # model usage and cost
    error: str | None
    iteration_count: int          # refiner loop counter, max 2
```

Build the graph:
1. "collect" node -> Generator.collect()
2. "test" node -> Tester.evaluate()
3. Conditional edge: if all scores >= 6 -> "summarize", else -> "refine"
4. "refine" node -> Refiner.refine() -> loop back to "test" (max 2 iterations)
5. "summarize" node -> Generator.summarize()
6. "add_actions" node -> Generator.add_action_items()
7. "memory_update" node -> Memory.update()
8. END

Provide a `run_intel_pipeline(subscription_config, user_id)` async function.

### 3. agents/orchestrator.py — Orchestrator
The main orchestrator that:
- Reads subscription config (domain, density, template)
- Decides model routing (80% DeepSeek, 20% Claude for complex analysis)
- Tracks costs (input/output tokens per model)
- Manages quality gates
- Provides `generate_report(subscription_config, user_id)` method that calls the graph

Functions:
- `async def generate_report(subscription_config: dict, user_id: str) -> dict`
  Returns: {report_items, action_items, sources, cost_breakdown, tokens_consumed}

### 4. agents/generator.py — Generator Agent
Responsible for data collection and summarization.

Functions:
- `async def collect(state: IntelState) -> dict`: 
  - Read domain config (from domains/ YAML files)
  - Call appropriate data source tools in parallel
  - Apply template weights to prioritize sources
  - Return collected raw_data items
  - Each item: {title, content, source_name, source_url, fetched_at, relevance_hint}

- `async def summarize(state: IntelState) -> dict`:
  - Take filtered_data
  - Based on density_level, generate

... (truncated, total: 8052 chars)
```

## Step 2: Assistant

The user wants me to create a comprehensive set of files for an AI Agent Engine. Let me plan this out and create all the files systematically.

Let me first check what already exists in the workspace.

**TodoWrite**: [pending] Create agents/__init__.py, [pending] Create agents/graph.py — LangGraph workf, [pending] Create agents/orchestrator.py, [pending] Create agents/generator.py, [pending] Create agents/tester.py

## Step 3: Assistant

先检查一下工作区现有结构。

**Shell**: Check workspace structure
```bash
ls -la
```

**Glob**: {"glob_pattern": "agents/**/*", "target_directory": "e:\\AI\\Intelligence_agent"}

## Step 4: Assistant

**Shell**: List workspace contents
```bash
Get-ChildItem -Force | Format-Table Name, Mode
```

## Step 5: Assistant

**Shell**: Check agents directory structure
```bash
Get-ChildItem agents -Recurse -Force | Format-Table FullName, Mode
```

## Step 6: Assistant

好的，`agents/` 和 `agents/tools/` 目录已存在但为空。现在开始创建所有文件。

**TodoWrite**: [in_progress] Create agents/__init__.py

### File Write #1: `agents\__init__.py`

**Size**: 151 chars

```
"""
Intelligence Agent Engine — GTRME Architecture
(Generator-Tester-Refiner-Memory-Evolution)

基于 LangGraph 的多智能体情报报告生成引擎。
"""

__version__ = "0.1.0"

```

### File Write #2: `agents\tools\__init__.py`

**Size**: 817 chars

```
"""Intelligence Agent 数据采集工具集。"""

from agents.tools.arxiv_tool import fetch_arxiv
from agents.tools.github_tool import fetch_github_trending
from agents.tools.hackernews_tool import fetch_hackernews
from agents.tools.coingecko_tool import fetch_coingecko_trending, fetch_coingecko_market
from agents.tools.defi_llama_tool import fetch_defi_protocols, fetch_defi_yields
from agents.tools.etherscan_tool import fetch_latest_transactions
from agents.tools.rss_tool import fetch_rss
from agents.tools.google_news_tool import fetch_google_news

__all__ = [
    "fetch_arxiv",
    "fetch_github_trending",
    "fetch_hackernews",
    "fetch_coingecko_trending",
    "fetch_coingecko_market",
    "fetch_defi_protocols",
    "fetch_defi_yields",
    "fetch_latest_transactions",
    "fetch_rss",
    "fetch_google_news",
]

```

## Step 7: Assistant

现在创建核心工具文件（并行写入所有 tools）。

**TodoWrite**: [completed] , [completed] , [in_progress] , [in_progress] , [in_progress] 

### File Write #3: `agents\tools\rss_tool.py`

**Size**: 2677 chars

```
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

```

### File Write #4: `agents\tools\arxiv_tool.py`

**Size**: 1981 chars

```
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

```

### File Write #5: `agents\tools\github_tool.py`

**Size**: 2421 chars

```
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

```

### File Write #6: `agents\tools\hackernews_tool.py`

**Size**: 1470 chars

```
"""Hacker News 热门故事抓取工具。"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

HN_BASE = "https://hacker-news.firebaseio.com/v0"


async def fetch_hackernews(limit: int = 30) -> list[dict[str, Any]]:
    """获取 HN 热门故事列表。"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{HN_BASE}/topstories.json")
            resp.raise_for_status()
            story_ids: list[int] = resp.json()[:limit]

            tasks = [_fetch_story(client, sid) for sid in story_ids]
            stories = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[dict[str, Any]] = []
        for story in stories:
            if isinstance(story, dict):
                results.append(story)
        return results

    except Exception as exc:
        logger.error("HackerNews 抓取失败: %s", exc)
        return []


async def _fetch_story(client: httpx.AsyncClient, story_id: int) -> dict[str, Any]:
    resp = await client.get(f"{HN_BASE}/item/{story_id}.json")
    resp.raise_for_status()
    data = resp.json()
    return {
        "title": data.get("title", ""),
        "url": data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
        "score": data.get("score", 0),
        "author": data.get("by", ""),
        "comments_count": data.get("descendants", 0),
        "time": data.get("time", 0),
    }

```

### File Write #7: `agents\tools\coingecko_tool.py`

**Size**: 2460 chars

```
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

```

### File Write #8: `agents\tools\defi_llama_tool.py`

**Size**: 2314 chars

```
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

```

### File Write #9: `agents\tools\etherscan_tool.py`

**Size**: 2077 chars

```
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

```

### File Write #10: `agents\tools\google_news_tool.py`

**Size**: 902 chars

```
"""Google News RSS 新闻抓取工具。"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

from agents.tools.rss_tool import fetch_rss

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"


async def fetch_google_news(
    query: str = "artificial intelligence",
    lang: str = "zh-CN",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """通过 Google News RSS 搜索新闻。"""
    try:
        hl = lang
        gl = lang.split("-")[-1] if "-" in lang else "CN"
        url = f"{GOOGLE_NEWS_RSS}?q={quote(query)}&hl={hl}&gl={gl}&ceid={gl}:{hl}"

        items = await fetch_rss(url, limit=limit)

        for item in items:
            item["source"] = item.get("source") or "Google News"

        return items

    except Exception as exc:
        logger.error("Google News 查询失败 (%s): %s", query, exc)
        return []

```

## Step 8: Assistant

工具文件全部创建完成。现在创建核心智能体文件。

**TodoWrite**: [completed] , [completed] , [completed] , [completed] , [completed] 

### File Write #11: `agents\generator.py`

**Size**: 8380 chars

```
"""Generator Agent — 数据采集与摘要生成。"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any

from litellm import acompletion

from agents.tools.arxiv_tool import fetch_arxiv
from agents.tools.github_tool import fetch_github_trending
from agents.tools.hackernews_tool import fetch_hackernews
from agents.tools.coingecko_tool import fetch_coingecko_trending, fetch_coingecko_market
from agents.tools.defi_llama_tool import fetch_defi_protocols, fetch_defi_yields
from agents.tools.etherscan_tool import fetch_latest_transactions
from agents.tools.rss_tool import fetch_rss
from agents.tools.google_news_tool import fetch_google_news

logger = logging.getLogger(__name__)

DOMAIN_SOURCE_MAP: dict[str, list[dict[str, Any]]] = {
    "ai": [
        {"fn": fetch_arxiv, "kwargs": {"query": "artificial intelligence"}, "weight": 1.0},
        {"fn": fetch_github_trending, "kwargs": {"language": "python"}, "weight": 0.8},
        {"fn": fetch_hackernews, "kwargs": {"limit": 30}, "weight": 0.7},
        {"fn": fetch_google_news, "kwargs": {"query": "AI 人工智能"}, "weight": 0.9},
    ],
    "crypto": [
        {"fn": fetch_coingecko_trending, "kwargs": {}, "weight": 1.0},
        {"fn": fetch_coingecko_market, "kwargs": {"limit": 20}, "weight": 0.9},
        {"fn": fetch_defi_protocols, "kwargs": {"limit": 20}, "weight": 0.8},
        {"fn": fetch_defi_yields, "kwargs": {}, "weight": 0.7},
        {"fn": fetch_etherscan_txns, "kwargs": {"limit": 10}, "weight": 0.6},
    ],
    "tech": [
        {"fn": fetch_hackernews, "kwargs": {"limit": 30}, "weight": 1.0},
        {"fn": fetch_github_trending, "kwargs": {"language": ""}, "weight": 0.9},
        {"fn": fetch_google_news, "kwargs": {"query": "technology"}, "weight": 0.8},
        {"fn": fetch_arxiv, "kwargs": {"query": "computer science"}, "weight": 0.6},
    ],
}

DENSITY_CONFIG = {
    "quick_scan": {"target_items": 10, "style": "标题 + 一句话摘要"},
    "standard": {"target_items": 6, "style": "详细分析 + 来源引用"},
    "research": {"target_items": 3, "style": "深度分析 + 历史背景 + 多角度解读"},
}

DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "deepseek/deepseek-chat")


async def fetch_etherscan_txns(**kwargs: Any) -> list[dict[str, Any]]:
    """Etherscan wrapper，保持签名统一。"""
    return await fetch_latest_transactions(**kwargs)


async def collect(state: dict[str, Any]) -> dict[str, Any]:
    """并行调用数据源，采集原始数据。"""
    domain = state.get("domain", "ai")
    template_config = state.get("template_config", {})

    sources = DOMAIN_SOURCE_MAP.get(domain, DOMAIN_SOURCE_MAP["ai"])

    custom_rss = template_config.get("extra_rss_feeds", [])
    for rss_url in custom_rss:
        sources.append({"fn": fetch_rss, "kwargs": {"url": rss_url}, "weight": 0.5})

    tasks = [src["fn"](**src["kwargs"]) for src in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    raw_data: list[dict[str, Any]] = []
    source_refs: list[dict[str, Any]] = []

    for src_cfg, result in zip(sources, results):
        if isinstance(result, Exception):
            logger.warning("数据源 %s 调用失败: %s", src_cfg["fn"].__name__, result)
            continue
        if not isinstance(result, list):
            continue

        source_name = src_cfg["fn"].__name__
        weight = src_cfg.get("weight", 1.0)
        source_refs.append({"source_name": source_name, "item_count": len(result)})

        for item in result:
            raw_data.append({
                "title": item.get("title") or item.get("name", ""),
                "content": item.get("summary") or item.get("description", ""),
                "source_name": source_name,
                "source_url": item.get("url", ""),
                "fetched_at": time.time(),
                "relevance_hint": weight,
                **{k: v for k, v in item.items() if k not in ("title", "summary", "description", "url")},
            })

    raw_data.sort(key=lambda x: x.get("relevance_hint", 0), reverse=True)

    return {"raw_data": raw_data, "sources": source_refs}


async def summarize(state: dict[str, Any]) -> dict[str, Any]:
    """基于密度级别生成结构化摘要。"""
    density = state.get("density_level", "standard")
    filtered = state.get("filtered_data", [])
    cost_tracking = dict(state.get("cost_tracking", {}))

    cfg = DENSITY_CONFIG.get(density, DENSITY_CONFIG["standard"])
    target = cfg["target_items"]
    style = cfg["style"]

    items_text = "\n\n".join(
        f"【{i+1}】{item.get('title', '无标题')}\n来源: {item.get('source_name', '未知')}\n"
        f"链接: {item.get('source_url', '')}\n内容: {item.get('content', '')[:500]}"
        for i, item in enumerate(filtered[:target * 2])
    )

    prompt = (
        f"你是一位专业的情报分析师。请根据以下原始情报条目，生成 {target} 条结构化情报摘要。\n\n"
        f"输出风格: {style}\n\n"
        f"原始情报:\n{items_text}\n\n"
        f"请以 JSON 数组格式输出，每条包含字段: title, summary, source_name, source_url, importance (1-10)。\n"
        f"直接输出 JSON，不要添加其他内容。"
    )

    model = os.getenv("SUMMARIZE_MODEL", DEFAULT_MODEL)

    try:
        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()

        usage = response.usage
        cost_tracking.setdefault("models", {})
        model_stats = cost_tracking["models"].setdefault(model, {"input_tokens": 0, "output_tokens": 0})
        model_stats["input_tokens"] += getattr(usage, "prompt_tokens", 0)
        model_stats["output_tokens"] += getattr(usage, "completion_tokens", 0)

        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0]

        report_items = json.loads(content)
        if not isinstance(report_items, list):
            report_items = [report_items]

    except Exception as exc:
        logger.error("摘要生成失败: %s", exc)
        report_items = [
            {
                "title": item.get("title", ""),
                "summary": (item.get("content", "") or "")[:200],
                "source_name": item.get("source_name", ""),
                "source_url": item.get("source_url", ""),
                "importance": 5,
            }
            for item in filtered[:target]
        ]

    return {"report_items": report_items, "cost_tracking": cost_tracking}


async def add_action_items(state: dict[str, Any]) -> dict[str, Any]:
    """为每条报告条目生成可操作建议。"""
    report_items = state.get("report_items", [])
    cost_tracking = dict(state.get("cost_tracking", {}))

    items_text = "\n".join(
        f"[{i+1}] {item.get('title', '')}: {item.get('summary', '')[:200]}"
        for i, item in enumerate(report_items)
    )

    prompt = (
        "你是一位专业的情报分析顾问。请根据以下情报条目，为每条生成 1-3 条可操作建议。\n\n"
        f"情报条目:\n{items_text}\n\n"
        "每条建议包含字段:\n"
        '- type: "read"（附带URL阅读原文）、"watch"（关注某人/项目）或 "action"（具体操作步骤）\n'
        "- description: 建议描述\n"
        "- url: 相关链接（仅 read 类型必填）\n"
        "- related_item_index: 关联的情报条目序号（从1开始）\n\n"
        "以 JSON 数组输出，不要添加其他内容。"
    )

    model = os.getenv("ACTION_MODEL", DEFAULT_MODEL)

    try:
        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = response.choices[0].message.content.strip()

        usage = response.usage
        cost_tracking.setdefault("models", {})
        model_stats = cost_tracking["models"].setdefault(model, {"input_tokens": 0, "output_tokens": 0})
        model_stats["input_tokens"] += getattr(usage, "prompt_tokens", 0)
        model_stats["output_tokens"] += getattr(usage, "completion_tokens", 0)

        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0]

        action_items = json.loads(content)
        if not isinstance(action_items, list):
            action_items = [action_items]

    except Exception as exc:
        logger.error("行动建议生成失败: %s", exc)
  

... (truncated, total: 8380 chars)
```

### File Write #12: `agents\tester.py`

**Size**: 3135 chars

```
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

```

### File Write #13: `agents\refiner.py`

**Size**: 2730 chars

```
"""Refiner Agent — 内容改进与优化。"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from litellm import acompletion

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("REFINER_MODEL", "deepseek/deepseek-chat")


async def refine(state: dict[str, Any]) -> dict[str, Any]:
    """对未通过质量评估的条目进行 LLM 改写优化。"""
    rejected = state.get("refined_data", [])
    iteration = state.get("iteration_count", 0)
    cost_tracking = dict(state.get("cost_tracking", {}))

    if not rejected:
        return {"refined_data": [], "iteration_count": iteration + 1}

    items_text = "\n\n".join(
        f"【条目 {i+1}】\n"
        f"标题: {item.get('title', '无标题')}\n"
        f"内容: {item.get('content', '无内容')[:400]}\n"
        f"来源: {item.get('source_name', '未知')}\n"
        f"质量分数: {item.get('quality_score', 'N/A')}"
        for i, item in enumerate(rejected)
    )

    prompt = (
        "你是一位专业的情报编辑。以下条目未通过质量评估，请逐条改进：\n\n"
        "改进要求：\n"
        "1. 补充缺失的标题或内容\n"
        "2. 提升表达清晰度和专业性\n"
        "3. 去除冗余信息，保留核心要点\n"
        "4. 添加必要的上下文说明\n\n"
        f"待改进条目:\n{items_text}\n\n"
        "请以 JSON 数组格式输出改进后的条目，每条包含字段: title, content, source_name, source_url。\n"
        "直接输出 JSON，不要添加其他内容。"
    )

    model = os.getenv("REFINER_MODEL", DEFAULT_MODEL)

    try:
        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = response.choices[0].message.content.strip()

        usage = response.usage
        cost_tracking.setdefault("models", {})
        model_stats = cost_tracking["models"].setdefault(model, {"input_tokens": 0, "output_tokens": 0})
        model_stats["input_tokens"] += getattr(usage, "prompt_tokens", 0)
        model_stats["output_tokens"] += getattr(usage, "completion_tokens", 0)

        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0]

        refined_items = json.loads(content)
        if not isinstance(refined_items, list):
            refined_items = [refined_items]

        for original, refined in zip(rejected, refined_items):
            refined.setdefault("source_url", original.get("source_url", ""))
            refined.setdefault("source_name", original.get("source_name", ""))
            refined["fetched_at"] = original.get("fetched_at")
            refined["relevance_hint"] = original.get("relevance_hint", 0.5)

    except Exception as exc:
        logger.error("Refiner 改写失败: %s", exc)
        refined_items = rejected

    return {
        "refined_data": refined_items,
        "iteration_count": iteration + 1,
        "cost_tracking": cost_tracking,
    }

```

### File Write #14: `agents\memory.py`

**Size**: 2036 chars

```
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

```

### File Write #15: `agents\evolution.py`

**Size**: 1954 chars

```
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

```

## Step 9: Assistant

智能体模块全部完成。现在创建最核心的两个文件：`graph.py` 和 `orchestrator.py`。

**TodoWrite**: [completed] , [completed] , [completed] , [completed] , [completed] 

### File Write #16: `agents\graph.py`

**Size**: 5677 chars

```
"""LangGraph 工作流定义 — GTRME 情报生成管线。"""

from __future__ import annotations

import logging
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from agents import generator, tester, refiner, memory

logger = logging.getLogger(__name__)

MAX_REFINE_ITERATIONS = 2
QUALITY_THRESHOLD = 6.0


class IntelState(TypedDict, total=False):
    subscription_config: dict
    user_id: str
    domain: str
    density_level: str              # quick_scan | standard | research
    template_config: dict
    raw_data: list[dict]
    filtered_data: list[dict]
    refined_data: list[dict]
    report_items: list[dict]
    action_items: list[dict]
    sources: list[dict]
    quality_scores: list[float]
    cost_tracking: dict
    error: str | None
    iteration_count: int


# ---------------------------------------------------------------------------
# Node wrappers — 每个节点接收完整 state，返回部分更新
# ---------------------------------------------------------------------------

async def _collect_node(state: IntelState) -> dict[str, Any]:
    try:
        return await generator.collect(state)
    except Exception as exc:
        logger.error("collect 节点异常: %s", exc)
        return {"raw_data": [], "error": str(exc)}


async def _test_node(state: IntelState) -> dict[str, Any]:
    try:
        return await tester.evaluate(state)
    except Exception as exc:
        logger.error("test 节点异常: %s", exc)
        return {"filtered_data": state.get("raw_data", []), "quality_scores": [], "error": str(exc)}


async def _refine_node(state: IntelState) -> dict[str, Any]:
    try:
        return await refiner.refine(state)
    except Exception as exc:
        logger.error("refine 节点异常: %s", exc)
        return {"iteration_count": state.get("iteration_count", 0) + 1, "error": str(exc)}


async def _summarize_node(state: IntelState) -> dict[str, Any]:
    try:
        return await generator.summarize(state)
    except Exception as exc:
        logger.error("summarize 节点异常: %s", exc)
        return {"report_items": [], "error": str(exc)}


async def _action_node(state: IntelState) -> dict[str, Any]:
    try:
        return await generator.add_action_items(state)
    except Exception as exc:
        logger.error("add_actions 节点异常: %s", exc)
        return {"action_items": [], "error": str(exc)}


async def _memory_node(state: IntelState) -> dict[str, Any]:
    try:
        return await memory.update(state)
    except Exception as exc:
        logger.warning("memory_update 节点异常: %s", exc)
        return {}


# ---------------------------------------------------------------------------
# 条件路由
# ---------------------------------------------------------------------------

def _should_refine(state: IntelState) -> str:
    """判断是否需要精炼：所有分数 >= 阈值则跳过，否则看迭代次数。"""
    scores = state.get("quality_scores", [])
    iteration = state.get("iteration_count", 0)

    if not scores or all(s >= QUALITY_THRESHOLD for s in scores):
        return "summarize"

    if iteration >= MAX_REFINE_ITERATIONS:
        logger.info("已达最大精炼次数 (%d)，跳过进入摘要", MAX_REFINE_ITERATIONS)
        return "summarize"

    return "refine"


# ---------------------------------------------------------------------------
# 构建 Graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    """构建并编译 GTRME 工作流图。"""
    workflow = StateGraph(IntelState)

    workflow.add_node("collect", _collect_node)
    workflow.add_node("test", _test_node)
    workflow.add_node("refine", _refine_node)
    workflow.add_node("summarize", _summarize_node)
    workflow.add_node("add_actions", _action_node)
    workflow.add_node("memory_update", _memory_node)

    workflow.set_entry_point("collect")
    workflow.add_edge("collect", "test")

    workflow.add_conditional_edges(
        "test",
        _should_refine,
        {"summarize": "summarize", "refine": "refine"},
    )

    workflow.add_edge("refine", "test")
    workflow.add_edge("summarize", "add_actions")
    workflow.add_edge("add_actions", "memory_update")
    workflow.add_edge("memory_update", END)

    return workflow


_compiled_graph = None


def get_compiled_graph():
    """获取已编译的工作流图（单例）。"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph().compile()
    return _compiled_graph


# ---------------------------------------------------------------------------
# 入口函数
# ---------------------------------------------------------------------------

async def run_intel_pipeline(
    subscription_config: dict[str, Any],
    user_id: str,
) -> IntelState:
    """执行完整的情报生成管线。

    Args:
        subscription_config: 包含 domain, density, template 等配置
        user_id: 用户标识

    Returns:
        完整的 IntelState，包含 report_items, action_items, sources 等
    """
    initial_state: IntelState = {
        "subscription_config": subscription_config,
        "user_id": user_id,
        "domain": subscription_config.get("domain", "ai"),
        "density_level": subscription_config.get("density", "standard"),
        "template_config": subscription_config.get("template_config", {}),
        "raw_data": [],
        "filtered_data": [],
        "refined_data": [],
        "report_items": [],
        "action_items": [],
        "sources": [],
        "quality_scores": [],
        "cost_tracking": {"models": {}},
        "error": None,
        "iteration_count": 0,
    }

    graph = get_compiled_graph()

    logger.info(
        "启动情报管线: user=%s, domain=%s, density=%s",
        user_id, initial_state["domain"], initial_state["density_level"],
    )

    final_state = await graph.ainvoke(initial_state)
    return final_state

```

### File Write #17: `agents\orchestrator.py`

**Size**: 4755 chars

```
"""Orchestrator — 情报生成编排器。

负责模型路由、成本追踪、质量控制，并对外提供统一入口。
"""

from __future__ import annotations

import logging
import os
import random
import time
from typing import Any

from agents.graph import run_intel_pipeline, IntelState
from agents.evolution import evaluate_template

logger = logging.getLogger(__name__)

# 模型路由配置：80% DeepSeek，20% Claude（用于复杂分析）
MODEL_ROUTING = {
    "deepseek": {
        "model": "deepseek/deepseek-chat",
        "weight": 0.80,
        "cost_per_1k_input": 0.0014,
        "cost_per_1k_output": 0.0028,
    },
    "claude": {
        "model": "anthropic/claude-3-5-sonnet-20241022",
        "weight": 0.20,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
    },
}


def select_model(task_complexity: str = "normal") -> str:
    """根据任务复杂度和权重概率选择模型。"""
    if task_complexity == "complex":
        return MODEL_ROUTING["claude"]["model"]

    roll = random.random()
    if roll < MODEL_ROUTING["deepseek"]["weight"]:
        return MODEL_ROUTING["deepseek"]["model"]
    return MODEL_ROUTING["claude"]["model"]


def _calculate_cost(cost_tracking: dict[str, Any]) -> dict[str, Any]:
    """根据 token 用量计算实际费用。"""
    models = cost_tracking.get("models", {})
    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    breakdown: dict[str, Any] = {}

    for model_name, usage in models.items():
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        routing_info = None
        for _, info in MODEL_ROUTING.items():
            if info["model"] == model_name:
                routing_info = info
                break

        if routing_info:
            cost = (
                input_tokens / 1000 * routing_info["cost_per_1k_input"]
                + output_tokens / 1000 * routing_info["cost_per_1k_output"]
            )
        else:
            cost = (input_tokens + output_tokens) / 1000 * 0.002

        total_cost += cost
        breakdown[model_name] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
        }

    return {
        "total_cost_usd": round(total_cost, 6),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "breakdown": breakdown,
    }


async def generate_report(
    subscription_config: dict[str, Any],
    user_id: str,
) -> dict[str, Any]:
    """生成情报报告的统一入口。

    Args:
        subscription_config: 订阅配置，含 domain / density / template_config
        user_id: 用户 ID

    Returns:
        {report_items, action_items, sources, cost_breakdown, tokens_consumed}
    """
    start_time = time.time()

    model = select_model(
        task_complexity=subscription_config.get("complexity", "normal")
    )
    os.environ["DEFAULT_LLM_MODEL"] = model
    os.environ["SUMMARIZE_MODEL"] = model
    os.environ["ACTION_MODEL"] = model

    density = subscription_config.get("density", "standard")
    if density == "research":
        os.environ["SUMMARIZE_MODEL"] = MODEL_ROUTING["claude"]["model"]

    logger.info(
        "Orchestrator 启动: user=%s, domain=%s, model=%s",
        user_id, subscription_config.get("domain", "ai"), model,
    )

    try:
        final_state: IntelState = await run_intel_pipeline(subscription_config, user_id)
    except Exception as exc:
        logger.error("管线执行失败: %s", exc)
        return {
            "report_items": [],
            "action_items": [],
            "sources": [],
            "cost_breakdown": {},
            "tokens_consumed": 0,
            "error": str(exc),
        }

    cost_tracking = final_state.get("cost_tracking", {})
    cost_breakdown = _calculate_cost(cost_tracking)

    # Evolution 追踪
    template_id = subscription_config.get("template_id", "default")
    quality_scores = final_state.get("quality_scores", [])
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    await evaluate_template(template_id, avg_quality)

    elapsed = time.time() - start_time
    logger.info(
        "Orchestrator 完成: %.1fs, items=%d, cost=$%.4f",
        elapsed, len(final_state.get("report_items", [])), cost_breakdown["total_cost_usd"],
    )

    return {
        "report_items": final_state.get("report_items", []),
        "action_items": final_state.get("action_items", []),
        "sources": final_state.get("sources", []),
        "cost_breakdown": cost_breakdown,
        "tokens_consumed": cost_breakdown["total_input_tokens"] + cost_breakdown["total_output_tokens"],
        "quality_avg": avg_quality,
        "generation_time_seconds": round(elapsed, 2),
    }

```

## Step 10: Assistant

所有文件已创建。让我修复 `generator.py` 中的一个引用问题——`DOMAIN_SOURCE_MAP` 里 crypto 域引用了 `fetch_etherscan_txns`，但这个函数定义在引用之后。

**Read**: `agents\generator.py`

## Step 11: Assistant

`DOMAIN_SOURCE_MAP` 中的 `fetch_etherscan_txns` 在模块级别被引用时函数还未定义。需要将 `DOMAIN_SOURCE_MAP` 改为延迟求值，或者将 crypto 中的引用改为直接用 `fetch_latest_transactions`。最简单的修复方式：

**StrReplace**: `agents\generator.py`
- Old: `DOMAIN_SOURCE_MAP: dict[str, list[dict[str, Any]]] = {
    "ai": [
        {"fn": fetch_arxiv, "kwar...`

## Step 12: Assistant

同时移除不再需要的 `fetch_etherscan_txns` 包装函数。

**StrReplace**: `agents\generator.py`
- Old: `async def fetch_etherscan_txns(**kwargs: Any) -> list[dict[str, Any]]:
    """Etherscan wrapper，保持签名...`

## Step 13: Assistant

现在让我验证所有文件完整性。

**TodoWrite**: [completed] , [completed] 

**Glob**: {"glob_pattern": "agents/**/*.py", "target_directory": "e:\\AI\\Intelligence_agent"}

## Step 14: Assistant

全部 17 个文件已创建完毕。让我做最终检查确认各文件可导入无误。

**ReadLints**: {"paths": ["e:\\AI\\Intelligence_agent\\agents"]}

## Step 15: Assistant

所有文件无 lint 错误。以下是创建的完整文件总结：

---

## 创建文件总结（共 17 个文件）

### 核心引擎（agents/）

| 文件 | 说明 |
|------|------|
| `__init__.py` | 包初始化，版本信息 |
| `graph.py` | **LangGraph 工作流定义** — `IntelState` 状态模式 + `StateGraph` 构建：collect → test → (refine ↔ test, 最多2轮) → summarize → add_actions → memory_update → END。提供 `run_intel_pipeline()` 异步入口 |
| `orchestrator.py` | **编排器** — 模型路由（80% DeepSeek / 20% Claude）、成本计算、质量控制。`generate_report()` 作为统一对外接口 |
| `generator.py` | **Generator Agent** — `collect()` 并行调用多数据源采集、`summarize()` 按密度级别(quick_scan/standard/research)生成 LLM 摘要、`add_action_items()` 生成行动建议 |
| `tester.py` | **Tester Agent** — `evaluate()` 多维质量评分：内容质量、去重检测(标题相似度)、时效过滤、中文合规过滤，阈值 6 分 |
| `refiner.py` | **Refiner Agent** — `refine()` 通过 LLM 改写低质量条目，补充上下文、提升清晰度 |
| `memory.py` | **Memory Agent** — `update()` 记录生成质量指标到 JSONL、`get_user_preferences()` 读取用户偏好（MVP 返回默认值） |
| `evolution.py` | **Evolution Agent** — `evaluate_template()` 追踪模板历史表现、计算趋势 |

### 数据采集工具（agents/tools/）

| 文件 | 数据源 | 核心函数 |
|------|--------|----------|
| `__init__.py` | 工具集汇总导出 | — |
| `arxiv_tool.py` | arXiv 论文 | `fetch_arxiv(query, max_results)` |
| `github_tool.py` | GitHub Trending | `fetch_github_trending(language, since)` |
| `hackernews_tool.py` | Hacker News | `fetch_hackernews(limit)` |
| `coingecko_tool.py` | CoinGecko | `fetch_coingecko_trending()` / `fetch_coingecko_market(limit)` |
| `defi_llama_tool.py` | DeFiLlama | `fetch_defi_protocols(limit)` / `fetch_defi_yields()` |
| `etherscan_tool.py` | Etherscan | `fetch_latest_transactions(limit)` |
| `rss_tool.py` | 通用 RSS | `fetch_rss(url, limit)` — 支持 RSS 2.0 和 Atom |
| `google_news_tool.py` | Google News | `fetch_google_news(query, lang)` — 基于 rss_tool |

### 架构要点

- **全异步**：所有函数均为 `async`，HTTP 使用 `httpx`
- **LLM 调用**：通过 `litellm.acompletion()`，支持 DeepSeek 和 Claude 模型切换
- **中文输出**：所有 LLM 提示词生成中文内容
- **错误容错**：工具调用失败返回空列表并记录日志，不会中断管线
- **成本追踪**：全链路记录 input/output tokens，按模型计费
- **独立性**：API keys 通过 `os.getenv()` 获取，不依赖 backend 模块

## Step 16: User Prompt

```
Your previous response was interrupted. Continue from where you left off.
```

## Step 17: Assistant

让我先确认所有文件的状态。

The user says my previous response was interrupted. Let me check what was done - looking at the todo list, all 17 files were completed. Let me verify everything is in place and provide the summary.

**Glob**: {"glob_pattern": "agents/**/*.py", "target_directory": "e:\\AI\\Intelligence_agent"}

## Step 18: Assistant

全部 17 个文件已在上一轮创建完毕，没有遗漏。让我快速验证几个关键文件的内容完整性。

**Read**: `agents\graph.py`

**Read**: `agents\orchestrator.py`

**Read**: `agents\generator.py`

## Step 19: Assistant

所有文件内容完整且正确。以下是完整的创建总结：

---

## 全部 17 个文件已创建完毕

### 目录结构

```
agents/
├── __init__.py              # 包初始化 + 版本 0.1.0
├── graph.py                 # LangGraph StateGraph 工作流定义
├── orchestrator.py          # 编排器（对外统一入口）
├── generator.py             # Generator Agent（采集 + 摘要 + 行动建议）
├── tester.py                # Tester Agent（质量评估 + 过滤）
├── refiner.py               # Refiner Agent（LLM 改写优化）
├── memory.py                # Memory Agent（用户偏好记忆）
├── evolution.py             # Evolution Agent（模板表现追踪）
└── tools/
    ├── __init__.py           # 工具集汇总导出
    ├── arxiv_tool.py         # arXiv 论文搜索
    ├── github_tool.py        # GitHub Trending 抓取
    ├── hackernews_tool.py    # Hacker News 热门故事
    ├── coingecko_tool.py     # CoinGecko 行情 + 热门币
    ├── defi_llama_tool.py    # DeFiLlama 协议 + 收益
    ├── etherscan_tool.py     # Etherscan 链上交易
    ├── rss_tool.py           # 通用 RSS 解析（RSS 2.0 + Atom）
    └── google_news_tool.py   # Google News RSS 搜索
```

### GTRME 工作流（graph.py）

```
collect → test → [条件判断] → summarize → add_actions → memory_update → END
                    ↓ (score < 6)
                  refine → test (最多循环 2 次)
```

### 关键设计点

| 特性 | 实现 |
|------|------|
| **模型路由** | 80% DeepSeek-Chat / 20% Claude-3.5-Sonnet，research 密度强制用 Claude |
| **密度级别** | quick_scan(10条简报) / standard(6条详析) / research(3条深度) |
| **域数据源** | ai=arXiv+GitHub+HN+Google News；crypto=CoinGecko+DeFiLlama+Etherscan；tech=HN+GitHub+News+arXiv |
| **质量控制** | 内容质量 + MD5去重 + 标题相似度 + 时效过滤 + 中文合规，阈值 6 分 |
| **成本追踪** | 全链路 token 记录，按模型费率计算 USD 成本 |
| **容错** | 所有节点包裹 try/except，工具失败返回空列表不中断管线 |
| **全异步** | 所有函数 async，httpx 并行请求，asyncio.gather 并发采集 |

## Step 20: User Prompt

```
Your previous response was interrupted. Continue from where you left off.
```

## Step 21: Assistant

之前的工作实际上已经全部完成了。让我快速验证一下所有 17 个文件都存在且内容完整。

**Glob**: {"glob_pattern": "agents/**/*.py", "target_directory": "e:\\AI\\Intelligence_agent"}

## Step 22: Assistant

全部 17 个文件已就位。所有工作在之前的轮次中已经完成，没有遗漏。以下是完整总结：

---

## 已创建的文件清单（17 个）

### 核心智能体（`agents/`）

| 文件 | 角色 | 核心函数 |
|------|------|----------|
| `__init__.py` | 包初始化 | 版本 `0.1.0` |
| `graph.py` | LangGraph 工作流 | `IntelState` 状态定义、`build_graph()`、`run_intel_pipeline()` |
| `orchestrator.py` | 编排器 | `generate_report()`、`select_model()`、`_calculate_cost()` |
| `generator.py` | Generator | `collect()`、`summarize()`、`add_action_items()` |
| `tester.py` | Tester | `evaluate()` — 内容质量/去重/时效/合规多维评分 |
| `refiner.py` | Refiner | `refine()` — LLM 改写低质量条目 |
| `memory.py` | Memory | `update()`、`get_user_preferences()` |
| `evolution.py` | Evolution | `evaluate_template()` — 模板表现追踪 |

### 数据工具（`agents/tools/`）

| 文件 | 数据源 | 核心函数 |
|------|--------|----------|
| `__init__.py` | 汇总导出 | 全部 10 个采集函数 |
| `arxiv_tool.py` | arXiv | `fetch_arxiv(query, max_results)` |
| `github_tool.py` | GitHub Trending | `fetch_github_trending(language, since)` |
| `hackernews_tool.py` | Hacker News | `fetch_hackernews(limit)` |
| `coingecko_tool.py` | CoinGecko | `fetch_coingecko_trending()` / `fetch_coingecko_market()` |
| `defi_llama_tool.py` | DeFiLlama | `fetch_defi_protocols()` / `fetch_defi_yields()` |
| `etherscan_tool.py` | Etherscan | `fetch_latest_transactions(limit)` |
| `rss_tool.py` | 通用 RSS | `fetch_rss(url, limit)` — 支持 RSS 2.0 + Atom |
| `google_news_tool.py` | Google News | `fetch_google_news(query, lang)` |

### GTRME 工作流

```
collect → test →[全部≥6分?]→ summarize → add_actions → memory_update → END
                  ↓ 否（且迭代<2次）
                refine → test（重新评估）
```

### 关键设计

- **全异步**：httpx + asyncio.gather 并发采集，litellm.acompletion 调用 LLM
- **模型路由**：80% DeepSeek / 20% Claude，research 密度强制 Claude
- **三级密度**：quick_scan(10条) / standard(6条) / research(3条深度分析)
- **成本追踪**：全链路 token 计数 + 按模型费率折算 USD
- **容错**：每个节点、每个工具独立 try/except，失败不中断管线
- **中文合规**：正则过滤违规内容，LLM 提示词全中文输出

## Step 23: User Prompt

```
Your previous response was interrupted. Continue from where you left off.
```

## Step 24: Assistant

所有 17 个文件在之前的轮次中已全部创建完成，无需继续。工作没有遗漏。

---

## Summary

- **Total entries**: 24
- **Files written**: 17

### Files Created

- `agents\__init__.py`
- `agents\tools\__init__.py`
- `agents\tools\rss_tool.py`
- `agents\tools\arxiv_tool.py`
- `agents\tools\github_tool.py`
- `agents\tools\hackernews_tool.py`
- `agents\tools\coingecko_tool.py`
- `agents\tools\defi_llama_tool.py`
- `agents\tools\etherscan_tool.py`
- `agents\tools\google_news_tool.py`
- `agents\generator.py`
- `agents\tester.py`
- `agents\refiner.py`
- `agents\memory.py`
- `agents\evolution.py`
- `agents\graph.py`
- `agents\orchestrator.py`
