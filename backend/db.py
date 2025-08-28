# backend/db.py
import os, ssl
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

# Load .env next to this file (works with uvicorn --reload)
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL missing. Expected .env at {env_path}")

# ---- Secure SSL context (verify certs, check hostname) ----
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# ---- Declarative base ----
class Base(DeclarativeBase):
    pass

# ---- Async engine (PgBouncer transaction pooler safe) ----
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        "ssl": ssl_ctx,
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0
    },
    pool_pre_ping=True,
    poolclass=NullPool
)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
async_sessionmaker = AsyncSessionLocal

# FastAPI dependency
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
