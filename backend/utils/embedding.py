from __future__ import annotations

import logging
from typing import Any

import chromadb
import openai

from backend.config import settings

logger = logging.getLogger(__name__)

_chroma_client: chromadb.HttpClient | None = None
_openai_client: openai.AsyncOpenAI | None = None

COLLECTION_NAME = "intel_reports"


def _get_chroma() -> chromadb.HttpClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
    return _chroma_client


def _get_embedding_client() -> openai.AsyncOpenAI:
    """返回嵌入客户端。
    - EMBEDDING_BASE_URL 为空  → OpenAI 官方 (api.openai.com)
    - EMBEDDING_BASE_URL 非空 → 任意 OpenAI 兼容端点（OpenRouter / SiliconFlow / DashScope …）
    """
    global _openai_client
    if _openai_client is None:
        api_key = settings.EMBEDDING_API_KEY or settings.OPENAI_API_KEY
        kwargs: dict = {"api_key": api_key}
        if settings.EMBEDDING_BASE_URL:
            kwargs["base_url"] = settings.EMBEDDING_BASE_URL
        _openai_client = openai.AsyncOpenAI(**kwargs)
    return _openai_client


async def generate_embedding(text: str) -> list[float]:
    """生成嵌入向量。服务商由 EMBEDDING_BASE_URL / EMBEDDING_API_KEY 配置决定。"""
    client = _get_embedding_client()
    kwargs: dict = {
        "model": settings.EMBEDDING_MODEL,
        "input": text,
    }
    # dimensions 参数仅 OpenAI 官方支持截断；第三方端点不传，避免报错
    if not settings.EMBEDDING_BASE_URL and settings.EMBEDDING_DIMENSIONS:
        kwargs["dimensions"] = settings.EMBEDDING_DIMENSIONS
    response = await client.embeddings.create(**kwargs)
    return response.data[0].embedding


def store_embedding(
    doc_id: str,
    embedding: list[float],
    metadata: dict[str, Any],
) -> None:
    """Store embedding in ChromaDB."""
    client = _get_chroma()
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        metadatas=[metadata],
    )


async def search_similar(
    query_embedding_id: str | None = None,
    query_embedding: list[float] | None = None,
    filters: dict | None = None,
    top_k: int = 5,
    min_score: float = 0.7,
) -> list[dict]:
    """Search ChromaDB for similar documents."""
    client = _get_chroma()
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    if query_embedding is None and query_embedding_id:
        try:
            result = collection.get(ids=[query_embedding_id], include=["embeddings"])
            if result["embeddings"]:
                query_embedding = result["embeddings"][0]
        except Exception:
            logger.warning("Could not retrieve embedding for id %s", query_embedding_id)
            return []

    if query_embedding is None:
        return []

    where_filter = None
    if filters:
        conditions = [
            {k: {"$eq": v}} for k, v in filters.items()
        ]
        if len(conditions) == 1:
            where_filter = conditions[0]
        elif len(conditions) > 1:
            where_filter = {"$and": conditions}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
    )

    output: list[dict] = []
    if results and results["ids"]:
        for i, doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results.get("distances") else 0
            score = 1.0 - distance
            if score >= min_score:
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                output.append({
                    "id": doc_id,
                    "score": score,
                    "metadata": metadata,
                })

    return output
