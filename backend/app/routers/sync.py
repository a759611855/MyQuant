from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import PriceBar, Symbol, SyncJob
from ..schemas import SyncJobOut, SyncRequest, SymbolOut
from ..services.market_data import DEFAULT_WATCHLIST, fetch_bars

router = APIRouter(prefix="/api/sync", tags=["sync"])


def _ensure_watchlist(db: Session) -> None:
    existing = {s.ticker for s in db.scalars(select(Symbol)).all()}
    for item in DEFAULT_WATCHLIST:
        if item["ticker"] not in existing:
            db.add(Symbol(**item))
    db.commit()


@router.get("/symbols", response_model=list[SymbolOut])
def list_symbols(db: Session = Depends(get_db)) -> list[Symbol]:
    _ensure_watchlist(db)
    return list(db.scalars(select(Symbol).order_by(Symbol.ticker)).all())


@router.get("/jobs", response_model=list[SyncJobOut])
def list_jobs(db: Session = Depends(get_db), limit: int = 30) -> list[SyncJob]:
    return list(db.scalars(select(SyncJob).order_by(SyncJob.started_at.desc()).limit(limit)).all())


@router.post("/run", response_model=list[SyncJobOut])
def run_sync(payload: SyncRequest, db: Session = Depends(get_db)) -> list[SyncJob]:
    _ensure_watchlist(db)
    symbols = list(db.scalars(select(Symbol)).all())
    symbol_map = {s.ticker.upper(): s for s in symbols}

    tickers = payload.tickers or [s.ticker for s in symbols]
    jobs: list[SyncJob] = []

    for raw in tickers:
        ticker = raw.upper().strip()
        if not ticker:
            continue
        if ticker not in symbol_map:
            symbol = Symbol(ticker=ticker, name=ticker, market="US")
            db.add(symbol)
            db.flush()
            symbol_map[ticker] = symbol

        job = SyncJob(ticker=ticker, status="running", started_at=datetime.utcnow())
        db.add(job)
        db.flush()

        try:
            bars, source = fetch_bars(ticker, period=payload.period)
            db.execute(delete(PriceBar).where(PriceBar.ticker == ticker))
            for bar in bars:
                db.add(PriceBar(**bar))
            job.bars_synced = len(bars)
            job.status = "success"
            job.message = f"synced via {source}"
        except Exception as exc:  # noqa: BLE001
            job.status = "failed"
            job.message = str(exc)
            job.bars_synced = 0
        finally:
            job.finished_at = datetime.utcnow()
            jobs.append(job)

    db.commit()
    for job in jobs:
        db.refresh(job)
    return jobs
