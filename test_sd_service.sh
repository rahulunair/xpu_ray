#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test directory
TEST_DIR="sd_test_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Load token from environment
source ../.auth_token.env

# Function to check if file is a valid PNG
check_image() {
    local file=$1
    # Check PNG header magic number (89 50 4E 47 0D 0A 1A 0A)
    if [ "$(hexdump -n 8 -e '8/1 "%02X"' "$file")" = "89504E470D0A1A0A" ]; then
        echo -e "${GREEN}✓ Valid PNG file: $file${NC}"
        return 0
    else
        echo -e "${RED}✗ Invalid PNG file: $file${NC}"
        cat "$file"  # Show content if it's an error message
        return 1
    fi
}

# Function to test model
test_model() {
    local model=$1
    local steps=$2
    local guidance=$3
    local size=$4
    local prompt="a magical cosmic unicorn in a cyberpunk city"
    
    echo -e "\n${YELLOW}Testing $model...${NC}"
    echo "Steps: $steps, Guidance: $guidance, Size: ${size}x${size}"
    
    local output_file="${model}_test.png"
    
    curl -X POST "http://localhost:9000/imagine/generate" \
         -H "Authorization: Bearer $VALID_TOKEN" \
         -H "Content-Type: application/json" \
         -d "{
           \"prompt\": \"$prompt\",
           \"img_size\": $size,
           \"guidance_scale\": $guidance,
           \"num_inference_steps\": $steps
         }" \
         --output "$output_file" \
         --silent
    
    if [ $? -eq 0 ]; then
        check_image "$output_file"
    else
        echo -e "${RED}✗ Request failed for $model${NC}"
    fi
}

# Main test sequence
echo -e "${YELLOW}Starting SD Service Tests${NC}"
echo -e "${YELLOW}Test results will be saved in: $TEST_DIR${NC}\n"

# Test health endpoint
echo -e "\n${YELLOW}Testing health endpoint...${NC}"
curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/health | jq .

# Test info endpoint
echo -e "\n${YELLOW}Testing info endpoint...${NC}"
curl -s -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/info | jq .

# Test image generation for each model
echo -e "\n${YELLOW}Testing image generation...${NC}"

# Fast models first
test_model "sdxl-turbo" 1 0.0 512
test_model "sdxl-lightning" 4 0.0 512

# Standard models
test_model "sdxl" 30 7.5 1024
test_model "sd2" 30 7.5 768

# Summary
echo -e "\n${YELLOW}Test Summary${NC}"
echo "Generated files:"
ls -lh *.png 2>/dev/null

echo -e "\n${GREEN}Tests completed!${NC}"
echo "Results saved in: $TEST_DIR" 