"""
内容格式化模块 - 将报告内容适配到不同分发平台的格式要求。
"""

import logging
import html
from typing import Any

logger = logging.getLogger(__name__)

TWITTER_MAX_CHARS = 280


def _truncate(text: str, max_len: int, suffix: str = "…") -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def format_for_twitter(
    report_items: list[dict[str, Any]], platform_url: str
) -> list[str]:
    """将报告条目格式化为 Twitter 推文线程。

    每条推文不超过 280 字符，最后一条包含平台链接。

    Args:
        report_items: 报告条目列表，每项包含 title, summary, url 等字段。
        platform_url: 平台完整报告链接。

    Returns:
        推文文本列表，按线程顺序排列。
    """
    if not report_items:
        return []

    tweets: list[str] = []

    header = "🔍 今日情报精选\n\n"
    tweets.append(_truncate(header, TWITTER_MAX_CHARS))

    for i, item in enumerate(report_items, 1):
        title = item.get("title", "")
        summary = item.get("summary", "")
        url = item.get("url", "")

        tweet = f"{i}. {title}\n{summary}"
        if url:
            url_suffix = f"\n{url}"
            tweet = _truncate(tweet, TWITTER_MAX_CHARS - len(url_suffix)) + url_suffix
        else:
            tweet = _truncate(tweet, TWITTER_MAX_CHARS)

        tweets.append(tweet)

    footer = f"📖 查看完整报告：\n{platform_url}"
    tweets.append(_truncate(footer, TWITTER_MAX_CHARS))

    return tweets


def format_for_telegram(
    report_items: list[dict[str, Any]], platform_url: str
) -> str:
    """将报告条目格式化为 Telegram Markdown 消息。

    Args:
        report_items: 报告条目列表。
        platform_url: 平台完整报告链接。

    Returns:
        Telegram MarkdownV2 格式的消息文本。
    """
    if not report_items:
        return "暂无最新情报。"

    lines: list[str] = ["*📋 今日情报精选*\n"]

    for i, item in enumerate(report_items, 1):
        title = item.get("title", "")
        summary = item.get("summary", "")
        url = item.get("url", "")

        line = f"*{i}\\. {_escape_telegram_md(title)}*"
        if summary:
            line += f"\n{_escape_telegram_md(summary)}"
        if url:
            line += f"\n[🔗 原文链接]({url})"
        lines.append(line)

    lines.append(f"\n[📖 查看完整报告]({platform_url})")

    return "\n\n".join(lines)


def _escape_telegram_md(text: str) -> str:
    """转义 Telegram MarkdownV2 特殊字符。"""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    escaped = ""
    for ch in text:
        if ch in special_chars:
            escaped += f"\\{ch}"
        else:
            escaped += ch
    return escaped


def format_for_wechat(
    report_items: list[dict[str, Any]], platform_url: str
) -> str:
    """将报告条目格式化为微信公众号文章 HTML。

    Args:
        report_items: 报告条目列表。
        platform_url: 平台完整报告链接。

    Returns:
        微信公众号兼容的 HTML 内容。
    """
    if not report_items:
        return "<p>暂无最新情报。</p>"

    sections: list[str] = [
        '<section style="padding: 16px;">',
        '<h1 style="font-size: 22px; color: #333; border-bottom: 2px solid #07c160; '
        'padding-bottom: 8px;">📋 今日情报精选</h1>',
    ]

    for i, item in enumerate(report_items, 1):
        title = html.escape(item.get("title", ""))
        summary = html.escape(item.get("summary", ""))
        url = item.get("url", "")

        sections.append(
            f'<section style="margin: 16px 0; padding: 12px; '
            f'background: #f9f9f9; border-radius: 8px;">'
            f'<h3 style="font-size: 16px; color: #333;">{i}. {title}</h3>'
            f'<p style="font-size: 14px; color: #666; line-height: 1.6;">{summary}</p>'
        )
        if url:
            sections.append(
                f'<a href="{html.escape(url)}" style="color: #07c160; '
                f'font-size: 13px;">🔗 查看原文</a>'
            )
        sections.append("</section>")

    sections.append(
        f'<section style="text-align: center; margin-top: 20px; padding: 12px;">'
        f'<a href="{html.escape(platform_url)}" style="color: #07c160; '
        f'font-size: 15px; font-weight: bold;">📖 查看完整报告</a>'
        f"</section>"
    )
    sections.append("</section>")

    return "\n".join(sections)


def format_for_zhihu(
    report_items: list[dict[str, Any]], platform_url: str
) -> str:
    """将报告条目格式化为知乎文章格式。

    Args:
        report_items: 报告条目列表。
        platform_url: 平台完整报告链接。

    Returns:
        知乎兼容的 Markdown 内容。
    """
    if not report_items:
        return "暂无最新情报。"

    lines: list[str] = ["# 📋 今日情报精选\n"]

    for i, item in enumerate(report_items, 1):
        title = item.get("title", "")
        summary = item.get("summary", "")
        url = item.get("url", "")

        lines.append(f"## {i}. {title}\n")
        if summary:
            lines.append(f"{summary}\n")
        if url:
            lines.append(f"> [🔗 查看原文]({url})\n")

    lines.append("---\n")
    lines.append(f"📖 [查看完整报告]({platform_url})")

    return "\n".join(lines)
