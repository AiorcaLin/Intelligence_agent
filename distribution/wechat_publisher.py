"""
微信公众号发布模块（MVP 阶段为存根实现）。

完整的微信公众号集成需要：
1. 已认证的微信公众号
2. 微信公众平台 API 接口权限
3. 通过微信认证的服务号或订阅号

当前阶段仅记录发布意图，不进行实际 API 调用。
"""

import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "")


async def publish_article(title: str, content: str) -> str:
    """发布微信公众号文章（存根实现）。

    MVP 阶段记录发布意图并返回占位 ID。
    正式集成后将调用微信公众平台接口：
    1. 获取 access_token
    2. 上传图文素材
    3. 群发或定时发布

    Args:
        title: 文章标题。
        content: 文章 HTML 内容。

    Returns:
        占位文章 ID 字符串。
    """
    timestamp = datetime.utcnow().isoformat()
    placeholder_id = f"wechat_stub_{timestamp}"

    if not all([WECHAT_APP_ID, WECHAT_APP_SECRET]):
        logger.warning(
            "WeChat credentials not configured (WECHAT_APP_ID, WECHAT_APP_SECRET). "
            "Publishing is in stub mode."
        )

    logger.info(
        "WeChat publish intent recorded: title='%s', content_length=%d, stub_id='%s'",
        title,
        len(content),
        placeholder_id,
    )

    return placeholder_id


async def get_access_token() -> str:
    """获取微信公众平台 access_token（存根实现）。

    Returns:
        空字符串（MVP 阶段）。
    """
    if not all([WECHAT_APP_ID, WECHAT_APP_SECRET]):
        logger.warning("WeChat credentials not configured. Cannot obtain access_token.")
        return ""

    logger.info("WeChat access_token retrieval: stub mode, returning empty token.")
    return ""


async def upload_media(media_path: str, media_type: str = "image") -> str:
    """上传媒体素材到微信（存根实现）。

    Args:
        media_path: 本地媒体文件路径。
        media_type: 素材类型（image/voice/video/thumb）。

    Returns:
        空字符串（MVP 阶段）。
    """
    logger.info(
        "WeChat media upload intent: path='%s', type='%s' (stub mode)",
        media_path,
        media_type,
    )
    return ""
