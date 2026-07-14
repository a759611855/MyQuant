#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export PATH="$HOME/.local/bin:$PATH"

if [[ ! -d "$ROOT/backend/.venv" ]]; then
  python3 -m venv "$ROOT/backend/.venv"
  # shellcheck disable=SC1091
  source "$ROOT/backend/.venv/bin/activate"
  pip install -r "$ROOT/backend/requirements.txt"
else
  # shellcheck disable=SC1091
  source "$ROOT/backend/.venv/bin/activate"
fi

if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
  (cd "$ROOT/frontend" && npm install)
fi

uvicorn app.main:app --app-dir "$ROOT/backend" --reload --port 8000 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT

cd "$ROOT/frontend"
npm run dev -- --host 127.0.0.1 --port 5173
