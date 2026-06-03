from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["ingest"])


class IngestRequest(BaseModel):
    limit: int = 500


class IngestResponse(BaseModel):
    collected: int
    failed: int
    indexed: int
    elapsed_seconds: float


@router.post("/ingest", response_model=IngestResponse)
async def ingest_jobs(request: IngestRequest) -> IngestResponse:
    raise NotImplementedError
