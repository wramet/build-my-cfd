---
name: claude-code-guide
author: sickn33 (Ported)
description: Master guide for using Claude Code effectively, including prompting strategies and "Thinking" keywords.
---

# Claude Code Guide

## Purpose
To provide a comprehensive reference for configuring and using Claude Code (the agentic coding tool) to its full potential. This skill synthesizes best practices, configuration templates, and advanced usage patterns.

## Advanced Features

### Thinking Keywords
Use these keywords in your prompts to trigger deeper reasoning from the agent:
- "Think step-by-step"
- "Analyze the root cause"
- "Plan before executing"
- "Verify your assumptions"

### Debugging
If the agent is stuck or behaving unexpectedly:
1. **Clear Context**: Start a new session or ask the agent to "forget previous instructions" if confused.
2. **Explicit Instructions**: Be extremely specific about paths, filenames, and desired outcomes.
3. **Logs**: Ask the agent to "check the logs" or "run the command with verbose output".

## Best Practices
1. **Small Contexts**: Don't dump the entire codebase into the context. Use `grep` or `find` to locate relevant files first.
2. **Iterative Development**: Ask for small changes, verify, then proceed.
3. **Feedback Loop**: If the agent makes a mistake, correct it immediately and ask it to "add a lesson" to its memory (if supported) or `CLAUDE.md`.

## Reference
Based on [Claude Code Guide by zebbern](https://github.com/zebbern/claude-code-guide).
