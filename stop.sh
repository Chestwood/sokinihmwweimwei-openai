#!/bin/bash
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"
if [ -f .sokinihmwweimwei.pid ]; then
  PID="$(cat .sokinihmwweimwei.pid)"
  kill "$PID" 2>/dev/null || true
  rm -f .sokinihmwweimwei.pid
fi
echo "Sokinihmwweimwei stopped."
