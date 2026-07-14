"""Fetch recent market news from public RSS feeds."""

from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser
import httpx

FEEDS = [
    {
        "source": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rssindex",
    },
    {
        "source": "CNBC Markets",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    },
    {
        "source": "MarketWatch",
        "url": "https://feeds.marketwatch.com/marketwatch/topstories/",
    },
]

FALLBACK_NEWS = [
    {
        "title": "美股科技股延续分化，AI 相关标的仍受关注",
        "summary": "市场关注大型科技股财报与利率预期，短线波动加大。",
        "source": "MyQuant Digest",
        "url": "",
        "ticker": "",
        "published_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    },
    {
        "title": "风险偏好回暖，宽基 ETF 资金流入增加",
        "summary": "投资者在波动中增配指数产品，关注量价与宏观数据共振。",
        "source": "MyQuant Digest",
        "url": "",
        "ticker": "SPY",
        "published_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    },
    {
        "title": "半导体制造与算力链条仍是中期主线",
        "summary": "机构报告指出供需与资本开支节奏将主导板块估值修复。",
        "source": "MyQuant Digest",
        "url": "",
        "ticker": "NVDA",
        "published_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    },
]


def _parse_date(entry: dict[str, Any]) -> str:
    for key in ("published", "updated"):
        raw = entry.get(key)
        if not raw:
            continue
        try:
            return parsedate_to_datetime(raw).isoformat()
        except Exception:  # noqa: BLE001
            return str(raw)
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _guess_ticker(text: str, watchlist: list[str]) -> str:
    upper = text.upper()
    for ticker in watchlist:
        token = ticker.upper()
        if f" {token} " in f" {upper} " or f"${token}" in upper:
            return token
    return ""


def fetch_news(limit: int = 30, watchlist: list[str] | None = None) -> list[dict]:
    watchlist = watchlist or []
    items: list[dict] = []

    headers = {"User-Agent": "MyQuant/1.0 (+personal research)"}
    for feed in FEEDS:
        try:
            with httpx.Client(timeout=12.0, follow_redirects=True, headers=headers) as client:
                resp = client.get(feed["url"])
                resp.raise_for_status()
                parsed = feedparser.parse(resp.text)
        except Exception:  # noqa: BLE001
            continue

        for entry in parsed.entries[:20]:
            title = (entry.get("title") or "").strip()
            if not title:
                continue
            summary = (entry.get("summary") or entry.get("description") or "").strip()
            if "<" in summary:
                import re

                summary = re.sub(r"<[^>]+>", " ", summary)
                summary = re.sub(r"\s+", " ", summary).strip()
            blob = f"{title} {summary}"
            items.append(
                {
                    "title": title[:500],
                    "summary": summary[:800],
                    "source": feed["source"],
                    "url": entry.get("link") or "",
                    "ticker": _guess_ticker(blob, watchlist),
                    "published_at": _parse_date(entry),
                }
            )

    if not items:
        return FALLBACK_NEWS[:limit]

    # de-dupe by title
    seen: set[str] = set()
    unique: list[dict] = []
    for item in items:
        key = item["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    unique.sort(key=lambda x: x.get("published_at") or "", reverse=True)
    return unique[:limit]
