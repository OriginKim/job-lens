from collections import Counter
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Job
from app.core.normalizer import str_to_skills
from app.core.rag import query as rag_query

router = APIRouter(tags=["roadmap"])

VALID_JOB_TYPES = {"backend", "qa", "ai_verification"}
VALID_CAREER_TYPES = {"entry", "experienced", "any"}

ROADMAP_PROMPT_TEMPLATE = """직군: {job_type_label}
경력 조건: {career_label}

위 직군으로 취업하려는 사람을 위해, 채용공고 데이터를 바탕으로 학습 로드맵을 만들어주세요.
단순 빈도 나열이 아니라 "먼저 배워야 할 기술 → 이후에 추가할 기술" 순서로 작성하세요.
각 단계마다 기술명과 그 이유를 간단히 써주세요. 최대 8단계."""

JOB_TYPE_LABELS: dict[str, str] = {
    "backend": "백엔드 개발자",
    "qa": "QA 엔지니어",
    "ai_verification": "AI 검증 엔지니어",
}
CAREER_LABELS: dict[str, str] = {
    "entry": "신입",
    "experienced": "경력",
    "any": "경력무관",
}


class RoadmapStep(BaseModel):
    order: int
    skill: str
    reason: str


class RoadmapResponse(BaseModel):
    job_type: str
    career_type: Optional[str]
    top_skills: list[str]
    roadmap_text: str


@router.get("/roadmap", response_model=RoadmapResponse)
def get_roadmap(
    job_type: str,
    career_type: Optional[str] = None,
    db: Session = Depends(get_db),
) -> RoadmapResponse:
    if job_type not in VALID_JOB_TYPES:
        raise HTTPException(status_code=422, detail=f"job_type은 {VALID_JOB_TYPES} 중 하나여야 합니다.")
    if career_type and career_type not in VALID_CAREER_TYPES:
        raise HTTPException(status_code=422, detail=f"career_type은 {VALID_CAREER_TYPES} 중 하나여야 합니다.")

    stmt = select(Job).where(Job.job_type == job_type)
    if career_type:
        stmt = stmt.where(Job.career_type == career_type)
    jobs = db.execute(stmt).scalars().all()

    counter: Counter = Counter()
    for job in jobs:
        for skill in str_to_skills(job.skills_normalized or ""):
            counter[skill] += 1
    top_skills = [s for s, _ in counter.most_common(10)]

    question = ROADMAP_PROMPT_TEMPLATE.format(
        job_type_label=JOB_TYPE_LABELS.get(job_type, job_type),
        career_label=CAREER_LABELS.get(career_type or "any", "경력무관"),
    )

    try:
        roadmap_text, _ = rag_query(question=question, job_type=job_type, career_type=career_type, top_k=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RoadmapResponse(
        job_type=job_type,
        career_type=career_type,
        top_skills=top_skills,
        roadmap_text=roadmap_text,
    )
