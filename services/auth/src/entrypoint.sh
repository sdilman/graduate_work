#!/bin/bash
set -e
set -x

python -m helpers.wait_for_services &
PG_PID=$!

wait $PG_PID

python -m migrations.run
gunicorn -c gunicorn_conf.py main:app
