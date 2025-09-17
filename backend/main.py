from fastapi.middleware.cors import CORSMiddleware
from .db import get_session, engine, DATABASE_URL
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import inspect, select, delete, text, or_, asc, desc, func
from .models import JobPost
from datetime import datetime
from typing import Literal
from fastapi import FastAPI, Depends, HTTPException, Query
from uuid import UUID
import os, json, pathlib

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    On startup, connect to the DB and print the actual columns
    of the job_post table to diagnose schema issues.
    """
    print("--- Database Schema Diagnostic ---")
    print(f"--- Application connecting to database at URL: {DATABASE_URL} ---")
    try:
        # Use a separate engine for a one-off inspection
        engine = create_async_engine(DATABASE_URL)
        async with engine.connect() as conn:
            def get_columns(sync_conn):
                inspector = inspect(sync_conn)
                return inspector.get_columns('job_post')

            columns = await conn.run_sync(get_columns)

            print("--- Columns found in 'job_post' table: ---")
            column_names = [column['name'] for column in columns]
            print(column_names)

    except Exception as e:
        print(f"Error during diagnostic: {e}")
        print("This might mean the 'job_post' table does not exist at all.")
    print("---------------------------------")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000", "job-tracker-one-pearl.vercel.app"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class JobIn(BaseModel):
    title: str
    company: str | None = None
    source: str | None = None
    location: str | None = None
    description_snippet: str | None = None
    description_sections: dict | None = None
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

def get_job_desc_dir() -> pathlib.Path:
    job_desc_dir = pathlib.Path(__file__).parent / "job_descriptions"
    job_desc_dir.mkdir(exist_ok=True) # Ensure it exists
    return job_desc_dir

# List all job description JSON files and their metadata
@app.get("/job-descriptions")
async def list_job_descriptions(job_desc_dir: pathlib.Path = Depends(get_job_desc_dir)):
    job_files = [f for f in os.listdir(job_desc_dir) if f.endswith(".json")]
    jobs = []

    for filename in job_files:
        path = os.path.join(job_desc_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                job = json.load(f)
                job["filename"] = filename
                jobs.append(job)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    return jobs

# Fetch a specific job description JSON file by filename
@app.get("/job-descriptions/{filename}")
async def get_job_description(filename: str, job_desc_dir: pathlib.Path = Depends(get_job_desc_dir)):
    path = job_desc_dir / filename
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Job description not found")
    try:
        with open(path, "r", encoding="utf-8") as f:
            job = json.load(f)
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading job description: {e}")
