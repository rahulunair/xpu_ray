#!/bin/bash

# ==============================================================================
# Deploy Stable Diffusion API Service on Intel XPUs
# ==============================================================================
# This script deploys the Stable Diffusion API service with the specified model.
# It manages Docker services, generates authentication tokens, and provides
# options to skip restarting base services.
# ==============================================================================

set -e

# ------------------------------------------------------------------------------
# Displays usage information and available options.
# ------------------------------------------------------------------------------
show_help() {
    echo "Usage: ./deploy.sh [MODEL] [OPTIONS]"
    echo
    echo "Deploy Stable Diffusion API service with specified model"
    echo
    echo "Available Models:"
    python3 -c '
import sys
from config.model_configs import MODEL_CONFIGS
for name, config in MODEL_CONFIGS.items():
    default = " (default)" if config.get("default", False) else ""
    steps = config["default_steps"]
    print(f"  {name:<15} {steps:>2} steps{default}")
    '
    echo
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --skip-base    Don't restart base services (Traefik & Auth)"
    echo
    echo "Examples:"
    echo "  ./deploy.sh                     # Deploy with default model (sdxl-lightning)"
    echo "  ./deploy.sh sdxl                # Deploy with SDXL model"
    echo "  ./deploy.sh sdxl --skip-base    # Change to SDXL without restarting base services"
}

# ------------------------------------------------------------------------------
# Parse Command-Line Arguments
# ------------------------------------------------------------------------------
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    show_help
    exit 0
fi

# Validate model name against available configs
if [ -n "$1" ] && [ "$1" != "--skip-base" ]; then
    if ! python3 -c "from config.model_configs import MODEL_CONFIGS; exit(0 if '$1' in MODEL_CONFIGS else 1)"; then
        echo "Error: Invalid model name '$1'"
        echo "Run './deploy.sh --help' to see available models"
        exit 1
    fi
fi

DEFAULT_MODEL=${1:-"sdxl-lightning"}
echo "ℹ️  Model: $DEFAULT_MODEL will be loaded"
export DEFAULT_MODEL="$DEFAULT_MODEL"

# ------------------------------------------------------------------------------
# Generates a token with both memorability and entropy
# For production consider using tokens with higher entropy
# Current entropy: ~ 96 bits
# ------------------------------------------------------------------------------
generate_secure_token() {
    local adjectives=(
        "swift" "bright" "unique" "calm" "deep" "bold"
        "wise" "kind" "pure" "humble" "warm" "cool"
        "fresh" "clear" "radiant" "keen" "firm" "true"
    )

    local nouns=(
        "wave" "star" "moon" "sun" "wind"
        "tree" "lake" "bird" "cloud" "rose" "light"
        "peak" "rain" "leaf" "seed" "song"
    )
    local adj1_idx=$(($(openssl rand -hex 1 | od -An -i) % ${#adjectives[@]}))
    local adj2_idx=$(($(openssl rand -hex 1 | od -An -i) % ${#adjectives[@]}))
    local noun_idx=$(($(openssl rand -hex 1 | od -An -i) % ${#nouns[@]}))
    local random_hex=$(openssl rand -hex 12)
    echo "${adjectives[$adj1_idx]}-${adjectives[$adj2_idx]}-${nouns[$noun_idx]}-${random_hex}"
}

# ------------------------------------------------------------------------------
# Check Docker Status
# ------------------------------------------------------------------------------
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# ------------------------------------------------------------------------------
# Token Generation
# ------------------------------------------------------------------------------
TOKEN_FILE=".auth_token.env"
if [ -f "$TOKEN_FILE" ]; then
    source "$TOKEN_FILE"
    echo "Using existing token: $VALID_TOKEN"
else
    export VALID_TOKEN=$(generate_secure_token)
    echo "export VALID_TOKEN=$VALID_TOKEN" >"$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    echo "Generated new token: $VALID_TOKEN"
fi

# ------------------------------------------------------------------------------
# Manage Docker Services
# ------------------------------------------------------------------------------
if [ "$2" != "--skip-base" ]; then
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
else
    echo "Skipping base services startup (--skip-base flag detected)"
fi

echo "2. Starting SD service with model: $DEFAULT_MODEL..."
docker compose up -d
echo "Waiting for services to be ready, SD service will take some time to load models..."

# ------------------------------------------------------------------------------
# Wait for Service to be Ready
# ------------------------------------------------------------------------------
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

TIMEOUT=120
START_TIME=$(date +%s)
while true; do
    if curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/health >/dev/null; then
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

# ------------------------------------------------------------------------------
# Display Available Models and Example Usage
# ------------------------------------------------------------------------------
echo -e "\n=== Model Info ==="
sleep 5
response=$(curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/info)
if echo "$response" | python3 -m json.tool >/dev/null 2>&1; then
    echo "$response" | python3 -m json.tool
else
    echo "Error getting model info. Raw response:"
    echo "$response"
    echo -e "\nTry checking the logs with: docker compose logs"
fi

echo -e "\n=== Quick API Examples ==="
echo "# Health Check"
echo "curl http://localhost:9000/imagine/health -H \"Authorization: Bearer \$VALID_TOKEN\""
echo
echo "# Get Model Info"
echo "curl http://localhost:9000/imagine/info -H \"Authorization: Bearer \$VALID_TOKEN\""
echo
echo "# Generate Image"
echo "curl -X POST http://localhost:9000/imagine/generate -H \"Authorization: Bearer \$VALID_TOKEN\" -H \"Content-Type: application/json\" -d '{\"prompt\":\"a magical cosmic unicorn\",\"img_size\":1024,\"guidance_scale\":0,\"num_inference_steps\":4}' --output image.png"

echo -e "\n=== Monitor Service ==="
echo "./monitor_sd.sh"
