---
name: qa
description: Capture and answer questions about CFD learning content with context-aware model routing
---

# Active Learning Q&A

Capture questions during walkthrough reading and record AI-generated answers directly in the walkthrough document.

## Core Process

When a user asks a question about walkthrough content:

1. **Extract Context** - Find relevant section from walkthrough
2. **Select Model** - Route to appropriate specialist model
3. **Generate Answer** - Create detailed response
4. **Format Entry** - Create Q&A entry with tags
5. **Insert into Walkthrough** - Append to walkthrough document

## Two Usage Modes

### Mode 1: User in Terminal (Direct Python Script)

When a user wants interactive Q&A in their terminal:

```
Tell the user to run: python3 .claude/skills/qa/interactive_mode.py --day XX
```

The interactive script provides:
- Section-by-section navigation
- Suggested questions for each section
- Direct answer generation via DeepSeek
- Auto-saving to walkthrough file

### Mode 2: Claude Assistance (You Handle the Workflow)

When user asks you to do Q&A (like "let's do Q&A for day 02 section 3.1"):

1. **Read the walkthrough** to understand context
2. **Present the section content** to the user
3. **Accept user's question** (natural language)
4. **Select appropriate model** based on question type and section
5. **Generate answer** using DeepSeek MCP
6. **Format and append** Q&A entry to walkthrough

Do NOT try to run `interactive_mode.py` - it requires terminal stdin and won't work when you invoke it.

## Model Assignment

| Question Type | Section | Model | Purpose |
|---------------|---------|-------|---------|
| clarification | theory | DeepSeek R1 | Theoretical explanations |
| deeper-dive | theory | DeepSeek R1 | Math derivations |
| implementation | code | DeepSeek Chat | Code examples |
| debugging | code | DeepSeek Chat | Troubleshooting |
| general | any | DeepSeek Chat | Default |

## Question Types

| Type | Purpose | Example |
|------|---------|---------|
| `clarification` | Explain unclear concepts | "What does $\nabla \cdot \mathbf{U}$ mean?" |
| `deeper-dive` | Explore beyond content | "Why is Gauss theorem used here?" |
| `implementation` | Practical coding questions | "How do I implement this in OpenFOAM?" |
| `debugging` | Troubleshooting help | "Why is my simulation diverging?" |
| `connection` | Link to other topics | "How does this relate to boundary conditions?" |

## Auto-Tagged Topics

Questions are automatically tagged for organization:

- `RTT` - Reynolds Transport Theorem
- `control-volume` - Control volume analysis
- `FVM` - Finite Volume Method
- `discretization` - Discretization schemes
- `boundary` - Boundary conditions
- `turbulence` - Turbulence modeling
- `mesh` - Mesh/grid topics
- `gradient` - Gradient operators
- `openfoam` - OpenFOAM-specific
- `matrix` - Matrix solvers, fvMatrix

## Output Location

Q&A entries are appended to:
```
daily_learning/walkthroughs/day_XX_walkthrough.md
```

In the `## Active Learning Q&A` section.

## Q&A Entry Format

```markdown
### 💬 Clarification Question
**Section:** [Section name] | **Asked:** [Timestamp]

**Question:**
[User's question]

**Answer:**
[Full detailed answer with math/code]

**Tags:** `tag1` `tag2` `tag3`

**Related Content:**
> [Snippet from walkthrough]

---
```

## Integration

This skill integrates with:

- `DeepSeekMCPClient` - Model routing for DeepSeek R1/Chat via MCP
- MCP integration in `.claude/mcp/` - Direct API calls
- `qa_manager.py` - Backend logic for Q&A capture (Python use only)

## See Also

- [Q&A examples](references/examples.md)
- [Integration details](references/integration.md)
- [Walkthrough skill](../walkthrough/SKILL.md)
