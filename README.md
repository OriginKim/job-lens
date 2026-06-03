# Job-Lens

**채용공고 기반 IT 직무 분석 및 커리어 로드맵 추천 플랫폼**

사람인 공식 API로 백엔드·QA·AI검증 채용공고 500건을 수집·벡터화하여
자연어 질의응답과 기술 트렌드 분석을 제공합니다.

---

## 배경

백엔드·QA·AI검증 직군 취업을 준비하면서 수백 개의 공고를 개별 확인하는 과정이 비효율적이었습니다.
"QA 엔지니어가 요즘 뭘 요구하지?", "AI 검증 직군은 Python을 얼마나 쓰지?" 같은 질문에
데이터 기반으로 답하는 도구가 없어 직접 만들었습니다.

---

## 주요 기능

| 기능 | 설명 |
|---|---|
| **자연어 질의응답** | 채용공고 데이터 기반 RAG — 질문에 관련 공고를 검색해 Gemini가 답변 |
| **기술 스택 분석** | 직군·경력별 요구 기술 빈도 Top N, 비율 시각화 |
| **커리어 로드맵** | 공고 빈도 기반 3단계 학습 순서 + AI 생성 상세 로드맵 |
| **트렌드 분석** | 최근 30일 공고 기준 기술 스택 변화 |

---

## 아키텍처

```
사람인 API
    │
    ▼
collector.py  →  SQLite (원본 보존)
    │
    ▼
normalizer.py (기술 스택 정규화: Java/JAVA/java → Java)
    │
    ▼
embedder.py   →  gemini-embedding-001
    │
    ▼
indexer.py    →  ChromaDB (2-level 청크: 공고 단위 + 기술스택 분리)
    │
    ▼
rag.py        →  Top-K 검색 → Gemini 2.5 Flash → 답변 + 출처
```

**2-level 청크 전략**: 공고 전체 텍스트(의미 검색용) + 기술 스택 항목 분리(정밀 매칭용)으로 검색 정확도를 높였습니다.

---

## 기술 스택

| 분류 | 기술 | 선택 이유 |
|---|---|---|
| 언어 | Python 3.11 | RAG 생태계 중심 |
| 프레임워크 | FastAPI | 비동기 처리, Swagger 자동 생성 |
| LLM | Gemini 2.5 Flash | 무료 티어, 긴 컨텍스트 지원 |
| 임베딩 | gemini-embedding-001 | Gemini 계열 통일, 무료 |
| 벡터 DB | ChromaDB | 로컬 설치, 별도 인프라 불필요 |
| 원본 저장 | SQLite | 경량, 재인덱싱 가능하도록 원본 보존 |
| 데이터 수집 | 사람인 API | 공식 API, 합법, 무료 |
| 배포 | Railway | 컨테이너 배포 간편 |

---

## 로컬 실행

### 1. 환경 설정

```bash
git clone https://github.com/OriginKim/job-lens.git
cd job-lens
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일에 API 키를 입력합니다:

```env
GEMINI_API_KEY=your_gemini_api_key
SARAMIN_API_KEY=your_saramin_api_key
```

> Gemini API 키: [Google AI Studio](https://aistudio.google.com/apikey)
> 사람인 API 키: [사람인 개발자센터](https://oapi.saramin.co.kr)

### 3. 서버 실행

```bash
uvicorn app.main:app --reload
```

브라우저에서 `http://localhost:8000` 접속 → 프론트엔드 UI
Swagger 문서는 `http://localhost:8000/docs`

### 4. 데이터 수집 및 인덱싱

서버가 실행 중인 상태에서:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"limit": 500}'
```

또는 Swagger UI에서 `POST /ingest` 실행.

수집 완료 후 프론트엔드에서 바로 질의응답, 기술스택 분석, 로드맵 확인 가능합니다.

---

## API 명세

| 메서드 | 경로 | 설명 | 주요 파라미터 |
|---|---|---|---|
| `GET` | `/` | 프론트엔드 UI | — |
| `POST` | `/query` | RAG 질의응답 | `question`, `job_type`, `career_type`, `region` |
| `GET` | `/stats/skills` | 기술 스택 Top N | `job_type`, `career_type`, `top_n` |
| `GET` | `/stats/trend` | 최근 30일 트렌드 | `job_type` |
| `GET` | `/roadmap` | 커리어 로드맵 추천 | `job_type`, `career_type` |
| `POST` | `/ingest` | 데이터 수집 및 인덱싱 | `limit` |
| `GET` | `/health` | 서버 상태 확인 | — |

**job_type 값**: `backend` · `qa` · `ai_verification`
**career_type 값**: `entry` (신입) · `experienced` (경력)

### 질의응답 예시

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "신입 QA 엔지니어가 가장 많이 요구받는 기술은?",
    "job_type": "qa",
    "career_type": "entry"
  }'
```

```json
{
  "answer": "신입 QA 엔지니어 공고 기준 가장 많이 요구되는 기술은 ...",
  "sources": ["카카오", "네이버", "라인플러스"]
}
```

---

## 프로젝트 구조

```
job-lens/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 환경변수 관리
│   ├── api/
│   │   ├── query.py         # POST /query
│   │   ├── stats.py         # GET /stats/*
│   │   ├── roadmap.py       # GET /roadmap
│   │   └── ingest.py        # POST /ingest
│   ├── core/
│   │   ├── collector.py     # 사람인 API 수집
│   │   ├── normalizer.py    # 기술 스택 정규화
│   │   ├── embedder.py      # Gemini 임베딩
│   │   ├── indexer.py       # ChromaDB 인덱싱
│   │   └── rag.py           # RAG 파이프라인
│   ├── db/
│   │   ├── database.py      # SQLAlchemy 세션
│   │   ├── models.py        # Job 모델
│   │   └── crud.py          # upsert 로직
│   └── static/
│       └── index.html       # 프론트엔드 SPA
├── data/
│   ├── jobs.db              # SQLite 원본 데이터
│   └── chroma/              # ChromaDB 벡터 저장소
├── scripts/
│   └── ingest.py            # 수동 수집 스크립트
├── docs/
│   └── requirements.md      # 요구사항 명세서
├── .env.example
├── requirements.txt
└── railway.toml
```

---

## 설계 결정

**왜 LangChain을 쓰지 않았나요?**
RAG 파이프라인이 단순해서 직접 구현이 더 명확합니다. LangChain 추상화 없이 임베딩→검색→생성 각 단계를 직접 제어할 수 있어 디버깅과 튜닝이 쉽습니다.

**왜 ChromaDB인가요?**
로컬 파일 기반이라 별도 인프라 없이 바로 사용 가능합니다. 프로덕션이라면 Pinecone이나 Weaviate를 고려하겠지만, 2주 프로토타입에서는 속도가 우선이었습니다.

**중복 공고는 어떻게 처리하나요?**
사람인 API의 공고 ID를 기준으로 SQLite에서 upsert 처리합니다. `/ingest`를 여러 번 호출해도 데이터가 중복되지 않습니다.
