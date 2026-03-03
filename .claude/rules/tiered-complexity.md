# Tiered Complexity Standard

Defines four content tiers for the 84-session curriculum. Use this file as a **pre-generation spec** and a **post-generation QC checklist**.

---

## Tier Definitions

### Tier 1 — Concept Introduction

**When:** A single new C++ feature is being introduced. Minimal CFD integration. Self-contained.

**Examples:** Day 01 (Templates), Day 02 (Concepts), Day 06 (Smart Pointers), Day 08 (Perfect Forwarding), Day 11 (Ranges)

| Metric | Minimum |
|--------|---------|
| Line count | **350** |
| Code examples | **3** (problem + solution + variant) |
| Structure | **4-Part minimum** |
| Deliverable section | ✅ Required |
| Benchmark/profile | ❌ Optional |

**Required content pattern:**
```
Part 1 — The Problem  (what breaks without this feature)
Part 2 — The Concept  (how the feature works, syntax, semantics)
Part 3 — Implementation  (complete working example)
Part 4 — Deliverable  (specific build target + compile command)
```

**Quality markers:**
- Each code block is runnable in isolation (no mystery includes)
- "Bad" (old) pattern shown before "Good" (modern) pattern
- Compiler error or runtime consequence explained

---

### Tier 2 — Applied Pattern

**When:** A concept is applied to CFD data structures with profiling, benchmarking, or a multi-step workflow.

**Examples:** Day 03 (Mesh-Field Relationship), Day 04 (CRTP), Day 07 (Move Semantics), Day 17 (LDU Multiply), Day 19 (Cache Patterns), Day 45 (Auto-Vectorization), Day 47 (OpenMP Basics)

| Metric | Minimum |
|--------|---------|
| Line count | **550** |
| Code examples | **4** (problem + 2 implementations + benchmark) |
| Structure | **5-Part minimum** |
| Deliverable section | ✅ Required |
| Benchmark/profile | ✅ Required |

**Required content pattern:**
```
Part 1 — The Problem  (CFD-specific motivating example)
Part 2 — The Concept  (C++ feature + theory)
Part 3 — Implementation  (complete working class or function)
Part 4 — Profiling / Benchmark  (measurable result or expected output)
Part 5 — Deliverable  (specific build target + test command)
```

**Quality markers:**
- At least one data table comparing before/after or Option A vs Option B
- Numbers given (e.g., "1M cells = 8 MB at 8 bytes/double")
- OpenFOAM comparison note (what OpenFOAM does, why we differ)
- Code compiles as shown with no hidden headers

---

### Tier 3 — Architecture / Integration Day

**When:** Multiple concepts combine into a system-level design. Design decisions and trade-offs are the core of the lesson.

**Examples:** Day 10 (C++20 Modules), Day 18 (Matrix Assembly), Day 23 (PMR), Day 31 (Factory Pattern), Day 35 (Object Registry), Day 37 (BC Interface), Day 46 (SIMD Intrinsics), Day 49 (False Sharing), Day 51 (Zero-Allocation Loop), Day 52 (Mesh Bandwidth)

| Metric | Minimum |
|--------|---------|
| Line count | **750** |
| Code examples | **5** (problem + 2–3 implementations + integration glue) |
| Structure | **5-Part minimum** |
| Deliverable section | ✅ Required |
| Design trade-off section | ✅ Required |
| Test or verification | ✅ Required |

**Required content pattern:**
```
Part 1 — The Problem  (architectural gap or performance bottleneck)
Part 2 — Design Decisions  (why this approach, what alternatives exist)
Part 3 — Core Implementation  (primary class or function, fully implemented)
Part 4 — Integration  (how it connects to existing code from prior days)
Part 5 — Deliverable  (runnable program + expected output)
```

**Quality markers:**
- At least one Mermaid diagram (class hierarchy, data flow, or state machine)
- Trade-off table or bullet list comparing at least 2 design approaches
- Code shows entire class (not just snippets) — no `// ... rest of implementation`
- Integration with a prior day's deliverable explicitly shown

