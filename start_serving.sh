#!/bin/bash
export RAY_SERVE_ENABLE_EXPERIMENTAL_STREAMING=1
export RAY_SERVE_HTTP_OPTIONS='{"host": "0.0.0.0", "port": 8000}'

ray start --head
serve run serve:entrypoint 