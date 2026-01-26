# Commands & Agents Quick Reference

## 🎯 One-Command Content Creation

```bash
/create-day 03
```
Automatically creates complete daily content (7000+ lines) with:
- ✅ Auto-detects topic from roadmap
- ✅ Extracts ground truth from OpenFOAM
- ✅ Routes to correct agents (architect → engineer → verifier)
- ✅ Verifies all formulas against source code
- ✅ Outputs to `daily_learning/Phase_XX_XXX/03.md`

---

## 📋 All Available Commands

### Skills (`.claude/skills/`)

| Command | Description | Agent Used |
|---------|-------------|------------|
| `/create-day` | Create daily content automatically | architect → engineer → verifier |
| `/source-first` | Enforce Source-First methodology | verifier |
| `/git-guru` | Git best practices and commits | architect |
| `/ground-truth-verification` | Verify against source code | verifier |
| `/engineering-thai` | Translate to Engineering Thai | translator |
| `/cfd-content-structure` | Structure CFD learning content | architect |

### Commands (`.claude/commands/`)

| Command | Description | Workflow |
|---------|-------------|----------|
| `/qc-modular` | Section-by-section QC | qc-agent |
| `/walkthrough` | Interactive content review | architect → verifier |
| `/delegate` | Switch to specific agent | (specified agent) |

---

## 🤖 All Available Agents

| Agent | Model | Backend | Best For |
|-------|-------|---------|----------|
| **architect** | glm-4.7 | Z.ai | Planning, structuring, roadmap alignment |
| **engineer** | deepseek-chat | DeepSeek | C++ code, implementation, debugging |
| **verifier** | deepseek-reasoner | DeepSeek | Source verification, reasoning, QC |
| **researcher** | glm-4.7 | Z.ai | Documentation search, web research |
| **translator** | glm-4.7 | Z.ai | English → Engineering Thai |
| **qc-agent** | glm-4.7 | Z.ai | Syntax checking, formatting validation |

---

## 🔄 Proxy Routing

### GLM-4.7 Models → Z.ai Backend
- architect
- researcher
- translator
- qc-agent

**Backend:** `https://api.z.ai/api/paas/v4`

### DeepSeek Models → DeepSeek Backend
- engineer (deepseek-chat)
- verifier (deepseek-reasoner)

**Backend:** `https://api.deepseek.com`

---

## 💡 Usage Examples

### Content Creation
```bash
# Full automation
/create-day 03

# Manual workflow with agents
/delegate architect "Plan Day 03 structure"
/delegate engineer "Write the theory section"
/delegate verifier "Check formulas against source"
/delegate translator "Add Thai headers"
/delegate qc-agent "Check for syntax errors"
```

### Quality Control
```bash
# Full QC
/qc-modular --file=daily_learning/Phase_01_Foundation_Theory/03.md

# Specific check
/delegate verifier "Verify the divergence schemes in Day 03"
```

### Research
```bash
# Find documentation
/delegate researcher "Search for OpenFOAM TVD schemes documentation"

# Verify claim
/delegate verifier "Check if upwind scheme inherits from surfaceInterpolationScheme"
```

### Translation
```bash
# Add Thai headers
/delegate translator "Translate headers in Day 03 to Engineering Thai"
```

### Git
```bash
# Smart commit
/git-guru commit "Add Day 03 content"
```

---

## 🎓 Typical Workflow

```bash
# 1. Create content (one command)
/create-day 03

# 2. Review walkthrough (optional)
/walkthrough daily_learning/Phase_01_Foundation_Theory/03.md

# 3. QC check (optional)
/qc-modular --file=daily_learning/Phase_01_Foundation_Theory/03.md

# 4. Commit (when ready)
/git-guru commit "Complete Day 03: Spatial Discretization"
```

---

## 🔍 Debug Routing

```bash
# Monitor proxy logs
tail -f /tmp/proxy_test.log | grep SUBAGENT-ROUTING

# Check configuration
curl http://localhost:8888/debug/config | jq

# Test specific model routing
curl -X POST http://localhost:8888/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-4.7","messages":[{"role":"user","content":"test"}]}'
```

---

## ✅ Status

**All commands:** ✅ Available and working
**All agents:** ✅ Compatible with proxy
**Proxy routing:** ✅ DeepSeek + GLM-4.7 configured

**Ready to use!** 🚀
