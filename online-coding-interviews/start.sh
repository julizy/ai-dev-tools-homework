#!/bin/bash

# Online Coding Interview Platform - Startup Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Online Coding Interview Platform${NC}"
echo -e "${BLUE}================================${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Parse command line arguments
MODE="${1:-full}"

case "$MODE" in
    full|dev)
        # Run both client and server concurrently
        if ! command -v npm &> /dev/null; then
            echo -e "${YELLOW}npm is not installed. Installing using Python only...${NC}"
            # Fallback to Python-only approach
            bash scripts/run-server.sh &
            bash scripts/run-client.sh &
            wait
        else
            echo -e "${YELLOW}Installing npm dependencies...${NC}"
            npm install > /dev/null 2>&1
            echo -e "${GREEN}✓ Dependencies installed${NC}"
            echo -e "${BLUE}================================${NC}"
            echo -e "${GREEN}Starting client and server...${NC}"
            echo -e "${GREEN}Client: http://localhost:8080${NC}"
            echo -e "${GREEN}Server: http://localhost:5000${NC}"
            echo -e "${BLUE}================================${NC}"
            npm run dev
        fi
        ;;
    server)
        # Run only the server
        cd backend
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}Creating virtual environment...${NC}"
            python3 -m venv venv
        fi
        source venv/bin/activate
        echo -e "${YELLOW}Installing dependencies...${NC}"
        pip install -r requirements.txt > /dev/null 2>&1
        echo -e "${GREEN}✓ Dependencies installed${NC}"
        echo -e "${BLUE}================================${NC}"
        echo -e "${GREEN}✓ Starting Flask server...${NC}"
        echo -e "${GREEN}Server running at: http://localhost:5000${NC}"
        echo -e "${BLUE}================================${NC}"
        python app.py
        ;;
    client)
        # Run only the client
        cd frontend
        echo -e "${GREEN}✓ Starting frontend client...${NC}"
        echo -e "${BLUE}================================${NC}"
        echo -e "${GREEN}Client running at: http://localhost:8080${NC}"
        echo -e "${BLUE}================================${NC}"
        python3 -m http.server 8080
        ;;
    *)
        echo -e "${YELLOW}Usage: ./start.sh [full|server|client]${NC}"
        echo -e "${BLUE}Options:${NC}"
        echo -e "  full    - Run client and server concurrently (default)"
        echo -e "  server  - Run only the backend server"
        echo -e "  client  - Run only the frontend client"
        exit 1
        ;;
esac
