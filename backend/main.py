# backend/main.py (replace your FAKE_JOBS handler)
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from typing import Optional, List
from pydantic import BaseModel
from db import get_session
from models import JobPost


app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    posted_at: Optional[str] = None
    ingested_at: Optional[str] = None
    class Config: from_attributes = True

@app.get("/jobs", response_model=List[JobOut])
async def list_jobs(
    q: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session = Depends(get_session),
):
    stmt = select(JobPost).order_by(JobPost.posted_at.desc().nullslast(), JobPost.id.desc())
    if q:
        # simple ILIKE search across key fields
        from sqlalchemy import or_
        ilike = f"%{q}%"
        stmt = stmt.where(or_(JobPost.title.ilike(ilike), JobPost.company.ilike(ilike), JobPost.location.ilike(ilike)))
    if source:
        stmt = stmt.where(JobPost.source == source)
    stmt = stmt.limit(limit).offset(offset)
    rows = (await session.execute(stmt)).scalars().all()
    return rows
