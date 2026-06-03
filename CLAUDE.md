# Job-Lens

채용공고 기반 IT 직무 분석 및 커리어 로드맵 추천 플랫폼.
워크넷 공공 API로 백엔드·QA·AI검증 채용공고 500건을 수집·벡터화하여
자연어 질의응답과 기술 트렌드 분석을 제공한다.

상세 요구사항: `docs/requirements.md`

---

## 기술 스택

- **언어**: Python 3.11
- **프레임워크**: FastAPI
- **LLM**: Gemini 2.0 Flash (`gemini-2.0-flash`)
- **임베딩**: text-embedding-004
- **벡터 DB**: ChromaDB (로컬)
- **원본 저장**: SQLite (`data/jobs.db`)
- **데이터 수집**: 워크넷 API (고용24)
- **배포**: Railway

---

## 디렉토리 구조

```
job-lens/
├── CLAUDE.md
├── docs/
│   └── requirements.md
├── app/
│   ├── main.py              # FastAPI 진입점
│   ├── api/
│   │   ├── query.py         # POST /query
│   │   ├── stats.py         # GET /stats/*
│   │   ├── roadmap.py       # GET /roadmap
│   │   └── ingest.py        # POST /ingest
│   ├── core/
│   │   ├── collector.py     # 워크넷 API 수집
│   │   ├── normalizer.py    # 기술 스택 정규화
│   │   ├── embedder.py      # 임베딩 생성
│   │   ├── indexer.py       # ChromaDB 인덱싱
│   │   └── rag.py           # RAG 파이프라인
│   ├── db/
│   │   ├── database.py      # SQLite 연결
│   │   └── models.py        # 테이블 정의
│   └── config.py            # 환경변수
├── data/
│   └── jobs.db              # SQLite 원본 데이터
├── scripts/
│   └── ingest.py            # 수동 수집 스크립트
├── tests/
├── .env.example
├── requirements.txt
├── railway.toml
└── README.md
```

---

## 타겟 직군

| job_type 값 | 직군 | 워크넷 검색 키워드 |
|---|---|---|
| `backend` | 백엔드 | 백엔드, 서버, Java, Spring |
| `qa` | QA / 테스트 | QA, 품질보증, 테스트, 소프트웨어 검증 |
| `ai_verification` | AI 검증 | AI 검증, AI 신뢰성, ML 엔지니어 |

---

## 코딩 컨벤션

- 함수·변수명: snake_case
- 클래스명: PascalCase
- 타입 힌트 필수 (모든 함수 파라미터, 반환값)
- Pydantic 모델로 요청/응답 스키마 정의
- 코드 내 주석 금지 — 코드 자체로 의도가 드러나도록 작성
- 환경변수는 반드시 `.env`에서 관리, 하드코딩 금지
- 에러는 FastAPI HTTPException으로 처리

---

## 환경변수

```
GEMINI_API_KEY=
WORKNET_API_KEY=
CHROMA_PATH=./data/chroma
DATABASE_URL=sqlite:///./data/jobs.db
TOP_K=5
```

---

## 자주 쓰는 명령어

```bash
# 로컬 실행
uvicorn app.main:app --reload

# 데이터 수집 및 인덱싱
python scripts/ingest.py --limit 500

# 테스트
pytest tests/

# 의존성 설치
pip install -r requirements.txt
```

---

## API 엔드포인트 요약

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | /query | RAG 질의응답 |
| GET | /stats/skills | 기술 스택 Top N |
| GET | /stats/trend | 최근 30일 트렌드 |
| GET | /roadmap | 커리어 로드맵 추천 |
| POST | /ingest | 데이터 수집 및 인덱싱 |
| GET | /health | 서버 상태 확인 |

---

## 핵심 설계 결정 (Claude Code 작업 시 참고)

**청크 전략**: 공고 단위 전체 텍스트 + 기술 스택 항목 분리 저장 (2-level)
**Top-K**: 기본값 5, 환경변수로 조정 가능
**기술 스택 정규화**: `normalizer.py`에서 alias 딕셔너리 기반으로 처리
**중복 제거**: 공고 ID 기준 SQLite upsert
**응답 출처**: 모든 RAG 답변에 참조 공고 회사명 포함

---

## 제외 사항 (구현하지 않음)

- SSE 스트리밍
- 회사 규모별 비교
- 프론트엔드 UI (Swagger UI로 대체)
- 사용자 인증
- 민간 플랫폼 크롤링
