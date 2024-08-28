#!/bin/bash

set -e
set -x

echo 'Waiting for Billing App to start...'

python -m helpers.wait_for_services &
B_APP_PID=$!

wait $B_APP_PID

alembic upgrade head

pytest
