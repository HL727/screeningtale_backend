#! /usr/bin/env bash

# Let the DB start
python /app/app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Pre-seed DB with data
python /app/app/pre_seed_db.py

# Run the application with hot-reload
exec uvicorn --reload --host "0.0.0.0" --port 80 --forwarded-allow-ips "*" "app.main:app"