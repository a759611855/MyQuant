from datetime import datetime

from pydantic import BaseModel, Field


class SymbolOut(BaseModel):
    id: int
    ticker: str
    name: str
    market: str

    class Config:
        from_attributes = True


class SyncRequest(BaseModel):
    tickers: list[str] | None = None
    period: str = "6mo"


class SyncJobOut(BaseModel):
    id: int
    ticker: str
    status: str
    bars_synced: int
    message: str
    started_at: datetime
    finished_at: datetime | None

    class Config:
        from_attributes = True


class ScoreOut(BaseModel):
    id: int | None = None
    ticker: str
    momentum: float
    volatility: float
    trend: float
    liquidity: float
    total: float
    grade: str
    note: str
    computed_at: datetime | None = None

    class Config:
        from_attributes = True


class NewsOut(BaseModel):
    id: int | None = None
    title: str
    summary: str
    source: str
    url: str
    ticker: str
    published_at: str
    fetched_at: datetime | None = None

    class Config:
        from_attributes = True


class DashboardOut(BaseModel):
    symbol_count: int
    bar_count: int
    last_sync_at: datetime | None
    score_count: int
    news_count: int
    top_scores: list[ScoreOut] = Field(default_factory=list)
    recent_news: list[NewsOut] = Field(default_factory=list)
    recent_syncs: list[SyncJobOut] = Field(default_factory=list)
    watchlist: list[SymbolOut] = Field(default_factory=list)
