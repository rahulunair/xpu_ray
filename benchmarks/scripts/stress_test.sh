#!/bin/bash

echo "Starting stress test..."
check_health() {
    curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/health > /dev/null
    return $?
}

for connections in 4 8 16 32 64; do
    threads=$((connections/4))
    if [ $threads -lt 1 ]; then
        threads=1
    fi 
    echo "Testing with $connections connections and $threads threads..."
    echo "date"
    wrk -t$threads -c$connections -d30s -s $(dirname $0)/test.lua http://localhost:9000/imagine/generate
    if ! check_health; then
        echo "Service became unresponsive at $connections connections!"
        break
    fi
    echo "Waiting 10s before next test..."
    sleep 10
done 