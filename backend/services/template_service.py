from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.template import Template, TemplateTrial
from backend.models.template_contributor import TemplateContributor


class TemplateService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_templates(
        self,
        domain: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Template], int]:
        query = select(Template).where(Template.is_active.is_(True))
        count_query = select(func.count(Template.id)).where(Template.is_active.is_(True))

        if domain:
            query = query.where(Template.domain == domain)
            count_query = count_query.where(Template.domain == domain)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        result = await self.db.execute(
            query.order_by(Template.adoption_count.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    async def get_template_detail(self, template_id: uuid.UUID) -> Template:
        result = await self.db.execute(
            select(Template).where(Template.id == template_id)
        )
        template = result.scalar_one_or_none()
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        return template

    async def get_lineage(self, template_id: uuid.UUID) -> list[dict]:
        """Recursive CTE to build ancestor lineage chain."""
        cte_query = text("""
            WITH RECURSIVE lineage AS (
                SELECT id, name, creator_type, creator_id, parent_template_id, 0 AS depth
                FROM templates
                WHERE id = :tid
                UNION ALL
                SELECT t.id, t.name, t.creator_type, t.creator_id, t.parent_template_id, l.depth + 1
                FROM templates t
                INNER JOIN lineage l ON t.id = l.parent_template_id
            )
            SELECT id, name, creator_type, creator_id, depth
            FROM lineage
            ORDER BY depth ASC
        """)
        result = await self.db.execute(cte_query, {"tid": template_id})
        rows = result.fetchall()
        return [
            {
                "id": row.id,
                "name": row.name,
                "creator_type": row.creator_type,
                "creator_id": row.creator_id,
                "depth": row.depth,
            }
            for row in rows
        ]

    async def try_template(self, template_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        template = await self.get_template_detail(template_id)

        existing = await self.db.execute(
            select(TemplateTrial).where(
                and_(
                    TemplateTrial.template_id == template_id,
                    TemplateTrial.user_id == user_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="您已试用过此模板")

        trial = TemplateTrial(template_id=template_id, user_id=user_id)
        self.db.add(trial)
        await self.db.flush()

        return {
            "ok": True,
            "template_name": template.name,
            "message": "试用已开始，将生成一份示例报告",
        }

    async def adopt_template(self, template_id: uuid.UUID, user_id: uuid.UUID) -> None:
        template = await self.get_template_detail(template_id)
        template.adoption_count = (template.adoption_count or 0) + 1
        await self.db.flush()

    async def fork_template(
        self, template_id: uuid.UUID, user_id: uuid.UUID, new_config: dict
    ) -> Template:
        parent = await self.get_template_detail(template_id)

        forked = Template(
            name=new_config.get("name", f"{parent.name} (Fork)"),
            description=new_config.get("description", parent.description),
            domain=parent.domain,
            parent_template_id=parent.id,
            creator_type="human",
            creator_id=user_id,
            prompt_config=new_config.get("prompt_config", parent.prompt_config),
            version=1,
        )
        self.db.add(forked)
        await self.db.flush()
        await self.db.refresh(forked)
        return forked

    @staticmethod
    def calculate_revenue_split(
        credits_consumed: float,
        lineage: list[dict],
    ) -> dict[str, float]:
        """
        Revenue split:
        - Platform: 67%
        - Creator (immediate parent): 20%
        - Contributors (along lineage, by score): 10%
        - Operations: 3%
        """
        total = Decimal(str(credits_consumed))
        platform_share = float(total * Decimal("0.67"))
        creator_share = float(total * Decimal("0.20"))
        contributor_pool = float(total * Decimal("0.10"))
        operations_share = float(total * Decimal("0.03"))

        distribution: dict[str, float] = {"platform": platform_share, "operations": operations_share}

        if lineage and len(lineage) > 1:
            creator_node = lineage[1]
            if creator_node.get("creator_id"):
                distribution[str(creator_node["creator_id"])] = creator_share
            else:
                distribution["platform"] = platform_share + creator_share

            contributor_nodes = lineage[2:]
            if contributor_nodes:
                per_contributor = contributor_pool / len(contributor_nodes)
                for node in contributor_nodes:
                    cid = str(node.get("creator_id", "platform"))
                    distribution[cid] = distribution.get(cid, 0) + per_contributor
            else:
                distribution["platform"] = distribution.get("platform", 0) + contributor_pool
        else:
            distribution["platform"] = platform_share + creator_share + contributor_pool

        return distribution
