#!/bin/sh
set -e
echo "Running Alembic migrations..."
alembic upgrade head
echo "Starting JobHunter backend..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
