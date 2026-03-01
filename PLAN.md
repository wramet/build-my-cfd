# C++ Learning Curriculum - Refactoring Plan

**Project:** Transform from R410A CFD Engine Development to C++ & Software Engineering Learning
**Created:** 2026-03-01
**Status:** Phase 0 Complete (10/17 tasks = 59%)
**Estimated Total:** ~60 hours

---

## 📋 Executive Summary

This document outlines the complete refactoring plan to transform the project from a **90-day R410A refrigerant CFD engine development** curriculum into an **84-session C++ & Software Engineering learning** curriculum using OpenFOAM as a case study.

**Key Changes:**
- **Target:** Learn intermediate-to-advanced C++ through real-world OpenFOAM patterns
- **Approach:** Project-based learning with 5 progressive phases
- **Focus:** C++ templates, RAII, smart pointers, software architecture, performance optimization
- **Duration:** 84 sessions (reduced from 90 days)

---

## 🎯 Transformation Objectives

### From (R410A CFD Engine):
❌ Overly ambitious: Build complete CFD engine in 90 days
❌ Narrow domain: Refrigerant two-phase flow only
❌ Limited applicability: Specific to R410A evaporators

### To (C++ Through OpenFOAM):
✅ Achievable goal: Learn C++ through studying production code
✅ Broad applicability: Software engineering patterns used everywhere
✅ Real-world case study: OpenFOAM (industrial-quality C++ codebase)
✅ Practical focus: Intermediate-advanced C++ skills transferable to any domain

---

## 📊 17-Task Refactoring Roadmap

### Phase 0: Tooling Preparation (9 tasks)

#### ✅ TASK 001: Create phase_mapping.yaml and phase_utils.py
**Status:** COMPLETE | **Time:** 25 min | **Priority:** CRITICAL

- `.claude/config/phase_mapping.yaml` - Single source of truth for day→phase mapping
- `.claude/scripts/phase_utils.py` - Shared helper module

#### ✅ TASK 002: Archive R410A files and rewrite configs
**Status:** COMPLETE | **Time:** 30 min | **Priority:** CRITICAL

- Archive: `.claude/archive/r410a/` (7 files)
- Rewrite: `.claude/config/project_context.yaml`
- Replace: `r410a_implementation.yaml` → `curriculum_tasks.yaml`

#### ✅ TASK 003: Rewrite roadmap.md with new 5-phase structure
**Status:** COMPLETE | **Time:** 60 min | **Priority:** CRITICAL

- `roadmap.md` - 875 lines, 84 sessions, 5 phases

#### ✅ TASK 004: Rewrite topics.json for 84 sessions
**Status:** COMPLETE | **Time:** 30 min | **Priority:** HIGH

- `.claude/config/topics.json` - 84 sessions with topic, short name, template, and source files

#### ✅ TASK 005: Create new content templates (4 JSON files)
**Status:** COMPLETE | **Time:** 30 min | **Priority:** HIGH

- cpp_deep_dive, architecture_analysis, performance_lab, solver_implementation

#### ✅ TASK 006: Refactor scripts to use phase_utils.py
**Status:** COMPLETE | **Time:** 60 min | **Priority:** HIGH

- generate_blueprint.py, run_content_workflow.sh, load_project_context.py

#### ✅ TASK 007: Refactor skills (create-module, walkthrough, qa)
**Status:** COMPLETE | **Time:** 60 min | **Priority:** HIGH

- Removed R410A hardcoding, fixed Phase_01 paths

#### ✅ TASK 008: Update agent definitions and documentation
**Status:** COMPLETE | **Time:** 45 min | **Priority:** MEDIUM

- architect.md, researcher.md, deepseek-chat.md, CLAUDE.md, SKILL.md

#### ✅ TASK 009: End-to-end verification (V1-V7)
**Status:** COMPLETE | **Time:** 15 min | **Priority:** CRITICAL

- V1-V6: All passed. V7: R410A only in legacy scripts (not in core pipeline)

---

### Phase 1-5: Content Generation (6 tasks)

#### ⏸️ TASK 010-015: Generate all 84 days of content
**Status:** PENDING | **Time:** ~56 hours | **Priority:** HIGH/MEDIUM

- Days 01-14: C++ Through OpenFOAM
- Days 15-28: Data Structures & Memory
- Days 29-42: Software Architecture
- Days 43-56: Performance Optimization
- Days 57-84: Focused Implementation

---

### Phase 6: Cleanup (2 tasks)

#### ⏸️ TASK 016-017: Archive and reorganize
**Status:** PENDING | **Time:** 45 min | **Priority:** LOW

- Archive old Phase_01/Phase_02 content
- Reorganize MODULE_* directories

---

## 📈 Progress: 10/17 tasks complete (59%)

```
Phase 0: Tooling    ██████████████████ 9/9 (100%) ✅
Phase 1-5: Content  ░░░░░░░░░░░░░░░░░░ 0/6 (0%)
Phase 6: Cleanup    ░░░░░░░░░░░░░░░░░░ 0/2 (0%)

Completed: Tasks 001-009
Pending:   Tasks 010-017
```

---

## 🔧 Key Technical Changes

### 1. Phase Mapping System
```yaml
# .claude/config/phase_mapping.yaml
phases:
  - id: "Phase_01_CppThroughOpenFOAM"
    days: [1, 14]
    folder: "Phase_01_CppThroughOpenFOAM"
    template: "cpp_deep_dive"
    target_lines: 900
```

### 2. Phase Utilities Module
```python
# .claude/scripts/phase_utils.py
get_phase_for_day(day) -> Dict
get_folder_for_day(day) -> str
get_template_for_day(day) -> str
get_target_lines(day) -> int
```

### 3. New Content Templates
- cpp_deep_dive (65% code)
- architecture_analysis (60% code)
- performance_lab (70% code)
- solver_implementation (75% code)

---

## 📝 Next Steps

### Immediate (Tasks 10-15)
Generate all 84 days of content (~56 hours)

### Long-term (Tasks 16-17)
Cleanup and archive old MODULE_* directories

---

## 📚 Related Documents

- **roadmap.md** - 84-session learning curriculum
- **CLAUDE.md** - Project documentation
- **.claude/tasks/curriculum_tasks.yaml** - Official task tracker

---

**Last Updated:** 2026-03-01
**Status:** Phase 0 Complete (59%) — Ready for content generation (Tasks 010-015)
