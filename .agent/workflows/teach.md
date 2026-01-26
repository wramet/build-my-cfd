---
description: Generate daily CFD lesson using DeepSeek R1+V3 hybrid with Claude as scout
---

# /teach - Daily Lesson Generation

Generate hardcore CFD learning content for Day N using the DeepSeek hybrid workflow.

## Usage

```
/teach Day 5
```

or with explicit topic:

```
/teach 05 "Mesh Topology Concepts"
```

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONTENT GENERATION PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PHASE 1: GENERATION (DeepSeek - Thai Output)                          │
│  ─────────────────────────────────────────────                          │
│  Claude Scout  →  R1 Analyze  →  V3 Write                               │
│  (Find files)     (Math/Logic)   (Thai Engineering content)             │
│                                                                         │
│  PHASE 2: QC & AUDIT (Claude/Gemini Only)                               │
│  ─────────────────────────────────────────────                          │
│  Apply quality_control_checklist.md                                     │
│  Audit Physics/Code (No Translation needed)                             │
│                                                                         │
│  Output: daily_learning/YYYY-MM-DD.md                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow Steps

### Step 1: Read Roadmap

Read `roadmap.md` to find the topic for the specified day.
Extract: topic title, key concepts, expected deliverables.

### Step 2: Load Context Chain (Critical for Consistency)

**Always load these files before generating:**

1. **Phase Context** (if exists): `daily_learning/phase_N_context.md`
   - Contains: Notation standards, Class names, Key concepts
   - Purpose: Ensures consistent math notation across days

2. **Previous Day** (if exists): `daily_learning/YYYY-MM-{Day-1}.md`
   - Contains: Previous day's content
   - Purpose: Ensures continuity and avoids repetition

3. **CONVENTIONS.md** (MANDATORY): `CONVENTIONS.md` at project root
   - Contains: 8-pillar governance rules (Accuracy, Pedagogy, DRY, Context, Verification, Tone, Progression, Visualization)
   - Purpose: Ensures consistent quality across all generated content

**Print:** "📖 Context loaded: phase_N_context.md + Day {N-1} + CONVENTIONS.md"

### Step 2.5: Skill Invocation

Before generating content, conceptually "load" these skills:
- **`auto_qc`**: Will be applied after V3 writes content (Engineering Thai fixes)
- **`quality_gate`**: Final checklist before delivery (Physics, Pedagogy, Style)

### Step 3: Search Existing Modules (Claude Scout)

Search MODULE_01 through MODULE_09 for related content:
- Scope: `MODULE_*/CONTENT/**/*.md` and `MODULE_*/00_Navigator.md`
- Use: `grep -r "keyword"` or find patterns
- Pick: Only 2-3 most relevant existing files
- Print: "📚 Module Reference: Found related content in ..."

**Rules:**
- ✅ OK to explain same concepts as Modules (more detail = better)
- ❌ DO NOT duplicate content from OTHER daily_learning files

### Step 4: Scout OpenFOAM Source (Claude Scout)

Search in `./openfoam_src` for relevant files:
- Scope: `src/` and `applications/` only (ignore tutorials, wmake)
- Use: `grep -r "class ClassName"` or `find . -name "*.H"`
- Pick: Only 2-3 core files (.H and .C pairs)
- Print: "🔍 Scouting Result: Targeted files: ..."

### Step 5: Analyze with R1 (via Aider)

```bash
aider --alias r1 --read CONVENTIONS.md --read openfoam_src/...
```

Prompt R1:
> "Analyze the math & logic in the discovered files. Focus on:
> - Mathematical formulation
> - Class structure and relationships
> - Key algorithms
> Output: Technical breakdown only (no prose)."

### Step 6: Write with V3 (via Aider)

```bash
aider --alias v3 --read CONVENTIONS.md daily_learning/YYYY-MM-DD.md
```

Prompt V3:
> "Create daily_learning/YYYY-MM-DD.md based on R1 analysis.
> 
> **CONTEXT CHAIN (must reference):**
> - Use notation from phase_N_context.md
> - Connect to concepts from Day {N-1}
> 
> **CONTENT:**
> - Theory section with LaTeX equations
> - OpenFOAM code analysis  
> - Mermaid.js diagrams for complex topics
> - Simplified implementation notes
> - Concept checks with answers
> 
> **IMPORTANT: Write everything in ENGINEERING THAI (Technical style).**
> - Use English for technical terms (e.g., "Field", "Mesh", "Flux")
> - Use Thai for explanations and glues."

### Step 7: Report

Print: "✅ Day generated: daily_learning/YYYY-MM-DD.md"

---

## Expected Output

- File: `daily_learning/YYYY-MM-DD.md`
- Structure:
  1. Theory (LaTeX equations)
  2. OpenFOAM Reference (real source code)
  3. Design (class diagrams)
  4. Implementation (simplified code)
  5. Test (verification)
  6. Concept Checks (Q&A)
- Quality: Claude/Gemini applies `quality_control_checklist.md`
- Language: Thai (V3) → Refined Engineering Thai (Claude QC)

---

## QC Checklist Summary

| # | Category | Key Checks |
|---|----------|-----------|
| 0 | Physics | Equations correct, Units consistent, Assumptions clear |
| 1 | Layout | Clean headers, Wiki-links, Callout syntax, LaTeX |
| 2 | Language | Engineering Thai, No over-translation |
| 3 | Visuals | Mermaid diagrams for complex topics |
| 4 | Pedagogy | Learning objectives, Summaries, Concept checks |
| 5 | Final | Code syntax, Links work, Metadata complete |
