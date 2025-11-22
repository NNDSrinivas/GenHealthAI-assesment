#!/bin/bash

# Kill any existing Flask processes
pkill -f "flask\|run_server\|python.*app" 2>/dev/null || true

# Navigate to project directory
cd "/Users/mounikakapa/Desktop/GenHealth.AI assesment"

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export FLASK_APP=app
export FLASK_ENV=production
export PORT=8001

# Start Flask server with nohup to prevent interruption
echo "Starting Flask server on port 8001..."
nohup python -c "
from app import create_app
import logging
logging.basicConfig(level=logging.INFO)

app = create_app()
print('Starting Flask server on 0.0.0.0:8001...')
print('Press Ctrl+C to stop')
app.run(host='0.0.0.0', port=8001, debug=False, use_reloader=False, threaded=True)
" > server.log 2>&1 &

SERVER_PID=$!
echo "Flask server started with PID: $SERVER_PID"

# Wait for server to start
sleep 3

# Test server
echo "Testing server..."
curl -s http://localhost:8001/health && echo " - Server is responding!" || echo " - Server not responding"

echo "Server log location: server.log"
echo "To stop server: kill $SERVER_PID"