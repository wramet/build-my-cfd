# Content Generation Workflow Guide

**Project:** C++ & Software Engineering Through OpenFOAM
**Last Updated:** 2026-03-01

---

## Current API Status (as of 2026-03-01)

| API | Status | Notes |
|-----|--------|-------|
| Claude Sonnet 4.6 (main) | ✅ Working | Primary generation model |
| DeepSeek Chat V3 | ✅ Working | Key updated, path fixed |
| DeepSeek R1 (reasoner) | ✅ Working | Key updated, path fixed |
| DeepSeek MCP Server | ✅ Fixed | Path updated to worktree location |

**Note:** `.mcp.json` was updated (new key + correct server path). Restart Claude Code
for MCP server changes to take effect.

---

## Overview

This document describes how content is actually generated for this curriculum, and distinguishes
between the **ideal** (documented) workflow and the **practical** (what was actually done) workflow.

---

## Quick Reference: Which Day Are You On?

```bash
# Check current progress
ls daily_learning/Phase_01_CppThroughOpenFOAM/ | wc -l  # Phase 1
ls daily_learning/Phase_02_DataStructures_Memory/ | wc -l  # Phase 2

# Check phase for a day number
python3 .claude/scripts/phase_utils.py 29  # e.g., day 29 → Phase 3
```

---

## Workflow A: Ideal (Source-First, Full Verification)

This is the workflow defined in `.claude/skills/content-creation/SKILL.md`. Use it when strict
accuracy is required (mini-projects, Phases 4–5 performance work, Phase 5 solver implementation).

### Stage 1: Extract Ground Truth
```bash
# Extract facts from OpenFOAM source
python3 .claude/scripts/extract_facts.py --day=29 --mode hierarchy
# Output: /tmp/verified_facts_day29.json
```

### Stage 2: Generate Skeleton
- Ask architect agent to create `daily_learning/skeletons/day29_skeleton.json`
- Must align with `roadmap.md` topic for that day
- All facts marked ⭐

### Stage 2.5: Generate Blueprint
```bash
python3 .claude/scripts/generate_blueprint.py 29 "RTS Factory Pattern"
# Output: daily_learning/blueprints/day29_blueprint.json
```

### Stage 3: Verify Skeleton (DeepSeek R1)
- Ask verifier agent to check skeleton against ground truth
- STOP if verification fails

### Stage 4: Generate Content (DeepSeek Chat V3)
- Use deepseek-chat agent with skeleton + blueprint as context
- Output: `daily_learning/Phase_03_SoftwareArchitecture/29.md`
- English only, progressive overload structure

### Stage 5: Final Technical Verify (DeepSeek R1)
```bash
python3 .claude/scripts/verify_content.py --file=29.md --ground-truth=/tmp/verified_facts_day29.json
```

### Stage 6: Syntax QC
```bash
python3 .claude/scripts/qc_syntax_check.py --file=daily_learning/Phase_03_SoftwareArchitecture/29.md
python3 .claude/scripts/verify_code_blocks.py --dir daily_learning/Phase_03_SoftwareArchitecture
```

---

## Workflow B: Practical (What Was Actually Done for Phases 1–2)

Phases 1 and 2 were generated using a **bulk AI generation** approach, NOT the full 6-stage workflow.

### What Actually Happened

1. **Input:** `roadmap.md` day topic descriptions
2. **Agent:** `deepseek-chat` agent (or Claude Claude main agent) given the roadmap topic + phase context
3. **Generation:** Full markdown file generated in one pass
4. **Post-hoc QC:** `verify_code_blocks.py` run after all 14 files created
5. **Accepted issues:** Missing OpenFOAM headers in test environment = expected behavior

### Why It Worked

- Roadmap provides sufficient structure (what to cover, deliverable)
- Agents understand OpenFOAM patterns from training
- Post-hoc verification caught real issues (code block balance)
- Phase 2 benefited from lessons documented from Phase 1

### Limitations of Practical Workflow

- ⚠️ No formal ground truth extraction per day
- ⚠️ Code snippets are educational approximations, not verified against actual source
- ⚠️ Topic ordering deviated from roadmap starting Day 18 (see below)
- ⚠️ No DeepSeek API usage — pure Claude generation

---

## Known Topic Deviation: Phase 2 (Days 18–26)

The generated content does NOT follow the roadmap exactly from Day 18 onward.

