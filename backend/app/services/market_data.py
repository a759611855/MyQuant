"""Market data sync via yfinance, with deterministic fallback."""

from __future__ import annotations

import math
from datetime import datetime, timedelta

import pandas as pd


DEFAULT_WATCHLIST = [
    {"ticker": "AAPL", "name": "Apple Inc.", "market": "US"},
    {"ticker": "MSFT", "name": "Microsoft", "market": "US"},
    {"ticker": "NVDA", "name": "NVIDIA", "market": "US"},
    {"ticker": "TSLA", "name": "Tesla", "market": "US"},
    {"ticker": "SPY", "name": "S&P 500 ETF", "market": "US"},
    {"ticker": "QQQ", "name": "Nasdaq 100 ETF", "market": "US"},
]


def _fallback_bars(ticker: str, days: int = 120) -> list[dict]:
    """Generate realistic synthetic OHLCV when live fetch fails."""
    seed = sum(ord(c) for c in ticker)
    base = 80 + (seed % 400)
    bars: list[dict] = []
    price = float(base)
    start = datetime.utcnow().date() - timedelta(days=days + 10)

    for i in range(days):
        day = start + timedelta(days=i)
        if day.weekday() >= 5:
            continue
        drift = math.sin((i + seed) / 9.0) * 0.012
        shock = math.cos((i + seed) / 3.7) * 0.008
        open_p = price
        close_p = max(1.0, open_p * (1 + drift + shock))
        high_p = max(open_p, close_p) * (1 + abs(shock) * 0.4)
        low_p = min(open_p, close_p) * (1 - abs(drift) * 0.4)
        volume = 1_000_000 + ((seed * (i + 3)) % 8_000_000)
        bars.append(
            {
                "ticker": ticker,
                "date": day.isoformat(),
                "open": round(open_p, 4),
                "high": round(high_p, 4),
                "low": round(low_p, 4),
                "close": round(close_p, 4),
                "volume": float(volume),
            }
        )
        price = close_p
    return bars


def fetch_bars(ticker: str, period: str = "6mo") -> tuple[list[dict], str]:
    """Return (bars, source_message)."""
    try:
        import yfinance as yf

        hist = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if hist is None or hist.empty:
            bars = _fallback_bars(ticker)
            return bars, "fallback: empty live response"
        bars = []
        for idx, row in hist.iterrows():
            date = idx.date().isoformat() if hasattr(idx, "date") else str(idx)[:10]
            bars.append(
                {
                    "ticker": ticker.upper(),
                    "date": date,
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row.get("Volume", 0) or 0),
                }
            )
        return bars, "yfinance"
    except Exception as exc:  # noqa: BLE001
        bars = _fallback_bars(ticker)
        return bars, f"fallback: {exc}"


def bars_to_frame(bars: list[dict]) -> pd.DataFrame:
    if not bars:
        return pd.DataFrame()
    df = pd.DataFrame(bars)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date")
