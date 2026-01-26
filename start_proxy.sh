#!/bin/bash

# start_proxy.sh
# Starts the LiteLLM proxy via Uvicorn (Fix for Python 3.14 uvloop bug)

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$PROJECT_ROOT/.claude/configs/litellm_config.yaml"
LOG_FILE="$PROJECT_ROOT/proxy.log"

echo "🚀 Starting LiteLLM Proxy (Python 3.14 Safe Mode)..."
echo "📍 URL: http://localhost:4000"
echo "📋 Config: $CONFIG_FILE"
echo ""

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ ERROR: Config file not found: $CONFIG_FILE"
    exit 1
fi

# Check if port 4000 is in use
if lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 4000 is already in use. Attempting to kill old process..."
    lsof -ti:4000 2>/dev/null | xargs kill -9 2>/dev/null
    sleep 1
    if lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "❌ ERROR: Could not free port 4000"
        exit 1
    fi
    echo "✅ Old process killed"
fi

# Clear old log
> "$LOG_FILE"

# Run the proxy
cd "$PROJECT_ROOT"
echo "🔧 Starting Uvicorn directly with --loop asyncio..."
echo ""

# ---------------------------------------------------------------------
# THE FIX: Run Uvicorn directly, explicitly using 'asyncio' instead of 'uvloop'
# ---------------------------------------------------------------------
export LITELLM_CONFIG_PATH="$CONFIG_FILE"
nohup python3 run_litellm_proxy.py > "$LOG_FILE" 2>&1 &
PID=$!

# Wait a bit for proxy to start
sleep 2

# Check if proxy started successfully
if ! kill -0 $PID 2>/dev/null; then
    echo "❌ ERROR: Proxy failed to start. Check log: $LOG_FILE"
    cat "$LOG_FILE"
    exit 1
fi

echo "✅ Proxy started successfully!"
echo "   PID: $PID"
echo "   Port: 4000"
echo "   Loop: asyncio (Python 3.14 Safe)"
echo ""