# Enhanced Lab System

> **Natural C++/DSA Integration** - Learn CFD with authentic C++ and DSA concepts from OpenFOAM

---

## Overview

This lab system implements **natural C++/DSA integration** with hands-on coding exercises:

- **Primary Focus:** CFD implementation using OpenFOAM
- **Integrated Learning:** C++ and DSA concepts as they naturally appear in OpenFOAM code
- **No Artificial Topics:** Only teach what's actually used in OpenFOAM

---

## Directory Structure

```
daily_learning/labs/
├── README.md                  # This file
├── 01_lab.md                  # Lab 1: Continuity Equation
├── 02_lab.md                  # Lab 2: (when generated)
├── ...
└── [Labs generated with /create-lab]
```

---

## How Labs Work

### Enhanced Lab Structure (6 Parts)

Each lab follows a flexible 6-part structure:

| Part | Duration | Focus |
|------|----------|-------|
| **1. Setup** | 10% | Environment, files, verification |
| **2. CFD Implementation** | 35% | OpenFOAM implementation |
| **3. C++ Deep Dive** | 20% | Template classes, smart pointers, operators |
| **4. DSA Connection** | 20% | Sparse matrices, complexity, algorithms |
| **5. Integration Challenge** | 10% | Combine CFD + C++ + DSA knowledge |
| **6. Debugging & Analysis** | 5% | Troubleshooting, performance |

**Total time:** 3-8 hours per lab (varies by C++/DSA richness)

---

## Natural C++/DSA Integration

### Philosophy

**Only teach C++/DSA that naturally appears in OpenFOAM.**

**DO Include (Natural to OpenFOAM):**
| Topic | OpenFOAM Example | When |
|-------|-----------------|------|
| Templates | `tmp<>`, `Field<Type>`, `fvMatrix<Type>` | Always relevant |
| Smart Pointers | `tmp<>`, `autoPtr`, `refPtr` | Memory management |
| Sparse Matrices | `LduMatrix`, LDU format | Linear systems |
| Containers | `List`, `HashTable`, `Map` | Field operations |
| Operators | `operator+`, `operator==` | Field expressions |
| Trees | `octree`, `cellTree` | Spatial search |

**DON'T Include (Not Natural):**
- Graph algorithms (BFS, DFS, shortest path)
- Dynamic programming
- Backtracking
- Advanced trees (AVL, red-black)
- Heaps/priority queues

---

## Lab Duration by C++/DSA Richness

| C++/DSA Score | Duration | Examples |
|---------------|----------|----------|
| **Low (0-2)** | 3 hours | Basic BCs, simple source terms |
| **Medium (3-5)** | 4-5 hours | Continuity equation, discretization |
| **High (6-8)** | 6-8 hours | Custom solvers, advanced templates |

**Detection:**
```bash
python3 .claude/scripts/detect_natural_cpp_dsa.py --day=XX
```

---

## Example: Lab 01 Structure

```markdown
# Lab 1: Implementing the Continuity Equation

**Duration:** 4.5 hours
**C++/DSA Richness:** High (7/8)

## Content Breakdown
- CFD Implementation: 70% (continuity equation, mass conservation)
- C++ Deep Dive: 15% (templates, smart pointers, operators)
- DSA Connection: 15% (sparse matrices, memory complexity)

## Parts
1. Setup (30 min)
2. CFD Implementation (80 min)
3. Integration Challenge (45 min) ← Mini-solver with custom sparse matrix
4. Independent Challenges (60 min)
5. Debugging & Analysis (45 min)
6. Results Analysis (30 min)
```

---

## Spaced Repetition Schedule

```
Week 1:
  Day 01: Theory (Governing Equations)
  Day 02: Theory (Finite Volume Method)
  Day 03: ⭐ Lab 01 (Continuity equation + C++/DSA)
          → Spaced practice of Days 01-02

Week 2:
  Day 04: Theory (Spatial Discretization)
  Day 05: Theory (Temporal Discretization)
  Day 06: ⭐ Lab 02 (FVM discretization + C++/DSA)
          → Spaced practice of Days 04-05
```

