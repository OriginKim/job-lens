from typing import Any, Optional

import chromadb
import chromadb.api

from app.config import settings
from app.core.embedder import embed_texts, build_job_document
from app.core.normalizer import str_to_skills

JOB_COLLECTION = "jobs"
SKILL_COLLECTION = "skills"
BATCH_SIZE = 50

_client: Optional[chromadb.api.ClientAPI] = None


def _get_client() -> chromadb.api.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_path)
    return _client


def get_collection(name: str) -> chromadb.api.models.Collection.Collection:
    return _get_client().get_or_create_collection(name)


def _index_job_chunks(jobs: list[dict[str, Any]]) -> int:
    collection = get_collection(JOB_COLLECTION)
    total = 0

    for i in range(0, len(jobs), BATCH_SIZE):
        batch = jobs[i : i + BATCH_SIZE]
        documents = [build_job_document(j) for j in batch]
        embeddings = embed_texts(documents)
        ids = [f"job_{j['job_id']}" for j in batch]
        metadatas = [
            {
                "job_id": j["job_id"],
                "company_name": j["company_name"],
                "title": j["title"],
                "job_type": j["job_type"],
                "career_type": j.get("career_type", "any"),
                "region": j.get("region", ""),
                "skills": j.get("skills_normalized", ""),
            }
            for j in batch
        ]

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        total += len(batch)

    return total


def _index_skill_chunks(jobs: list[dict[str, Any]]) -> int:
    collection = get_collection(SKILL_COLLECTION)
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for job in jobs:
        skills = str_to_skills(job.get("skills_normalized", ""))
        for skill in skills:
            chunk_id = f"skill_{job['job_id']}_{skill.replace(' ', '_')}"
            ids.append(chunk_id)
            documents.append(f"{skill} | {job['title']} | {job['company_name']} | {job['job_type']}")
            metadatas.append(
                {
                    "skill": skill,
                    "job_id": job["job_id"],
                    "job_type": job["job_type"],
                    "career_type": job.get("career_type", "any"),
                    "region": job.get("region", ""),
                }
            )

    if not ids:
        return 0

    total = 0
    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i : i + BATCH_SIZE]
        batch_docs = documents[i : i + BATCH_SIZE]
        batch_meta = metadatas[i : i + BATCH_SIZE]
        embeddings = embed_texts(batch_docs)
        collection.upsert(ids=batch_ids, embeddings=embeddings, documents=batch_docs, metadatas=batch_meta)
        total += len(batch_ids)

    return total


def index_jobs(jobs: list[dict[str, Any]]) -> int:
    if not jobs:
        return 0
    job_count = _index_job_chunks(jobs)
    skill_count = _index_skill_chunks(jobs)
    print(f"[indexer] job 청크: {job_count}개, skill 청크: {skill_count}개")
    return job_count


def search_jobs(
    query_embedding: list[float],
    n_results: int = 5,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    collection = get_collection(JOB_COLLECTION)
    kwargs: dict[str, Any] = {"query_embeddings": [query_embedding], "n_results": n_results}
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)
    metadatas = results.get("metadatas", [[]])[0]
    documents = results.get("documents", [[]])[0]

    return [
        {**meta, "document": doc}
        for meta, doc in zip(metadatas, documents)
    ]


def get_total_count() -> dict[str, int]:
    return {
        "jobs": get_collection(JOB_COLLECTION).count(),
        "skills": get_collection(SKILL_COLLECTION).count(),
    }
