#!/bin/bash

# Run the backend server

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/../backend"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✓ Starting Flask server...${NC}"
echo -e "${GREEN}Server running at: http://localhost:5000${NC}"

python app.py
