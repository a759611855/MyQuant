import { useEffect, useState } from "react";
import { api, type NewsItem } from "../api";

export default function NewsPage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    setNews(await api.news());
  }

  useEffect(() => {
    load().catch((err) =>
      setError(err instanceof Error ? err.message : "加载失败"),
    );
  }, []);

  async function onRefresh() {
    setBusy(true);
    setError("");
    try {
      setNews(await api.refreshNews());
    } catch (err) {
      setError(err instanceof Error ? err.message : "刷新失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <header className="page-head">
        <div>
          <h1>最近新闻</h1>
          <p>聚合公开财经 RSS；若外网不可达，将回退到平台内置摘要。</p>
        </div>
        <div className="actions">
          <button className="btn btn-primary" onClick={onRefresh} disabled={busy}>
            {busy ? "获取中…" : "获取最近新闻"}
          </button>
        </div>
      </header>

      {error && <div className="banner">{error}</div>}

      <section className="panel">
        <div className="news-list">
          {news.map((item, idx) => (
            <article
              className="news-item"
              key={`${item.title}-${idx}`}
              style={{ animationDelay: `${idx * 40}ms` }}
            >
              <div className="news-meta">
                <span>{item.source}</span>
                <span>{item.published_at || "刚刚"}</span>
                {item.ticker && <span>{item.ticker}</span>}
              </div>
              <h4>
                {item.url ? (
                  <a href={item.url} target="_blank" rel="noreferrer">
                    {item.title}
                  </a>
                ) : (
                  item.title
                )}
              </h4>
              {item.summary && <p className="muted">{item.summary}</p>}
            </article>
          ))}
          {!news.length && (
            <div className="empty">暂无新闻缓存，点击右上角获取最近新闻。</div>
          )}
        </div>
      </section>
    </div>
  );
}
