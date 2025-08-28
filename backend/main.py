from fastapi.middleware.cors import CORSMiddleware
from .db import get_session, engine
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from .models import JobPost
from datetime import datetime
from typing import Literal
from sqlalchemy import select, delete, text, or_, asc, desc, func
from fastapi import FastAPI, Depends, HTTPException, Query
from uuid import UUID


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class JobIn(BaseModel):
    title: str
    company: str | None = None
    source: str | None = None
    location: str | None = None
    description_snippet: str | None = None
    posted_at: datetime | None = None      # <-- datetime, not str
    canonical_url: str | None = None
    salary_text: str | None = None
    hash_key: str | None = None

class JobOut(JobIn):
    id: UUID                                # <-- UUID, not str
    created_at: datetime | None = None      # <-- datetime, not str
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 "orm_mode"

# --- Endpoints ---
@app.get("/jobs", response_model=list[JobOut])
async def list_jobs(
    q: str | None = None,
    source: str | None = None,
    sort: Literal["posted_at_desc","posted_at_asc"] = "posted_at_desc",
    page: int = 1,
    limit: int = 10,
    include_inactive: bool = False,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(JobPost)
    if not include_inactive:
        stmt = stmt.where(JobPost.is_active.is_(True))

    if q:
        ilike = f"%{q}%"
        stmt = stmt.where(or_(
            JobPost.title.ilike(ilike),
            JobPost.company.ilike(ilike),
            JobPost.location.ilike(ilike),
        ))

    if source:
        stmt = stmt.where(JobPost.source == source)

    stmt = stmt.order_by(
        desc(JobPost.posted_at) if sort == "posted_at_desc" else asc(JobPost.posted_at)
    )

    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)

    rows = (await session.execute(stmt)).scalars().all()
    return rows


@app.post("/jobs", response_model=JobOut)
async def create_job(payload: JobIn, session: AsyncSession = Depends(get_session)):
    job = JobPost(**payload.model_dump())
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job

@app.get("/jobs/{job_id}", response_model=JobOut)
async def get_job(job_id: UUID, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(JobPost).where(JobPost.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: UUID, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(JobPost).where(JobPost.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await session.delete(job)
    await session.commit()
    return {"ok": True}

class SourceStat(BaseModel):
    source: str
    active_count: int
    last_seen: datetime | None

class StatsOut(BaseModel):
    total_active: int
    per_source: list[SourceStat]

@app.get("/stats", response_model=StatsOut)
async def stats(session: AsyncSession = Depends(get_session)):
    total_active = await session.scalar(
        select(func.count()).select_from(JobPost).where(JobPost.is_active.is_(True))
    )

    rows = (await session.execute(
        select(
            JobPost.source.label("source"),
            func.count().filter(JobPost.is_active.is_(True)).label("active_count"),
            func.max(JobPost.last_seen).label("last_seen"),
        ).group_by(JobPost.source)
    )).all()

    per_source = [SourceStat(source=r.source, active_count=r.active_count or 0, last_seen=r.last_seen) for r in rows]
    return StatsOut(total_active=total_active or 0, per_source=per_source)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/dbz")
async def dbz():
    async with engine.begin() as conn:
        val = await conn.scalar(text("SELECT 1"))
    return {"db_ok": (val == 1)}
