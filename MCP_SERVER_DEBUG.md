# DeepSeek MCP Server - Setup & Debug Guide

**Created:** 2026-01-27
**Commit:** `721a174`
**Status:** ⚠️ Pending testing after Claude Code restart

---

## Quick Status Check

When you start a new session, first verify:

```bash
# Check MCP server is configured
cat .mcp.json

# Check DeepSeek API key is set
echo $DEEPSEEK_API_KEY

# Check settings.json has server enabled
grep "enabledMcpjsonServers" ~/.claude/settings.json
```

**Expected output:**
- `.mcp.json` exists with deepseek server config
- `DEEPSEEK_API_KEY` is set
- `enabledMcpjsonServers` contains `"deepseek"`

---

## What Was Set Up

### Files Created

| File | Purpose |
|------|---------|
| `.claude/mcp/deepseek_mcp_server.py` | MCP server implementation |
| `.claude/agents/deepseek-chat-mcp.md` | V3 agent (coding specialist) |
| `.claude/agents/deepseek-reasoner-mcp.md` | R1 agent (reasoning specialist) |
| `.mcp.json` | Project MCP server configuration |
| `~/.claude/settings.json` | User settings (enabled deepseek) |

### Dependencies Installed

```bash
pip3 list | grep -i mcp
# Should show: mcp (version)
```

---

## Testing Steps (In Order)

### Step 1: Verify MCP Server Loads

**In new Claude Code session, ask:**

```
List all available MCP tools
```

**Expected:** Should see `deepseek-chat` and `deepseek-reasoner` tools

**If fails:** See "Error: MCP tools not available" below

---

### Step 2: Test DeepSeek Chat (V3)

**Ask:**

```
Use deepseek-chat-mcp agent to write a simple hello world in C++
```

**Expected:**
- Agent is invoked
- Returns C++ hello world code
- No errors about missing tools

**If fails:** See "Error: Agent not found" below

---

### Step 3: Test DeepSeek Reasoner (R1)

**Ask:**

```
Use deepseek-reasoner-mcp agent to explain what TVD means in CFD
```

**Expected:**
- Agent is invoked
- Explains Total Variation Diminishing
- Shows mathematical reasoning

**If fails:** See "Error: DeepSeek API call failed" below

---

### Step 4: Test Tool Access

**Ask:**

```
Use deepseek-chat-mcp to read .mcp.json and tell me what it contains
```

**Expected:**
- Agent successfully reads the file
- Describes the MCP configuration

**If fails:** See "Error: Tools not working" below

---

## Common Errors & Solutions

### Error: MCP tools not available

**Symptoms:**
```
No tools found
MCP server not loaded
```

**Solutions:**

1. **Check MCP server config:**
   ```bash
   cat .mcp.json
   # Should have valid JSON with deepseek server
   ```

2. **Check server is enabled:**
   ```bash
   grep "enabledMcpjsonServers" ~/.claude/settings.json
   # Should show: "enabledMcpjsonServers": ["deepseek"]
   ```

3. **Restart Claude Code completely:**
   ```bash
   exit
   claude
   ```

4. **Check Python MCP module:**
   ```bash
   python3 -c "import mcp.server; print('OK')"
   # Should print: OK
   ```

---

### Error: Agent not found

**Symptoms:**
```
Agent deepseek-chat-mcp not found
Unknown agent: deepseek-reasoner-mcp
```

**Solutions:**

1. **Check agent files exist:**
   ```bash
   ls -la .claude/agents/deepseek-*-mcp.md
   # Should show both agent files
   ```

2. **Verify agent syntax:**
   ```bash
   head -5 .claude/agents/deepseek-chat-mcp.md
   # Should have YAML frontmatter with name and description
   ```

3. **Try /agents command:**
   ```
   /agents
   # Should list all available agents including the new ones
   ```

---

### Error: DeepSeek API call failed

**Symptoms:**
```
HTTP Error: 401
DEEPSEEK_API_KEY not set
Error calling DeepSeek API
```

**Solutions:**

1. **Check API key in environment:**
   ```bash
   echo $DEEPSEEK_API_KEY
   # Should show: sk-9ea39bd4d5e042c49f7b0337668162b6
   ```

2. **Check API key in .mcp.json:**
   ```bash
   grep "DEEPSEEK_API_KEY" .mcp.json
   # Should have the key
   ```

3. **Test API directly:**
   ```bash
   curl -X POST https://api.deepseek.com/v1/chat/completions \
     -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"test"}]}'
   # Should return a response
   ```

---

### Error: Tools not working

