#!/bin/bash
# Production startup script for GenHealth.AI Assessment
# This script ensures the API runs continuously without stopping

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/mounikakapa/Desktop/GenHealth.AI assesment"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
PID_FILE="$PROJECT_DIR/api.pid"
LOG_FILE="$PROJECT_DIR/api.log"

echo -e "${BLUE}🚀 Starting GenHealth.AI Assessment API...${NC}"

# Function to check if API is running
check_api() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo -e "${GREEN}✅ API is running (PID: $PID)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  PID file exists but process not running${NC}"
            rm -f "$PID_FILE"
        fi
    fi
    echo -e "${RED}❌ API is not running${NC}"
    return 1
}

# Function to start the API
start_api() {
    echo -e "${BLUE}📡 Starting Flask API...${NC}"
    
    cd "$PROJECT_DIR"
    
    # Start the API in background and capture PID
    nohup "$VENV_PYTHON" run.py > "$LOG_FILE" 2>&1 &
    API_PID=$!
    
    # Save PID to file
    echo $API_PID > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 3
    
    if kill -0 $API_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Flask API started successfully (PID: $API_PID)${NC}"
        echo -e "${GREEN}📊 API running on: http://127.0.0.1:3000${NC}"
        echo -e "${GREEN}📊 Network access: http://192.168.1.166:3000${NC}"
        echo -e "${GREEN}📋 Log file: $LOG_FILE${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to start Flask API${NC}"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the API
stop_api() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}🛑 Stopping API (PID: $PID)...${NC}"
        kill $PID 2>/dev/null || true
        rm -f "$PID_FILE"
        echo -e "${GREEN}✅ API stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  No PID file found${NC}"
    fi
}

# Function to restart the API
restart_api() {
    echo -e "${BLUE}🔄 Restarting API...${NC}"
    stop_api
    sleep 2
    start_api
}

# Function to show status
status() {
    echo -e "${BLUE}📊 GenHealth.AI API Status:${NC}"
    echo "=================================="
    
    if check_api; then
        PID=$(cat "$PID_FILE")
        echo -e "Status: ${GREEN}RUNNING${NC}"
        echo -e "PID: ${GREEN}$PID${NC}"
        echo -e "Local URL: ${GREEN}http://127.0.0.1:3000${NC}"
        echo -e "Network URL: ${GREEN}http://192.168.1.166:3000${NC}"
        echo -e "Log file: ${BLUE}$LOG_FILE${NC}"
        
        # Test API health
        if curl -s http://127.0.0.1:3000/health > /dev/null 2>&1; then
            echo -e "Health Check: ${GREEN}PASS${NC}"
        else
            echo -e "Health Check: ${RED}FAIL${NC}"
        fi
        
        # Show recent logs
        if [ -f "$LOG_FILE" ]; then
            echo -e "\n${BLUE}📋 Recent logs:${NC}"
            tail -5 "$LOG_FILE"
        fi
    else
        echo -e "Status: ${RED}STOPPED${NC}"
    fi
    
    echo "=================================="
}

# Function to show logs
logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}📋 Showing API logs (Ctrl+C to exit):${NC}"
        tail -f "$LOG_FILE"
    else
        echo -e "${YELLOW}⚠️  No log file found${NC}"
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        if check_api; then
            echo -e "${YELLOW}⚠️  API is already running${NC}"
            status
        else
            start_api
        fi
        ;;
    stop)
        stop_api
        ;;
    restart)
        restart_api
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo -e "${BLUE}Usage: $0 {start|stop|restart|status|logs}${NC}"
        echo ""
        echo -e "${GREEN}Commands:${NC}"
        echo -e "  start   - Start the API (default)"
        echo -e "  stop    - Stop the API"
        echo -e "  restart - Restart the API"
        echo -e "  status  - Show API status"
        echo -e "  logs    - Show live logs"
        exit 1
        ;;
esac