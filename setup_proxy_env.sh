#!/bin/bash
# Configure Claude Code to use local LiteLLM proxy

# Point Claude to the local proxy
export ANTHROPIC_BASE_URL="http://localhost:4000"

# Set a dummy API key (LiteLLM handles the real keys)
export ANTHROPIC_API_KEY="sk-dummy-key"

echo "✅ Environment configured for LiteLLM Proxy."
echo "   Base URL: $ANTHROPIC_BASE_URL"
echo "   Run 'source setup_proxy_env.sh' to apply to your current shell."
