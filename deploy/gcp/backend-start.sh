#!/usr/bin/env sh
set -eu

if [ "${RAG_PROVIDER:-local}" = "vertex" ] && [ ! -f /app/vertex_index.json ]; then
  python /app/scripts/ingest_syllabus.py
fi

exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8080}"
