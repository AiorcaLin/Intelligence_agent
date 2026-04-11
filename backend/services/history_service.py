from __future__ import annotations

import uuid

from backend.utils.embedding import search_similar


class HistoryService:
    async def get_related_history(
        self,
        embedding_id: str,
        user_id: uuid.UUID,
        domain: str | None = None,
        top_k: int = 5,
        min_score: float = 0.7,
    ) -> list[dict]:
        filters: dict = {"user_id": str(user_id)}
        if domain:
            filters["domain"] = domain

        results = await search_similar(
            query_embedding_id=embedding_id,
            filters=filters,
            top_k=top_k,
            min_score=min_score,
        )

        return [
            {
                "report_id": r["id"],
                "title": r["metadata"].get("title", ""),
                "domain": r["metadata"].get("domain", ""),
                "similarity": r["score"],
                "created_at": r["metadata"].get("created_at"),
            }
            for r in results
        ]
