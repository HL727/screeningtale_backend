#! /usr/bin/env bash
set -e

python /app/app/celeryworker_pre_start.py

# celery [OPTIONS] COMMAND [OPTIONS]
# -A is the app
# beat is the COMMAND
# -l is the log level
celery -A app.worker beat -l info