# # test.py
# import os, asyncio, ssl, certifi
# from dotenv import load_dotenv
# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy import text

# load_dotenv('.env')

# ssl_ctx = ssl.create_default_context()
# ssl_ctx.check_hostname = False
# ssl_ctx.verify_mode = ssl.CERT_NONE

# engine = create_async_engine(
#     os.getenv("DATABASE_URL"),
#     connect_args={"ssl": ssl_ctx},
#     echo=True,
# )


# async def t():
#     async with engine.begin() as c:
#         v = await c.scalar(text("SELECT 1"))
#         print("DB OK?", v == 1)

# asyncio.run(t())
