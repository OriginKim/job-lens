"""더미 채용공고 20건을 SQLite + ChromaDB에 시딩하고 RAG 파이프라인을 검증한다."""

import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import rag
from app.core.indexer import get_total_count, index_jobs
from app.core.normalizer import normalize_skills, skills_to_str, str_to_skills
from app.db.crud import upsert_jobs
from app.db.database import SessionLocal, init_db

DUMMY_JOBS = [
    # ── 백엔드 7건 ──────────────────────────────────────────────────────────
    {
        "job_id": "dummy-backend-001",
        "company_name": "카카오",
        "title": "백엔드 신입 개발자",
        "job_type": "backend",
        "career_type": "entry",
        "region": "경기 성남시",
        "skills_raw": "Java,Spring Boot,MySQL,Git,Docker",
        "description": "Java Spring Boot 기반 백엔드 API 개발. MySQL 설계, Docker 컨테이너 환경 운영.",
        "posted_at": datetime(2026, 5, 20),
    },
    {
        "job_id": "dummy-backend-002",
        "company_name": "네이버",
        "title": "서버 개발자",
        "job_type": "backend",
        "career_type": "experienced",
        "region": "경기 성남시",
        "skills_raw": "Java,Spring Boot,Redis,Docker,Kubernetes,AWS",
        "description": "대규모 트래픽 처리 서버 개발. Redis 캐시 설계, Kubernetes 기반 MSA 운영.",
        "posted_at": datetime(2026, 5, 18),
    },
    {
        "job_id": "dummy-backend-003",
        "company_name": "토스",
        "title": "백엔드 엔지니어 (신입)",
        "job_type": "backend",
        "career_type": "entry",
        "region": "서울 강남구",
        "skills_raw": "Kotlin,Spring Boot,MySQL,Kafka,Git",
        "description": "핀테크 서비스 백엔드 개발. Kotlin Spring Boot REST API 구현, Kafka 이벤트 처리.",
        "posted_at": datetime(2026, 5, 22),
    },
    {
        "job_id": "dummy-backend-004",
        "company_name": "쿠팡",
        "title": "백엔드 개발자 (신입)",
        "job_type": "backend",
        "career_type": "entry",
        "region": "서울 송파구",
        "skills_raw": "Java,Spring Boot,MySQL,Docker,Git,AWS",
        "description": "이커머스 플랫폼 백엔드 서비스 개발. Java Spring Boot API 설계, AWS 클라우드 배포.",
        "posted_at": datetime(2026, 5, 21),
    },
    {
        "job_id": "dummy-backend-005",
        "company_name": "배달의민족",
        "title": "서버 사이드 엔지니어",
        "job_type": "backend",
        "career_type": "experienced",
        "region": "서울 송파구",
        "skills_raw": "Java,Spring Boot,MySQL,Redis,AWS,Kafka",
        "description": "배달 플랫폼 고가용성 서버 설계. Redis 캐싱, Kafka 비동기 처리, AWS 인프라 운영.",
        "posted_at": datetime(2026, 5, 19),
    },
    {
        "job_id": "dummy-backend-006",
        "company_name": "당근마켓",
        "title": "백엔드 개발자",
        "job_type": "backend",
        "career_type": "experienced",
        "region": "서울 마포구",
        "skills_raw": "Go,MySQL,Docker,Kubernetes,AWS,PostgreSQL",
        "description": "Go 기반 마이크로서비스 백엔드 개발. Kubernetes 클러스터 관리, PostgreSQL 최적화.",
        "posted_at": datetime(2026, 5, 17),
    },
    {
        "job_id": "dummy-backend-007",
        "company_name": "라인",
        "title": "신입 백엔드 엔지니어",
        "job_type": "backend",
        "career_type": "entry",
        "region": "서울 강남구",
        "skills_raw": "Java,Spring Boot,PostgreSQL,Docker,Git,REST",
        "description": "글로벌 메신저 플랫폼 백엔드 개발. Java Spring Boot REST API 설계, PostgreSQL 운영.",
        "posted_at": datetime(2026, 5, 23),
    },
    # ── QA 7건 ──────────────────────────────────────────────────────────────
    {
        "job_id": "dummy-qa-001",
        "company_name": "삼성전자",
        "title": "QA 엔지니어 (신입)",
        "job_type": "qa",
        "career_type": "entry",
        "region": "경기 수원시",
        "skills_raw": "Python,Selenium,Jira,Git,SQL",
        "description": "모바일·가전 SW 품질 검증. Python Selenium 자동화 테스트, Jira 이슈 트래킹.",
        "posted_at": datetime(2026, 5, 20),
    },
    {
        "job_id": "dummy-qa-002",
        "company_name": "LG전자",
        "title": "테스트 엔지니어",
        "job_type": "qa",
        "career_type": "experienced",
        "region": "서울 영등포구",
        "skills_raw": "Java,JUnit,Selenium,Jira,SQL,Git",
        "description": "가전 SW 테스트 자동화. Java JUnit 단위 테스트, Selenium E2E 테스트 구축.",
        "posted_at": datetime(2026, 5, 18),
    },
    {
        "job_id": "dummy-qa-003",
        "company_name": "카카오",
        "title": "QA 엔지니어",
        "job_type": "qa",
        "career_type": "experienced",
        "region": "경기 성남시",
        "skills_raw": "Python,Pytest,Selenium,Jira,SQL,Git",
        "description": "카카오 서비스 품질 보증. Python Pytest 자동화, Selenium UI 테스트, SQL 데이터 검증.",
        "posted_at": datetime(2026, 5, 22),
    },
    {
        "job_id": "dummy-qa-004",
        "company_name": "슈어소프트테크",
        "title": "QA 엔지니어 (신입)",
        "job_type": "qa",
        "career_type": "entry",
        "region": "서울 강남구",
        "skills_raw": "Python,Selenium,Jira,Git,SQL,Appium",
        "description": "자동차 SW 품질 검증 신입. Python Selenium/Appium 테스트 자동화, SQL 데이터 검증.",
        "posted_at": datetime(2026, 5, 21),
    },
    {
        "job_id": "dummy-qa-005",
        "company_name": "NHN",
        "title": "소프트웨어 테스트 엔지니어",
        "job_type": "qa",
        "career_type": "entry",
        "region": "경기 성남시",
        "skills_raw": "Python,Pytest,SQL,Jira,Git,Selenium",
        "description": "게임·웹 서비스 QA. Python Pytest 테스트 코드 작성, Jira 이슈 관리, SQL 검증.",
        "posted_at": datetime(2026, 5, 19),
    },
    {
        "job_id": "dummy-qa-006",
        "company_name": "넥슨",
        "title": "QA 엔지니어",
        "job_type": "qa",
        "career_type": "experienced",
        "region": "경기 성남시",
        "skills_raw": "Python,Selenium,JMeter,SQL,Jira,Git",
        "description": "온라인 게임 QA. Python Selenium 자동화, JMeter 성능 테스트, SQL 데이터 검증.",
        "posted_at": datetime(2026, 5, 17),
    },
    {
        "job_id": "dummy-qa-007",
        "company_name": "네이버",
        "title": "품질보증 엔지니어 (신입)",
        "job_type": "qa",
        "career_type": "entry",
        "region": "경기 성남시",
        "skills_raw": "Python,Selenium,Appium,Jira,SQL,Git",
        "description": "네이버 서비스 품질 보증 신입. Python Selenium/Appium 자동화, Jira 이슈 트래킹.",
        "posted_at": datetime(2026, 5, 23),
    },
    # ── AI 검증 6건 ─────────────────────────────────────────────────────────
    {
        "job_id": "dummy-ai-001",
        "company_name": "슈어소프트테크",
        "title": "AI 검증 엔지니어 (신입)",
        "job_type": "ai_verification",
        "career_type": "entry",
        "region": "서울 강남구",
        "skills_raw": "Python,scikit-learn,Git,SQL,TensorFlow",
        "description": "자동차 AI 시스템 신뢰성 검증 신입. Python scikit-learn 모델 평가, 검증 데이터셋 구축.",
        "posted_at": datetime(2026, 5, 20),
    },
    {
        "job_id": "dummy-ai-002",
        "company_name": "LG AI Research",
        "title": "AI 신뢰성 엔지니어",
        "job_type": "ai_verification",
        "career_type": "experienced",
        "region": "서울 강서구",
        "skills_raw": "Python,PyTorch,MLflow,Docker,Git,scikit-learn",
        "description": "LLM 모델 신뢰성 평가. PyTorch 기반 모델 검증, MLflow 실험 관리, Docker 환경 구성.",
        "posted_at": datetime(2026, 5, 18),
    },
    {
        "job_id": "dummy-ai-003",
        "company_name": "삼성리서치",
        "title": "ML 엔지니어",
        "job_type": "ai_verification",
        "career_type": "experienced",
        "region": "서울 서초구",
        "skills_raw": "Python,TensorFlow,PyTorch,Docker,AWS,scikit-learn",
        "description": "비전·언어 AI 모델 검증 및 최적화. TensorFlow PyTorch 모델 평가, AWS GPU 인프라 운영.",
        "posted_at": datetime(2026, 5, 22),
    },
    {
        "job_id": "dummy-ai-004",
        "company_name": "카카오브레인",
        "title": "AI 검증 엔지니어",
        "job_type": "ai_verification",
        "career_type": "experienced",
        "region": "경기 성남시",
        "skills_raw": "Python,PyTorch,scikit-learn,Git,SQL,MLflow",
        "description": "생성형 AI 모델 품질 검증. PyTorch 모델 평가 파이프라인 구축, SQL 데이터 분석.",
        "posted_at": datetime(2026, 5, 21),
    },
    {
        "job_id": "dummy-ai-005",
        "company_name": "네이버 AI Lab",
        "title": "AI QA 엔지니어 (신입)",
        "job_type": "ai_verification",
        "career_type": "entry",
        "region": "경기 성남시",
        "skills_raw": "Python,TensorFlow,Selenium,Git,SQL",
        "description": "AI 서비스 품질 검증 신입. Python TensorFlow 모델 테스트, SQL 데이터 품질 검증.",
        "posted_at": datetime(2026, 5, 19),
    },
    {
        "job_id": "dummy-ai-006",
        "company_name": "현대자동차",
        "title": "AI 신뢰성 검증 엔지니어",
        "job_type": "ai_verification",
        "career_type": "experienced",
        "region": "서울 서초구",
        "skills_raw": "Python,PyTorch,TensorFlow,Docker,Git,scikit-learn",
        "description": "자율주행 AI 안전성 검증. PyTorch TensorFlow 모델 신뢰성 평가, Docker 실험 환경 구성.",
        "posted_at": datetime(2026, 5, 17),
    },
]


