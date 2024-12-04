#!/bin/bash

# Generate a secure token if not provided
if [ -z "$VALID_TOKEN" ]; then
    export VALID_TOKEN=$(openssl rand -hex 32)
    echo "Generated token: $VALID_TOKEN"
fi

# Start services
docker compose up -d

echo "Waiting for services to be ready..."
until curl -s http://localhost:8000/health | grep -q '"status":"healthy"'; do
    echo "Service not ready yet... waiting"
    sleep 10
done

echo "Services started and healthy!"
echo "Access the API at: http://localhost:8000"
echo "Use the token in Authorization header: Bearer $VALID_TOKEN"

# Show available models
echo -e "\nAvailable models:"
curl -s http://localhost:8000/info | grep -o '"available_models":\[[^]]*\]'