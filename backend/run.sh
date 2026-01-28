#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

exec ./.venv/bin/python -m uvicorn app.main:app \
  --host 0.0.0.0 --port 80 --workers 1