**Symptoms:**
```
Agent cannot read files
Permission denied using tools
```

**Solutions:**

1. **Check agent has tools configured:**
   ```bash
   grep "^tools:" .claude/agents/deepseek-chat-mcp.md
   # Should list tools: Read, Grep, Glob, Bash, Edit, Write
   ```

2. **Test agent can access tools:**
   ```
   Use deepseek-chat-mcp to list files in current directory
   ```

3. **Check permissions in settings:**
   ```bash
   cat ~/.claude/settings.json | grep -A 10 "permissions"
   ```

---

### Error: MCP server won't start

**Symptoms:**
```
MCP server failed to start
Python error in deepseek_mcp_server.py
```

**Solutions:**

1. **Test MCP server directly:**
   ```bash
   python3 .claude/mcp/deepseek_mcp_server.py
   # Should start server (will wait for stdin)
   # Press Ctrl+C to exit
   ```

2. **Check for Python errors:**
   ```bash
   python3 -m py_compile .claude/mcp/deepseek_mcp_server.py
   # Should have no syntax errors
   ```

3. **Check all dependencies:**
   ```bash
   pip3 list | grep -E "mcp|httpx"
   # Should show mcp and httpx installed
   ```

---

## Rollback / Revert

If MCP setup is broken and you need to revert:

### Option 1: Revert MCP Commit

```bash
# Go back to commit before MCP setup
git reset --hard 721a174~1

# Remove MCP config
rm .mcp.json

# Update settings.json to remove deepseek
# Edit ~/.claude/settings.json and remove "deepseek" from enabledMcpjsonServers
```

### Option 2: Disable MCP Server

**Edit `~/.claude/settings.json`:**

```json
{
  "disabledMcpjsonServers": ["deepseek"]
}
```

### Option 3: Keep Using Python Wrapper

The old Python wrapper still works:

```bash
# DeepSeek Chat
echo "Your question" | python3 .claude/scripts/deepseek_content.py deepseek-chat /dev/stdin

# DeepSeek Reasoner
echo "Your question" | python3 .claude/scripts/deepseek_content.py deepseek-reasoner /dev/stdin
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code (GLM-4.7)                    │
│                 Main session with tools                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ├─────────────┬─────────────┐
                           │             │             │
                           ↓             ↓             ↓
              ┌────────────────┐  ┌──────────┐  ┌──────────┐
              │deepseek-chat   │  │deepseek- │  │  GLM-4.7  │
              │   (MCP tool)   │  │reasoner  │  │ subagent │
              └───────┬────────┘  │(MCP tool)│  └──────────┘
                      │           └─────┬────┘
                      │                 │
              ┌───────▼─────────────────▼────┐
              │     MCP Server               │
              │  (deepseek_mcp_server.py)   │
              └──────────────┬───────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │  DeepSeek API           │
              │  api.deepseek.com/v1    │
              └────────────────────────┘
```

---

## Success Checklist

After restart, verify:

- [ ] MCP server loads without errors
- [ ] `deepseek-chat` tool is available
- [ ] `deepseek-reasoner` tool is available
- [ ] `deepseek-chat-mcp` agent exists
- [ ] `deepseek-reasoner-mcp` agent exists
- [ ] DeepSeek Chat can generate responses
- [ ] DeepSeek Reasoner can do complex reasoning
- [ ] Both agents can use tools (Read, Grep, etc.)
- [ ] Multi-turn conversations work

---

## Next Steps After Success

Once MCP is working, you can:

1. **Brainstorm with DeepSeek R1:**
   ```
   Use deepseek-reasoner-mcp to explore TVD limiter implementations
   and suggest the best approach for our evaporator solver
   ```

2. **Code with DeepSeek V3:**
   ```
   Use deepseek-chat-mcp to implement the chosen limiter approach
   ```

3. **Collaborate between models:**
   ```
   Have deepseek-reasoner-mcp design the architecture,
   then deepseek-chat-mcp implement it
   ```

---

## Files Reference

| File | Path | Purpose |
|------|------|---------|
| MCP Server | `.claude/mcp/deepseek_mcp_server.py` | Main server |
| Chat Agent | `.claude/agents/deepseek-chat-mcp.md` | V3 specialist |
| Reasoner Agent | `.claude/agents/deepseek-reasoner-mcp.md` | R1 specialist |
| MCP Config | `.mcp.json` | Project config |
| User Settings | `~/.claude/settings.json` | User config |
| Old Wrapper | `.claude/scripts/deepseek_content.py` | Fallback |

---

**Last Updated:** 2026-01-27
**Commit:** `721a174`
