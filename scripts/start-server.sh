#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

for p in 5173 8000; do
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${p}/tcp" >/dev/null 2>&1 || true
  else
    lsof -ti tcp:"$p" | xargs -r kill >/dev/null 2>&1 || true
  fi
done

npm run start &
SERVER_PID=$!

sleep 2
if command -v setsid >/dev/null 2>&1; then
  setsid -f xdg-open http://localhost:5173/ >/dev/null 2>&1 || true
else
  xdg-open http://localhost:5173/ >/dev/null 2>&1 || true
fi

wait "$SERVER_PID"
