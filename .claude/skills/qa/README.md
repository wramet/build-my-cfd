# Active Learning Q&A System

Enable active learning by allowing users to ask questions during walkthrough reading and having those Q&A recorded for future reference.

## Overview

The Q&A system provides two modes of interaction:

1. **Interactive Mode**: Read walkthroughs section-by-section with real-time Q&A
2. **Command Mode**: Ask questions on-demand and have them appended to the walkthrough

## Features

- **Smart Model Routing**: Questions are routed to specialist AI models based on type:
  - DeepSeek R1 (Reasoner): Mathematical derivations, theoretical deep-dives
  - DeepSeek Chat: Code analysis, implementation help, debugging
  - GLM-4.7: Practical guidance (future)

- **Context Awareness**: Answers reference specific content from the walkthrough

- **Auto-Tagging**: Questions are automatically tagged for easy organization:
  - Topics: FVM, discretization, boundary, turbulence, mesh, RTT, etc.

- **Multi-View Organization** (planned):
  - Chronological view (by learning session)
  - Section-based view (theory/code/implementation)
  - Topic-based view (using tags)

## Usage

### Interactive Mode

Read a walkthrough section-by-section and ask questions as you go:

```bash
/interactive --day 1
```

**Controls:**
- `N` - Next section
- `P` - Previous section
- `Q` - Ask a question about current section
- `J` - Jump to specific section
- `S` - Show session summary
- `H` - Help
- `E` or Ctrl-D - Exit

### Command Mode

Ask a specific question and have it recorded:

```bash
/qa --day 1 --section theory "Why does RTT use control volume approach?"

# With question type specified
/qa --day 2 --type deeper-dive "Derive the upwind scheme limiters"
```

**Question Types:**
- `clarification`: Explain unclear concepts
- `deeper-dive`: Explore beyond content
- `implementation`: Practical coding questions
- `debugging`: Troubleshooting help
- `connection`: Link to other topics

## File Structure

```
.claude/skills/qa/
├── qa_manager.py              # Main Q&A capture and management
├── interactive_mode.py        # Interactive walkthrough with real-time Q&A
├── prompts/
│   └── answer_generation.md   # AI prompts for answering questions
├── templates/
│   └── qa_entry.md            # Template for Q&A entry format
└── README.md                  # This file
```

## Q&A Entry Format

Each Q&A entry is formatted as:

```markdown
### 💬 Clarification Question
**Section:** Theory | **Asked:** 2026-01-28 14:30

**Question:**
Why does the Reynolds Transport Theorem use the control volume approach?

**Answer:**
The RTT connects the system (Lagrangian) and control volume (Eulerian) viewpoints...
*(Answered by DeepSeek R1)*

**Tags:** `RTT` `control-volume` `Eulerian`

**Related Content:**
> Snippet from the walkthrough section...

---
```

## Model Routing

| Question Type | Section | Model | Why |
|---------------|---------|-------|-----|
| clarification | theory | DeepSeek R1 | Theoretical explanations |
| deeper-dive | theory | DeepSeek R1 | Math derivations |
| implementation | code | DeepSeek Chat | Code examples |
| debugging | code | DeepSeek Chat | Troubleshooting |
| general | any | DeepSeek Chat | Default |

## Auto-Tagged Topics

- `RTT` - Reynolds Transport Theorem
- `control-volume` - Control volume analysis
- `FVM` - Finite Volume Method
- `discretization` - Discretization schemes
- `boundary` - Boundary conditions
- `turbulence` - Turbulence modeling
- `mesh` - Mesh/grid topics
- `gradient` - Gradient operators
- `time-derivative` - Time derivatives (ddt)
- `conservation` - Conservation laws
- `gauss` - Gauss/divergence theorem
- `openfoam` - OpenFOAM-specific
- `matrix` - Matrix solvers, fvMatrix

## Integration with Walkthroughs

Q&A entries are appended to the walkthrough document in the "Active Learning Q&A" section. This section is automatically added:

1. When a walkthrough is generated (via the updated template)
2. When the first question is asked (inserted before Verification Summary)

## Example Workflow

### Learning Session

```bash
# Start interactive walkthrough for Day 1
/interactive --day 1

# Navigate through sections...
>>> N                    # Next section
>>> N                    # Next section
>>> Q                    # Ask a question

Your question: Why is Gauss theorem used in FVM?

Select type [1-5, default=1]: 2

Generating answer...
[Answer displayed...]

Save this Q&A? [Y/n]: Y
✅ Q&A saved!

>>> N                    # Continue reading
>>> E                    # Exit when done
```

### Quick Question

```bash
# Ask a quick question while reviewing
/qa --day 1 --section theory "What's the difference between d/dt and ∂/∂t?"

# Output:
✅ Q&A saved to day_01_walkthrough.md
   Type: clarification
   Model: deepseek-reasoner
   Tags: RTT, time-derivative

---
[Answer displayed]
---
```

## Testing

To test the Q&A system:

```bash
# Test basic Q&A capture
python3 .claude/skills/qa/qa_manager.py --day 1 --question "Test question"

# Test interactive mode
python3 .claude/skills/qa/interactive_mode.py --day 1

# Verify Q&A appears in walkthrough
grep -A 20 "Active Learning Q&A" daily_learning/walkthroughs/day_01_walkthrough.md
```

## Troubleshooting

### MCP Client Not Available

If you see "MCP client not available" warnings:
1. Check that DeepSeek API credentials are configured
2. The system will fall back to placeholder answers
3. Full functionality requires MCP integration

### Walkthrough File Not Found

If the walkthrough doesn't exist:
1. Generate it first using `/walkthrough --day N`
2. The Q&A system will create a basic skeleton if needed

### Empty Answers

If answers appear empty or as placeholders:
1. Check MCP server is running
2. Verify DeepSeek API key is set
3. Check logs for specific error messages

## Future Enhancements

- [ ] Multi-view organization (chronological, section, topic)
- [ ] Follow-up question support ("Why?" chains)
- [ ] Q&A export as separate knowledge base
- [ ] Cross-day Q&A linking
- [ ] Q&A analytics (learning progress, topic gaps)
- [ ] Search/filter within Q&A
