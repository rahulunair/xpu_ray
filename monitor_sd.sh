#!/bin/bash

# Set colors for better visibility
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Monitoring SD Service Status...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop monitoring${NC}\n"

while true; do
    clear
    echo -e "${GREEN}=== SD Service Status ===${NC}"
    echo -e "${GREEN}$(date)${NC}\n"
    
    docker compose exec sd-service serve status
    
    sleep 2
done 