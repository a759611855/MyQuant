import { useEffect, useState } from "react";
import { api, type Score } from "../api";

function Bar({ label, value }: { label: string; value: number }) {
  return (
    <div className="score-bar">
      <span>{label}</span>
      <i>
        <em style={{ width: `${Math.max(4, Math.min(100, value))}%` }} />
      </i>
      <span>{value.toFixed(0)}</span>
    </div>
  );
}

export default function ScoresPage() {
  const [scores, setScores] = useState<Score[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    setScores(await api.scores());
  }

  useEffect(() => {
    load().catch((err) =>
      setError(err instanceof Error ? err.message : "加载失败"),
    );
  }, []);

  async function onCompute() {
    setBusy(true);
    setError("");
    try {
      setScores(await api.computeScores());
    } catch (err) {
      setError(err instanceof Error ? err.message : "计算失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <header className="page-head">
        <div>
          <h1>评分</h1>
          <p>动量、波动、趋势与流动性四因子加权，输出综合分与等级。</p>
        </div>
        <div className="actions">
          <button className="btn btn-primary" onClick={onCompute} disabled={busy}>
            {busy ? "计算中…" : "重新计算评分"}
          </button>
        </div>
      </header>

      {error && <div className="banner">{error}</div>}

      <section className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>等级</th>
              <th>综合</th>
              <th>因子拆解</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            {scores.map((s) => (
              <tr key={s.ticker}>
                <td className="ticker">{s.ticker}</td>
                <td>
                  <span className={`grade ${s.grade}`}>{s.grade}</span>
                </td>
                <td>{s.total.toFixed(1)}</td>
                <td>
                  <div className="score-bars">
                    <Bar label="动量" value={s.momentum} />
                    <Bar label="波动" value={s.volatility} />
                    <Bar label="趋势" value={s.trend} />
                    <Bar label="流动性" value={s.liquidity} />
                  </div>
                </td>
                <td className="muted">{s.note}</td>
              </tr>
            ))}
            {!scores.length && (
              <tr>
                <td colSpan={5} className="empty">
                  暂无评分。请先在「数据同步」拉取行情，再点击重新计算。
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
