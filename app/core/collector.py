from typing import Any
import httpx
from app.config import settings

WORKNET_BASE_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callWkOccupationInfoSrch.do"

JOB_TYPE_KEYWORDS: dict[str, list[str]] = {
    "backend": ["백엔드", "서버", "Java", "Spring"],
    "qa": ["QA", "품질보증", "테스트", "소프트웨어 검증"],
    "ai_verification": ["AI 검증", "AI 신뢰성", "ML 엔지니어", "AI QA"],
}


def fetch_jobs(job_type: str, limit: int) -> list[dict[str, Any]]:
    raise NotImplementedError


def collect_all(limit: int = 500) -> tuple[list[dict[str, Any]], int]:
    raise NotImplementedError
