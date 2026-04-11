"""
Telegram Bot 发布模块 - 通过 Telegram Bot API 向频道和用户推送消息。
"""

import asyncio
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

MAX_MESSAGE_LENGTH = 4096
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3


def _get_bot():
    """获取 Telegram Bot 实例。缺少 token 时返回 None。"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not configured. Telegram publishing disabled.")
        return None

    try:
        from telegram import Bot

        return Bot(token=TELEGRAM_BOT_TOKEN)
    except ImportError:
        logger.error("python-telegram-bot is not installed. Run: pip install python-telegram-bot")
        return None


def _split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """将超长消息按段落拆分为多条。"""
    if len(text) <= max_length:
        return [text]

    parts: list[str] = []
    current = ""

    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_length:
            if current:
                parts.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"

    if current.strip():
        parts.append(current.strip())

    return parts


async def send_to_channel(channel_id: str, message: str) -> Optional[list[int]]:
    """向 Telegram 频道发送格式化消息。

    超长消息会自动拆分为多条发送。

    Args:
        channel_id: 频道 ID 或 @username。
        message: MarkdownV2 格式的消息文本。

    Returns:
        成功发送的消息 ID 列表，失败返回 None。
    """
    bot = _get_bot()
    if bot is None:
        return None

    parts = _split_message(message)
    message_ids: list[int] = []

    async with bot:
        for i, part in enumerate(parts):
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    result = await bot.send_message(
                        chat_id=channel_id,
                        text=part,
                        parse_mode="MarkdownV2",
                        disable_web_page_preview=True,
                    )
                    message_ids.append(result.message_id)
                    logger.info(
                        "Sent part %d/%d to channel %s (msg_id: %d)",
                        i + 1, len(parts), channel_id, result.message_id,
                    )
                    break

                except Exception as e:
                    logger.error(
                        "Failed to send to channel %s (attempt %d/%d): %s",
                        channel_id, attempt, MAX_RETRIES, e,
                    )
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)
                    else:
                        logger.error("Giving up on part %d after %d retries.", i + 1, MAX_RETRIES)

    return message_ids if message_ids else None


async def send_to_user(user_id: int, message: str) -> Optional[list[int]]:
    """向单个用户发送消息。

    Args:
        user_id: 用户的 Telegram ID。
        message: MarkdownV2 格式的消息文本。

    Returns:
        成功发送的消息 ID 列表，失败返回 None。
    """
    bot = _get_bot()
    if bot is None:
        return None

    parts = _split_message(message)
    message_ids: list[int] = []

    async with bot:
        for part in parts:
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    result = await bot.send_message(
                        chat_id=user_id,
                        text=part,
                        parse_mode="MarkdownV2",
                    )
                    message_ids.append(result.message_id)
                    break

                except Exception as e:
                    logger.error(
                        "Failed to send to user %d (attempt %d/%d): %s",
                        user_id, attempt, MAX_RETRIES, e,
                    )
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)

    return message_ids if message_ids else None


async def handle_bot_commands() -> None:
    """启动 Telegram Bot 命令处理器。

    支持的命令：
    - /start: 欢迎消息和使用说明
    - /subscribe: 订阅每日情报推送
    - /unsubscribe: 取消订阅
    - /domains: 查看可用领域列表
    """
    bot_token = TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not set. Bot commands handler disabled.")
        return

    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
    except ImportError:
        logger.error("python-telegram-bot is not installed. Run: pip install python-telegram-bot")
        return

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "👋 欢迎使用 AI Intelligence Agent！\n\n"
            "可用命令：\n"
            "/subscribe - 订阅每日情报推送\n"
            "/unsubscribe - 取消订阅\n"
            "/domains - 查看可用领域"
        )

    async def cmd_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        logger.info("User %d subscribed.", user_id)
        await update.message.reply_text("✅ 订阅成功！你将每天收到情报推送。")

    async def cmd_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        logger.info("User %d unsubscribed.", user_id)
        await update.message.reply_text("❌ 已取消订阅。")

    async def cmd_domains(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "📂 可用领域：\n"
            "• AI - 人工智能\n"
            "• Crypto - 加密货币\n\n"
            "更多领域即将上线！"
        )

    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("subscribe", cmd_subscribe))
    app.add_handler(CommandHandler("unsubscribe", cmd_unsubscribe))
    app.add_handler(CommandHandler("domains", cmd_domains))

    logger.info("Telegram bot command handler started.")
    await app.run_polling()
