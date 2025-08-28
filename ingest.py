# ingest.py
import asyncio
from datetime import datetime, timezone

from backend.db import async_sessionmaker
from backend.repo import upsert_jobs, deactivate_missing_for_source
from backend.utils_normalize import make_hash_key
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ingest")

# ---- Replace this with real provider fetchers later ----
async def fetch_seek() -> list[dict]:
    # Return list of dicts matching our upsert keys (except hash_key; we’ll add it)
    return [
        {
            "source": "seek",
            "title": "Junior Software Developer",
            "company": "Acme Pty Ltd",
            "location": "Sydney NSW",
            "description_snippet": "Work with Python/FastAPI",
            "posted_at": datetime.now(timezone.utc),
            "canonical_url": "https://example.com/seek/acme-junior",
            "salary_text": "$80k–$95k",
        },
        {
            "source": "seek",
            "title": "Backend Engineer",
            "company": "FinTech Global",
            "location": "Melbourne VIC",
            "description_snippet": "APIs, async Python, Postgres",
            "posted_at": datetime.now(timezone.utc),
            "canonical_url": "https://example.com/seek/fintech-backend",
            "salary_text": "$110k–$130k",
        },
    ]
# --------------------------------------------------------

async def run_once_for_source(source: str, fetcher):
    crawl_started_at = datetime.now(timezone.utc)
    items = await fetcher()

    # compute hash_key for each item
    rows = []
    for it in items:
        it = dict(it)  # shallow copy
        it["hash_key"] = make_hash_key(
            source=it.get("source") or source,
            title=it.get("title", ""),
            company=it.get("company"),
            location=it.get("location"),
            canonical_url=it.get("canonical_url"),
        )
        rows.append(it)

    async with async_sessionmaker() as session:
        await upsert_jobs(session, rows)
        await deactivate_missing_for_source(session, source, crawl_started_at)

async def main():
    await run_once_for_source("seek", fetch_seek)
    # Add others as you build them:
    # await run_once_for_source("linkedin", fetch_linkedin)
    # await run_once_for_source("indeed", fetch_indeed)

if __name__ == "__main__":
    asyncio.run(main())
