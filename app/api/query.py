from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core import rag

router = APIRouter(tags=["query"])

VALID_JOB_TYPES = {"backend", "qa", "ai_verification"}
VALID_CAREER_TYPES = {"entry", "experienced", "any"}


class QueryRequest(BaseModel):
    question: str
    job_type: Optional[str] = None
    career_type: Optional[str] = None
    region: Optional[str] = None
    top_k: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("/query", response_model=QueryResponse)
async def query_jobs(request: QueryRequest) -> QueryResponse:
    if request.job_type and request.job_type not in VALID_JOB_TYPES:
        raise HTTPException(status_code=422, detail=f"job_type은 {VALID_JOB_TYPES} 중 하나여야 합니다.")
    if request.career_type and request.career_type not in VALID_CAREER_TYPES:
        raise HTTPException(status_code=422, detail=f"career_type은 {VALID_CAREER_TYPES} 중 하나여야 합니다.")

    try:
        answer, sources = rag.query(
            question=request.question,
            job_type=request.job_type,
            career_type=request.career_type,
            region=request.region,
            top_k=request.top_k,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return QueryResponse(answer=answer, sources=sources)
