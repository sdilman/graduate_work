#!/bin/bash
set -e
set -x

echo 'Waiting for Postgres to start...'

python -m helpers.wait_for_services &
PG_PID=$!

wait $PG_PID

echo "Starting billing service..."

gunicorn -c gunicorn_conf.py main:app
