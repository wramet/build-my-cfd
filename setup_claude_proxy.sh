#!/bin/bash

# setup_claude_proxy.sh
# Configure Claude Code to route through local LiteLLM proxy

echo "🔧 Configuring Claude Code to use Local Proxy"
echo ""

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Stop existing proxy
echo "1️⃣  Stopping existing proxy..."
./stop_proxy.sh > /dev/null 2>&1

# Start proxy
echo "2️⃣  Starting LiteLLM proxy on port 4000..."
./start_proxy.sh > /dev/null 2>&1
sleep 2

# Verify proxy is running
if ! lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "❌ ERROR: Proxy failed to start on port 4000"
    echo "   Check: tail -20 proxy.log"
    exit 1
fi

# Export environment variables for Claude Code
echo "3️⃣  Setting environment variables..."
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_API_KEY="sk-dummy-key"

# Test proxy with a simple request
echo "4️⃣  Testing proxy connection..."
RESPONSE=$(curl -s http://localhost:4000/health 2>&1)
if [ $? -eq 0 ]; then
    echo "✅ Proxy is responding"
else
    echo "⚠️  Proxy responding but health check failed"
fi

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Environment Variables (for current shell session):"
echo "   ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL"
echo "   ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
echo ""
echo "📄 Monitor proxy logs in another terminal:"
echo "   tail -f $PROJECT_ROOT/proxy.log"
echo ""
echo "⚠️  IMPORTANT: These variables are only set for THIS shell session."
echo "   To make permanent, add to your ~/.zshrc:"
echo ""
echo "   export ANTHROPIC_BASE_URL=\"http://localhost:4000\""
echo "   export ANTHROPIC_API_KEY=\"sk-dummy-key\""
echo ""