| Day | Roadmap Topic | Generated Topic |
|-----|--------------|-----------------|
| 18 | Sparse Matrix Assembly (`fvMatrix`) | `List<T>` & `UList<T>` |
| 19 | Cache Access Patterns | `DynamicList` |
| 20 | OpenFOAM `List<T>` | `PtrList` & `UPtrList` |
| 21 | `DynamicList` & `CompactListList` | `IndirectList` (not in roadmap) |
| 22 | `HashTable<T>` | `BiIndirectList` (not in roadmap) |
| 23 | `HashSet` & `wordHashSet` | `HashSet<T>` ✅ |
| 24 | Memory Pools — `SubList` | `SubList` ✅ |
| 25 | Compact Storage — `labelList` | `CompactListList<T>` |
| 26 | `Field<T>` Memory — Alignment | Memory Alignment & SIMD ✅ |

**Decision:** Accept the deviation. Container coverage is comprehensive; fvMatrix assembly
is adequately covered in the mini-project (Days 27–28). Adding a Day 18a remediation is
optional before starting Phase 3.

---

## Recommended Workflow for Phase 3+ (Hybrid, DeepSeek Available)

Use a simplified 4-stage approach for best speed/quality tradeoff:

```
1. Read roadmap.md for the day's topic and deliverable
2. Ask deepseek-chat agent to generate content following the roadmap spec
   - Context: roadmap day spec + adjacent days for continuity
   - Output format: same 5-part structure as Phase 1 files
3. Run verify_code_blocks.py on the file
4. Spot-check one code snippet against openfoam_temp/ source
```

For mini-project days (e.g., Day 41–42, Day 55–56) use **Workflow A** since accuracy is critical.

---

## Phase Folder Mapping

| Phase | Days | Folder |
|-------|------|--------|
| 1 | 01–14 | `daily_learning/Phase_01_CppThroughOpenFOAM/` |
| 2 | 15–28 | `daily_learning/Phase_02_DataStructures_Memory/` |
| 3 | 29–42 | `daily_learning/Phase_03_SoftwareArchitecture/` |
| 4 | 43–56 | `daily_learning/Phase_04_PerformanceOptimization/` |
| 5 | 57–84 | `daily_learning/Phase_05_FocusedCFDComponent/` |

**Source of truth:** `.claude/config/phase_mapping.yaml`
**Never hardcode paths** — use `python3 .claude/scripts/phase_utils.py <day>` instead.

---

## Verification Commands

```bash
# Check code block balance for a whole phase
python3 .claude/scripts/verify_code_blocks.py \
    --dir daily_learning/Phase_03_SoftwareArchitecture --json

# QC a single file
python3 .claude/scripts/qc_syntax_check.py \
    --file daily_learning/Phase_03_SoftwareArchitecture/29.md

# Count lines in a file
wc -l daily_learning/Phase_03_SoftwareArchitecture/29.md
# Target: ~900 lines (Phase 3), ~1000 lines (Phase 4)
```

---

## Known Issues (Open)

| # | Issue | Impact | Status |
|---|-------|--------|--------|
| 1 | Old folders in `daily_learning/`: `Phase_01_Foundation_Theory`, `Phase_02_Geometry_Mesh`, `Day03_SpatialDiscretization` | Confusing | ⏸️ Defer to Phase 6 cleanup |
| 2 | R410A scripts still present: `verify_two_phase.py`, `verify_expansion_term.py` | No current impact | ⏸️ Defer to Phase 6 |
| 3 | Redundant scripts: `verify_equations.py` ↔ `verify_formulas.py`, `auto_fix.py` ↔ `repair_syntax.py` | Minor confusion | ⏸️ Defer to Phase 6 |
| 4 | Task manager (`task_manager.py`) points to `r410a_implementation.yaml` | Misleading if used | ⏸️ Defer to Phase 6 |
| 5 | Phase 2 topic deviation from roadmap (Days 18–26) | Content gap for fvMatrix standalone | ✅ Accepted |
| 6 | Phase 2 code uses idealized implementations vs actual source | Less source-first rigor | ✅ Accepted for learning content |

---

## Content Quality Expectations

| Metric | Phase 1–2 Actual | Target for Phase 3+ |
|--------|-----------------|---------------------|
| Lines per file | 900–1940 | ≥900 |
| Code blocks balanced | 100% | 100% |
| LaTeX standards | ✅ Pass | ✅ Pass |
| Mermaid diagrams | ≥2 per file | ≥2 per file |
| ⭐ verification markers | Present | Present |
| Source citations | Good (P1), Fair (P2) | Good |

---

*See also: `roadmap.md`, `PLAN.md`, `.claude/skills/content-creation/SKILL.md`*
