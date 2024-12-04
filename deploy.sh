#!/bin/bash

# Exit on error
set -e

generate_fun_token() {
    local adjectives=("magical" "cosmic" "quantum" "stellar" "mystic" "cyber" "neural" "atomic")
    local nouns=("unicorn" "phoenix" "dragon" "wizard" "ninja" "samurai" "warrior" "sage")
    local adj=${adjectives[$RANDOM % ${#adjectives[@]}]}
    local noun=${nouns[$RANDOM % ${#nouns[@]}]}
    local random_hex=$(openssl rand -hex 8)
    echo "${adj}-${noun}-${random_hex}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Token generation
TOKEN_FILE=".auth_token.env"
if [ -f "$TOKEN_FILE" ]; then
    source "$TOKEN_FILE"
    echo "Using existing token: $VALID_TOKEN"
else
    export VALID_TOKEN=$(generate_fun_token)
    echo "export VALID_TOKEN=$VALID_TOKEN" > "$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    echo "Generated new token: $VALID_TOKEN"
fi

echo "Ensuring network exists..."
docker network inspect sd_network >/dev/null 2>&1 || docker network create sd_network

echo "Stopping any existing services..."
docker compose -f docker-compose.base.yml down --remove-orphans
docker compose down --remove-orphans

echo "Building services..."
echo "1. Building base services..."
docker compose -f docker-compose.base.yml build
echo "2. Building SD service..."
docker compose build

echo "Starting services in order..."
echo "1. Starting base services (Traefik and Auth)..."
docker compose -f docker-compose.base.yml up -d
echo "Waiting for base services to be healthy..."
sleep 5

echo "2. Starting SD service..."
docker compose up -d
echo "Waiting for services to be ready, SD service will take some time to load models..."

echo -e "\n🎨 XPU Ray Stable Diffusion Service is starting!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 API URL: http://localhost:9000"
echo "🔑 Auth Token: $VALID_TOKEN"
echo "🔐 Use with: Authorization: Bearer $VALID_TOKEN"
echo "💡 To source token in new shell: source .auth_token.env"
echo "📊 Traefik Dashboard: http://localhost:8080"
echo "🔍 Monitor SD service: ./monitor_sd.sh"

echo -e "\n⏳ Waiting for SD service to be ready..."
echo "You can monitor the status with: ./monitor_sd.sh"

# Wait for service to be ready with timeout
TIMEOUT=300  # 5 minutes
START_TIME=$(date +%s)
while true; do
    if curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/health > /dev/null; then
        break
    fi
    
    CURRENT_TIME=$(date +%s)
    ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED_TIME -gt $TIMEOUT ]; then
        echo "Timeout waiting for service to be ready"
        echo "Please check logs with: docker compose logs"
        exit 1
    fi
    
    echo "Waiting for service to be ready... (${ELAPSED_TIME}s)"
    sleep 5
done

echo -e "\n📚 Available Models:"
curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/info | grep -o '"available_models":\[[^]]*\]'

echo -e "\n🚀 Example Usage:"
echo "curl -X POST \"http://localhost:9000/imagine/sdxl-turbo?prompt=a%20magical%20cosmic%20unicorn\" \\"
echo "     -H \"Authorization: Bearer $VALID_TOKEN\""

echo -e "\n💡 For monitoring service status:"
echo "./monitor_sd.sh"