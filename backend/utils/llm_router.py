from __future__ import annotations

import logging

import litellm

from backend.config import settings

logger = logging.getLogger(__name__)

TASK_MODEL_MAP: dict[str, str] = {
    "collection": "deepseek/deepseek-chat",
    "formatting": "deepseek/deepseek-chat",
    "analysis": "anthropic/claude-3-5-sonnet-20241022",
    "summary": "anthropic/claude-3-5-sonnet-20241022",
}


def route_llm(task_type: str) -> str:
    """Return the appropriate model name for the given task type."""
    return TASK_MODEL_MAP.get(task_type, "deepseek/deepseek-chat")


async def call_llm(
    prompt: str,
    task_type: str,
    system_prompt: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> dict:
    """Call LLM via LiteLLM with automatic model routing."""
    model = route_llm(task_type)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    api_key = None
    api_base = None
    if model.startswith("deepseek/"):
        api_key = settings.DEEPSEEK_API_KEY
        api_base = settings.DEEPSEEK_BASE_URL
    elif model.startswith("anthropic/"):
        api_key = settings.CLAUDE_API_KEY

    try:
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            api_base=api_base,
        )

        return {
            "content": response.choices[0].message.content,
            "model": model,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }
    except Exception:
        logger.exception("LLM call failed for model %s", model)
        raise
