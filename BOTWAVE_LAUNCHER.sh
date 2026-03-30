#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# BOTWAVE EMPIRE LAUNCHER
# Optimized for 8GB VRAM (RTX 5060)
# ═══════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           BOTWAVE EMPIRE LAUNCHER                        ║"
echo "║           Optimized for 8GB VRAM                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check LM Studio
echo -n "Checking LM Studio... "
if curl -s http://localhost:1234/v1/models | grep -q '"data"'; then
    echo -e "${GREEN}RUNNING${NC}"
else
    echo -e "${RED}NOT RUNNING${NC}"
    echo ""
    echo "${YELLOW}Please start LM Studio server first:${NC}"
    echo "  1. Open LM Studio"
    echo "  2. Load model: qwen3.5-4b-uncensored-hauhaucs-aggressive"
    echo "  3. Click 'Start Server' on port 1234"
    echo ""
    exit 1
fi

# Show current models
echo ""
echo -e "${CYAN}Loaded Models:${NC}"
curl -s http://localhost:1234/v1/models | python3 -c "
import sys, json
models = json.load(sys.stdin).get('data', [])
for m in models:
    print(f'  • {m[\"id\"]}')
"

# VRAM Check
echo ""
echo -e "${CYAN}VRAM Status:${NC}"
nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader | awk '{
    used=$1; free=$2
    gsub(/ MiB/, "", used)
    gsub(/ MiB/, "", free)
    used_gb=used/1024
    free_gb=free/1024
    printf "  Used: %.1f GB | Free: %.1f GB\n", used_gb, free_gb
}'

# Recommendation
echo ""
if [ $(curl -s http://localhost:1234/v1/models | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',[])))") -gt 2 ]; then
    echo -e "${YELLOW}⚠ TIP: Multiple models detected.${NC}"
    echo "   For best performance, keep only these in LM Studio:"
    echo "   • qwen3.5-4b-uncensored-hauhaucs-aggressive (main)"
    echo ""
    echo "   To unload others: Right-click model → Unload in LM Studio"
fi

# Menu
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Select an option:${NC}"
echo ""
echo "  1) Botwave Agent TUI (chat like Claude Code)"
echo "  2) Dashboard (web UI on port 5000)"
echo "  3) Run all SCRYPT KEEPER scripts"
echo "  4) Agent Job Runner (auto-coding with aider)"
echo "  5) System Status"
echo "  6) Exit"
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo -n "> "

read -r choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Launching Botwave Agent TUI...${NC}"
        echo -e "${YELLOW}Commands: /help, /clear, /status, /quit${NC}"
        echo ""
        python3 /home/gringo/BotwaveEmpire/bin/botwave-agent -i
        ;;
    2)
        echo ""
        echo -e "${GREEN}Starting Dashboard on http://localhost:5000${NC}"
        cd /home/gringo/BotwaveEmpire/dashboard
        python3 web_app.py &
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        wait
        ;;
    3)
        echo ""
        echo -e "${GREEN}Running all SCRYPT KEEPER scripts...${NC}"
        cd /home/gringo/BotwaveEmpire
        python3 scrypt_keeper_master.py --run-all
        ;;
    4)
        echo ""
        echo -e "${GREEN}Agent Job Runner${NC}"
        echo "This uses aider + LM Studio to auto-fix code issues"
        echo ""
        python3 /home/gringo/BotwaveEmpire/skills/active/self-audit/audit.py --list-issues
        echo ""
        echo -e "${YELLOW}To fix issues, run:${NC}"
        echo "  aid --yes <files>"
        ;;
    5)
        echo ""
        botwave status
        ;;
    6)
        echo -e "${GREEN}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac
