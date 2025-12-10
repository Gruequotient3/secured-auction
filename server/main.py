import aiosqlite
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.auction import Auction

# Routers
from api.auction import auction_router
from api.auth import router as auth_router

from config.config import DB_PATH

app = FastAPI(
    title="Secured Auction",
    description="Auction backend on FastAPI + SQLite",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(auction_router)


async def init_db():
    with open("db_schemas.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        f.write('')

    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(schema_sql)
        await db.commit()




@app.on_event("startup")
async def on_startup():
    await init_db()
    asyncio.create_task(Auction.check_auctions_status())
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
