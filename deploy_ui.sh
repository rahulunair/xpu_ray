#!/bin/bash

# ==============================================================================
# Deploy Image Generation UI
# ==============================================================================
# This script deploys the Streamlit UI for the Image Generation service
# and optionally creates a public demo endpoint using Cloudflare Tunnel.
# ==============================================================================

set -e
echo "🎉🎉 Starting a demo UI for the deployed service...🎉🎉"

# ------------------------------------------------------------------------------
# Check Dependencies and Environment
# ------------------------------------------------------------------------------
if [ ! -f ".auth_token.env" ]; then
    echo "❌ Error: Auth token not found. Please run deploy.sh first"
    exit 1
fi

if [ ! -d "simple_ui" ]; then
    echo "❌ Error: simple_ui directory not found"
    exit 1
fi

mkdir -p generated_images
source .auth_token.env
echo "🔍 Checking service health..."
health_response=$(curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/health)
if echo "$health_response" | grep -q "healthy"; then
    echo "✅ Image service is running and healthy"
else
    echo "❌ Error: Image service is not running or not healthy"
    echo "Response: $health_response"
    echo "Please start it first with deploy.sh"
    exit 1
fi

# ------------------------------------------------------------------------------
# Cleanup existing processes
# ------------------------------------------------------------------------------
echo "🧹 Cleaning up existing UI processes..."
pkill -f "streamlit run" || true
sleep 2

# ------------------------------------------------------------------------------
# Install Dependencies
# ------------------------------------------------------------------------------
echo "📦 Installing UI dependencies..."
pip install streamlit requests pillow >/dev/null 2>&1

# ------------------------------------------------------------------------------
# Deploy UI
# ------------------------------------------------------------------------------
echo "🚀 Starting UI server..."
nohup streamlit run simple_ui/app.py >/dev/null 2>&1 &  # Changed from video_app.py to app.py
UI_PID=$!

# Wait briefly for Streamlit to start
sleep 3

# ------------------------------------------------------------------------------
# Optional Tunnel Setup
# ------------------------------------------------------------------------------
echo -e "\n📡 Public Demo Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "🌐 Create public demo endpoint via Cloudflare Tunnel? [y/N] \c"
read -r create_tunnel

if [[ $create_tunnel =~ ^[Yy]$ ]]; then
    echo -e "\n⚠️  NOTICE: For evaluation purposes only"
    echo "🔄 Starting Cloudflare tunnel..."
    
    # Check if cloudflared is installed
    if ! command -v cloudflared &> /dev/null; then
        echo "📥 Installing cloudflared..."
        curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb >/dev/null 2>&1
        sudo dpkg -i cloudflared.deb >/dev/null 2>&1
        rm cloudflared.deb
        echo "✅ Cloudflared installed successfully"
    fi

    # Start tunnel for Streamlit UI
    echo "🚇 Starting tunnel for UI service..."
    trap 'kill $UI_PID 2>/dev/null || true' EXIT INT TERM
    cloudflared tunnel --url http://localhost:8501
else
    echo -e "\n🎉 UI Setup Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 Access the UI at: http://localhost:8501"
    echo "💡 Press Ctrl+C to stop the UI"
    trap 'kill $UI_PID 2>/dev/null || true' EXIT INT TERM
    wait $UI_PID
fi