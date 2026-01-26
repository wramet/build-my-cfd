#!/bin/bash
# Set Claude Code to use DeepSeek models for subagents
# This CLAUDE_CODE_SUBAGENT_MODEL environment variable controls
# which model the Task tool uses when delegating to subagents

echo "🔄 Setting Claude Code subagent model to DeepSeek..."
echo ""

# Option 1: Set DeepSeek Chat V3 for all subagents
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-chat"

echo "✅ Subagent model set to: $CLAUDE_CODE_SUBAGENT_MODEL"
echo ""
echo "⚠️  IMPORTANT: This affects ALL Task tool delegations"
echo "   - researcher → deepseek-chat"
echo "   - architect → deepseek-chat"
echo "   - verifier → deepseek-chat"
echo "   - deepseek-chat → deepseek-chat"
echo ""
echo "📋 Proxy routing:"
echo "   When Task tool delegates to subagent_type=verifier"
echo "   Claude Code will call: $ANTHROPIC_BASE_URL"
echo "   With model: deepseek-chat (from CLAUDE_CODE_SUBAGENT_MODEL)"
echo "   LiteLLM proxy will route: deepseek-chat → deepseek/deepseek-chat"
echo ""
echo "💡 To verify this works:"
echo "   1. Run a Task delegation:"
echo "      /delegate verifier \"test verification\""
echo "   2. Check proxy logs:"
echo "      tail -f proxy.log"
echo "   3. Look for 'Model: deepseek-chat' in the logs"
echo ""
echo "🔁 To reset to GLM:"
echo "   export CLAUDE_CODE_SUBAGENT_MODEL=\"glm-4.5-air\""
