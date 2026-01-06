---
description: Batch generate Phase 1 (Days 01-12) using Hybrid DeepSeek R1 + V3 Pipeline
---

# Hybrid Batch Generation Workflow (R1 + V3)

## Prerequisites
1. `DEEPSEEK_API_KEY` ตั้งค่าแล้ว
2. `aider` installed
3. Templates ready in `daily_learning/templates/` (using V3 expansion template)

## Pipeline Overview

```
Scout (Agent) → R1 (Skeleton) → V3 (Expand) → QC (Agent)
```

## Step-by-Step Execution

### 1. Preparation
```bash
# Ensure directories exist
mkdir -p daily_learning/skeletons daily_learning/drafts
```

### 2. Per-Day Loop (Day 01 - 12)

#### 2.1 Scout Phase
Identify relevant OpenFOAM source files for the day's topic.

#### 2.2 Analysis Phase (DeepSeek R1)
Generate JSON Skeleton.
**Important:** Use `--read` for context and templates.

```bash
export DEEPSEEK_API_KEY="..."
aider --model r1 --yes-always \
  --read daily_learning/phase_1_context.md \
  --read daily_learning/templates/deepseek_r1_template.md \
  {source_files} \
  --message "Day {N}: {Topic}
  Analyze and create JSON skeleton following deepseek_r1_template.md.
  Output: daily_learning/skeletons/day{N}_skeleton.json"
```

#### 2.3 Expansion Phase (DeepSeek V3)
Expand to full content (1500+ lines).
**Critical:** Use `--no-git` to avoid repo confusion and ensure file writing.

```bash
# Must run from daily_learning directory to match relative paths if needed, 
# or use absolute paths. Recommended: Run from root with explicit paths.

cd daily_learning
aider --model v3 --yes-always --no-git \
  --read phase_1_context.md \
  --read templates/deepseek_v3_expand_template.md \
  --read skeletons/day{N}_skeleton.json \
  --message "Day {N}: {Topic}
  Expand skeleton to FULL lesson (1500+ lines) using deepseek_v3_expand_template.md.
  Output: drafts/day{N}_draft.md"
cd .. # Return to root
```

#### 2.4 QC Phase
Review `daily_learning/drafts/day{N}_draft.md`:
- Check for 1500+ lines
- Check for "Hardcore" depth
- Move to `daily_learning/2026-01-{DD}.md`

### 3. Context Update
Isolate critical equations/classes from finished day and append to `phase_1_context.md` (optional but recommended for continuity).

## Day-Topic Mapping

| Day | Topic | Key Files |
|-----|-------|-----------|
| 01 | Governing Equations | fvMatrix.H, volFields.H |
| 02 | Finite Volume Method | fvMesh.H, surfaceInterpolation.H |
| 03 | Spatial Discretization | gaussConvectionScheme.H, upwind/linearSchemes |
| 04 | Temporal Discretization | ddtScheme.H, eulerDdtScheme.H |
| 05 | Mesh Topology | polyMesh.H, primitiveMesh.H |
| 06 | Boundary Conditions | fvPatchField.H, fixedValue/zeroGradient |
| 07 | Linear Algebra | lduMatrix.H, PCG.H |
| 08 | Iterative Solvers | smoothSolver.H, GAMG.H |
| 09 | Pressure-Velocity | PISO.H, SIMPLE.H |
| 10 | Two-Phase Flow | interfaceProperties.H, alphaEqn.H |
| 11 | Phase Change Theory | phaseChangeTwoPhaseMixture.H |
| 12 | Phase 1 Review | N/A |
