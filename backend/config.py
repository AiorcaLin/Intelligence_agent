from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/intel_agent"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── LLM Keys ─────────────────────────────────────────────
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    CLAUDE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # ── Embedding ─────────────────────────────────────────────
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    # 留空 = OpenAI 官方 (api.openai.com)；填入则走自定义 OpenAI 兼容端点
    EMBEDDING_BASE_URL: str = ""
    # 留空 = 使用 OPENAI_API_KEY；填入则覆盖（用于独立嵌入服务商的 Key）
    EMBEDDING_API_KEY: str = ""

    # ── Credits / Pricing ─────────────────────────────────────
    PLATFORM_MULTIPLIER: float = 15.0
    CREDIT_TO_RMB_RATE: float = 0.01
    DAILY_FREE_CREDITS: int = 50
    DENSITY_MULTIPLIERS: dict[str, float] = {
        "quick_scan": 0.6,
        "standard": 1.0,
        "research": 2.0,
    }

    # ── Twitter ───────────────────────────────────────────────
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN_SECRET: str = ""
    TWITTER_BEARER_TOKEN: str = ""

    # ── Telegram ──────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = ""

    # ── Payment ───────────────────────────────────────────────
    PAYMENT_PROVIDER: str = "mock"
    PAYMENT_SECRET: str = ""

    # ── R2 / Object Storage ───────────────────────────────────
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "intel-agent"
    R2_PUBLIC_URL: str = ""

    # ── App ───────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── Celery ────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