---

### Tier 4 — Mini-Project Day

**When:** A complete, tested, benchmarked implementation across multiple simulated files. Milestone day.

**Examples:** Days 13–14, 27–28, 41–42, 55–56, and all Phase 5 paired solver days (63–84)

| Metric | Minimum |
|--------|---------|
| Line count | **900** |
| Code examples | **6** (header + implementation + test + main + build + expected output) |
| Structure | **6-Part minimum** |
| Deliverable section | ✅ Required |
| Test cases | ✅ Required (≥ 2 named tests) |
| Benchmark results | ✅ Required (table with actual numbers) |

**Required content pattern:**
```
Part 1 — Project Overview  (what we are building, how it fits the roadmap)
Part 2 — File Structure  (directory layout + CMakeLists.txt)
Part 3 — Core Implementation  (primary library: .h + .cpp, fully written)
Part 4 — Tests  (Google Test / Catch2 test cases, named, with EXPECT_ assertions)
Part 5 — Benchmark  (timing table comparing baseline vs this day's result)
Part 6 — Deliverable  (build steps + expected terminal output)
```

**Quality markers:**
- A `cmake -S . -B build && cmake --build build` sequence is shown and works
- Test file uses Google Test or Catch2 with `EXPECT_EQ`, `EXPECT_NEAR`, or similar
- Benchmark table contains at least 2 columns (e.g., Before / After or N=1k / N=1M)
- No `// TODO` or placeholder comments left in code
- Connects back to Phase milestone (explicitly stated at top)

---

## Day-to-Tier Lookup Table

### Phase 1 — Modern C++ Foundation (Days 01–14)

| Day | Topic | Tier |
|-----|-------|------|
| 01 | Templates & Generic Programming | **T1** |
| 02 | C++20 Concepts & Constraints | **T1** |
| 03 | Mesh-to-Field Relationship | **T2** |
| 04 | CRTP — Static Polymorphism | **T2** |
| 05 | Policy-Based Design | **T2** |
| 06 | Smart Pointers | **T1** |
| 07 | Move Semantics | **T2** |
| 08 | Perfect Forwarding | **T1** |
| 09 | Expression Templates Part 1 | **T2** |
| 10 | C++20 Modules — Replacing Header Files | **T3** |
| 11 | C++20 Ranges | **T1** |
| 12 | Type Traits & SFINAE | **T2** |
| 13 | Mini-Project Part 1 | **T4** |
| 14 | Mini-Project Part 2 | **T4** |

### Phase 2 — Data Structures & Memory (Days 15–28)

| Day | Topic | Tier |
|-----|-------|------|
| 15 | LDU Matrix Format | **T2** |
| 16 | LDU Addressing | **T2** |
| 17 | Cache-Friendly LDU Multiply | **T3** |
| 18 | Sparse Matrix Assembly | **T3** |
| 19 | Cache Access Patterns | **T2** |
| 20 | Zero-Copy Views with `std::span` | **T2** |
| 21 | Flat Arrays & Offsets | **T2** |
| 22 | Modern Hashing | **T2** |
| 23 | Polymorphic Memory Resources (PMR) | **T3** |
| 24 | Mesh Topology Storage | **T2** |
| 25 | Memory Alignment | **T2** |
| 26 | Matrix Boundary Conditions | **T3** |
| 27 | Mini-Project Part 1 | **T4** |
| 28 | Mini-Project Part 2 | **T4** |

### Phase 3 — Architecture & Build Systems (Days 29–42)

| Day | Topic | Tier |
|-----|-------|------|
| 29 | Modern CMake Part 1 | **T2** |
| 30 | Modern CMake Part 2 | **T2** |
| 31 | The Modern Factory Pattern | **T3** |
| 32 | Plugin Self-Registration | **T3** |
| 33 | Configuration I/O — JSON | **T2** |
| 34 | Dynamic Configuration — Factory + JSON | **T3** |
| 35 | The Object Registry | **T3** |
| 36 | Time & State Control | **T3** |
| 37 | Boundary Condition Interface | **T3** |
| 38 | Modern Error Handling | **T2** |
| 39 | Dependency Management — FetchContent | **T2** |
| 40 | Logging — `spdlog` | **T2** |
| 41 | Mini-Project Part 1 | **T4** |
| 42 | Mini-Project Part 2 | **T4** |

