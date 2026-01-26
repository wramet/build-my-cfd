# MCP Configuration for CFD Content Creation

## MCP Servers

### 1. Filesystem MCP (Recommended)

**Purpose:** Structured file/folder operations

**Install:**
```bash
npx -y @modelcontextprotocol/server-filesystem
```

**Configuration (~/.claude.json):**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/woramet/Documents/th_new"
      ],
      "disabled": false
    }
  }
}
```

**What it gives you:**
- `search_files()` - Search by name/pattern
- `read_file()` - Read multiple files at once
- `directory_tree()` - Get folder structure
- `write_file()` - Write files

**VS Current:**
- Read tool (single file)
- Grep tool (search content)
- Glob tool (find files)
- Bash ls/find

**Verdict:** Nice-to-have, but not essential

---

### 2. GitHub MCP (Optional)

**Purpose:** Clone/search OpenFOAM repositories

**Configuration:**
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "YOUR_TOKEN_HERE"
      },
      "disabled": true  // Disabled by default
    }
  }
}
```

**Use case:** If you want to browse OpenFOAM source on GitHub

**Verdict:** Optional - You already have local source

---

## Context Window Warning

**⚠️ Important:** Each MCP server uses ~2k-5k tokens

Best practice (from everything-claude-code):
- **20-30 MCPs configured max**
- **Keep under 10 enabled per project**
- **Under 80 tools active**

Your current state:
- Tools: ~20 ✅
- MCPs: 0 ✅

**If you add MCP:** Keep it under 3-4 servers enabled

---

## Recommendation

### For your CFD content workflow:

**Skip MCP for now.** Your current setup is sufficient:

```bash
# You can already do this:
Read /path/to/openfoam/src/file.H
Grep "class upwind" openfoam_temp/src/
find openfoam_temp/src -name "*.H"

# MCP would give you:
search_files({pattern: "*.H", path: "openfoam_temp/src/"})
```

**Result:** Same capability, different interface.

---

## When to Add MCP

Add MCP when you need something specific:

1. **Filesystem MCP** - If you want structured file queries across large codebases
2. **GitHub MCP** - If you want to browse OpenFOAM repos without cloning
3. **Database MCP** - If you add a database to track content
4. **Custom MCP** - If you build a custom tool (unlikely needed)

---

## Decision Matrix

| Need | Solution |
|------|----------|
| Read files | ✅ Use Read tool (no MCP needed) |
| Search file names | ✅ Use Glob tool (no MCP needed) |
| Search content | ✅ Use Grep tool (no MCP needed) |
| Run scripts | ✅ Use Bash tool (no MCP needed) |
| Structured file queries | ⚠️ Filesystem MCP (optional) |
| GitHub integration | ⚠️ GitHub MCP (optional) |
| Database access | ❌ Not needed |

---

## My Verdict

**For NOW:** Skip MCP. Your setup is complete.

**LATER:** Add Filesystem MCP only if you find yourself doing complex file operations frequently.

---

## Alternative: Script-Based Approach (Your Current Way)

Your `orchestrator.py` + `extract_facts.py` approach is actually **better** than MCP for your use case because:

1. **Faster** - Direct Python scripts
2. **More control** - Custom extraction logic
3. **No token overhead** - Scripts run externally
4. **Battle-tested** - You've verified they work

**Keep doing what you're doing!** ✅
