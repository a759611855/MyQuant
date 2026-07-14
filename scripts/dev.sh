#!/usr/bin/env bash
# 本地一键启动 MyQuant（后端 :8000 + 前端 :5173）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "缺少命令: $1"
    exit 1
  }
}

need python3
need npm

if [[ ! -d "$ROOT/backend/.venv" ]]; then
  echo ">> 创建 Python 虚拟环境…"
  python3 -m venv "$ROOT/backend/.venv"
  # shellcheck disable=SC1091
  source "$ROOT/backend/.venv/bin/activate"
  pip install -U pip
  pip install -r "$ROOT/backend/requirements.txt"
else
  # shellcheck disable=SC1091
  source "$ROOT/backend/.venv/bin/activate"
fi

if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
  echo ">> 安装前端依赖…"
  (cd "$ROOT/frontend" && npm install)
fi

cleanup() {
  if [[ -n "${API_PID:-}" ]] && kill -0 "$API_PID" 2>/dev/null; then
    kill "$API_PID" 2>/dev/null || true
    wait "$API_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo ">> 启动 API  http://127.0.0.1:8000"
(
  cd "$ROOT/backend"
  uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
) &
API_PID=$!

# 等待 API 就绪
for _ in $(seq 1 40); do
  if curl -sf http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done

echo ">> 启动前端 http://127.0.0.1:5173"
echo "   浏览器打开上述地址；Ctrl+C 同时停止前后端"
cd "$ROOT/frontend"
npm run dev -- --host 127.0.0.1 --port 5173
