#!/usr/bin/env sh
set -eu

if [ ! -f /app/chroma_db/chroma.sqlite3 ]; then
  echo "[startup] chroma_db missing, rebuilding from syllabus docs..."
  python /app/scripts/ingest_syllabus.py
else
  echo "[startup] existing chroma_db found, skipping ingest"
fi

exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8080}"
