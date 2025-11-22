#!/bin/bash
# Persistent ngrok tunnel for GenHealth.AI Assessment
# This script ensures ngrok stays running for the assessment period

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/mounikakapa/Desktop/GenHealth.AI assesment"
PID_FILE="$PROJECT_DIR/ngrok.pid"
LOG_FILE="$PROJECT_DIR/ngrok.log"
URL_FILE="$PROJECT_DIR/ngrok_url.txt"

echo -e "${BLUE}🌐 Starting Persistent Ngrok Tunnel...${NC}"

# Function to check if ngrok is running
check_ngrok() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo -e "${GREEN}✅ Ngrok is running (PID: $PID)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  PID file exists but process not running${NC}"
            rm -f "$PID_FILE"
        fi
    fi
    echo -e "${RED}❌ Ngrok is not running${NC}"
    return 1
}

# Function to get ngrok URL
get_ngrok_url() {
    # Wait a moment for ngrok to start
    sleep 3
    
    # Try to get URL from ngrok API
    URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    for tunnel in tunnels:
        if tunnel.get('proto') == 'https':
            print(tunnel['public_url'])
            break
except:
    pass
" 2>/dev/null)
    
    if [ -n "$URL" ]; then
        echo "$URL" > "$URL_FILE"
        echo -e "${GREEN}🌐 Public URL: $URL${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Could not retrieve ngrok URL yet${NC}"
        return 1
    fi
}

# Function to start ngrok
start_ngrok() {
    echo -e "${BLUE}🚀 Starting ngrok tunnel on port 3000...${NC}"
    
    cd "$PROJECT_DIR"
    
    # Start ngrok in background
    nohup ngrok http 3000 --log=stdout > "$LOG_FILE" 2>&1 &
    NGROK_PID=$!
    
    # Save PID to file
    echo $NGROK_PID > "$PID_FILE"
    
    # Wait and check if it started successfully
    sleep 5
    
    if kill -0 $NGROK_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Ngrok started successfully (PID: $NGROK_PID)${NC}"
        
        # Try to get the URL
        if get_ngrok_url; then
            echo -e "${GREEN}📋 URL saved to: $URL_FILE${NC}"
        else
            echo -e "${YELLOW}⚠️  URL will be available shortly. Check with: ./start_ngrok.sh url${NC}"
        fi
        return 0
    else
        echo -e "${RED}❌ Failed to start ngrok${NC}"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop ngrok
stop_ngrok() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}🛑 Stopping ngrok (PID: $PID)...${NC}"
        kill $PID 2>/dev/null || true
        rm -f "$PID_FILE"
        rm -f "$URL_FILE"
        echo -e "${GREEN}✅ Ngrok stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  No PID file found${NC}"
    fi
}

# Function to restart ngrok
restart_ngrok() {
    echo -e "${BLUE}🔄 Restarting ngrok...${NC}"
    stop_ngrok
    sleep 2
    start_ngrok
}

# Function to show status
status() {
    echo -e "${BLUE}🌐 Ngrok Tunnel Status:${NC}"
    echo "=================================="
    
    if check_ngrok; then
        PID=$(cat "$PID_FILE")
        echo -e "Status: ${GREEN}RUNNING${NC}"
        echo -e "PID: ${GREEN}$PID${NC}"
        echo -e "Local Port: ${GREEN}3000${NC}"
        echo -e "Web Interface: ${GREEN}http://localhost:4040${NC}"
        
        if [ -f "$URL_FILE" ]; then
            URL=$(cat "$URL_FILE")
            echo -e "Public URL: ${GREEN}$URL${NC}"
        else
            if get_ngrok_url; then
                URL=$(cat "$URL_FILE")
                echo -e "Public URL: ${GREEN}$URL${NC}"
            else
                echo -e "Public URL: ${YELLOW}Retrieving...${NC}"
            fi
        fi
        
        # Show recent logs
        if [ -f "$LOG_FILE" ]; then
            echo -e "\n${BLUE}📋 Recent logs:${NC}"
            tail -3 "$LOG_FILE" | grep -v "^$" || echo "No recent activity"
        fi
    else
        echo -e "Status: ${RED}STOPPED${NC}"
    fi
    
    echo "=================================="
}

# Function to show URL
show_url() {
    if check_ngrok; then
        if [ -f "$URL_FILE" ]; then
            URL=$(cat "$URL_FILE")
            echo -e "${GREEN}🌐 Public URL: $URL${NC}"
        else
            if get_ngrok_url; then
                URL=$(cat "$URL_FILE")
                echo -e "${GREEN}🌐 Public URL: $URL${NC}"
            else
                echo -e "${YELLOW}⚠️  URL not available yet. Ngrok might still be starting.${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ Ngrok is not running${NC}"
    fi
}

# Function to show logs
logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}📋 Showing ngrok logs (Ctrl+C to exit):${NC}"
        tail -f "$LOG_FILE"
    else
        echo -e "${YELLOW}⚠️  No log file found${NC}"
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        if check_ngrok; then
            echo -e "${YELLOW}⚠️  Ngrok is already running${NC}"
            status
        else
            start_ngrok
        fi
        ;;
    stop)
        stop_ngrok
        ;;
    restart)
        restart_ngrok
        ;;
    status)
        status
        ;;
    url)
        show_url
        ;;
    logs)
        logs
        ;;
    *)
        echo -e "${BLUE}Usage: $0 {start|stop|restart|status|url|logs}${NC}"
        echo ""
        echo -e "${GREEN}Commands:${NC}"
        echo -e "  start   - Start ngrok tunnel (default)"
        echo -e "  stop    - Stop ngrok tunnel"
        echo -e "  restart - Restart ngrok tunnel"
        echo -e "  status  - Show tunnel status"
        echo -e "  url     - Show public URL"
        echo -e "  logs    - Show live logs"
        exit 1
        ;;
esac