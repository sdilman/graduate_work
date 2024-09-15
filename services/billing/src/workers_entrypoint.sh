#!/bin/bash
set -e
set -x

echo 'Waiting for services to start...'

python -m helpers.wait_for_services &
PG_PID=$!

wait $PG_PID

echo "Upgrading database..."

alembic upgrade head

WORKER_NAME=$1
echo "Starting $WORKER_NAME worker..."
python workers/"$WORKER_NAME"
