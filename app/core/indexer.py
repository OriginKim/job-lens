from typing import Any
import chromadb
from app.config import settings

_client: chromadb.PersistentClient | None = None


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_path)
    return _client


def get_collection(name: str = "jobs") -> chromadb.Collection:
    return get_chroma_client().get_or_create_collection(name)


def index_jobs(jobs: list[dict[str, Any]]) -> int:
    raise NotImplementedError


def search_jobs(
    query_embedding: list[float],
    n_results: int,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    raise NotImplementedError
