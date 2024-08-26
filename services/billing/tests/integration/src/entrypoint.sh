#!/bin/bash

set -e
set -x

python -m helpers.wait_for_app
pytest
