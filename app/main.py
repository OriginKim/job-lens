from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import query, stats, roadmap, ingest
from app.db.database import init_db

_STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Job-Lens",
    description="채용공고 기반 IT 직무 분석 및 커리어 로드맵 추천 플랫폼",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(query.router)
app.include_router(stats.router)
app.include_router(roadmap.router)
app.include_router(ingest.router)

app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    return FileResponse(_STATIC / "index.html")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
