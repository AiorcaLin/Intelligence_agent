from __future__ import annotations

import re

SENSITIVE_PATTERNS: list[str] = [
    r"翻墙",
    r"VPN",
    r"色情",
    r"赌博",
    r"毒品",
    r"枪支",
    r"暴力恐怖",
    r"邪教",
    r"传销",
    r"洗钱",
]

_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in SENSITIVE_PATTERNS]


def check_compliance(text: str) -> tuple[bool, list[str]]:
    """
    Basic sensitive content detection for Chinese compliance.
    Returns (is_safe, reasons).
    """
    if not text:
        return True, []

    reasons: list[str] = []
    for pattern in _compiled_patterns:
        if pattern.search(text):
            reasons.append(f"包含敏感内容: {pattern.pattern}")

    is_safe = len(reasons) == 0
    return is_safe, reasons
