#!/bin/bash
set -e
set -x

echo "Waiting for dependant containers to be ready..."

# TODO

echo "Starting billing service..."

gunicorn -c gunicorn_conf.py main:app
