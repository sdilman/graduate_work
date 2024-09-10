#!/bin/bash

set -e
set -x

python -m helpers.wait_for_services &
W_PID=$!

wait $W_PID

pytest -vv
