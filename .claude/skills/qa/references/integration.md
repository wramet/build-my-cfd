# Q&A Integration Details

Technical details on integrating the Q&A skill with other components.

## Integration Components

The Q&A system integrates with several components:

### walkthrough_orchestrator.py

Reads existing walkthroughs for context extraction:
- Section-based context matching
- Keyword search for relevant paragraphs
- Snippet inclusion with answers

### DeepSeekMCPClient

Model routing for DeepSeek R1/Chat:
- Direct API calls bypassing proxy
- Response caching for efficiency
- Context overflow handling

### MCP Server

**Location:** `.claude/mcp/deepseek_mcp_server.py`

**Configuration:** `.mcp.json`

```json
{
  "mcpServers": {
    "deepseek": {
      "command": "python3",
      "args": [".claude/mcp/deepseek_mcp_server.py"],
      "env": {
        "DEEPSEEK_API_KEY": "...",
        "PROMPT_CACHE_ENABLED": "true",
        "CACHE_SIZE_MB": "100",
        "CACHE_DIR": "/tmp/prompt_cache"
      }
    }
  }
}
```

## Context Extraction

The Q&A system extracts relevant context from walkthroughs:

1. **Section-based**: Matches question to theory/code/implementation sections
2. **Keyword search**: Finds relevant paragraphs in content
3. **Snippet inclusion**: Includes related content with each answer

## Model Routing Logic

```python
if question_type in ['clarification', 'deeper-dive'] and section == 'theory':
    model = 'deepseek-reasoner'  # DeepSeek R1 for math/theory
elif question_type in ['implementation', 'debugging'] and section == 'code':
    model = 'deepseek-chat'  # DeepSeek Chat for code
else:
    model = 'deepseek-chat'  # Default
```

## Interactive Mode

**Script:** `.claude/skills/qa/interactive_mode.py`

**Controls:**
- `N` - Next section
- `P` - Previous section
- `Q` - Ask a question
- `J` - Jump to section
- `S` - Show summary
- `H` - Help
- `E` or Ctrl-D - Exit

### Interactive Question Flow

When pressing `[Q]` to ask a question:

1. **Display suggested questions** for current section (numbered 1-N)
2. **Show "Ask my own question"** option (last choice)
3. **Auto-detect question type** for suggested questions
4. **Generate answer** using appropriate DeepSeek model
5. **Show summary** in terminal (full answer saved to file)
6. **Ask if ready for next section** after saving Q&A

## Output Location

Q&A entries are appended to:
```
daily_learning/walkthroughs/day_XX_walkthrough.md
```

In the `## Active Learning Q&A` section.

## Troubleshooting

### "Walkthrough file not found"
- Generate walkthrough first using walkthrough skill
- Check file exists in `daily_learning/walkthroughs/`

### "No response from DeepSeek"
- Check API credentials are configured
- Verify MCP server is running
- Check network connection to DeepSeek API

### "Empty Q&A section"
- First question creates the section automatically
- Subsequent questions append properly

### "Wrong tags assigned"
- Tags are keyword-based; edit manually if needed
- Common topics: FVM, discretization, boundary, turbulence

## Example Session

```bash
# 1. Generate walkthrough first
/walkthrough 1

# 2. Read and ask questions interactively
/interactive --day 1

# Navigation:
>>> N                    # Next section
>>> N                    # Next section
>>> Q                    # Ask a question

📝 Suggested questions for this section:
  1. Why doesn't the momentum equation provide an equation for pressure?
  2. What does it mean that momentum is 'elliptic in space for pressure'?
  3. How does the pressure-velocity coupling cause numerical difficulties?
  4. What are the differences between SIMPLE, PISO, and PIMPLE algorithms?
  5. ✏️  Ask my own question

Select question [1-5, default=1]: 2

📌 Selected: What does it mean that momentum is 'elliptic in space for pressure'?

🤔 Generating answer...

======================================================================
ANSWER SUMMARY
======================================================================
In CFD, elliptic means instantaneous propagation of information and
global coupling. The pressure Poisson equation requires all cells to
be solved simultaneously...
📁 Full detailed answer saved to: day_01_walkthrough.md

💾 Save this Q&A? [Y/n]: Y
✅ Q&A saved to walkthrough!

-----------------------------------------------------------------------
➡️  Ready for next section? ('2.2 The Non-Linearity Challenge') [Y/n]:
```

## Success Criteria

- ✅ Questions captured with context
- ✅ Routed to appropriate specialist model
- ✅ Auto-tagged by topic
- ✅ Appended to walkthrough document
- ✅ Timestamped and organized
- ✅ Interactive mode for real-time learning
- ✅ Command mode for on-demand questions
