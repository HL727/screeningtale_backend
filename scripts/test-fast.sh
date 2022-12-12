#! /usr/bin/env bash

# Exit in case of error
# set -e

docker-compose up -d
docker-compose exec -T backend bash /app/scripts/test.sh "$@"