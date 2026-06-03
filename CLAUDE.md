# Job-Lens

채용공고 기반 IT 직무 분석 및 커리어 로드맵 추천 플랫폼.
사람인 공식 API로 백엔드·QA·AI검증 채용공고 500건을 수집·벡터화하여
자연어 질의응답과 기술 트렌드 분석을 제공한다.

상세 요구사항: `docs/requirements.md`

---

## 기술 스택

- **언어**: Python 3.11
- **프레임워크**: FastAPI
- **LLM**: Gemini 2.5 Flash (`gemini-2.5-flash`)
- **임베딩**: gemini-embedding-001
- **벡터 DB**: ChromaDB (로컬)
- **원본 저장**: SQLite (`data/jobs.db`)
- **데이터 수집**: 사람인 API (oapi.saramin.co.kr)
- **배포**: Railway

---

## 디렉토리 구조

```
job-lens/
├── CLAUDE.md
├── docs/
│   └── requirements.md
├── app/
│   ├── main.py              
│   ├── api/
│   │   ├── query.py         
│   │   ├── stats.py         
│   │   ├── roadmap.py       
│   │   └── ingest.py        
│   ├── core/
│   │   ├── collector.py     
│   │   ├── normalizer.py    
│   │   ├── embedder.py      
│   │   ├── indexer.py       
│   │   └── rag.py           
│   ├── db/
│   │   ├── database.py      
│   │   └── models.py        
│   └── config.py            
├── data/
│   └── jobs.db              
├── scripts/
│   └── ingest.py            
├── tests/
├── .env.example
├── requirements.txt
├── railway.toml
└── README.md
```

---

## 타겟 직군

| job_type 값 | 직군 | 사람인 검색 키워드 |
|---|---|---|
| `backend` | 백엔드 | 백엔드, 서버개발, Java개발자, Spring |
| `qa` | QA / 테스트 | QA엔지니어, 품질보증, 테스트엔지니어, 소프트웨어테스트 |
| `ai_verification` | AI 검증 | AI검증, AI신뢰성, ML엔지니어 |

---

## Git 규칙

### 작업 워크플로우

모든 작업은 반드시 아래 순서를 따른다:

```
1. 이슈 생성     gh issue create --title "[feat] 기능명" --body "작업 내용"
2. 브랜치 생성   git checkout -b feat/#{이슈번호}-기능명
3. 작업 및 커밋  커밋 메시지 규칙 준수
4. PR 생성       gh pr create --title "feat: 제목" --body "PR 템플릿 준수"
5. Squash Merge  gh pr merge --squash
6. 브랜치 삭제   git branch -d feat/#{이슈번호}-기능명
```

### 브랜치 전략 (GitHub Flow)

```
main                          # 항상 배포 가능한 상태 유지, 직접 커밋 금지
feat/#{이슈번호}-기능명        # 기능 개발
fix/#{이슈번호}-버그명         # 버그 수정
chore/#{이슈번호}-작업명       # 설정, 문서, 기타
```

브랜치 예시:
```
feat/#1-initial-setup
feat/#2-worknet-collector
feat/#3-chroma-indexer
fix/#4-skill-normalizer
chore/#5-railway-deploy
```

### 커밋 메시지 규칙 (Conventional Commits, 한글)

형식:
```
타입(scope): 제목
```

타입 종류:
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `refactor`: 기능 변경 없는 코드 개선
- `docs`: 문서 수정
- `test`: 테스트 추가/수정
- `chore`: 빌드, 설정 변경

규칙:
- 제목 40자 이내
- 마침표 없음
- 명사형으로 끝내기 (`~구현`, `~수정`, `~추가`, `~개선`)
- scope는 모듈명 영문 유지

커밋 예시:
```
feat(collector): 사람인 API 백엔드 직군 페이지네이션 수집 구현
fix(normalizer): Spring Boot 대소문자 변형 처리 누락 수정
refactor(rag): ChromaDB 쿼리로 Top-K 검색 로직 단순화
docs(readme): 로컬 실행 방법 추가
chore(railway): 배포 설정 추가
```

### 이슈 규칙

제목 형식: `[타입] 작업 내용`

```
[feat] 사람인 API 수집 모듈 구현
[fix] 기술 스택 정규화 누락 수정
[docs] README 로컬 실행 방법 추가
[chore] Railway 배포 설정
```

### PR 규칙

```
## 요약
무엇을 구현했는지 한 줄 요약

## 변경 사항
- 변경된 파일/모듈 목록

## 테스트
- 어떻게 검증했는지

## 관련 이슈
closes #이슈번호
```

### 병합 규칙

- `main` 직접 커밋 금지, PR을 통해서만 병합
- PR 병합 전 반드시 `main` 최신화 후 충돌 해결
- 병합 방식: Squash and Merge

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
SARAMIN_API_KEY=
CHROMA_PATH=./data/chroma
DATABASE_URL=sqlite:///./data/jobs.db
TOP_K=5
```

---

## 자주 쓰는 명령어

```bash
uvicorn app.main:app --reload
python scripts/ingest.py --limit 500
pytest tests/
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

## 핵심 설계 결정

- **청크 전략**: 공고 단위 전체 텍스트 + 기술 스택 항목 분리 저장 (2-level)
- **Top-K**: 기본값 5, 환경변수로 조정 가능
- **기술 스택 정규화**: `normalizer.py`에서 alias 딕셔너리 기반으로 처리
- **중복 제거**: 공고 ID 기준 SQLite upsert
- **응답 출처**: 모든 RAG 답변에 참조 공고 회사명 포함

---

## 제외 사항 (구현하지 않음)

- SSE 스트리밍
- 회사 규모별 비교
- 프론트엔드 UI (Swagger UI로 대체)
- 사용자 인증
- 민간 플랫폼 크롤링
