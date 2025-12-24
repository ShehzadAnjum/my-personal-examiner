#!/bin/bash

# Kill Ports Script
# Forcefully closes processes running on specified ports
# Usage: ./kill-ports.sh [port1] [port2] [port3] ...
# Default: Kills ports 3000, 3001, 3002

set -e

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default ports if none specified
PORTS="${@:-3000 3001 3002}"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}           Port Killer - Force Close Stuck Ports        ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Function to kill processes on a port
kill_port() {
    local port=$1

    echo -e "${YELLOW}🔍 Checking port ${port}...${NC}"

    # Collect PIDs from multiple sources (handles both IPv4 and IPv6)
    PIDS=""

    # Try lsof first (most reliable for IPv4)
    if command -v lsof &> /dev/null; then
        PIDS=$(lsof -ti :$port 2>/dev/null || true)
    fi

    # Also check with netstat/ss (catches IPv6 processes that lsof might miss)
    if command -v ss &> /dev/null; then
        SS_PIDS=$(ss -tlnp 2>/dev/null | grep ":$port " | sed -n 's/.*pid=\([0-9]*\).*/\1/p' || true)
        PIDS="$PIDS $SS_PIDS"
    elif command -v netstat &> /dev/null; then
        NET_PIDS=$(netstat -tlnp 2>/dev/null | grep -E ":$port\s" | awk '{print $7}' | cut -d'/' -f1 || true)
        PIDS="$PIDS $NET_PIDS"
    fi

    # Try fuser as additional fallback
    if command -v fuser &> /dev/null; then
        FUSER_PIDS=$(fuser $port/tcp 2>/dev/null | awk '{print $1}' || true)
        PIDS="$PIDS $FUSER_PIDS"
    fi

    # Remove duplicates and empty values
    PIDS=$(echo $PIDS | tr ' ' '\n' | sort -u | grep -v '^$' || true)

    if [ -z "$PIDS" ]; then
        echo -e "${GREEN}✓ Port ${port} is already free${NC}"
        echo ""
        return 0
    fi

    # Show process details
    for PID in $PIDS; do
        if [ -d "/proc/$PID" ]; then
            PROCESS_NAME=$(ps -p $PID -o comm= 2>/dev/null || echo "unknown")
            PROCESS_CMD=$(ps -p $PID -o args= 2>/dev/null || echo "unknown")

            echo -e "${RED}✗ Found process on port ${port}:${NC}"
            echo -e "  PID:     ${PID}"
            echo -e "  Name:    ${PROCESS_NAME}"
            echo -e "  Command: ${PROCESS_CMD}"

            # Try graceful kill first
            echo -e "${YELLOW}  → Attempting graceful shutdown (SIGTERM)...${NC}"
            kill $PID 2>/dev/null || true
            sleep 1

            # Check if still running
            if kill -0 $PID 2>/dev/null; then
                echo -e "${RED}  → Graceful shutdown failed, forcing (SIGKILL)...${NC}"
                kill -9 $PID 2>/dev/null || true
                sleep 0.5
            fi

            # Verify killed
            if ! kill -0 $PID 2>/dev/null; then
                echo -e "${GREEN}  ✓ Process ${PID} killed successfully${NC}"
            else
                echo -e "${RED}  ✗ Failed to kill process ${PID}${NC}"
            fi
        fi
    done

    echo ""
}

# Kill all specified ports
KILLED_COUNT=0
for PORT in $PORTS; do
    # Validate port number
    if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
        echo -e "${RED}✗ Invalid port number: ${PORT}${NC}"
        echo ""
        continue
    fi

    kill_port $PORT
    KILLED_COUNT=$((KILLED_COUNT + 1))
done

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Processed ${KILLED_COUNT} port(s)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Verify ports are free
echo -e "${YELLOW}🔍 Verifying ports are free...${NC}"
ALL_FREE=true
for PORT in $PORTS; do
    if command -v lsof &> /dev/null; then
        if lsof -i :$PORT &> /dev/null; then
            echo -e "${RED}✗ Port ${PORT} still in use${NC}"
            ALL_FREE=false
        else
            echo -e "${GREEN}✓ Port ${PORT} is free${NC}"
        fi
    fi
done
echo ""

if $ALL_FREE; then
    echo -e "${GREEN}🎉 All ports successfully freed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some ports are still in use. Try running with sudo if needed.${NC}"
    exit 1
fi
