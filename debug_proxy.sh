#!/bin/bash

# debug_proxy.sh
# Monitors proxy logs in real-time and filters for model routing info

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_ROOT/proxy.log"

echo "🔍 Proxy Debug Monitor"
echo "======================"
echo ""

# Check if proxy is running
if ! lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "❌ ERROR: Proxy is NOT running on port 4000"
    echo ""
    echo "Start it first with:"
    echo "   ./start_proxy.sh"
    exit 1
fi

echo "✅ Proxy is running on port 4000"
echo ""
echo "📋 Environment Variables:"
echo "   ANTHROPIC_BASE_URL: ${ANTHROPIC_BASE_URL:-NOT_SET}"
echo "   ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+(set)}"
echo "   CLAUDE_CODE_SUBAGENT_MODEL: ${CLAUDE_CODE_SUBAGENT_MODEL:-NOT_SET}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 Live Proxy Log (filtered for model routing):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Tail the log and filter for important info
tail -f "$LOG_FILE" | grep --line-buffered -E "(model:|POST /v1|error|Error|ERROR|route|Route)" | while read line; do
    # Highlight model names
    line=$(echo "$line" | sed -E 's/(claude-3-5-(sonnet|haiku)-20241022|deepseek-(chat|coder|reasoner)|glm-4\.7)/\\033[1;33m\1\\033[0m/g')
    # Highlight errors
    line=$(echo "$line" | sed -E 's/(error|Error|ERROR)/\\033[1;31m\1\\033[0m/g')
    # Highlight POST requests
    line=$(echo "$line" | sed -E 's/(POST)/\\033[1;32m\1\\033[0m/g')
    echo "$line"
done
