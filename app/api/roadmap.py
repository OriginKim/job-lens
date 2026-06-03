from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["roadmap"])


class RoadmapStep(BaseModel):
    order: int
    skill: str
    reason: str


class RoadmapResponse(BaseModel):
    job_type: str
    career_type: Optional[str]
    steps: list[RoadmapStep]


@router.get("/roadmap", response_model=RoadmapResponse)
async def get_roadmap(
    job_type: str,
    career_type: Optional[str] = None,
) -> RoadmapResponse:
    raise NotImplementedError
