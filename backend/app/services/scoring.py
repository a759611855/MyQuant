"""Multi-factor scoring for synced price series."""

from __future__ import annotations

import math

import pandas as pd


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _grade(total: float) -> str:
    if total >= 85:
        return "A"
    if total >= 70:
        return "B"
    if total >= 55:
        return "C"
    if total >= 40:
        return "D"
    return "F"


def score_bars(ticker: str, df: pd.DataFrame) -> dict:
    if df is None or df.empty or len(df) < 20:
        return {
            "ticker": ticker,
            "momentum": 0.0,
            "volatility": 0.0,
            "trend": 0.0,
            "liquidity": 0.0,
            "total": 0.0,
            "grade": "F",
            "note": "数据不足，至少需要约 20 个交易日",
        }

    closes = df["close"].astype(float)
    volumes = df["volume"].astype(float)
    returns = closes.pct_change().dropna()

    # Momentum: 20d / 60d return blend
    ret_20 = float(closes.iloc[-1] / closes.iloc[-21] - 1) if len(closes) > 21 else 0.0
    ret_60 = float(closes.iloc[-1] / closes.iloc[-61] - 1) if len(closes) > 61 else ret_20
    momentum = _clamp(50 + (ret_20 * 180) + (ret_60 * 80))

    # Volatility: lower realized vol scores higher (risk-adjusted preference)
    vol = float(returns.tail(20).std() * math.sqrt(252)) if len(returns) >= 5 else 0.3
    volatility = _clamp(100 - vol * 220)

    # Trend: price vs SMA20 / SMA60
    sma20 = float(closes.tail(20).mean())
    sma60 = float(closes.tail(60).mean()) if len(closes) >= 60 else sma20
    last = float(closes.iloc[-1])
    vs_sma20 = (last / sma20 - 1) if sma20 else 0.0
    vs_sma60 = (last / sma60 - 1) if sma60 else 0.0
    trend = _clamp(50 + vs_sma20 * 250 + vs_sma60 * 120)

    # Liquidity: relative volume vs median
    med_vol = float(volumes.tail(60).median()) if len(volumes) else 0.0
    last_vol = float(volumes.iloc[-1])
    liq_ratio = (last_vol / med_vol) if med_vol > 0 else 1.0
    liquidity = _clamp(40 + math.log1p(liq_ratio) * 28)

    total = round(
        momentum * 0.35 + volatility * 0.20 + trend * 0.30 + liquidity * 0.15,
        2,
    )
    grade = _grade(total)

    notes = []
    if ret_20 > 0.05:
        notes.append("近月动量偏强")
    elif ret_20 < -0.05:
        notes.append("近月回调明显")
    if vol > 0.35:
        notes.append("波动偏高")
    if last > sma20 > sma60:
        notes.append("均线多头排列")
    elif last < sma20 < sma60:
        notes.append("均线空头排列")

    return {
        "ticker": ticker,
        "momentum": round(momentum, 2),
        "volatility": round(volatility, 2),
        "trend": round(trend, 2),
        "liquidity": round(liquidity, 2),
        "total": total,
        "grade": grade,
        "note": "；".join(notes) if notes else "结构中性",
    }
