#!/bin/sh

set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

cleanup() {
  if [ -n "${API_PID:-}" ]; then
    kill "$API_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

cd "$ROOT_DIR"
./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
API_PID=$!

cd "$ROOT_DIR/frontend"
npm run dev -- --host 127.0.0.1
