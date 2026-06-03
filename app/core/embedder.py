from typing import Optional
from google import genai
from app.config import settings

_client: Optional[genai.Client] = None
EMBED_MODEL = "gemini-embedding-001"
BATCH_SIZE = 20


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def embed_texts(texts: list[str]) -> list[list[float]]:
    client = _get_client()
    results: list[list[float]] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = client.models.embed_content(model=EMBED_MODEL, contents=batch)
        results.extend(e.values for e in response.embeddings)

    return results


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]


def build_job_document(job: dict) -> str:
    parts = [
        job.get("title", ""),
        job.get("company_name", ""),
        job.get("description", ""),
        job.get("skills_normalized", ""),
        job.get("region", ""),
    ]
    return " | ".join(p for p in parts if p)
