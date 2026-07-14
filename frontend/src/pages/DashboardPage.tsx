import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Dashboard } from "../api";

function fmtTime(value: string | null | undefined) {
  if (!value) return "尚未同步";
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const dash = await api.dashboard();
        if (alive) setData(dash);
      } catch (err) {
        if (alive) setError(err instanceof Error ? err.message : "加载失败");
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  return (
    <div>
      <header className="page-head">
        <div>
          <h1>看板</h1>
          <p>一眼掌握同步状态、评分排序与最近市场新闻。</p>
        </div>
        <div className="actions">
          <Link className="btn btn-ghost" to="/sync">
            去同步
          </Link>
          <Link className="btn btn-primary" to="/scores">
            查看评分
          </Link>
        </div>
      </header>

      {error && <div className="banner">{error}</div>}

      <section className="hero-board">
        <div className="hero-kicker">MyQuant Desk</div>
        <h2>把行情、评分与资讯收进同一张工作台</h2>
        <p>
          先同步观察列表，再计算多因子评分，并拉取最近新闻——个人量化研究从这里开始。
        </p>
        <div className="metric-strip">
          <div className="metric">
            <strong>{loading ? "…" : data?.symbol_count ?? 0}</strong>
            <span>观察标的</span>
          </div>
          <div className="metric">
            <strong>{loading ? "…" : data?.bar_count ?? 0}</strong>
            <span>K 线样本</span>
          </div>
          <div className="metric">
            <strong>{loading ? "…" : data?.score_count ?? 0}</strong>
            <span>已评分</span>
          </div>
          <div className="metric">
            <strong>{loading ? "…" : data?.news_count ?? 0}</strong>
            <span>新闻缓存</span>
          </div>
        </div>
      </section>

      <div className="panel-grid">
        <section className="panel">
          <h3>评分前列</h3>
          <p className="panel-desc">按综合分排序 · 最近一次计算</p>
          {!data?.top_scores?.length ? (
            <div className="empty">暂无评分，请先同步并计算。</div>
          ) : (
            <div className="list">
              {data.top_scores.map((s) => (
                <div className="list-row" key={s.ticker}>
                  <div className="ticker">{s.ticker}</div>
                  <div>
                    <div>{s.note}</div>
                    <div className="muted">综合 {s.total.toFixed(1)}</div>
                  </div>
                  <span className={`grade ${s.grade}`}>{s.grade}</span>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="panel">
          <h3>最近新闻</h3>
          <p className="panel-desc">
            最近同步时间：{fmtTime(data?.last_sync_at)}
          </p>
          {!data?.recent_news?.length ? (
            <div className="empty">暂无新闻，请到「新闻」页刷新。</div>
          ) : (
            <div className="list">
              {data.recent_news.slice(0, 5).map((n, idx) => (
                <div className="list-row" key={`${n.title}-${idx}`}>
                  <div className="ticker">{n.ticker || "MKT"}</div>
                  <div>
                    <div>{n.title}</div>
                    <div className="muted">{n.source}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
