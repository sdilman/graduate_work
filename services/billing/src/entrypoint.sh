#!/bin/bash
set -e
set -x

echo 'Waiting for services to start...'

python -m helpers.wait_for_services &
PG_PID=$!

wait $PG_PID

echo "Starting billing service..."

alembic upgrade head

gunicorn -c gunicorn_conf.py main:app
