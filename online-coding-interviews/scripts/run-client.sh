#!/bin/bash

# Run the frontend client

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/../frontend"

echo -e "${GREEN}✓ Starting frontend client...${NC}"
echo -e "${GREEN}Client running at: http://localhost:8080${NC}"

python3 -m http.server 8080
