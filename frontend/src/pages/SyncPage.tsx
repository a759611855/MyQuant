import { useEffect, useState } from "react";
import { api, type SyncJob, type SymbolItem } from "../api";

export default function SyncPage() {
  const [symbols, setSymbols] = useState<SymbolItem[]>([]);
  const [jobs, setJobs] = useState<SyncJob[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const [syms, js] = await Promise.all([api.symbols(), api.syncJobs()]);
    setSymbols(syms);
    setJobs(js);
  }

  useEffect(() => {
    load().catch((err) =>
      setError(err instanceof Error ? err.message : "加载失败"),
    );
  }, []);

  async function onSync() {
    setBusy(true);
    setError("");
    try {
      const result = await api.runSync();
      setJobs(result);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "同步失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <header className="page-head">
        <div>
          <h1>数据同步</h1>
          <p>拉取观察列表行情到本地 SQLite；网络异常时自动回退到可复现样本数据。</p>
        </div>
        <div className="actions">
          <button className="btn btn-primary" onClick={onSync} disabled={busy}>
            {busy ? "同步中…" : "同步全部观察列表"}
          </button>
        </div>
      </header>

      {error && <div className="banner">{error}</div>}

      <section className="panel" style={{ marginBottom: 18 }}>
        <h3>观察列表</h3>
        <p className="panel-desc">默认包含美股核心标的与宽基 ETF</p>
        <div className="list">
          {symbols.map((s) => (
            <div className="list-row" key={s.ticker}>
              <div className="ticker">{s.ticker}</div>
              <div>
                <div>{s.name}</div>
                <div className="muted">{s.market}</div>
              </div>
            </div>
          ))}
          {!symbols.length && <div className="empty">暂无标的</div>}
        </div>
      </section>

      <section className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>状态</th>
              <th>K 线条数</th>
              <th>说明</th>
              <th>完成时间</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id}>
                <td className="ticker">{job.ticker}</td>
                <td>
                  <span className={`status ${job.status}`}>{job.status}</span>
                </td>
                <td>{job.bars_synced}</td>
                <td className="muted">{job.message}</td>
                <td className="muted">
                  {job.finished_at
                    ? new Date(job.finished_at).toLocaleString("zh-CN", {
                        hour12: false,
                      })
                    : "—"}
                </td>
              </tr>
            ))}
            {!jobs.length && (
              <tr>
                <td colSpan={5} className="empty">
                  尚未执行同步
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
