#!/bin/bash
set -e
set -x

echo 'Waiting for services to start...'

python -m helpers.wait_for_app &
PG_PID=$!

wait $PG_PID

WORKER_NAME=$1
echo "Starting $WORKER_NAME worker..."
python workers/"$WORKER_NAME"