def _attach_normalized_skills(jobs: list[dict]) -> list[dict]:
    for job in jobs:
        raw = str_to_skills(job.get("skills_raw", ""))
        job["skills_normalized"] = skills_to_str(normalize_skills(raw))
    return jobs


def main() -> None:
    print("=" * 60)
    print("[seed] DB 초기화")
    init_db()

    print(f"[seed] 기술 스택 정규화 ({len(DUMMY_JOBS)}건)")
    jobs = _attach_normalized_skills(DUMMY_JOBS)

    print("[seed] SQLite 저장")
    with SessionLocal() as db:
        saved = upsert_jobs(db, jobs)
    print(f"       → {saved}건 저장 완료")

    print("[seed] ChromaDB 인덱싱 (Gemini 임베딩 생성 중...)")
    t0 = time.time()
    indexed = index_jobs(jobs)
    elapsed = time.time() - t0
    counts = get_total_count()
    print(f"       → {indexed}건 인덱싱 완료 ({elapsed:.1f}초)")
    print(f"       → ChromaDB: jobs={counts['jobs']}개, skills={counts['skills']}개")

    print("=" * 60)
    print("[RAG 테스트] 신입 백엔드 개발자가 뭐부터 공부해야 해?")
    print("=" * 60)

    answer, sources = rag.query(
        question="신입 백엔드 개발자가 뭐부터 공부해야 해?",
        job_type="backend",
        career_type="entry",
    )
    print(f"\n{answer}")
    print(f"\n출처: {', '.join(sources)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