### Phase 4 — Performance Optimization (Days 43–56)

| Day | Topic | Tier |
|-----|-------|------|
| 43 | Profiling Workflows | **T2** |
| 44 | Flame Graphs | **T2** |
| 45 | Auto-Vectorization | **T2** |
| 46 | SIMD Intrinsics | **T3** |
| 47 | OpenMP Basics | **T2** |
| 48 | C++17 Parallel Algorithms | **T2** |
| 49 | False Sharing & Reductions | **T3** |
| 50 | Allocation Profiling | **T2** |
| 51 | Eliminating Temporaries | **T3** |
| 52 | Mesh Bandwidth Optimization | **T3** |
| 53 | Parallel I/O Concepts | **T2** |
| 54 | MPI Fundamentals | **T2** |
| 55 | Mini-Project Part 1 | **T4** |
| 56 | Mini-Project Part 2 | **T4** |

### Phase 5 — VOF-Ready CFD Component (Days 57–84)

| Day | Topic | Tier |
|-----|-------|------|
| 57 | Project Architecture — CMake Structure Part 1 | **T3** |
| 58 | Project Architecture — CMake Structure Part 2 | **T3** |
| 59 | 1D Mesh Implementation Part 1 | **T3** |
| 60 | 1D Mesh Implementation Part 2 | **T3** |
| 61 | Geometric Fields Part 1 | **T3** |
| 62 | Geometric Fields Part 2 | **T3** |
| 63 | Equation Assembly — `fvMatrix` Part 1 | **T4** |
| 64 | Equation Assembly — `fvMatrix` Part 2 | **T4** |
| 65 | Temporal Operators — `fvm::ddt` Part 1 | **T3** |
| 66 | Temporal Operators — `fvm::ddt` Part 2 | **T3** |
| 67 | Spatial Operators — `div` and `laplacian` Part 1 | **T4** |
| 68 | Spatial Operators — `div` and `laplacian` Part 2 | **T4** |
| 69 | Linear Solver Integration — PCG Part 1 | **T4** |
| 70 | Linear Solver Integration — PCG Part 2 | **T4** |
| 71 | SIMPLE Loop — Pressure-Velocity Part 1 | **T4** |
| 72 | SIMPLE Loop — Pressure-Velocity Part 2 | **T4** |
| 73 | Rhie-Chow Interpolation Part 1 | **T4** |
| 74 | Rhie-Chow Interpolation Part 2 | **T4** |
| 75 | Scalar Transport & Flux Limiters Part 1 | **T4** |
| 76 | Scalar Transport & Flux Limiters Part 2 | **T4** |
| 77 | Boundedness Testing — VOF `alpha` Part 1 | **T3** |
| 78 | Boundedness Testing — VOF `alpha` Part 2 | **T3** |
| 79 | Factory-Driven Source Terms Part 1 | **T3** |
| 80 | Factory-Driven Source Terms Part 2 | **T3** |
| 81 | VTK Output — ParaView Part 1 | **T3** |
| 82 | VTK Output — ParaView Part 2 | **T3** |
| 83 | Final Benchmark and Retrospective Part 1 | **T4** |
| 84 | Final Benchmark and Retrospective Part 2 | **T4** |

---

## Pre-Generation Spec (Before Writing)

When starting a new file, look up its tier and use this checklist to set generation targets:

```markdown
## Pre-Generation Spec — Day XX (Tier N)

- [ ] Tier: T1 / T2 / T3 / T4
- [ ] Target line count: ___ (minimum from tier table)
- [ ] Required parts: ___ parts
- [ ] Code examples needed: ___ blocks
- [ ] Benchmark/profile required: Yes / No
- [ ] Mermaid diagram required: Yes (T3+) / No
- [ ] Test cases required: Yes (T4) / No
- [ ] Connected to prior day: Day ___ (deliverable reference)
- [ ] Phase milestone: ___
```

