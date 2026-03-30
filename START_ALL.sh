#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# BOTWAVE EMPIRE - START ALL SYSTEMS
# SCRYPT KEEPER STYLE - Multi-Agent Parallel Execution
# ═══════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         BOTWAVE EMPIRE - STARTING ALL SYSTEMS            ║"
echo "║         SCRYPT KEEPER STYLE - Multi-Agent                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd /home/gringo/BotwaveEmpire

# Check LM Studio
echo -n "Checking LM Studio... "
if curl -s http://localhost:1234/v1/models | grep -q '"data"'; then
    echo -e "${GREEN}RUNNING${NC}"
    curl -s http://localhost:1234/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); models=[m['id'] for m in d.get('data',[])]; print(f'  Models: {models[0] if models else \"NONE\"}')"
else
    echo -e "${RED}NOT RUNNING${NC}"
    echo "  Start LM Studio server first!"
    exit 1
fi

# Start Docker Compose
echo ""
echo -e "${CYAN}Starting Docker Compose...${NC}"
docker-compose up -d 2>&1 | tail -5 || echo "Docker compose skipped (may need docker-compose installed)"

# Start Dashboard
echo ""
echo -e "${CYAN}Starting Dashboard (port 5000)...${NC}"
cd dashboard
python3 web_app.py &
DASHBOARD_PID=$!
cd ..
sleep 2
if curl -s http://localhost:5000 | head -1 | grep -q "<!DOCTYPE"; then
    echo -e "  ${GREEN}Dashboard RUNNING${NC} - http://localhost:5000"
else
    echo -e "  ${YELLOW}Dashboard starting...${NC}"
fi

# Start Plumbing Bot (PUBLIC)
echo ""
echo -e "${CYAN}Starting Plumbing Bot (PUBLIC - Captain Obvious)...${NC}"
python3 botwave_plumbing_bot.py &
PLUMBING_PID=$!
sleep 2
echo -e "  ${GREEN}Plumbing Bot RUNNING${NC}"
echo -e "  Message it: https://t.me/BotWaveBusinessBot"

# Start Public Demo Bot
echo ""
echo -e "${CYAN}Starting Public Demo Bot (Captain Obvious)...${NC}"
python3 botwave_public_demo_bot.py &
DEMO_PID=$!
sleep 2
echo -e "  ${GREEN}Demo Bot RUNNING${NC}"
echo -e "  Message it: https://t.me/CaptainObviousBot"

# Start Personal Bot (PRIVATE)
echo ""
echo -e "${CYAN}Starting Personal Bot (Boti1904 - PRIVATE)...${NC}"
python3 botwave_personal_bot.py &
PERSONAL_PID=$!
sleep 2
echo -e "  ${GREEN}Personal Bot RUNNING${NC}"
echo -e "  Only you can access: https://t.me/Boti1904Bot"

# Summary
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}           ALL SYSTEMS STARTED${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo ""
echo "  Dashboard:    http://localhost:5000"
echo "  API:          http://localhost:8080"
echo "  Plumbing Bot: t.me/BotWaveBusinessBot (PUBLIC)"
echo "  Demo Bot:     t.me/CaptainObviousBot (PUBLIC)"
echo "  Personal Bot: t.me/Boti1904Bot (PRIVATE - You only)"
echo ""
echo "  PIDs: Dashboard=$DASHBOARD_PID Plumbing=$PLUMBING_PID Demo=$DEMO_PID Personal=$PERSONAL_PID"
echo ""
echo -e "${YELLOW}To stop all: kill $DASHBOARD_PID $PLUMBING_PID $DEMO_PID $PERSONAL_PID${NC}"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for interrupt
wait
