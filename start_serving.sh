#!/bin/bash
set -e
set -x

export RAY_SERVE_ENABLE_EXPERIMENTAL_STREAMING=1
export RAY_SERVE_HTTP_OPTIONS='{"host": "0.0.0.0", "port": 9002}'
export RAY_SERVE_PROXY_HOST="0.0.0.0"
export RAY_ADDRESS="0.0.0.0:6379"

ray start --head
python3 -m serve run serve:entrypoint