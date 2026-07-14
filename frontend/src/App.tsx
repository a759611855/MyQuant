import { NavLink, Route, Routes } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import SyncPage from "./pages/SyncPage";
import ScoresPage from "./pages/ScoresPage";
import NewsPage from "./pages/NewsPage";

const links = [
  { to: "/", label: "看板", end: true },
  { to: "/sync", label: "数据同步" },
  { to: "/scores", label: "评分" },
  { to: "/news", label: "新闻" },
];

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            My<span>Quant</span>
          </div>
          <div className="brand-sub">个人量化分析平台</div>
        </div>
        <nav className="nav">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              <span className="nav-dot" />
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/sync" element={<SyncPage />} />
          <Route path="/scores" element={<ScoresPage />} />
          <Route path="/news" element={<NewsPage />} />
        </Routes>
      </main>
    </div>
  );
}
