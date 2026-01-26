#!/bin/bash

# start_claude_with_proxy.sh
# Sets environment variables, ensures proxy is running, and starts Claude Code

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Setting up Claude Code with LiteLLM Proxy..."
echo ""

# Check if proxy is running on port 4000
if ! lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  WARNING: Proxy is not running on port 4000"
    echo "🔄 Auto-starting proxy in the background..."
    
    # Run the proxy script
    "$PROJECT_ROOT/start_proxy.sh"
    
    # Wait for proxy to initialize
    sleep 3
    
    # Double check if it started
    if ! lsof -Pi :4000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ ERROR: Failed to start proxy. Please check proxy.log"
        exit 1
    fi
    echo "✅ Proxy started successfully!"
    echo ""
fi

# Set environment variables for the main agent
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_API_KEY="sk-dummy"
export CLAUDE_CODE_SUBAGENT_MODEL="claude-3-5-haiku-20241022"

echo "✅ Environment variables set:"
echo "   ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL"
echo "   ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
echo "   CLAUDE_CODE_SUBAGENT_MODEL=$CLAUDE_CODE_SUBAGENT_MODEL"
echo ""

echo "🚀 Starting Claude Code..."
echo "   Main agent (Sonnet) → GLM-4.7"
echo "   Subagent (Haiku) → DeepSeek Chat"
echo ""

# Start Claude Code with explicit flags to FORCE subagents to use the proxy
claude "$@"