from typing import Any

from google import genai

from app.config import settings
from app.core.embedder import embed_text
from app.core.indexer import search_jobs

GENERATE_MODEL = "gemini-2.0-flash"

SYSTEM_PROMPT = """당신은 IT 채용 시장 분석 전문가입니다.
아래 채용공고 데이터를 참고하여 질문에 정확하고 유용하게 답변하세요.

규칙:
- 공고 데이터에 근거한 사실만 답변하세요.
- 답변 마지막에 반드시 "출처: 회사명1, 회사명2, ..." 형식으로 참고 공고를 명시하세요.
- 한국어로 답변하세요."""


def _build_where_filter(
    job_type: str | None,
    career_type: str | None,
    region: str | None,
) -> dict[str, Any] | None:
    conditions: list[dict[str, Any]] = []

    if job_type:
        conditions.append({"job_type": {"$eq": job_type}})
    if career_type:
        conditions.append({"career_type": {"$eq": career_type}})
    if region:
        conditions.append({"region": {"$contains": region}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def _build_context(contexts: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for i, ctx in enumerate(contexts, 1):
        lines.append(
            f"[공고 {i}] {ctx.get('company_name', '')} | {ctx.get('title', '')} | "
            f"직군: {ctx.get('job_type', '')} | 기술: {ctx.get('skills', '')} | "
            f"지역: {ctx.get('region', '')}"
        )
    return "\n".join(lines)


def query(
    question: str,
    job_type: str | None = None,
    career_type: str | None = None,
    region: str | None = None,
    top_k: int | None = None,
) -> tuple[str, list[str]]:
    k = top_k or settings.top_k
    query_embedding = embed_text(question)
    where = _build_where_filter(job_type, career_type, region)
    contexts = search_jobs(query_embedding, n_results=k, where=where)

    if not contexts:
        return "관련 채용공고를 찾을 수 없습니다.", []

    context_text = _build_context(contexts)
    prompt = f"""{SYSTEM_PROMPT}

채용공고 데이터:
{context_text}

질문: {question}"""

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(model=GENERATE_MODEL, contents=prompt)
    answer = response.text or ""

    sources = list(dict.fromkeys(
        ctx["company_name"] for ctx in contexts if ctx.get("company_name")
    ))
    return answer, sources
