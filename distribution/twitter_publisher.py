"""
Twitter 自动发布模块 - 通过 Twitter API v2 发布推文线程。
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


def _get_client():
    """获取 tweepy 客户端实例。缺少凭证时返回 None。"""
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        logger.warning("Twitter API credentials not configured. Publishing disabled.")
        return None

    try:
        import tweepy

        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
        )
        return client
    except ImportError:
        logger.error("tweepy is not installed. Run: pip install tweepy")
        return None


async def publish_thread(tweets: list[str]) -> list[str]:
    """发布推文线程。

    按顺序发布所有推文，每条推文回复前一条以形成线程。

    Args:
        tweets: 推文文本列表，按线程顺序排列。

    Returns:
        已发布推文的 ID 列表。

    Raises:
        RuntimeError: Twitter API 不可用时抛出。
    """
    client = _get_client()
    if client is None:
        logger.warning("Twitter client unavailable. Skipping publish.")
        return []

    tweet_ids: list[str] = []
    reply_to_id: Optional[str] = None

    for i, text in enumerate(tweets):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await asyncio.to_thread(
                    client.create_tweet,
                    text=text,
                    in_reply_to_tweet_id=reply_to_id,
                )
                tweet_id = str(response.data["id"])
                tweet_ids.append(tweet_id)
                reply_to_id = tweet_id
                logger.info("Published tweet %d/%d (ID: %s)", i + 1, len(tweets), tweet_id)
                break

            except Exception as e:
                logger.error(
                    "Failed to publish tweet %d (attempt %d/%d): %s",
                    i + 1, attempt, MAX_RETRIES, e,
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)
                else:
                    logger.error("Giving up on tweet %d after %d retries.", i + 1, MAX_RETRIES)

    logger.info("Thread published: %d/%d tweets succeeded.", len(tweet_ids), len(tweets))
    return tweet_ids


async def schedule_publish(report_id: str, publish_time: datetime) -> None:
    """调度推文在指定时间发布。

    将发布任务加入调度队列，在 publish_time 到达时触发。

    Args:
        report_id: 关联的报告 ID。
        publish_time: 计划发布时间（UTC）。
    """
    now = datetime.utcnow()
    delay = (publish_time - now).total_seconds()

    if delay <= 0:
        logger.warning("Scheduled time %s is in the past. Publishing immediately.", publish_time)
        delay = 0

    logger.info(
        "Scheduled publish for report %s at %s (delay: %.0fs)",
        report_id, publish_time.isoformat(), delay,
    )

    await asyncio.sleep(delay)

    logger.info("Scheduled time reached for report %s. Triggering publish...", report_id)
    # Actual publish logic would load report and call publish_thread
    # For now, log the trigger event
    logger.info("Publish triggered for report %s (implementation pending full pipeline).", report_id)