---

## Using Labs

### For Daily Learning

1. **Read theory** (`Phase_*/XX.md`)
2. **Wait 1-2 days** (spaced repetition)
3. **Do lab** (`labs/XX_lab.md`)
4. **Review concepts** with fresh perspective

### Lab Workflow

```bash
# 1. Detect natural C++/DSA content
python3 .claude/scripts/detect_natural_cpp_dsa.py --day=XX

# 2. Generate lab (uses /create-lab skill)
/create-lab --day=XX

# 3. Complete lab (follow the steps)
cd $FOAM_RUN/labXX
# ... [lab steps]

# 4. Verify results
python3 [analysis scripts]
```

---

## Lab Creation

Labs are generated using the `/create-lab` skill:

```bash
# Auto-detect lab type
/create-lab --day=XX

# Specify CFD lab
/create-lab --day=XX --type=cfd
```

**See:** `.claude/skills/create-lab/SKILL.md` for full workflow

---

## Content Breakdown by Lab Type

| Lab Type | CFD | C++ Deep Dive | DSA Connection | Duration |
|----------|-----|---------------|----------------|----------|
| **Rich C++/DSA** | 70% | 15% | 15% | 5-6 hours |
| **Medium C++/DSA** | 75% | 12% | 13% | 4-5 hours |
| **Minimal C++/DSA** | 85% | 8% | 7% | 3 hours |

**CFD remains the primary focus** in all labs.

---

## Lab Requirements

### Environment

- OpenFOAM v10 or later (v2306 recommended)
- C++ compiler supporting C++17
- Python 3+ (for analysis scripts)
- Git (for version control)

### Prerequisites

Each lab specifies:
- Required theory completion
- Estimated duration (3-8 hours)
- Difficulty level
- Required files/tools

### Deliverables

Each lab expects:
- Working code that compiles
- Simulation that runs successfully
- Results meeting validation criteria
- Performance analysis
- Code following OpenFOAM style guide

---

## Verification

All lab content is verified using **Source-First methodology**:

1. Extract ground truth from OpenFOAM source code
2. Verify code examples compile
3. Test expected outputs
4. Mark verified sections with ⭐

**Detection Script:**
```bash
python3 .claude/scripts/detect_natural_cpp_dsa.py --day=XX --output=json
```

---

## Progress Tracking

```bash
# List labs
ls -1 daily_learning/labs/*_lab.md

# Track completion
echo "$(date): Completed Lab 01" >> labs/progress.log
```

---

## Tips for Success

1. **Don't skip the theory** - Labs assume you've read the theory
2. **Code along, don't copy-paste** - Muscle memory matters
3. **Get stuck?** Check the troubleshooting section first
4. **Complete C++ Deep Dives** - That's where OpenFOAM understanding deepens
5. **Do Integration Challenges** - Combines all knowledge areas
6. **Space your repetition** - Don't do all labs in one day

---

## Key Files

| File | Purpose |
|------|---------|
| `.claude/skills/create-lab/SKILL.md` | Lab generation skill |
| `.claude/scripts/detect_natural_cpp_dsa.py` | C++/DSA detection |
| `.claude/templates/structural_blueprints.json` | Lab templates |
| `.claude/skills/create-lab/NATURAL_CPP_DSA_IMPLEMENTATION_COMPLETE.md` | Implementation docs |

---

## Related Documentation

- **Daily theory:** `daily_learning/Phase_*/XX.md`
- **Lab generation:** `.claude/skills/create-lab/SKILL.md`
- **CFD Standards:** `.claude/rules/cfd-standards.md`
- **Source-First:** `.claude/rules/source-first.md`

---

**Last Updated:** 2026-02-08
**Approach:** Natural C++/DSA Integration + Spaced Repetition
