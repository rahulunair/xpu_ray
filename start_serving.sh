#!/bin/bash
set -x

export RAY_SERVE_ENABLE_EXPERIMENTAL_STREAMING=1
export RAY_SERVE_HTTP_OPTIONS='{"host": "0.0.0.0", "port": 9002}'
export RAY_SERVE_PROXY_HOST="0.0.0.0"

# Clean up any existing Ray processes
ray stop || true
sleep 2

# Start Ray
ray start --head

# Start Serve
serve run serve:entrypoint 