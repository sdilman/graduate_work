#!/bin/bash
set -e
set -x

python -m migrations
gunicorn -c gunicorn_conf.py main:app
