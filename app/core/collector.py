import time
from typing import Any
from datetime import datetime

import httpx

from app.config import settings

WORKNET_LIST_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callWkOccupationInfoSrch.do"
WORKNET_DETAIL_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callWkJobDetailInfo.do"
PAGE_SIZE = 100
REQUEST_DELAY = 0.3

JOB_TYPE_KEYWORDS: dict[str, list[str]] = {
    "backend": ["백엔드", "서버개발", "Java", "Spring"],
    "qa": ["QA", "품질보증", "테스트엔지니어", "소프트웨어검증"],
    "ai_verification": ["AI검증", "AI신뢰성", "ML엔지니어", "AI QA"],
}

CAREER_TYPE_MAP: dict[str, str] = {
    "0": "any",
    "1": "entry",
    "2": "experienced",
}


def _fetch_list_page(keyword: str, page: int) -> dict[str, Any]:
    params = {
        "authKey": settings.worknet_api_key,
        "callTp": "L",
        "returnType": "JSON",
        "startPage": page,
        "display": PAGE_SIZE,
        "keyword": keyword,
    }
    response = httpx.get(WORKNET_LIST_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _fetch_detail(wanted_no: str) -> dict[str, Any]:
    params = {
        "authKey": settings.worknet_api_key,
        "callTp": "D",
        "returnType": "JSON",
        "wantedNo": wanted_no,
    }
    response = httpx.get(WORKNET_DETAIL_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _parse_date(date_str: str) -> datetime | None:
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def _extract_raw_skills(detail: dict[str, Any]) -> list[str]:
    skill_fields = [
        detail.get("preferentialTreat", ""),
        detail.get("qualification", ""),
        detail.get("jobCont", ""),
    ]
    combined = " ".join(f for f in skill_fields if f)

    skill_keywords = [
        "Java", "Python", "JavaScript", "TypeScript", "Go", "Kotlin", "C++", "C#", "Ruby",
        "Spring Boot", "Spring", "Django", "FastAPI", "Flask", "Node.js", "React", "Vue",
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Oracle",
        "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Linux",
        "Git", "GitHub", "GitLab", "Jira", "Confluence",
        "Selenium", "Pytest", "JUnit", "TestNG", "Appium", "JMeter",
        "TensorFlow", "PyTorch", "scikit-learn", "MLflow",
        "SQL", "REST", "GraphQL", "gRPC", "Kafka", "RabbitMQ",
        "Jenkins", "GitHub Actions", "CI/CD",
    ]

    found = []
    combined_lower = combined.lower()
    for kw in skill_keywords:
        if kw.lower() in combined_lower:
            found.append(kw)
    return found


def fetch_jobs(job_type: str, limit: int) -> tuple[list[dict[str, Any]], int]:
    keywords = JOB_TYPE_KEYWORDS[job_type]
    seen: dict[str, dict[str, Any]] = {}
    failed = 0
    per_keyword = max(1, limit // len(keywords))

    for keyword in keywords:
        page = 1
        keyword_count = 0

        while keyword_count < per_keyword:
            try:
                data = _fetch_list_page(keyword, page)
                items = data.get("HireInfo", {}).get("wanted", [])
                if not items:
                    break

                for item in items:
                    wanted_no = item.get("wantedNo", "")
                    if not wanted_no or wanted_no in seen:
                        continue

                    try:
                        time.sleep(REQUEST_DELAY)
                        detail_data = _fetch_detail(wanted_no)
                        detail = detail_data.get("HireInfo", {}).get("wantedInfo", {})
                    except Exception:
                        failed += 1
                        detail = {}

                    raw_skills = _extract_raw_skills(detail)

                    seen[wanted_no] = {
                        "job_id": wanted_no,
                        "company_name": item.get("company", "").strip(),
                        "title": item.get("title", "").strip(),
                        "job_type": job_type,
                        "career_type": CAREER_TYPE_MAP.get(str(item.get("careerCd", "0")), "any"),
                        "region": item.get("region", "").strip(),
                        "skills_raw": ",".join(raw_skills),
                        "description": detail.get("jobCont", item.get("title", "")),
                        "posted_at": _parse_date(item.get("regDt", "")),
                    }
                    keyword_count += 1

                    if keyword_count >= per_keyword:
                        break

                page += 1
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
