#! /usr/bin/env bash
set -e

python /app/app/celeryworker_pre_start.py

# celery [OPTIONS] COMMAND [OPTIONS]
# -A is the app
# worker is the COMMAND
# -l is the log level
# -Q is the queues to use (comma separated list)
# -c is the amount of concurrency (set to one since concurrency is handled by scaling amount of docker services running)
celery -A app.worker worker -l info -Q main-queue -c 1 --prefetch-multiplier 1