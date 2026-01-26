#!/bin/bash

# stop_proxy.sh
# Stops the background LiteLLM proxy

echo "🛑 Stopping LiteLLM Proxy..."

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_ROOT/proxy.log"

# Kill litellm proxy processes
if pkill -f "litellm --config"; then
    echo "✅ Proxy stopped successfully."
    sleep 1
else
    echo "⚠️  No proxy process found (it might already be stopped)."
fi

# Also clean up port 4000 if any process is using it
if lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Cleaning up port 4000..."
    lsof -ti:4000 2>/dev/null | xargs kill -9 2>/dev/null
    sleep 1
fi

# Verify port is free
if lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "❌ ERROR: Port 4000 still in use"
    lsof -i :4000
else
    echo "✅ Port 4000 is free"
fi

echo "📄 Log file saved at: $LOG_FILE"
