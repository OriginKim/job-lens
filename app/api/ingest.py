import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.collector import collect_all
from app.core.indexer import index_jobs
from app.db.crud import upsert_jobs
from app.db.database import get_db

router = APIRouter(tags=["ingest"])


class IngestRequest(BaseModel):
    limit: int = 500
    job_type: Optional[str] = None


class IngestResponse(BaseModel):
    collected: int
    failed: int
    saved: int
    indexed: int
    elapsed_seconds: float


@router.post("/ingest", response_model=IngestResponse)
def ingest_jobs(request: IngestRequest, db: Session = Depends(get_db)) -> IngestResponse:
    start = time.time()

    try:
        jobs, failed = collect_all(limit=request.limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"수집 실패: {e}")

    try:
        saved = upsert_jobs(db, jobs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {e}")

    try:
        indexed = index_jobs(jobs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인덱싱 실패: {e}")

    return IngestResponse(
        collected=len(jobs),
        failed=failed,
        saved=saved,
        indexed=indexed,
        elapsed_seconds=round(time.time() - start, 2),
    )
