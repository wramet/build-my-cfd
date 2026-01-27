# DeepSeek MCP Integration Plan

**Status:** ✅ MCP Server Working
**Created:** 2026-01-27
**Goal:** Integrate MCP-powered DeepSeek agents into existing workflows

---

## Current System Overview

```
Existing Workflows:
├── /create-day skill
│   ├── Stage 1-2: Ground truth extraction (GLM-4.7)
│   ├── Stage 3-5: Content generation (DeepSeek via Python wrapper)
│   └── Stage 6: Final formatting
│
├── /walkthrough skill
│   ├── Verification gates (Python scripts)
│   ├── Theory analysis (DeepSeek via Python wrapper)
│   └── Code analysis (DeepSeek via Python wrapper)
│
└── Source-First methodology
    ├── Extract facts from OpenFOAM source
    ├── Verify ground truth
    ├── Generate content based on verified facts
    └── Format and QC
```

---

## Integration Strategy: Hybrid Approach

**Keep what works, enhance where MCP adds value:**

| Component | Current | MCP-Enhanced | Why |
|-----------|---------|--------------|-----|
| Ground truth extraction | GLM-4.7 with tools | **Keep as-is** | Already works perfectly |
| Content generation | DeepSeek (Python wrapper) | **Add MCP option** | MCP enables interactive refinement |
| Walkthrough generation | DeepSeek (Python wrapper) | **Upgrade to MCP** | Can explore codebase independently |
| Brainstorming/research | Manual | **New MCP phase** | DeepSeek R1 can research independently |
| Code implementation | Manual/GLM-4.7 | **Add MCP** | DeepSeek V3 excels at coding |

---

## Integration Points

### 1. Enhanced `/walkthrough` Skill

**Current:**
```python
# walkthrough_orchestrator.py
def _generate_theory_walkthrough():
    # Calls DeepSeek via Python wrapper
    result = self._call_model("deepseek-reasoner", prompt)
```

**Enhanced:**
```python
def _generate_theory_walkthrough():
    # Option 1: Use MCP agent (can explore files)
    # Option 2: Use Python wrapper (fast, one-shot)

    if self.use_mcp:
        # DeepSeek R1 can now read source files itself!
        result = self._call_mcp_agent("deepseek-reasoner-mcp", task)
    else:
        # Fallback to Python wrapper
        result = self._call_model("deepseek-reasoner", prompt)
```

**Benefits:**
- DeepSeek R1 can verify facts against source code directly
- Can explore multiple files to find related implementations
- Interactive refinement possible

---

### 2. New Brainstorming Phase (Before Content Generation)

**Add to `/create-day` workflow:**

```
NEW: Stage 2.5 - Research & Design

Input: Ground truth facts + Skeleton
Process:
  1. GLM-4.7 identifies research needs
  2. DeepSeek R1 (MCP) explores codebase independently
  3. DeepSeek R1 proposes content structure/approach
  4. Discussion and refinement with GLM-4.7
  5. Approved design → Stage 3 (content generation)

Output: Content design plan with verified sources
```

**Example Interaction:**
```
GLM-4.7: We need to create content on TVD limiters.
         What research should we do?

DeepSeek R1 (MCP): [Searching OpenFOAM source...]
                   Found 5 limiter implementations: vanLeer,
                   SuperBee, MINMOD, vanAlbada, UMIST

                   [Reading vanLeer.H...]

                   Recommendation: Structure content as:
                   1. TVD condition derivation
                   2. Limiter function analysis
                   3. Code walkthrough of each limiter

                   Should I explore the flux scheme classes too?

GLM-4.7: Yes, check how limiters integrate with schemes.

DeepSeek R1: [Searching... analyzing...]
                   Found: limitedSurfaceInterpolationScheme base class

                   Updated structure: Add section 4 on scheme integration

GLM-4.7: Approved. Proceed to content generation.
```

---

### 3. Interactive Content Refinement

**Current:**
```bash
# One-shot generation
deepseek_content.py deepseek-chat < prompt.txt > output.md
```

**Enhanced:**
```
Generate initial content
    ↓
DeepSeek V3 (MCP) reviews its own output
    ↓
Can read source files to verify accuracy
    ↓
Can suggest improvements
    ↓
Interactive refinement loop
```

**Example:**
```
GLM-4.7: Generate content section 1.2 on TVD limiters

DeepSeek V3 (MCP): [Generates content]
                   [Self-review: Checking against vanLeer.H...]

                   I noticed: The formula I gave for r calculation
                   doesn't match the actual implementation in vanLeer.H:67.

                   [Reading source...]

                   Correction: Should use mag(r) not just r.
                   Should I update the section?

GLM-4.7: Yes, fix it and add the source reference.

DeepSeek V3: [Updates content]
                   ✅ Now verified against source
```

---

### 4. Code Implementation Assistant

**New feature: `/implement` command**

```
Use deepseek-chat-mcp to implement the designed feature

Process:
1. DeepSeek V3 reads relevant source files
2. Analyzes existing patterns
3. Writes new code following conventions
4. Compiles and tests
5. Reports results
```

---

## Implementation Steps

### Step 1: Update Walkthrough Orchestrator

**File:** `.claude/skills/walkthrough/walkthrough_orchestrator.py`

**Changes:**
```python
# Add MCP option
class WalkthroughOrchestrator:
    def __init__(self, day: int, use_mcp: bool = True):
        self.use_mcp = use_mcp
        # ... existing code

    def _call_deepseek(self, model: str, task: str) -> str:
        if self.use_mcp:
            # Use MCP agent (with tools!)
            return self._call_mcp_agent(model, task)
        else:
            # Use Python wrapper (fallback)
            return subprocess.call(["deepseek_content.py", ...])
```

