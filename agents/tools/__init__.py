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
