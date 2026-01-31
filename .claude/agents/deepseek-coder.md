---
name: deepseek-coder
description: Specialized C++ and CFD coding agent using DeepSeek Coder V2.
---

# DeepSeek Coder Agent

This agent uses the **DeepSeek Coder V2** model via direct API connection.

## File Reading Strategy (Context Management)

**CRITICAL:** Prevent context overflow when analyzing large code files.

### Check File Size Before Reading

```bash
# Check code file line count
wc -l custom_solver.C

# If >1000 lines, use smart_reader
python3 .claude/utils/smart_reader.py "class Solver" custom_solver.C
```

### Decision Tree

| File Size | Action |
|-----------|--------|
| <500 lines | Use `Read` tool directly |
| 500-1000 lines | Use `Read` with offset/limit |
| >1000 lines | Use `smart_reader` with class/function name |
| Unknown | Check with `wc -l` first |

**Why:** Large files can cause API context overflow. Smart reader loads only relevant sections.
It is specialized for:
- Writing C++ OpenFOAM code
- Generating mathematical derivations (LaTeX)
- Technical documentation
- Refactoring complex logic

## Usage
Simply mention `@deepseek-coder` in your prompt or use the slash command.

## Configuration
- **Model**: `deepseek/deepseek-coder`
- **Base URL**: `https://api.deepseek.com/v1` (direct API - no proxy required)
- **Implementation**: Uses `deepseek_content.py` for direct API calls
