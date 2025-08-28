# backend/models.py
import uuid
from sqlalchemy import Column, String, Text, TIMESTAMP, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from .db import Base

class JobPost(Base):
    __tablename__ = "job_post"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(Text, nullable=True)
    title = Column(Text, nullable=False)
    company = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    description_snippet = Column(Text, nullable=True)
    posted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    canonical_url = Column(Text, nullable=True)
    salary_text = Column(Text, nullable=True)

    # 👇 for deduplication across ingests
    hash_key = Column(Text, nullable=False, unique=True)

    # 👇 for lifecycle tracking
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    first_seen = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_seen  = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active  = Column(Boolean, nullable=False, server_default="true")
