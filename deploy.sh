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


echo "Starting services..."
docker compose up -d
echo "Waiting for services to be ready..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8000/health | grep -q '"status":"healthy"'; then
        echo "Services are ready!"
        break
    fi
    
    echo "Attempt $attempt of $max_attempts: Services not ready yet... waiting"
    sleep 10
    ((attempt++))
    
    if [ $attempt -gt $max_attempts ]; then
        echo "Services failed to start within the expected time"
        exit 1
    fi
done


echo -e "\n🎨 XPU Ray Stable Diffusion Service is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 API URL: http://localhost:8000"
echo "🔑 Auth Token: $VALID_TOKEN"
echo "🔐 Use with: Authorization: Bearer $VALID_TOKEN"
echo "💡 To source token in new shell: source .auth_token.env"

echo -e "\n📚 Available Models:"
curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:8000/info | grep -o '"available_models":\[[^]]*\]'


echo -e "\n🚀 Example Usage:"
echo "curl -X POST \"http://localhost:8000/imagine/sdxl-turbo\" \\"
echo "     -H \"Authorization: Bearer $VALID_TOKEN\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"prompt\": \"a magical cosmic unicorn\"}'"