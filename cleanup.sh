#!/bin/bash

echo "Stopping all services..."
docker compose -f docker-compose.base.yml down --remove-orphans
docker compose down --remove-orphans

echo "Removing service images..."
docker rmi sd_service sd_auth 2> /dev/null || true

echo "Pruning unused networks..."
docker network prune -f

echo "Pruning unused volumes..."
docker volume prune -f

echo "Pruning unused images..."
docker image prune -f
rm -f .auth_token.env
echo "Cleanup complete!"
