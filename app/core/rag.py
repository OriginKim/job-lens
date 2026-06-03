from typing import Any
from google import genai
from app.config import settings
from app.core.embedder import get_client

RAG_SYSTEM_PROMPT = """당신은 IT 채용 시장 분석 전문가입니다.
제공된 채용공고 데이터를 바탕으로 정확하고 유용한 답변을 제공하세요.
답변 마지막에는 참고한 공고의 회사명을 반드시 명시하세요."""


def generate_answer(question: str, contexts: list[dict[str, Any]]) -> tuple[str, list[str]]:
    raise NotImplementedError


def query(
    question: str,
    job_type: str | None = None,
    career_type: str | None = None,
    region: str | None = None,
    top_k: int | None = None,
) -> tuple[str, list[str]]:
    raise NotImplementedError
