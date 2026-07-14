from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import NewsItem, Symbol
from ..schemas import NewsOut
from ..services.news import fetch_news

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("", response_model=list[NewsOut])
def list_news(
    db: Session = Depends(get_db),
    limit: int = Query(40, ge=1, le=100),
    ticker: str | None = None,
) -> list[NewsItem]:
    stmt = select(NewsItem).order_by(NewsItem.published_at.desc()).limit(limit)
    if ticker:
        stmt = (
            select(NewsItem)
            .where(NewsItem.ticker == ticker.upper())
            .order_by(NewsItem.published_at.desc())
            .limit(limit)
        )
    rows = list(db.scalars(stmt).all())
    return rows


@router.post("/refresh", response_model=list[NewsOut])
def refresh_news(
    db: Session = Depends(get_db),
    limit: int = Query(30, ge=1, le=80),
) -> list[NewsItem]:
    watchlist = [s.ticker for s in db.scalars(select(Symbol)).all()]
    items = fetch_news(limit=limit, watchlist=watchlist)

    db.execute(delete(NewsItem))
    rows: list[NewsItem] = []
    now = datetime.utcnow()
    for item in items:
        row = NewsItem(
            title=item["title"],
            summary=item["summary"],
            source=item["source"],
            url=item["url"],
            ticker=item.get("ticker") or "",
            published_at=item.get("published_at") or "",
            fetched_at=now,
        )
        db.add(row)
        rows.append(row)

    db.commit()
    for row in rows:
        db.refresh(row)
    return rows
