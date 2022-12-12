#! /usr/bin/env bash

# Let the DB start
python /app/app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Pre-seed DB with data
python /app/app/pre_seed_db.py

# Run application
gunicorn -c /gunicorn.conf.py app.main:app