#!/bin/bash
set -e
set -x

export RAY_SERVE_ENABLE_EXPERIMENTAL_STREAMING=1
export RAY_SERVE_HTTP_OPTIONS='{"host": "0.0.0.0", "port": 9002}'
export RAY_SERVE_PROXY_HOST="0.0.0.0"
export RAY_ADDRESS="0.0.0.0:6379"

# Stop any existing Ray processes
ray stop || true
sleep 2

# Start Ray with explicit host binding
ray start --head --disable-usage-stats \
    --node-ip-address="0.0.0.0" \
    --port=6379 \
    --dashboard-host="0.0.0.0" \
    --dashboard-port=8265

# Start Serve
serve run serve:entrypoint