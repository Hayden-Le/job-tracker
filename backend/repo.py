# backend/repo.py
from sqlalchemy import select
from .models import JobPost

async def upsert_job(session, data: dict):
    # de-dupe by url if present, else by (title, company, posted_at)
    if data.get("url"):
        existing = (await session.execute(select(JobPost).where(JobPost.url == data["url"]))).scalars().first()
    else:
        existing = (await session.execute(select(JobPost).where(
            JobPost.title==data["title"], JobPost.company==data["company"], JobPost.posted_at==data.get("posted_at")
        ))).scalars().first()
    if existing:
        for k,v in data.items():
            setattr(existing, k, v)
        return existing
    obj = JobPost(**data)
    session.add(obj)
    return obj
