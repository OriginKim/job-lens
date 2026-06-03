import time
from datetime import datetime
from typing import Any

import httpx

from app.config import settings

SARAMIN_API_URL = "https://oapi.saramin.co.kr/job-search"
PAGE_SIZE = 110
REQUEST_DELAY = 0.5

JOB_TYPE_KEYWORDS: dict[str, list[str]] = {
    "backend": ["백엔드", "서버개발", "Java개발자", "Spring"],
    "qa": ["QA엔지니어", "품질보증", "테스트엔지니어", "소프트웨어테스트"],
    "ai_verification": ["AI검증", "AI신뢰성", "ML엔지니어", "AI QA"],
}


def _fetch_page(keyword: str, start: int) -> dict[str, Any]:
    params = {
        "access-key": settings.saramin_api_key,
        "keywords": keyword,
        "start": start,
        "count": PAGE_SIZE,
        "fields": "posting-date,keywords,position,company",
    }
    response = httpx.get(SARAMIN_API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _parse_career_type(exp_code: int) -> str:
    if exp_code == 1:
        return "entry"
    if exp_code >= 2:
        return "experienced"
    return "any"


def _parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str[:19])
    except (ValueError, TypeError):
        return None


def _parse_job(item: dict[str, Any], job_type: str) -> dict[str, Any]:
    position = item.get("position", {})
    exp_code = int(position.get("experience-level", {}).get("code", 0))
    keywords_str = item.get("keywords", "")
    raw_skills = [s.strip() for s in keywords_str.split(",") if s.strip()]

    return {
        "job_id": str(item.get("id", "")),
        "company_name": item.get("company", {}).get("detail", {}).get("name", ""),
        "title": position.get("title", ""),
        "job_type": job_type,
        "career_type": _parse_career_type(exp_code),
        "region": position.get("location", {}).get("name", ""),
        "skills_raw": ",".join(raw_skills),
        "description": position.get("title", ""),
        "posted_at": _parse_date(item.get("posting-date", "")),
    }


def fetch_jobs(job_type: str, limit: int) -> tuple[list[dict[str, Any]], int]:
    keywords = JOB_TYPE_KEYWORDS[job_type]
    seen: dict[str, dict[str, Any]] = {}
    failed = 0
    per_keyword = max(1, limit // len(keywords))

    for keyword in keywords:
        start = 0
        keyword_count = 0

        while keyword_count < per_keyword:
            try:
                data = _fetch_page(keyword, start)
                jobs_wrapper = data.get("jobs", {})
                total = int(jobs_wrapper.get("total", 0))
                items = jobs_wrapper.get("jobs", {}).get("job", [])

                if not items:
                    break
                if isinstance(items, dict):
                    items = [items]

                for item in items:
                    job_id = str(item.get("id", ""))
                    if not job_id or job_id in seen:
                        continue
                    seen[job_id] = _parse_job(item, job_type)
                    keyword_count += 1
                    if keyword_count >= per_keyword:
                        break

                start += PAGE_SIZE
                if start >= total:
                    break
                time.sleep(REQUEST_DELAY)

            except Exception:
                failed += 1
                break

    return list(seen.values()), failed


def collect_all(limit: int = 500) -> tuple[list[dict[str, Any]], int]:
    all_jobs: list[dict[str, Any]] = []
    total_failed = 0
    per_type = max(1, limit // len(JOB_TYPE_KEYWORDS))

    for job_type in JOB_TYPE_KEYWORDS:
        print(f"[collector] {job_type} 수집 중...")
        jobs, failed = fetch_jobs(job_type, per_type)
        all_jobs.extend(jobs)
        total_failed += failed
        print(f"[collector] {job_type}: {len(jobs)}건 수집, {failed}건 실패")

    return all_jobs, total_failed
