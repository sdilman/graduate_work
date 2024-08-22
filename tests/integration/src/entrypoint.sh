#!/bin/bash

set -e
set -x

python -m tests.helpers.wait_for_app
pytest /opt/app/tests/integration/src