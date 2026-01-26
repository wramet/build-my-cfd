# CFD Engine Development Project

## Project Goal

Build a custom CFD engine for **Refrigerant Two-Phase Flow with Evaporation in Tube** using OpenFOAM architecture.

**Target:** R410A evaporator simulation (liquid inlet → two-phase flow → vapor outlet)

---

## Key Files to Reference

| File | Purpose |
|------|---------|
| [roadmap.md](roadmap.md) | **Master learning plan** - 90 days, 6 phases |
| [.claude/rules/source-first.md](.claude/rules/source-first.md) | Ground truth extraction methodology |
| [.claude/rules/cfd-standards.md](.claude/rules/cfd-standards.md) | LaTeX, Mermaid, Code standards |
| [.claude/rules/verification-gates.md](.claude/rules/verification-gates.md) | 6 mandatory verification checkpoints |

---

## Daily Learning Content

**Location:** `daily_learning/Phase_01_Foundation_Theory/`

**Naming:** `01.md`, `02.md`, `03.md`, etc.

**Current Status:**
- Day 01: Governing Equations ✅
- Day 02: Finite Volume Method Basics ✅
- Day 03: Spatial Discretization (needs English-only regeneration)

---

## Creating New Daily Content

### Source-First Workflow (REQUIRED!)

When creating daily content, ALWAYS follow this sequence:

```
1. EXTRACT → Ground truth from OpenFOAM source code
2. VERIFY  → Check class hierarchies and formulas
3. RESEARCH → GLM 4.7 Web Search for documentation
4. GENERATE → Create content using verified facts
5. VERIFY  → Re-check against ground truth
6. FORMAT  → Apply CFD standards
```

### Commands Available

- `/create-day` - Generate new daily content with Source-First workflow
- `/walkthrough` - Interactive walkthrough with Source-First verification
- `/qc-modular` - Section-by-section QC for large files

### Scripts Available

```bash
# Ground truth extraction
.claude/scripts/extract_facts.py --mode hierarchy

# Verification
.claude/scripts/verify_skeleton.py
.claude/scripts/verify_formulas.py
.claude/scripts/verify_content.py
```

---

## Content Standards

### Language Preference

**Default:** English only (per user request)

Headers can be bilingual, but content should be English.

### Technical Accuracy

- ⭐ = Verified from source code
- ⚠️ = Unverified claim
- ❌ = Incorrect/Don't

### Code Standards

- All code blocks must have language tags
- All code blocks must be balanced
- No nested LaTeX delimiters
- File references must include paths and line numbers

---

## Project Architecture

```
th_new/
├── roadmap.md                           # Master plan (READ THIS FIRST)
├── CLAUDE.md                            # This file
├── daily_learning/
│   └── Phase_01_Foundation_Theory/     # Days 01-12
├── .claude/
│   ├── commands/                       # Slash commands
│   ├── agents/                         # Specialized subagents
│   ├── skills/                         # Reusable workflows
│   ├── rules/                          # Always-follow guidelines
│   ├── hooks/                          # Trigger-based automation
│   └── scripts/                        # Verification tools
└── MODULE_*/                           # Reference modules
```

---

## AI Model Strategy

| Task | Model | Why |
|------|-------|-----|
| Main orchestrator | GLM-4.7 | Native tools, Web Search, Top-Tier coding |
| Complex reasoning | DeepSeek R1 | Math derivations, analysis |
| Coding | DeepSeek V3 | Fast code generation |

---

## Quick Start for New Sessions

1. Read [roadmap.md](roadmap.md) to understand current day
2. Check [daily_learning/](daily_learning/) for existing content
3. Use `/create-day` to generate new content with Source-First workflow
4. Always verify ground truth BEFORE generating content

---

*Last Updated: 2026-01-24*
*Project Phase: Foundation (Day 01-12)*
