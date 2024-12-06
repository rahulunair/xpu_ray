#!/bin/bash
set -e
set -x

ray start --head --disable-usage-stats \
    --node-ip-address="0.0.0.0" \
    --port=6379 \
    --dashboard-host="0.0.0.0" \
    --dashboard-port=8265

serve deploy serve_config.yaml
tail -f /dev/null
