from __future__ import annotations

import math

from backend.config import settings

MODEL_PRICES: dict[str, dict[str, float]] = {
    "deepseek_v3": {"input": 0.001, "output": 0.002},
    "deepseek/deepseek-chat": {"input": 0.001, "output": 0.002},
    "claude_sonnet": {"input": 0.015, "output": 0.060},
    "anthropic/claude-3-5-sonnet-20241022": {"input": 0.015, "output": 0.060},
}


def calculate_credits(
    input_tokens: int,
    output_tokens: int,
    model_name: str,
    density_level: str,
) -> int:
    """
    Formula: ceil((T_in * P_in + T_out * P_out) * M_platform * M_density / R_credit)
    Where:
      T_in, T_out = token counts
      P_in, P_out = price per 1k tokens (converted to per-token)
      M_platform = platform multiplier (default 15)
      M_density = density multiplier
      R_credit = credit-to-RMB rate (default 0.01)
    """
    prices = MODEL_PRICES.get(model_name)
    if not prices:
        prices = MODEL_PRICES.get("deepseek_v3", {"input": 0.001, "output": 0.002})

    p_in = prices["input"] / 1000.0
    p_out = prices["output"] / 1000.0

    raw_cost = input_tokens * p_in + output_tokens * p_out

    m_density = settings.DENSITY_MULTIPLIERS.get(density_level, 1.0)

    credits = raw_cost * settings.PLATFORM_MULTIPLIER * m_density / settings.CREDIT_TO_RMB_RATE

    return math.ceil(credits)


def estimate_credits(density_level: str) -> int:
    """Approximate credits for preview based on average token usage."""
    avg_input = 2000
    avg_output = 1500

    return calculate_credits(avg_input, avg_output, "deepseek_v3", density_level)
