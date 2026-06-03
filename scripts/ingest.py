import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.collector import collect_all
from app.core.indexer import index_jobs
from app.db.crud import upsert_jobs
from app.db.database import init_db, SessionLocal


def main(limit: int) -> None:
    init_db()
    start = time.time()

    print(f"[ingest] 수집 시작 (목표: {limit}건)")
    jobs, failed = collect_all(limit=limit)
    print(f"[ingest] 수집 완료: {len(jobs)}건 / 실패: {failed}건")

    with SessionLocal() as db:
        saved = upsert_jobs(db, jobs)
    print(f"[ingest] DB 저장 완료: {saved}건")

    indexed = index_jobs(jobs)
    elapsed = time.time() - start
    print(f"[ingest] 인덱싱 완료: {indexed}건 | 소요시간: {elapsed:.1f}초")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()
    main(limit=args.limit)
