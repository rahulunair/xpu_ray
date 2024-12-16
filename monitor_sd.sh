#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}Monitoring Service Status...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop monitoring${NC}\n"

check_xpu_smi() {
    command -v xpu-smi >/dev/null 2>&1
}

counter=0
while true; do
    #clear
    echo -e "${GREEN}\n=== Service Status $(date) ===${NC}\n"

    echo -e "${GREEN}=== Services Health ===${NC}"
    for service in "sd_proxy:Traefik" "sd_auth:Auth" "sd_service:SD Service"; do
        name=${service#*:}
        container=${service%:*}
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            echo -e "${GREEN}✓ ${name}${NC}"
        else
            echo -e "${RED}✗ ${name} not running${NC}"
        fi
    done

    echo -e "\n${GREEN}=== API Health ===${NC}"
    if curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/health >/dev/null; then
        echo -e "${GREEN}✓ API responding${NC}"
    else
        echo -e "${RED}✗ API not responding${NC}"
    fi

    if [ $counter -eq 0 ]; then
        echo -e "\n${GREEN}=== Resource Usage ===${NC}"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        if check_xpu_smi; then
            echo -e "\n${GREEN}=== XPU Status ===${NC}"
            xpu-smi dump -m0,18,2 -n1 2>/dev/null || echo -e "${YELLOW}Unable to get XPU metrics${NC}"
        fi
        echo -e "\n${GREEN}=== Ray Status ===${NC}"
        docker exec sd_service ray status 2>/dev/null || echo -e "${RED}Ray status check failed${NC}"

        echo -e "\n${GREEN}=== Serve Status ===${NC}"
        docker exec sd_service serve status 2>/dev/null || echo -e "${RED}Serve status check failed${NC}"
    fi
    counter=$((($counter + 1) % 6))
    sleep 10
done
