from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert

from app.db.models import Job
from app.core.normalizer import normalize_skills, skills_to_str, str_to_skills


def upsert_jobs(db: Session, jobs: list[dict[str, Any]]) -> int:
    if not jobs:
        return 0

    rows = []
    for job in jobs:
        raw_skills = str_to_skills(job.get("skills_raw", ""))
        normalized = normalize_skills(raw_skills)
        rows.append({
            "job_id": job["job_id"],
            "company_name": job["company_name"],
            "title": job["title"],
            "job_type": job["job_type"],
            "career_type": job.get("career_type"),
            "region": job.get("region"),
            "skills_raw": job.get("skills_raw", ""),
            "skills_normalized": skills_to_str(normalized),
            "description": job.get("description", ""),
            "posted_at": job.get("posted_at"),
        })

    stmt = insert(Job).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["job_id"],
        set_={
            "company_name": stmt.excluded.company_name,
            "title": stmt.excluded.title,
            "skills_raw": stmt.excluded.skills_raw,
            "skills_normalized": stmt.excluded.skills_normalized,
            "description": stmt.excluded.description,
        },
    )
    db.execute(stmt)
    db.commit()
    return len(rows)
