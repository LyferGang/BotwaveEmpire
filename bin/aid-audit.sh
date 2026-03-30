#!/bin/bash
# Botwave Self-Audit with Aider
# Uses aider's /run command to execute audit tasks

set -e

EMPIRE_DIR="$HOME/BotwaveEmpire"
cd "$EMPIRE_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  BOTWAVE SELF-AUDIT WITH AIDER${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check LM Studio
echo -n "Checking LM Studio... "
if curl -s http://localhost:1234/v1/models | grep -q '"data"'; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC} - Start LM Studio first"
    exit 1
fi

# Run Python audit first to find issues
echo ""
echo "Scanning for issues..."
python3 skills/active/self-audit/audit.py --list-issues

echo ""
echo -e "${CYAN}========================================${NC}"
echo "To fix issues with aider, run:"
echo "  aid --yes <files_to_fix>"
echo ""
echo "Or interactively:"
echo "  aid"
echo "  Then use: /run python skills/active/self-audit/audit.py --fix"
echo -e "${CYAN}========================================${NC}"
