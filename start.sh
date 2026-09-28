#!/bin/bash
set -e
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"
PORT="$(grep '^PORT=' .env 2>/dev/null | cut -d= -f2- || true)"
PORT="${PORT:-8787}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python is missing. Run setup.sh first."
  exit 1
fi

if [ ! -f .env ]; then
  echo "OpenAI key is not configured. Run setup.sh first."
  exit 1
fi

if [ -f .sokinihmwweimwei.pid ] && kill -0 "$(cat .sokinihmwweimwei.pid)" 2>/dev/null; then
  :
else
  nohup python3 server.py > server.log 2>&1 &
  echo $! > .sokinihmwweimwei.pid
  sleep 1
fi

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://127.0.0.1:${PORT}" >/dev/null 2>&1 || true
fi