---

## Post-Generation QC (After Writing)

After generating or revising a file, run this checklist:

### Quick Scan (all tiers)

```bash
# 1. Count lines
wc -l <file.md>

# 2. Count code blocks (must be even)
grep -c '^\`\`\`' <file.md>

# 3. Check for deliverable section
grep -q 'Deliverable' <file.md> && echo "✅ Deliverable found" || echo "❌ Missing Deliverable"

# 4. Check for TODO placeholders
grep -n 'TODO\|// \.\.\.' <file.md> && echo "⚠️ Incomplete code" || echo "✅ Clean"
```

### Tier-Specific Checks

| Check | T1 | T2 | T3 | T4 |
|-------|----|----|----|----|
| Line count ≥ minimum | 350 | 550 | 750 | 900 |
| Code blocks ≥ N | 3 | 4 | 5 | 6 |
| Parts ≥ N | 4 | 5 | 5 | 6 |
| Has Deliverable | ✅ | ✅ | ✅ | ✅ |
| Has benchmark/numbers | — | ✅ | ✅ | ✅ |
| Has Mermaid diagram | — | — | ✅ | ✅ |
| Has test cases | — | — | — | ✅ |
| Has benchmark table | — | — | — | ✅ |
| Prior day referenced | — | ✅ | ✅ | ✅ |

### Revision Trigger Rules

A file **must be revised** if any of the following are true:

| Condition | Action |
|-----------|--------|
| Line count < minimum for its tier | Expand weakest part first |
| Missing Deliverable section | Add at end of last Part |
| Code blocks are unbalanced (odd count) | Find and close unclosed fence |
| Contains `// TODO` or `// ... rest` | Complete the implementation |
| Missing Mermaid diagram (T3/T4) | Add to Part 2 or Part 1 |
| Missing benchmark table (T4) | Add to Part 5 |
| Missing test cases (T4) | Add Google Test or Catch2 block |
| Prior day's deliverable not referenced | Add one-line reference at top or in Part 1 |

---

## Revision Priority Order

When a file needs expansion, add content in this order:

1. **Complete any `// TODO` code** — half-finished code is worse than no code
2. **Expand the shortest Part** — find the weakest section first
3. **Add benchmark/numbers** — replace vague claims with real data
4. **Add Mermaid diagram** — if T3/T4 and diagram is missing
5. **Add test cases** — if T4 and tests are missing
6. **Add prior day reference** — if integration is missing

---

## Integration with Workflow

### Before `/create-day`

1. Look up the day in the Day-to-Tier table above
2. Note the tier's minimum line count and required sections
3. Pass the tier spec as a constraint in the generation prompt:

```
Day: XX | Tier: T2 | Target: 550+ lines | 4 code examples | Benchmark required
```

### After content is generated

1. Run the Quick Scan commands above
2. Check the Tier-Specific table for the file's tier
3. If any Revision Trigger fires → revise immediately before committing
4. Only mark as `✅` in PLAN.md after all checks pass

---

## Common Failure Patterns

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Concept day written at T2 length | File hits 550 lines but concept is T1 | Accept — T1 minimum is 350. Over is fine. |
| Architecture day written at T1 length | T3 file < 550 lines | Must expand — T3 minimum is 750 |
| Missing deliverable | File ends at Part 4 content with no compile/run instruction | Add `## Deliverable` at end |
| Code snippets too small | Each block is 5–10 lines, concepts not illustrated | Replace with full working examples |
| No numbers | Claims "faster" without data | Add actual timings or a benchmark table |
| Integration gap | Never mentions prior days | Add a one-paragraph "connecting to Day N" at Part 1 or top |

---

*See also: `cfd-standards.md`, `source-first.md`, `verification-gates.md`*
*This file is used by: `/create-day`, content-creation agent, qc-agent*
