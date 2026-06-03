from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Job
from app.core.normalizer import str_to_skills

router = APIRouter(prefix="/stats", tags=["stats"])

VALID_JOB_TYPES = {"backend", "qa", "ai_verification"}
VALID_CAREER_TYPES = {"entry", "experienced", "any"}


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


def _aggregate_skills(jobs: list[Job], top_n: int) -> tuple[int, list[SkillStat]]:
    counter: Counter = Counter()
    for job in jobs:
        for skill in str_to_skills(job.skills_normalized or ""):
            counter[skill] += 1

    total = len(jobs)
    stats = [
        SkillStat(skill=skill, count=count, ratio=round(count / total, 4) if total else 0.0)
        for skill, count in counter.most_common(top_n)
    ]
    return total, stats


@router.get("/skills", response_model=SkillsResponse)
def get_skill_stats(
    job_type: Optional[str] = None,
    career_type: Optional[str] = None,
    top_n: int = 10,
    db: Session = Depends(get_db),
) -> SkillsResponse:
    if job_type and job_type not in VALID_JOB_TYPES:
        raise HTTPException(status_code=422, detail=f"job_type은 {VALID_JOB_TYPES} 중 하나여야 합니다.")
    if career_type and career_type not in VALID_CAREER_TYPES:
        raise HTTPException(status_code=422, detail=f"career_type은 {VALID_CAREER_TYPES} 중 하나여야 합니다.")

    stmt = select(Job)
    if job_type:
        stmt = stmt.where(Job.job_type == job_type)
    if career_type:
        stmt = stmt.where(Job.career_type == career_type)

    jobs = db.execute(stmt).scalars().all()
    total, skills = _aggregate_skills(list(jobs), top_n)

    return SkillsResponse(job_type=job_type, career_type=career_type, total_jobs=total, skills=skills)


@router.get("/trend", response_model=TrendResponse)
def get_trend(
    job_type: Optional[str] = None,
    db: Session = Depends(get_db),
) -> TrendResponse:
    if job_type and job_type not in VALID_JOB_TYPES:
        raise HTTPException(status_code=422, detail=f"job_type은 {VALID_JOB_TYPES} 중 하나여야 합니다.")

    cutoff = datetime.utcnow() - timedelta(days=30)
    stmt = select(Job).where(Job.posted_at >= cutoff)
    if job_type:
        stmt = stmt.where(Job.job_type == job_type)

    jobs = db.execute(stmt).scalars().all()
    total, skills = _aggregate_skills(list(jobs), top_n=20)

    return TrendResponse(job_type=job_type, period_days=30, skills=skills)
