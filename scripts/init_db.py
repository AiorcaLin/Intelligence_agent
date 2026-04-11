"""
数据库初始化脚本 - 创建所有数据表。

用法：python -m scripts.init_db
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def init_db() -> None:
    """创建数据库中的所有表。"""
    try:
        from backend.database import engine, Base
        from backend.models import *  # noqa: F401,F403  — import all models to register them

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables created successfully.")

    except ImportError as e:
        logger.error("Failed to import database modules: %s", e)
        logger.error("Make sure backend/database.py and backend/models/ exist.")
        sys.exit(1)

    except Exception as e:
        logger.error("Database initialization failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_db())
