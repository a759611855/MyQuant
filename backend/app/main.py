from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, SessionLocal, engine
from .models import Symbol
from .routers import dashboard, news, scores, sync
from .services.market_data import DEFAULT_WATCHLIST
from sqlalchemy import select


def seed_watchlist() -> None:
    db = SessionLocal()
    try:
        existing = {s.ticker for s in db.scalars(select(Symbol)).all()}
        for item in DEFAULT_WATCHLIST:
            if item["ticker"] not in existing:
                db.add(Symbol(**item))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_watchlist()
    yield


app = FastAPI(
    title="MyQuant",
    description="个人量化分析平台 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(sync.router)
app.include_router(scores.router)
app.include_router(news.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "MyQuant"}
