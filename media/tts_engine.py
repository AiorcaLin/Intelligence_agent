"""
文本转语音模块 - 基于 Edge-TTS 将文本内容转换为音频文件。

支持的语音：
  - zh-CN-XiaoxiaoNeural: 中文女声（默认）
  - zh-CN-YunxiNeural: 中文男声
  - en-US-JennyNeural: 英文女声
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

AVAILABLE_VOICES = {
    "zh-CN-female": "zh-CN-XiaoxiaoNeural",
    "zh-CN-male": "zh-CN-YunxiNeural",
    "en-US-female": "en-US-JennyNeural",
}

DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"


async def text_to_speech(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
) -> str:
    """将文本转换为 MP3 音频文件。

    Args:
        text: 需要转换的文本内容。
        output_path: 输出 MP3 文件路径。
        voice: Edge-TTS 语音名称。

    Returns:
        生成的音频文件路径。

    Raises:
        RuntimeError: edge-tts 不可用或转换失败时抛出。
    """
    if not text.strip():
        logger.warning("Empty text provided for TTS. Skipping.")
        return ""

    try:
        import edge_tts
    except ImportError:
        logger.error("edge-tts is not installed. Run: pip install edge-tts")
        raise RuntimeError("edge-tts is not installed")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        file_size = os.path.getsize(output_path)
        logger.info(
            "TTS completed: voice=%s, text_len=%d, output=%s, size=%d bytes",
            voice, len(text), output_path, file_size,
        )
        return output_path

    except Exception as e:
        logger.error("TTS generation failed: %s", e)
        raise RuntimeError(f"TTS generation failed: {e}") from e


async def generate_report_audio(
    report_items: list[dict[str, Any]],
    output_dir: str,
    voice: str = DEFAULT_VOICE,
) -> str:
    """将报告条目合成为一个完整的音频文件。

    将所有条目串联为自然的叙述文本，然后生成单个 MP3 文件。

    Args:
        report_items: 报告条目列表，每项包含 title 和 summary。
        output_dir: 输出目录路径。
        voice: Edge-TTS 语音名称。

    Returns:
        生成的 MP3 文件路径。
    """
    if not report_items:
        logger.warning("No report items provided for audio generation.")
        return ""

    narration_parts: list[str] = ["以下是今日情报精选。\n"]

    for i, item in enumerate(report_items, 1):
        title = item.get("title", "")
        summary = item.get("summary", "")

        narration_parts.append(f"第{_num_to_chinese(i)}条：{title}。")
        if summary:
            narration_parts.append(f"{summary}")
        narration_parts.append("")

    narration_parts.append("以上是今日全部情报，感谢收听。")
    narration_text = "\n".join(narration_parts)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "report_audio.mp3")

    return await text_to_speech(narration_text, output_path, voice)


def _num_to_chinese(n: int) -> str:
    """将小整数转换为中文数字（1-99）。"""
    digits = "零一二三四五六七八九"
    if n < 0 or n > 99:
        return str(n)
    if n < 10:
        return digits[n]
    tens = n // 10
    ones = n % 10
    result = ""
    if tens > 1:
        result += digits[tens]
    result += "十"
    if ones > 0:
        result += digits[ones]
    return result
