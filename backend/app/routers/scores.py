from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import PriceBar, Score, Symbol
from ..schemas import ScoreOut
from ..services.market_data import bars_to_frame
from ..services.scoring import score_bars

router = APIRouter(prefix="/api/scores", tags=["scores"])


@router.get("", response_model=list[ScoreOut])
def list_scores(db: Session = Depends(get_db)) -> list[Score]:
    return list(db.scalars(select(Score).order_by(Score.total.desc())).all())


@router.post("/compute", response_model=list[ScoreOut])
def compute_scores(db: Session = Depends(get_db)) -> list[Score]:
    symbols = list(db.scalars(select(Symbol)).all())
    if not symbols:
        raise HTTPException(status_code=400, detail="请先同步观察列表数据")

    results: list[Score] = []
    db.execute(delete(Score))

    for symbol in symbols:
        bars = list(
            db.scalars(
                select(PriceBar)
                .where(PriceBar.ticker == symbol.ticker)
                .order_by(PriceBar.date)
            ).all()
        )
        payload = [
            {
                "ticker": b.ticker,
                "date": b.date,
                "open": b.open,
                "high": b.high,
                "low": b.low,
                "close": b.close,
                "volume": b.volume,
            }
            for b in bars
        ]
        scored = score_bars(symbol.ticker, bars_to_frame(payload))
        row = Score(
            ticker=scored["ticker"],
            momentum=scored["momentum"],
            volatility=scored["volatility"],
            trend=scored["trend"],
            liquidity=scored["liquidity"],
            total=scored["total"],
            grade=scored["grade"],
            note=scored["note"],
            computed_at=datetime.utcnow(),
        )
        db.add(row)
        results.append(row)

    db.commit()
    for row in results:
        db.refresh(row)
    return sorted(results, key=lambda s: s.total, reverse=True)


@router.get("/{ticker}", response_model=ScoreOut)
def get_score(ticker: str, db: Session = Depends(get_db)) -> Score:
    row = db.scalar(select(Score).where(Score.ticker == ticker.upper()))
    if not row:
        raise HTTPException(status_code=404, detail="未找到评分，请先计算")
    return row
