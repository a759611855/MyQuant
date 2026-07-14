export type SymbolItem = {
  id: number;
  ticker: string;
  name: string;
  market: string;
};

export type SyncJob = {
  id: number;
  ticker: string;
  status: string;
  bars_synced: number;
  message: string;
  started_at: string;
  finished_at: string | null;
};

export type Score = {
  id?: number;
  ticker: string;
  momentum: number;
  volatility: number;
  trend: number;
  liquidity: number;
  total: number;
  grade: string;
  note: string;
  computed_at?: string | null;
};

export type NewsItem = {
  id?: number;
  title: string;
  summary: string;
  source: string;
  url: string;
  ticker: string;
  published_at: string;
  fetched_at?: string | null;
};

export type Dashboard = {
  symbol_count: number;
  bar_count: number;
  last_sync_at: string | null;
  score_count: number;
  news_count: number;
  top_scores: Score[];
  recent_news: NewsItem[];
  recent_syncs: SyncJob[];
  watchlist: SymbolItem[];
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>("/api/health"),
  dashboard: () => request<Dashboard>("/api/dashboard"),
  symbols: () => request<SymbolItem[]>("/api/sync/symbols"),
  syncJobs: () => request<SyncJob[]>("/api/sync/jobs"),
  runSync: (tickers?: string[]) =>
    request<SyncJob[]>("/api/sync/run", {
      method: "POST",
      body: JSON.stringify({ tickers: tickers ?? null, period: "6mo" }),
    }),
  scores: () => request<Score[]>("/api/scores"),
  computeScores: () =>
    request<Score[]>("/api/scores/compute", { method: "POST" }),
  news: (limit = 40) => request<NewsItem[]>(`/api/news?limit=${limit}`),
  refreshNews: () =>
    request<NewsItem[]>("/api/news/refresh", { method: "POST" }),
};
