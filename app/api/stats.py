from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/stats", tags=["stats"])


class SkillStat(BaseModel):
    skill: str
    count: int
    ratio: float


class SkillsResponse(BaseModel):
    job_type: Optional[str]
    career_type: Optional[str]
    total_jobs: int
    skills: list[SkillStat]


class TrendResponse(BaseModel):
    job_type: Optional[str]
    period_days: int
    skills: list[SkillStat]


@router.get("/skills", response_model=SkillsResponse)
async def get_skill_stats(
    job_type: Optional[str] = None,
    career_type: Optional[str] = None,
    top_n: int = 10,
) -> SkillsResponse:
    raise NotImplementedError


@router.get("/trend", response_model=TrendResponse)
async def get_trend(job_type: Optional[str] = None) -> TrendResponse:
    raise NotImplementedError
