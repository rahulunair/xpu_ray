#!/bin/bash

generate_fun_token() {
    local adjectives=("magical" "cosmic" "quantum" "stellar" "mystic" "cyber" "neural" "atomic")
    local nouns=("unicorn" "phoenix" "dragon" "wizard" "ninja" "samurai" "warrior" "sage")
    local adj=${adjectives[$RANDOM % ${#adjectives[@]}]}
    local noun=${nouns[$RANDOM % ${#nouns[@]}]}
    local random_hex=$(openssl rand -hex 8)
    echo "${adj}-${noun}-${random_hex}"
}

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

echo "Stopping any services before starting again"
docker compose down

echo "Rebuilding with cache"
docker compose build # use --no-cache to rebuild clean

echo "Starting services in order..."
echo "1. Starting Traefik..."
docker compose up -d traefik
sleep 5

echo "2. Starting Auth service..."
docker compose up -d auth
sleep 5

echo "3. Starting SD service..."
docker compose up -d sd-service
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

# Wait for service to be ready
until curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/health > /dev/null; do
    echo "Waiting for service to be ready..."
    sleep 5
done

echo -e "\n📚 Available Models:"
curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/info | grep -o '"available_models":\[[^]]*\]'

echo -e "\n🚀 Example Usage:"
echo "curl -X POST \"http://localhost:9000/imagine/sdxl-turbo\" \\"
echo "     -H \"Authorization: Bearer $VALID_TOKEN\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"prompt\": \"a magical cosmic unicorn\"}'"

echo -e "\n💡 For monitoring service status:"
echo "./monitor_sd.sh"