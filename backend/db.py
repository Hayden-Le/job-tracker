import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

async def test():
    async with engine.connect() as conn:
        result = await conn.execute("SELECT now()")
        print(result.fetchone())

asyncio.run(test())
