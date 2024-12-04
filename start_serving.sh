#!/bin/bash
set -e
set -x

export RAY_SERVE_ENABLE_EXPERIMENTAL_STREAMING=1
export RAY_SERVE_HTTP_OPTIONS='{"host": "0.0.0.0", "port": 8000}'

ray start --head --disable-usage-stats
serve deploy serve_config.yaml
tail -f /dev/null