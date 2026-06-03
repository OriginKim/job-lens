from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["query"])


class QueryRequest(BaseModel):
    question: str
    job_type: Optional[str] = None
    career_type: Optional[str] = None
    region: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("/query", response_model=QueryResponse)
async def query_jobs(request: QueryRequest) -> QueryResponse:
    raise NotImplementedError
