#!/usr/bin/env bash
# health-check.sh — valida que todo o stack do WebLogic está saudável
# Uso: ./health-check.sh [VM_IP]
# Default: localhost (assume rodando direto na VM)

set -u

VM_IP="${1:-localhost}"
ADMIN_PORT=7001
MS1_PORT=8001
MS2_PORT=8002
APP_PATH="/hello/"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    printf "  %-50s" "$name"
    status=$(curl -o /dev/null -s -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)

    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✓ $status${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}✗ $status (esperado $expected_status)${NC}"
        FAIL=$((FAIL + 1))
    fi
}

echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  WebLogic 14c Lab — Health Check${NC}"
echo -e "${CYAN}  Target: $VM_IP${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"

echo ""
echo -e "${YELLOW}▸ Management Plane${NC}"
check "AdminServer console"      "http://$VM_IP:$ADMIN_PORT/console/login/LoginForm.jsp"
check "AdminServer ready app"    "http://$VM_IP:$ADMIN_PORT/weblogic/ready"

echo ""
echo -e "${YELLOW}▸ Managed Servers${NC}"
check "ms1 ready"                "http://$VM_IP:$MS1_PORT/weblogic/ready"
check "ms2 ready"                "http://$VM_IP:$MS2_PORT/weblogic/ready"

echo ""
echo -e "${YELLOW}▸ Application deployed${NC}"
check "App on ms1"               "http://$VM_IP:$MS1_PORT$APP_PATH"
check "App on ms2"               "http://$VM_IP:$MS2_PORT$APP_PATH"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}  Todos os $PASS checks passaram ✓${NC}"
    exit 0
else
    echo -e "${RED}  $FAIL falha(s), $PASS sucesso(s)${NC}"
    exit 1
fi