### Step 2: Create Brainstorming Skill

**New file:** `.claude/skills/brainstorm/SKILL.md`

```yaml
---
name: brainstorm
description: Interactive research and design with DeepSeek R1
---

Uses deepseek-reasoner-mcp to:
- Explore OpenFOAM source codebase
- Research specific topics
- Design content structure
- Verify sources independently
```

### Step 3: Update Content Creation Workflow

**File:** `.claude/skills/content-creation/SKILL.md`

**Add new stage:**
```markdown
## Stage 2.5: Research & Design (NEW)

1. **Identify research needs**
   - GLM-4.7 reviews skeleton
   - Lists questions to investigate

2. **DeepSeek R1 research**
   - Uses MCP tools to explore codebase
   - Reads relevant source files
   - Proposes content structure

3. **Interactive refinement**
   - Discuss approach with GLM-4.7
   - Refine based on findings
   - Approve final design

4. **Proceed to Stage 3**
   - Content generation with verified sources
```

### Step 4: Add MCP Configuration Toggle

**File:** `.claude/config/features.yaml`

```yaml
mcp:
  enabled: true
  fallback_to_wrapper: true

walkthrough:
  use_mcp_for_theory: true
  use_mcp_for_code: true

content_creation:
  use_mcp_for_research: true
  use_mcp_for_generation: false  # Keep wrapper for speed
```

---

## Workflow Examples

### Example 1: Creating Day 13 Content

```
User: /create-day 13

GLM-4.7: Stage 1-2: Extract ground truth ✅
        Stage 2.5: Research & Design

        Topic: Multi-phase flow models in OpenFOAM
        Research needed: What phaseChange models exist?

DeepSeek R1 (MCP): [Grep: phaseChange in OpenFOAM...]
                   Found: thermalPhaseChange, phaseChangeTwoPhaseMixtures

                   [Reading thermalPhaseChange.H...]

                   [Reading phaseChangeTwoPhaseMixtures.H...]

                   Proposal: Structure as:
                   1. Phase change model hierarchy
                   2. thermalPhaseChange implementation
                   3. Two-phase mixture models
                   4. Example: Evaporating droplet

GLM-4.7: Approved. Continue to Stage 3.

Stage 3-5: Content generation (Python wrapper - fast)
Stage 6:   Final formatting ✅
```

### Example 2: Brainstorming Implementation

```
User: /brainstorm

Topic: How to implement evaporation for R410A?

DeepSeek R1 (MCP): [Exploring thermalPhaseChange...]
                   [Analyzing species transport...]

                   Current OpenFOAM supports:
                   - Thermal phase change (boiling)
                   - Species mass transfer

                   For R410A refrigerant evaporator:

                   1. Use twoPhaseTransport model
                   2. Enable phaseChange Properties
                   3. Add source terms for mass transfer
                   4. Coupled with energy equation

                   [Reading reactingEulerianFoam solver...]

                   Recommendation: Extend reactingEulerianFoam
                   rather than create from scratch.

                   Shall I explore the solver structure?

User: Yes

DeepSeek R1: [Analyzing solver files...]
              Main files to modify:
              - createFields.H (add evaporation model)
              - TEqn.H (add latent heat source)
              - YEqn.H (add species transfer)

              Ready to implement when you are.
```

---

## Migration Path

### Phase 1: Add MCP as Optional (Current)

- [x] MCP server working
- [ ] Add MCP toggle to walkthrough skill
- [ ] Add MCP toggle to content creation
- [ ] Keep Python wrapper as fallback
- [ ] Test both modes work

### Phase 2: Create New MCP-Only Features

- [ ] Create `/brainstorm` skill
- [ ] Create `/implement` command
- [ ] Add interactive refinement mode

### Phase 3: Full MCP Integration

- [ ] Make MCP default for research tasks
- [ ] Keep wrapper for batch generation
- [ ] Optimize for speed vs. capabilities

---

## Decision Tree: When to Use MCP

```
Task needs tools (Read, Grep, etc.)?
├── Yes → Use MCP (DeepSeek with tools)
│   ├── Research & exploration → DeepSeek R1 MCP
│   ├── Code implementation → DeepSeek V3 MCP
│   └── Interactive refinement → Either MCP
│
└── No → Use Python wrapper
    ├── Batch content generation → Wrapper
    ├── One-shot responses → Wrapper
    └── Simple questions → Wrapper
```

---

## Benefits Summary

| Benefit | How MCP Helps |
|---------|---------------|
| **Accuracy** | DeepSeek can verify against source code directly |
| **Flexibility** | Interactive refinement vs. one-shot generation |
| **Research** | Can explore codebase independently |
| **Collaboration** | Multi-turn discussions with tools |
| **Verification** | Self-verify against OpenFOAM source |

---

## Files to Modify

| File | Change | Priority |
|------|--------|----------|
| `walkthrough_orchestrator.py` | Add MCP option | High |
| `content-creation/SKILL.md` | Add Stage 2.5 | Medium |
| `.claude/skills/brainstorm/SKILL.md` | New skill | Medium |
| `.claude/config/features.yaml` | MCP toggles | Low |

---

## Testing Checklist

Before rolling out:

- [ ] MCP works in walkthrough skill
- [ ] MCP works in content creation (Stage 2.5)
- [ ] Fallback to wrapper works if MCP fails
- [ ] Speed is acceptable for interactive use
- [ ] Quality improvement is measurable

---

**Next Action:** Start with Step 1 (update walkthrough orchestrator) and test?

