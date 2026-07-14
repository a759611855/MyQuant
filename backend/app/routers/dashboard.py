from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import NewsItem, PriceBar, Score, Symbol, SyncJob
from ..schemas import DashboardOut, NewsOut, ScoreOut, SymbolOut, SyncJobOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db)) -> DashboardOut:
    symbol_count = db.scalar(select(func.count()).select_from(Symbol)) or 0
    bar_count = db.scalar(select(func.count()).select_from(PriceBar)) or 0
    score_count = db.scalar(select(func.count()).select_from(Score)) or 0
    news_count = db.scalar(select(func.count()).select_from(NewsItem)) or 0

    last_sync = db.scalar(select(SyncJob).order_by(desc(SyncJob.finished_at)).limit(1))
    top_scores = db.scalars(select(Score).order_by(desc(Score.total)).limit(6)).all()
    recent_news = db.scalars(select(NewsItem).order_by(desc(NewsItem.fetched_at)).limit(6)).all()
    recent_syncs = db.scalars(select(SyncJob).order_by(desc(SyncJob.started_at)).limit(8)).all()
    watchlist = db.scalars(select(Symbol).order_by(Symbol.ticker)).all()

    return DashboardOut(
        symbol_count=symbol_count,
        bar_count=bar_count,
        last_sync_at=last_sync.finished_at if last_sync else None,
        score_count=score_count,
        news_count=news_count,
        top_scores=[ScoreOut.model_validate(s) for s in top_scores],
        recent_news=[NewsOut.model_validate(n) for n in recent_news],
        recent_syncs=[SyncJobOut.model_validate(j) for j in recent_syncs],
        watchlist=[SymbolOut.model_validate(s) for s in watchlist],
    )
