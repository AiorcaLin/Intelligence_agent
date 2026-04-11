"""
模板种子数据脚本 - 从 templates/ 目录读取 YAML 并写入数据库。

用法：python -m scripts.seed_templates
"""

import asyncio
import logging
import sys
from pathlib import Path
from uuid import uuid4

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def seed_templates() -> None:
    """读取所有模板 YAML 文件并写入数据库。"""
    try:
        from sqlalchemy import select
        from backend.database import async_session
        from backend.models.template import Template
    except ImportError as e:
        logger.error("Failed to import required modules: %s", e)
        logger.error("Make sure backend/database.py and backend/models/template.py exist.")
        sys.exit(1)

    templates_dir = Path(__file__).parent.parent / "templates"
    if not templates_dir.exists():
        logger.error("Templates directory not found: %s", templates_dir)
        sys.exit(1)

    yaml_files = list(templates_dir.glob("*.yaml"))
    if not yaml_files:
        logger.warning("No YAML files found in %s", templates_dir)
        return

    logger.info("Found %d template files.", len(yaml_files))

    async with async_session() as session:
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                if not config or "template" not in config:
                    logger.warning("Skipping %s: missing 'template' key.", yaml_file.name)
                    continue

                template_data = config["template"]

                existing = await session.execute(
                    select(Template).where(Template.name == template_data["name"])
                )
                if existing.scalar_one_or_none():
                    logger.info("Template '%s' already exists, skipping.", template_data["name"])
                    continue

                template = Template(
                    id=uuid4(),
                    name=template_data["name"],
                    description=template_data["description"],
                    domain=template_data["domain"],
                    creator_type=template_data["creator_type"],
                    prompt_config=config.get("prompt_config", {}),
                    version=template_data.get("version", 1),
                )
                session.add(template)
                logger.info("Seeded template: %s", template_data["name"])

            except yaml.YAMLError as e:
                logger.error("Failed to parse %s: %s", yaml_file.name, e)
            except KeyError as e:
                logger.error("Missing required field in %s: %s", yaml_file.name, e)
            except Exception as e:
                logger.error("Error processing %s: %s", yaml_file.name, e)

        await session.commit()

    logger.info("Template seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed_templates())
