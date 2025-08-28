# backend/repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

UPSERT_SQL = text("""
insert into job_post (hash_key, source, title, company, location,
                      description_snippet, posted_at, canonical_url, salary_text,
                      first_seen, last_seen, is_active)
values
  (:hash_key, :source, :title, :company, :location,
   :description_snippet, :posted_at, :canonical_url, :salary_text,
   now(), now(), true)
on conflict (hash_key) do update
set title               = excluded.title,
    company             = excluded.company,
    location            = excluded.location,
    description_snippet = excluded.description_snippet,
    posted_at           = excluded.posted_at,
    canonical_url       = excluded.canonical_url,
    salary_text         = excluded.salary_text,
    last_seen           = now(),
    is_active           = true
""")

async def upsert_jobs(session: AsyncSession, rows: list[dict]):
    # rows: list of dicts with keys used above (including :hash_key)
    for r in rows:
        await session.execute(UPSERT_SQL, r)
    await session.commit()

async def deactivate_missing_for_source(session: AsyncSession, source: str, crawl_started_at: datetime):
    # Any active row for this source not touched during this crawl becomes inactive
    await session.execute(
        text("""
            update job_post
               set is_active = false
             where source = :source
               and is_active = true
               and last_seen < :ts
        """),
        {"source": source, "ts": crawl_started_at},
    )
    await session.commit()
